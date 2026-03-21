# KBO 데이터 수집 및 조회

네이버 스포츠 KBO API에서 야구 데이터를 수집(Scrapy)하고 조회(FastAPI)하는 프로젝트

## 요구사항

- Python >= 3.14
- [uv](https://docs.astral.sh/uv/) (패키지 매니저)

## 설치

```bash
# uv 설치 (없는 경우)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 패키지 설치
uv sync

# Playwright 브라우저 설치 (api_capture, html_crawl Spider 사용 시 필요)
uv run playwright install chromium
```

---

## API 서버 (FastAPI)

### 실행

```bash
# 일반 실행
make api

# 개발 모드 (코드 변경 시 자동 재시작)
make api-dev

# 서버 종료
make api-stop
```

### Swagger UI

서버 실행 후 브라우저에서 확인:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 엔드포인트

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/kbo/schedule/games?from_date=...&to_date=...` | 경기일정 조회 |
| GET | `/kbo/schedule/games/{game_id}/record` | 경기 기록 조회 |
| GET | `/kbo/seasons/{season}/teams` | 팀 순위/기록 조회 |
| GET | `/kbo/seasons/{season}/players/hitter?team_code=...` | 타자 선수 기록 조회 |
| GET | `/kbo/seasons/{season}/players/pitcher?team_code=...` | 투수 선수 기록 조회 |

### 요청 예시

```bash
# 경기일정
curl "http://localhost:8000/kbo/schedule/games?from_date=2026-03-21&to_date=2026-03-21"

# 경기 기록
curl "http://localhost:8000/kbo/schedule/games/20260321HHLT02026/record"

# 팀 순위
curl "http://localhost:8000/kbo/seasons/2026/teams"

# 타자 기록
curl "http://localhost:8000/kbo/seasons/2026/players/hitter?team_code=OB"

# 투수 기록
curl "http://localhost:8000/kbo/seasons/2026/players/pitcher?team_code=OB"
```

---

## 크롤러 (Scrapy)

> `scrapy.cfg`가 있는 `scrapying/` 디렉토리에서 실행해야 합니다.
>
> ```bash
> cd scrapying
> ```

### Spider 목록

| Spider | 설명 | 필수 파라미터 |
|--------|------|-------------|
| `naversports_kbo_schedule_games` | 경기일정 | `from_date`, `to_date` |
| `naversports_kbo_schedule_games_record` | 경기 기록 | `game_id` |
| `naversports_kbo_seasons_teams` | 팀 순위/기록 | `season` |
| `naversports_kbo_seasons_players_hitter` | 타자 선수 기록 | `season`, `team_code` |
| `naversports_kbo_seasons_players_pitcher` | 투수 선수 기록 | `season`, `team_code` |

### 실행 예시

```bash
# 경기일정
uv run scrapy crawl naversports_kbo_schedule_games -a from_date=2026-03-21 -a to_date=2026-03-21

# 경기 기록
uv run scrapy crawl naversports_kbo_schedule_games_record -a game_id=20260319HTHH02026

# 팀 순위
uv run scrapy crawl naversports_kbo_seasons_teams -a season=2026

# 타자 기록
uv run scrapy crawl naversports_kbo_seasons_players_hitter -a season=2026 -a team_code=OB

# 투수 기록
uv run scrapy crawl naversports_kbo_seasons_players_pitcher -a season=2026 -a team_code=OB
```

### 로그 레벨

```bash
# INFO: 수집 요약
uv run scrapy crawl <spider_name> -a ... -L INFO

# DEBUG: raw JSON 데이터 포함
uv run scrapy crawl <spider_name> -a ... -L DEBUG
```

---

## 팀 코드

| 팀명 | 코드 |
|------|------|
| LG 트윈스 | `LG` |
| 한화 이글스 | `HH` |
| SSG 랜더스 | `SK` |
| 삼성 라이온즈 | `SS` |
| NC 다이노스 | `NC` |
| KT 위즈 | `KT` |
| 롯데 자이언츠 | `LT` |
| KIA 타이거즈 | `HT` |
| 두산 베어스 | `OB` |
| 키움 히어로즈 | `WO` |

## 프로젝트 구조

```
scraping/
├── Makefile                    # make api, make api-dev, make api-stop
├── api/
│   ├── main.py                 # FastAPI app 생성 + router 등록
│   └── routers/
│       ├── naversports_kbo_router.py    # KBO 엔드포인트 (APIRouter)
│       ├── naversports_kbo_client.py    # httpx로 네이버 API 호출
│       └── naversports_kbo_schemas.py   # Pydantic 응답 모델
├── scrapying/
│   ├── scrapy.cfg
│   └── scrapying/
│       ├── constants.py
│       ├── items.py
│       ├── pipelines.py
│       ├── settings.py
│       └── spiders/
│           └── baseball/
│               ├── naversports_kbo_schedule_games.py
│               ├── naversports_kbo_schedule_games_record.py
│               ├── naversports_kbo_seasons_teams.py
│               ├── naversports_kbo_seasons_players_hitter.py
│               └── naversports_kbo_seasons_players_pitcher.py
└── docs/
    └── api-analysis/
        └── naversports-kbo-api.md       # API 명세
```

## 참고 문서

- [API 명세](docs/api-analysis/naversports-kbo-api.md)
- [Scrapy 공식 문서](https://docs.scrapy.org/en/latest/index.html)
- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
