# 웹 크롤링 아키텍처 설계: Python(Scrapy) 방식

## 개요

Python(Scrapy)을 크롤링 전용으로 사용하고, Spring은 데이터 가공/서빙을 담당하는 아키텍처.
핵심 원칙: **Python은 "바보 수집기"로 유지** — 크롤링 + S3 업로드만, 비즈니스 로직 없음.

## 전체 아키텍처

```
[데이터 수집층]              [저장층]           [가공/서빙층]

Scrapy (ECS Fargate)  ──→  S3 (원본)  ──→  Spring Batch (파싱/DB 저장)
                                           Spring API (데이터 서빙)
```

## 역할 분리

| 계층 | 역할 | 하지 않는 것 |
|------|------|-------------|
| Scrapy | 웹 크롤링 → 원본 그대로 S3 업로드 | 파싱, 가공, 비즈니스 로직 |
| S3 | 원본 데이터 보관 (JSON/HTML) | - |
| Spring Batch | S3에서 원본 읽기 → 파싱 → DB 저장 | 크롤링 |
| Spring API | DB 데이터 조회/서빙 | 크롤링, 파싱 |

## S3 경로 규칙

```
s3://bucket/raw/{source}/{data-type}/{yyyy}/{MM}/{dd}/{timestamp}.json
```

예시:
```
raw/naver-sports/kbo-team-rank/2026/03/19/1710842400.json
raw/naver-sports/kbo-hitter/2026/03/19/1710842400.html
raw/external-api/some-provider/2026/03/19/1710842400.json
```

- **source**: 데이터 출처 (naver-sports, external-api 등)
- **data-type**: 데이터 종류
- 크롤링이든 외부 API든 같은 경로 규칙 → Spring Batch에서 동일한 파이프라인으로 처리

## Scrapy 프로젝트 구조

```
scrapying/
├── scrapy.cfg
└── scrapying/
    ├── settings.py
    ├── constants.py        # URL 목록 관리
    ├── items.py
    ├── pipelines.py        # S3 업로드 파이프라인
    ├── middlewares.py
    └── spiders/
        ├── api_capture.py  # API URL 탐지 (Playwright)
        ├── api_call.py     # API 직접 호출
        └── html_crawl.py   # HTML 페이지 크롤링 (Playwright)
```

### Spider 역할
- **api_capture**: Playwright로 웹페이지를 열어 JS가 호출하는 API URL을 탐지
- **api_call**: 탐지된 API URL을 직접 HTTP 호출하여 JSON 수집
- **html_crawl**: JS 렌더링된 HTML 페이지를 그대로 수집

### Pipeline 역할
- Spider가 yield한 데이터를 S3에 업로드
- Spider는 S3를 모름. Pipeline이 업로드 책임

## 배포: ECS Fargate

### 왜 ECS Fargate인가
- Playwright(Chromium)가 필요하므로 Lambda는 부적합 (이미지 크기, 메모리, 콜드 스타트)
- 상시 서버 불필요 — 실행 시만 컨테이너를 띄우고 종료
- 비용 효율적

### Dockerfile (개략)

```dockerfile
FROM python:3.14-slim

RUN pip install playwright && playwright install chromium --with-deps

COPY . /app
WORKDIR /app/scrapying

ENTRYPOINT ["scrapy"]
CMD ["crawl", "api_call"]
```

### 실행 방식

| 실행 주체 | 방식 |
|-----------|------|
| EventBridge 스케줄 | 정해진 시간에 ECS RunTask 호출 |
| Spring 서버 | AWS SDK로 ECS RunTask 호출 (command 동적 지정) |
| 수동 | AWS CLI `aws ecs run-task --overrides ...` |

명령어 오버라이드로 하나의 이미지에서 다른 Spider/파라미터 실행:
```json
{
  "containerOverrides": [{
    "command": ["scrapy", "crawl", "api_call", "-a", "url=https://..."]
  }]
}
```

## Spring Batch 흐름

```
1. 스케줄러 실행 (또는 수동)
2. S3에서 미처리 파일 목록 조회
3. 원본 파일 읽기 (JSON/HTML)
4. source/data-type에 맞는 파서로 가공
5. DB 저장
6. 처리 완료 기록
```

## 크롤링 대상 URL 목록

### Naver Sports KBO

| 데이터 | URL | 비고 |
|--------|-----|------|
| 경기일정 | `https://m.sports.naver.com/kbaseball/schedule/index?category=kbo&date={yyyy-MM-dd}` | 날짜별 경기 일정/결과 |
| 팀정보 | `https://m.sports.naver.com/kbaseball/record/kbo?tab=teamRank` | 팀 순위 |
| 팀기록 | `https://m.sports.naver.com/kbaseball/record/kbo?seasonCode={yyyy}&tab=teamRecord` | 팀별 시즌 성적 |
| 타자목록 | `https://m.sports.naver.com/kbaseball/record/kbo?tab=hitter` | 전체 타자 성적 |
| 팀별 타자목록 | `https://m.sports.naver.com/kbaseball/record/kbo?tab=hitter&teamCode={teamCode}` | 팀별 타자 성적 |
| 투수목록 | `https://m.sports.naver.com/kbaseball/record/kbo?tab=pitcher` | 전체 투수 성적 |
| 팀별 투수목록 | `https://m.sports.naver.com/kbaseball/record/kbo?tab=pitcher&teamCode={teamCode}` | 팀별 투수 성적 |

