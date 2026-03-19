# CLAUDE.md

## 프로젝트 개요
데이터를 수집하는 Scrapy 크롤링 프로젝트

## 프로젝트 구조
- `scrapying/` - Scrapy 프로젝트 루트 (scrapy 명령어는 여기서 실행)
- `scrapying/scrapying/constants.py` - 크롤링 URL 목록 관리 (CrawlTarget + url_template)
- `scrapying/scrapying/pipelines.py` - S3 업로드 파이프라인
- `scrapying/scrapying/spiders/api_capture.py` - 웹페이지에서 API URL 탐지
- `scrapying/scrapying/spiders/api_call.py` - API 직접 호출 및 데이터 수집
- `scrapying/scrapying/spiders/html_crawl.py` - HTML 크롤링 Spider
- `scrapying/Dockerfile` - Docker 이미지 빌드
- `scrapying/tests/` - 테스트 코드
- `docs/` - 프로젝트 문서
- `docs/api-analysis/` - API 탐지 및 응답 구조 분석 문서

## 명령어 실행 위치
scrapy 명령어는 반드시 `scrapy.cfg`가 있는 디렉토리에서 실행
```bash
cd scrapying
scrapy crawl <스파이더명>
```

## 개발 규칙
- 스파이더 추가 시 docstring에 실행 방법과 동작 흐름 작성

## 패키지 관리
- 패키지 추가: `uv add <패키지명>`
- 실행: `uv run scrapy crawl <스파이더명>`

## 참고 문서
- `docs/NOTES.md` - Scrapy 전반 개념 및 사용법
- `docs/feature/naver-kbo-crawling.md` - 현재 작업 진행 상황