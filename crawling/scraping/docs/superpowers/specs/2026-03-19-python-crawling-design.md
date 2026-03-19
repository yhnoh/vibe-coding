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

## 데이터 소스 확장

외부 API 업체를 사용하게 될 경우:
- Scrapy에 새 Spider 추가 또는 별도 수집 스크립트
- S3에 같은 경로 규칙으로 저장
- Spring Batch는 새 파서만 추가

**S3가 수집과 가공 사이의 계약(contract) 역할.**

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