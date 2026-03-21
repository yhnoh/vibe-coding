# 2026-03-21 KBO 크롤링 프로젝트 작업 정리

## 1. Spider 구조 개편

### 디렉토리 구조 변경
- `spiders/kbo_schedule.py` → `spiders/baseball/naversports_kbo_schedule_games.py`
- 종목별 폴더(`baseball/`) + 데이터소스 접두사(`naversports_`) 네이밍 규칙 적용
- Scrapy가 하위 패키지를 자동 탐색하므로 `settings.py`의 `SPIDER_MODULES` 변경 불필요

### 네이밍 규칙 확정
- 파일명: `{데이터소스}_{종목}_{API경로}.py`
- Spider name: 파일명과 동일
- 클래스명: PascalCase + Spider 접미사

## 2. Spider 구현 (총 6개)

### API 기반 Spider (5개)

| Spider | API 엔드포인트 | 파라미터 |
|--------|---------------|----------|
| `naversports_kbo_schedule_games` | `/schedule/games` | `from_date`, `to_date` |
| `naversports_kbo_schedule_games_record` | `/schedule/games/{gameId}/record` | `game_id` |
| `naversports_kbo_seasons_teams` | `/statistics/.../seasons/{s}/teams` | `season` |
| `naversports_kbo_seasons_players_hitter` | `/statistics/.../seasons/{s}/players?playerType=HITTER` | `season`, `team_code` |
| `naversports_kbo_seasons_players_pitcher` | `/statistics/.../seasons/{s}/players?playerType=PITCHER` | `season`, `team_code` |

### Playwright 기반 Spider (1개)

| Spider | 페이지 | 파라미터 |
|--------|--------|----------|
| `naversports_kbo_schedule_games_lineup` | `/game/{gameId}/lineup` | `game_id` |

- 라인업 전용 API가 없어서 Playwright로 페이지를 렌더링 후 JavaScript로 DOM 파싱
- playerId, 선수명, 포지션, 타순 추출 가능

### 모든 파라미터 필수화
- 기존: 기본값 존재 (오늘 날짜, 현재 연도 등)
- 변경: 모든 파라미터 필수, 미지정 시 `ValueError` 발생

## 3. 파이프라인 변경

- `S3UploadPipeline` → `LoggingPipeline`으로 교체
- INFO: 수집 요약 로그, DEBUG: raw JSON 전체 출력
- S3 자격증명 없이도 개발 가능

## 4. FastAPI 서버 구현

### 구조
```
api/
├── main.py                          # FastAPI app + router 등록
└── routers/
    ├── naversports_kbo_router.py     # /kbo prefix 엔드포인트
    ├── naversports_kbo_client.py     # httpx로 네이버 API 호출
    └── naversports_kbo_schemas.py    # Pydantic 응답 모델
```

### 엔드포인트
| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/kbo/schedule/games` | 경기일정 |
| GET | `/kbo/schedule/games/{game_id}/record` | 경기 기록 |
| GET | `/kbo/seasons/{season}/teams` | 팀 순위 |
| GET | `/kbo/seasons/{season}/players/hitter` | 타자 기록 |
| GET | `/kbo/seasons/{season}/players/pitcher` | 투수 기록 |

### 실행 방법
```bash
make api       # 일반 실행
make api-dev   # 개발 모드 (자동 재시작)
make api-stop  # 서버 종료
```

- Swagger UI: http://localhost:8000/docs

## 5. API 분석 및 발견사항

### Playwright로 네이버 스포츠 API 리버스 엔지니어링
- 경기일정, 팀정보, 타자/투수 기록: API 엔드포인트 확인
- 경기 기록(박스스코어): `/schedule/games/{gameId}/record` 발견
- 라인업: API 없음, HTML DOM에서만 제공

### 경기 기록 API 주요 발견
- 타자 박스스코어: `playerCode` 필드로 선수 ID 확인 가능
- 투수 박스스코어: `pcode` 필드로 선수 ID 확인 가능
- `substituteIn: true`로 교체 선수 구분 가능
- 투수 배열 첫 번째가 선발투수

### 네이버 API 제약사항 확인
- 인증 불필요 (비인증 공개 API)
- User-Agent, Referer 제한 없음
- Rate Limit 헤더 없음 (연속 10회 요청 성공)
- CORS: 서버 사이드 요청이라 무관

## 6. 문서 작성

- `docs/api-analysis/naversports-kbo-api.md`: 5개 API 엔드포인트 명세
- `README.md`: API 서버 + Scrapy 실행 방법, 프로젝트 구조
- `Makefile`: FastAPI 서버 실행 명령어

## 7. 프로덕션 대비 남은 작업

| 항목 | 상태 |
|------|------|
| 에러 처리 (타임아웃, 4xx/5xx) | 미구현 |
| 재시도 전략 | Scrapy 기본값만 |
| 모니터링/알림 (Slack, CloudWatch) | 미구현 |
| 데이터 저장 (S3 or DB) | LoggingPipeline만 |
| 스케줄링 (EventBridge + ECS Task) | 미구현 |
| 환경 분리 (local/dev/prod) | 미구현 |
| 테스트 코드 | 미구현 |
| API 변경 감지 | 미구현 |
