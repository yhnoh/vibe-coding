# KBO 데이터 수집 (Scrapy)

네이버 스포츠 KBO API에서 야구 데이터를 수집하는 Scrapy 프로젝트

## 버전

- Python: 3.14.3
- uv: 0.10.11

## 설치

```bash
uv sync
uv run playwright install chromium
```

## 실행 방법

모든 명령어는 `scrapying/` 디렉토리에서 실행해야 합니다.

```bash
cd scrapying
```

### 경기일정 조회

```bash
# 특정 날짜
uv run scrapy crawl naversports_kbo_schedule_games -a from_date=2026-03-21 -a to_date=2026-03-21

# 날짜 범위
uv run scrapy crawl naversports_kbo_schedule_games -a from_date=2026-03-19 -a to_date=2026-03-21
```

| 파라미터 | 필수 | 설명 | 예시 |
|----------|------|------|------|
| `from_date` | Y | 조회 시작일 | `2026-03-21` |
| `to_date` | Y | 조회 종료일 | `2026-03-21` |

### 경기 기록 조회 (타자/투수 박스스코어)

```bash
uv run scrapy crawl naversports_kbo_schedule_games_record -a game_id=20260319HTHH02026
```

| 파라미터 | 필수 | 설명 | 예시 |
|----------|------|------|------|
| `game_id` | Y | 경기 ID | `20260319HTHH02026` |

> `game_id`는 경기일정 조회 응답의 `gameId` 필드에서 확인할 수 있습니다.

### 팀 순위/기록 조회

```bash
uv run scrapy crawl naversports_kbo_seasons_teams -a season=2026
```

| 파라미터 | 필수 | 설명 | 예시 |
|----------|------|------|------|
| `season` | Y | 시즌 연도 | `2026` |

### 타자 선수 기록 조회

```bash
uv run scrapy crawl naversports_kbo_seasons_players_hitter -a season=2026 -a team_code=OB
```

| 파라미터 | 필수 | 설명 | 예시 |
|----------|------|------|------|
| `season` | Y | 시즌 연도 | `2026` |
| `team_code` | Y | 팀 코드 | `OB` |

### 투수 선수 기록 조회

```bash
uv run scrapy crawl naversports_kbo_seasons_players_pitcher -a season=2026 -a team_code=OB
```

| 파라미터 | 필수 | 설명 | 예시 |
|----------|------|------|------|
| `season` | Y | 시즌 연도 | `2026` |
| `team_code` | Y | 팀 코드 | `OB` |

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

## 로그 레벨

```bash
# INFO: 수집 요약
uv run scrapy crawl <spider_name> -a ... -L INFO

# DEBUG: raw JSON 데이터 포함
uv run scrapy crawl <spider_name> -a ... -L DEBUG
```

## 프로젝트 구조

```
scrapying/
├── scrapy.cfg
└── scrapying/
    ├── constants.py                          # API_DOMAIN, CrawlTarget
    ├── items.py                              # CrawledItem 정의
    ├── pipelines.py                          # LoggingPipeline
    ├── settings.py                           # Scrapy 설정
    └── spiders/
        └── baseball/
            ├── naversports_kbo_schedule_games.py           # 경기일정
            ├── naversports_kbo_schedule_games_record.py    # 경기 기록
            ├── naversports_kbo_seasons_teams.py            # 팀 순위/기록
            ├── naversports_kbo_seasons_players_hitter.py   # 타자 선수 기록
            └── naversports_kbo_seasons_players_pitcher.py  # 투수 선수 기록
```

## 참고 문서

- [API 명세](docs/api-analysis/naversports-kbo-api.md)
- [Scrapy 공식 문서](https://docs.scrapy.org/en/latest/index.html)
