# 네이버 KBO 크롤링 작업 정리

## 목표
네이버 스포츠 KBO 페이지에서 경기일정, 팀 순위, 타자/투수 기록 데이터를 수집

---

## Spider 현황

### 디렉토리 구조

```
spiders/
├── baseball/
│   └── naversports_kbo_schedule_game.py   # KBO 경기일정
├── api_capture.py                         # API URL 탐지 (도구)
├── api_call.py                            # API 직접 호출 (테스트용)
├── html_crawl.py                          # HTML 크롤링
├── kbo_hitter.py                          # 타자 기록 (이동 예정)
├── kbo_pitcher.py                         # 투수 기록 (이동 예정)
└── kbo_team_stats.py                      # 팀 순위 (이동 예정)
```

### Spider 목록

| Spider | 파일 | API | 상태 |
|--------|------|-----|------|
| `naversports_kbo_schedule_game` | `baseball/naversports_kbo_schedule_game.py` | `/schedule/games` | 완료 |
| `kbo_hitter` | `kbo_hitter.py` | `/statistics/.../players?playerType=HITTER` | baseball/ 이동 예정 |
| `kbo_pitcher` | `kbo_pitcher.py` | `/statistics/.../players?playerType=PITCHER` | baseball/ 이동 예정 |
| `kbo_team_stats` | `kbo_team_stats.py` | `/statistics/.../teams` | baseball/ 이동 예정 |

### 실행 방법

```bash
cd scrapying

# 경기일정 - 오늘
uv run scrapy crawl naversports_kbo_schedule_game

# 경기일정 - 특정 날짜
uv run scrapy crawl naversports_kbo_schedule_game -a from_date=2026-03-21

# 경기일정 - 날짜 범위
uv run scrapy crawl naversports_kbo_schedule_game -a from_date=2026-03-19 -a to_date=2026-03-21
```

---

## 파이프라인

| Pipeline | 설명 | 상태 |
|----------|------|------|
| `LoggingPipeline` | 수집 결과를 로그로 출력 (INFO: 요약, DEBUG: raw JSON) | 사용 중 |
| `S3UploadPipeline` | S3에 원본 업로드 | 제거됨 (필요 시 복원) |

---

## 네이밍 규칙

- **파일명**: `{데이터소스}_{종목}_{데이터종류}.py` (예: `naversports_kbo_schedule_game.py`)
- **Spider name**: 파일명과 동일 (예: `naversports_kbo_schedule_game`)
- **클래스명**: PascalCase + Spider 접미사 (예: `NaversportsKboScheduleGameSpider`)
- **디렉토리**: 종목별 분류 (예: `spiders/baseball/`)

---

## 남은 작업

- [ ] 기존 `kbo_hitter`, `kbo_pitcher`, `kbo_team_stats` Spider를 `baseball/` 디렉토리로 이동 및 네이밍 통일
- [ ] `/schedule/calendar` API Spider 추가 (월별 캘린더)
- [ ] S3 또는 DB 저장 파이프라인 추가