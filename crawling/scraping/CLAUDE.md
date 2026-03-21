# CLAUDE.md

## 프로젝트 개요
네이버 스포츠 KBO API에서 야구 데이터를 수집(Scrapy)하고 조회(FastAPI)하는 프로젝트

## 프로젝트 구조
- `api/` - FastAPI 서버
- `api/routers/` - APIRouter 엔드포인트, httpx 클라이언트, Pydantic 스키마
- `scrapying/` - Scrapy 프로젝트 루트 (scrapy 명령어는 여기서 실행)
- `scrapying/scrapying/spiders/baseball/` - KBO 야구 Spider
- `scrapying/scrapying/pipelines.py` - LoggingPipeline
- `docs/` - 프로젝트 문서
- `docs/api-analysis/` - API 명세 문서

## 코딩 컨벤션

### Python
- 모든 함수에 타입 힌트 필수 (파라미터, 반환값, 클래스 변수)
- 네이밍: snake_case 엄수 (camelCase 사용 금지)
- API 쿼리 파라미터만 camelCase 허용 (네이버 API 스펙에 맞춤)
- 불필요한 import는 즉시 제거
- URL 쿼리 파라미터는 dict로 관리 (URL 인코딩 문자열 직접 작성 금지)

### Scrapy Spider
- 파라미터는 전부 필수값. 기본값 사용 금지. 미지정 시 ValueError 발생
- parse()에서 데이터를 가공하지 않는다. 원본 JSON을 그대로 CrawledItem에 전달
- docstring에 실행 방법과 동작 흐름 작성

### FastAPI
- 엔드포인트에 response_model 필수 (Pydantic 모델)
- APIRouter로 도메인별 분리

## 네이밍 규칙
- Spider 파일명: `{데이터소스}_{종목}_{API경로}.py` (예: `naversports_kbo_schedule_games.py`)
- Spider name: 파일명과 동일
- Spider 클래스명: PascalCase + Spider 접미사
- CrawledItem의 data_type: Spider name과 동일
- CrawledItem의 source: 데이터소스명 (예: `naversports`)
- Spider는 종목별 디렉토리에 배치 (`spiders/baseball/`, `spiders/soccer/` 등)

## Git
- .idea/, .vscode/, __pycache__/, .DS_Store 는 커밋하지 않는다
- 커밋 메시지는 한국어로 작성
- conventional commit 형식 사용 (feat:, fix:, refactor:, docs:, chore:)

## 문서화
- Spider 추가 시 반드시:
  1. docstring에 실행 방법과 동작 흐름 작성
  2. `docs/api-analysis/naversports-kbo-api.md`에 API 명세 추가
  3. `README.md`의 Spider 목록과 엔드포인트 테이블 업데이트

## 명령어 실행 위치
- scrapy: `cd scrapying && uv run scrapy crawl <스파이더명>`
- FastAPI: `make api` 또는 `make api-dev`

## 패키지 관리
- 패키지 추가: `uv add <패키지명>`
- 전체 설치: `uv sync`

## 세션 마무리 규칙
- 하루 작업 종료 시 반복된 지시 패턴을 분석하여 자동화 방향을 제시한다
  - 어떤 지시가 몇 번 반복되었는지 정리
  - CLAUDE.md에 추가할 수 있는 항목 제안
  - ~/.claude/CLAUDE.md (글로벌)로 빼야 할 항목 제안
  - hooks, 스킬, MCP 등 Claude Code 설정으로 자동화할 수 있는 항목 제안
  - Claude Code 외적으로 자동화할 수 있는 방법도 제안 (CI/CD, lint 설정 등)

## 작업 마무리 규칙
- 작업 내역을 도메인별 릴리즈 문서(`docs/feature/{도메인}/{파일명}.md`)에 반영한다
- 릴리즈 문서 목차: 개요, 기능별 유저 플로우, 작업 내역(날짜별), 프로덕션 체크리스트
- 문서 업데이트 방식:
  - **개요**: 프로젝트 설명이 변경되면 최신 상태로 덮어쓴다
  - **기능별 유저 플로우**: 항상 최신 상태를 유지한다. 기능이 변경되면 해당 항목을 수정한다. 새 기능이면 추가한다.
  - **작업 내역**: 날짜별로 변경사항을 추가한다 (이력 유지, append)
  - **프로덕션 체크리스트**: 진행 상태를 매 세션마다 업데이트한다 (미구현→진행중→완료)
- 단순 append가 아니라 기존 문서와 결합하여 읽는 사람이 항상 최신 상태를 파악할 수 있게 한다.
- 작업 중 발견한 기술 부채, 개선 포인트 정리
- 다음 세션에서 이어서 할 작업 목록 정리
- 프로젝트 전체 문서(`docs/project/`)도 변경사항이 있으면 함께 업데이트한다

## 문서 구조

### 비즈니스 feature 문서 (`docs/feature/{도메인}/`)
- 비즈니스 기능 단위로 관리 (예: kbo-crawling, kbo-schedule-alert 등)
- 목차: 개요, 기능별 유저 플로우, 작업 내역(날짜별), 프로덕션 체크리스트

### 프로젝트 전체 문서 (`docs/project/`)
- 프로젝트 공통 사항 관리
- `architecture.md` - 시스템 구조, 컴포넌트 관계, 기술 스택
- `environments.md` - 환경 설정 (local/dev/prod), 인프라 구성
- `known-issues.md` - 알려진 이슈, 제약사항, 기술 부채

### API 명세 (`docs/api-analysis/`)
- 외부 API 리버스 엔지니어링 결과

## 참고 문서
- `docs/api-analysis/naversports-kbo-api.md` - 네이버 스포츠 KBO API 명세
- `docs/feature/` - 비즈니스 feature 문서
- `docs/project/` - 프로젝트 전체 문서
