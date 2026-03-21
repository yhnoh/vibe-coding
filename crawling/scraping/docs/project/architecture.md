# 아키텍처

## 시스템 구조

```
[사용자/클라이언트]
       │
       ▼
[FastAPI 서버] ──httpx──▶ [네이버 스포츠 API]
  (api/)                   api-gw.sports.naver.com
       │
[Scrapy 크롤러] ──────────▶ [네이버 스포츠 API]
  (scrapying/)              api-gw.sports.naver.com
       │
       ├──Playwright──────▶ [네이버 스포츠 웹]
       │                    m.sports.naver.com
       ▼
[LoggingPipeline]
  (향후 S3/DB 저장)
```

## 컴포넌트

### FastAPI 서버 (`api/`)
- 역할: 네이버 API를 프록시하여 KBO 데이터를 클라이언트에 제공
- httpx로 비동기 API 호출
- Pydantic 모델로 응답 스키마 정의
- Swagger UI 자동 생성

### Scrapy 크롤러 (`scrapying/`)
- 역할: 배치 데이터 수집, HTML 크롤링
- API 기반 Spider: 네이버 API 직접 호출
- Playwright 기반 Spider: API가 없는 데이터 (라인업 등)
- Pipeline으로 수집 데이터 처리

### 관계
- FastAPI와 Scrapy는 독립적으로 동작
- 동일한 네이버 API를 사용하지만 URL/params 로직이 각각 존재
- 향후 Scrapy로 수집 → DB 저장 → FastAPI로 DB 조회 구조로 전환 가능

## 기술 스택

| 분류 | 기술 | 버전 | 용도 |
|------|------|------|------|
| 언어 | Python | 3.14 | |
| 패키지 관리 | uv | 0.10 | |
| 크롤링 | Scrapy | 2.14 | Spider 프레임워크 |
| 브라우저 | Playwright | - | HTML 크롤링 (라인업) |
| API 서버 | FastAPI | 0.135 | REST API |
| HTTP 클라이언트 | httpx | 0.28 | 비동기 API 호출 |
| 스키마 | Pydantic | 2.12 | 응답 모델, Swagger |

## 디렉토리 구조

```
scraping/
├── Makefile
├── pyproject.toml
├── api/
│   ├── main.py
│   └── routers/
│       ├── naversports_kbo_router.py
│       ├── naversports_kbo_client.py
│       └── naversports_kbo_schemas.py
├── scrapying/
│   ├── scrapy.cfg
│   └── scrapying/
│       ├── constants.py
│       ├── items.py
│       ├── pipelines.py
│       ├── settings.py
│       └── spiders/
│           └── baseball/
└── docs/
    ├── feature/          # 비즈니스 feature 문서
    ├── project/          # 프로젝트 전체 문서
    └── api-analysis/     # API 명세
```
