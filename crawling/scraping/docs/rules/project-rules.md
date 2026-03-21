# 프로젝트 규칙

## Scrapy Spider

- 파라미터는 전부 필수값. 기본값 사용 금지. 미지정 시 ValueError 발생
- parse()에서 데이터를 가공하지 않는다. 원본 JSON을 그대로 CrawledItem에 전달
- URL 쿼리 파라미터는 dict로 관리 (URL 인코딩 문자열 직접 작성 금지)
- docstring에 실행 방법과 동작 흐름 작성

## FastAPI

- 엔드포인트에 response_model 필수 (Pydantic 모델)
- APIRouter로 도메인별 분리

## 네이밍 규칙

- Spider 파일명: `{데이터소스}_{종목}_{API경로}.py` (예: `naversports_kbo_schedule_games.py`)
- Spider name: 파일명과 동일
- Spider 클래스명: PascalCase + Spider 접미사
- CrawledItem의 data_type: Spider name과 동일
- CrawledItem의 source: 데이터소스명 (예: `naversports`)
- Spider는 종목별 디렉토리에 배치 (`spiders/baseball/`, `spiders/soccer/` 등)

## 문서 업데이트 규칙

작업 완료 시 아래 문서 구조에 따라 변경사항을 반영한다.

| 문서 | 위치 | 업데이트 방식 |
|------|------|-------------|
| **feature 문서** | `docs/feature/{도메인}/` | 아래 섹션별 규칙 참고 |
| **아키텍처** | `docs/project/architecture.md` | 구조 변경 시 최신화 |
| **환경 설정** | `docs/project/environments.md` | 설정 변경 시 최신화 |
| **알려진 이슈** | `docs/project/known-issues.md` | 발견 시 추가, 해결 시 업데이트 |

### feature 문서 목차 및 업데이트 규칙

| 섹션 | 업데이트 방식 |
|------|-------------|
| **개요** | 최신 상태로 덮어쓴다 |
| **기능별 유저 플로우** | 최신 상태를 유지한다 (변경 시 수정, 신규 시 추가) |
| **작업 내역** | 날짜별로 추가한다 (이력 유지) |
| **프로덕션 체크리스트** | 상태를 업데이트한다 (미구현→진행중→완료) |

## CLAUDE.md 수정 정책

- CLAUDE.md는 함부로 수정하지 않는다
- 수정이 필요하면 제안만 하고, 사용자 승인 후 수정한다
