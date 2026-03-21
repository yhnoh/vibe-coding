# KBO 크롤링

## 개요

네이버 스포츠 KBO API에서 야구 데이터를 수집(Scrapy)하고 조회(FastAPI)하는 시스템.
비공식 API를 리버스 엔지니어링하여 경기일정, 팀정보, 선수기록, 경기기록, 라인업 데이터를 수집한다.

### 데이터 소스
- API: `api-gw.sports.naver.com` (비인증 공개 API)
- HTML: `m.sports.naver.com` (Playwright 크롤링)

### 기술 스택
- Scrapy + Playwright (크롤링)
- FastAPI + httpx (API 서버)
- uv (패키지 관리)

---

## 기능별 유저 플로우

### 1. 경기일정 조회
```
사용자 → FastAPI GET /kbo/schedule/games?from_date=...&to_date=...
       → httpx → api-gw.sports.naver.com/schedule/games
       → JSON 응답 반환 (경기 목록, 스코어, 선발투수 등)
```
- Scrapy: `naversports_kbo_schedule_games -a from_date=... -a to_date=...`

### 2. 경기 기록 조회 (박스스코어)
```
사용자 → FastAPI GET /kbo/schedule/games/{game_id}/record
       → httpx → api-gw.sports.naver.com/schedule/games/{game_id}/record
       → JSON 응답 반환 (타자/투수 박스스코어, playerCode 포함)
```
- Scrapy: `naversports_kbo_schedule_games_record -a game_id=...`
- 선발/교체 구분: `substituteIn: true` (교체), 투수 배열 첫 번째 = 선발

### 3. 팀 순위/기록 조회
```
사용자 → FastAPI GET /kbo/seasons/{season}/teams
       → httpx → api-gw.sports.naver.com/statistics/.../seasons/{season}/teams
       → JSON 응답 반환 (순위, 승률, 공격/수비 기록)
```
- Scrapy: `naversports_kbo_seasons_teams -a season=...`

### 4. 타자 선수 기록 조회
```
사용자 → FastAPI GET /kbo/seasons/{season}/players/hitter?team_code=...
       → httpx → api-gw.sports.naver.com/statistics/.../players?playerType=HITTER&teamCode=...
       → JSON 응답 반환 (타율, 홈런, OPS 등)
```
- Scrapy: `naversports_kbo_seasons_players_hitter -a season=... -a team_code=...`

### 5. 투수 선수 기록 조회
```
사용자 → FastAPI GET /kbo/seasons/{season}/players/pitcher?team_code=...
       → httpx → api-gw.sports.naver.com/statistics/.../players?playerType=PITCHER&teamCode=...
       → JSON 응답 반환 (ERA, 승, 탈삼진 등)
```
- Scrapy: `naversports_kbo_seasons_players_pitcher -a season=... -a team_code=...`

### 6. 라인업 크롤링 (Playwright)
```
Scrapy → Playwright → m.sports.naver.com/game/{game_id}/lineup
       → JavaScript로 DOM 파싱 → JSON 변환 (playerId, 선수명, 포지션, 타순)
```
- Scrapy: `naversports_kbo_schedule_games_lineup -a game_id=...`
- API가 없어서 HTML 크롤링 필요

---

## 작업 내역

### 2026-03-21

#### Spider 구현 (6개)

| Spider | API/페이지 | 파라미터 |
|--------|-----------|----------|
| `naversports_kbo_schedule_games` | `/schedule/games` | `from_date`, `to_date` |
| `naversports_kbo_schedule_games_record` | `/schedule/games/{id}/record` | `game_id` |
| `naversports_kbo_seasons_teams` | `/statistics/.../teams` | `season` |
| `naversports_kbo_seasons_players_hitter` | `/statistics/.../players?HITTER` | `season`, `team_code` |
| `naversports_kbo_seasons_players_pitcher` | `/statistics/.../players?PITCHER` | `season`, `team_code` |
| `naversports_kbo_schedule_games_lineup` | HTML DOM 파싱 (Playwright) | `game_id` |

#### FastAPI 서버 구현

| 엔드포인트 | 설명 |
|-----------|------|
| `GET /kbo/schedule/games` | 경기일정 |
| `GET /kbo/schedule/games/{game_id}/record` | 경기 기록 |
| `GET /kbo/seasons/{season}/teams` | 팀 순위 |
| `GET /kbo/seasons/{season}/players/hitter` | 타자 기록 |
| `GET /kbo/seasons/{season}/players/pitcher` | 투수 기록 |

#### 인프라/구조

- S3UploadPipeline → LoggingPipeline 교체
- Spider 디렉토리 구조 개편 (`spiders/baseball/`)
- 네이밍 규칙 확정 (`{데이터소스}_{종목}_{API경로}`)
- 모든 Spider 파라미터 필수화
- Pydantic 응답 모델 + Swagger 자동 생성
- Makefile 추가 (make api, make api-dev, make api-stop)

#### API 리버스 엔지니어링

- Playwright로 네이버 스포츠 페이지 네트워크 트래픽 분석
- 5개 API 엔드포인트 발견 및 문서화
- 인증/Rate Limit/CORS 제약 없음 확인
- 라인업은 API 없음 → HTML DOM에서만 제공 확인

---

## 프로덕션 체크리스트

| 항목 | 상태 | 비고 |
|------|------|------|
| Spider 구현 | 완료 | API 5개 + Playwright 1개 |
| FastAPI 서버 | 완료 | Swagger 포함 |
| 에러 처리 (타임아웃, 4xx/5xx) | 미구현 | |
| 재시도 전략 | 미구현 | Scrapy 기본값만 |
| 모니터링/알림 | 미구현 | CloudWatch + Slack |
| 데이터 저장 (S3 or DB) | 미구현 | LoggingPipeline만 |
| 스케줄링 | 미구현 | EventBridge + ECS Task |
| 환경 분리 (local/dev/prod) | 미구현 | |
| 테스트 코드 | 미구현 | |
| API 변경 감지 | 미구현 | 응답 스키마 검증 |
| 보안 (API Key) | 미구현 | FastAPI Security |