**참고:** 위 URL은 웹 페이지 URL이며, 실제 데이터는 JS 렌더링 후 내부 API(`api-gw.sports.naver.com`)를 호출하여 가져온다. `api_capture` 스파이더로 각 페이지의 실제 API 엔드포인트를 탐지해야 한다.

### 팀 코드 목록

| 팀명 | teamCode |
|------|----------|
| KIA 타이거즈 | KIA |
| 삼성 라이온즈 | SS |
| LG 트윈스 | LG |
| 두산 베어스 | OB |
| KT 위즈 | KT |
| SSG 랜더스 | SK |
| 롯데 자이언츠 | LT |
| 한화 이글스 | HH |
| NC 다이노스 | NC |
| 키움 히어로즈 | WO |

> 팀 코드는 네이버 스포츠에서 사용하는 코드이며, 실제 코드는 api_capture 실행 후 확인 필요

## 데이터 소스 확장

외부 API 업체를 사용하게 될 경우:
- Scrapy에 새 Spider 추가 또는 별도 수집 스크립트
- S3에 같은 경로 규칙으로 저장
- Spring Batch는 새 파서만 추가

**S3가 수집과 가공 사이의 계약(contract) 역할.**

## 구현 순서

API 구조를 먼저 파악한 후 코드를 설계한다.

```
1. 테스트 환경 셋업 (pytest, boto3, moto)
2. 페이지별 API 탐지 및 응답 구조 분석
   - api_capture로 각 페이지의 실제 API 엔드포인트 탐지
   - 탐지된 API를 직접 호출하여 응답 JSON 구조 파악
   - 페이지네이션, 필수 헤더, 팀 코드 등 확인
   - 결과를 문서화
3. 파악된 API 구조를 기반으로 constants.py, Item, Pipeline 설계 및 구현
4. Spider 구현 (api_call, html_crawl)
5. Dockerfile 작성
```

## 추후 구현 항목

현재 범위에서는 제외하되, 향후 필요한 기능들.

### api_capture 결과 저장
- 현재: 로그 출력만 → 수동으로 constants.py에 등록
- 개선: 탐지 결과를 파일 또는 DB에 자동 저장
- API URL 변경 자동 감지 기능

### 에러/실패 처리
- API 호출 실패 시 재시도 전략 (Scrapy 기본 retry 외 추가 로직)
- S3 업로드 실패 시 처리
- IP 차단 대응 (프록시 로테이션 등)
- 실패 알림 체계 (Slack, 이메일 등)

### 크롤링 실행 기록
- 언제, 어떤 Spider가, 어떤 URL을 크롤링했는지 추적
- 크롤링 정상 완료 여부 확인

### S3 미처리 파일 구분 (Spring Batch 쪽)
- 이미 처리한 파일과 새 파일을 어떻게 구분할 것인가
- 방안: 처리 완료 후 S3 파일 이동 (`raw/` → `processed/`), 또는 DB에 처리 기록

### 데이터 검증
- 빈 응답, 깨진 JSON, 에러 페이지 등 기본 검증
- 예상 필드 누락 감지

### 중복 수집 방지
- 같은 데이터를 여러 번 크롤링할 때 S3에 중복 파일이 쌓이는 문제
- 덮어쓰기 또는 중복 체크 전략

### constants.py → DB 전환
- 현재: CrawlTarget을 코드로 관리
- 향후: Spring DB에서 크롤링 대상을 관리하고 Scrapy 실행 시 파라미터로 전달
- CrawlTarget 필드를 DB 테이블 컬럼으로 매핑

### 크롤링 오케스트레이션
- 1단계 크롤링 결과(경기일정)가 2단계 크롤링의 입력이 되는 순서 관리
- Spring Batch Step으로 오케스트레이션

## 엣지 케이스

| 항목 | 설명 | 대응 시점 |
|------|------|----------|
| 페이지네이션 | 타자/투수 목록이 여러 페이지일 수 있음 | API 탐지 시 확인 |
| API 인증/헤더 | Referer, User-Agent 등 필수 헤더 | API 탐지 시 확인 |
| 빈 응답 | 경기 없는 날짜, 비시즌 기간 | 기본 검증으로 처리 |
| 팀 코드 정확성 | 실제 네이버 팀 코드와 다를 수 있음 | API 탐지 시 확인 |
| seasonCode 동적 결정 | 매년 바뀌는 시즌 코드 | 실행 시 파라미터로 전달 |
| API URL 변경 | 네이버 내부 API 구조 변경 가능 | 추후 자동 감지 |

## 트레이드오프

### 장점
- Scrapy가 크롤링에 필요한 기능을 기본 제공 (throttling, retry, dedup, middleware, pipeline)
- scrapy-playwright 통합이 성숙함
- 적은 코드량으로 크롤링 구현 가능
- 크롤링과 서빙의 생명주기가 분리되어 운영이 자연스러움

### 단점
- Python + Spring 두 스택 관리 필요
- 별도 Docker 이미지, ECR, ECS Task Definition 관리
- 팀에 Python 읽을 수 있는 사람 필요
- Python 환경 디버깅이 Spring 개발자에게 생소할 수 있음