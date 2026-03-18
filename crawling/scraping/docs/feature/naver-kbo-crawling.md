# 네이버 KBO 크롤링 작업 정리

## 목표
네이버 스포츠 KBO 페이지에서 팀 순위, 팀 기록, 타자/투수 기록 데이터를 수집

---

## 작업 순서

### 1단계 - Scrapy 프로젝트 셋팅
```bash
uv run scrapy startproject scrapying .
uv add scrapy-playwright
uv run playwright install chromium
```

### 2단계 - settings.py 수정
Playwright 연동 및 크롤링 속도 설정

```python
DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
ROBOTSTXT_OBEY = False
CONCURRENT_REQUESTS_PER_DOMAIN = 1
DOWNLOAD_DELAY = 1
```

### 3단계 - constants.py 작성
크롤링할 URL을 한 곳에서 관리

```python
WebUrl (브라우저 HTML 페이지 URL)
  └── ApiUrl (해당 페이지에서 호출하는 API URL 목록)
```

### 4단계 - api_capture 스파이더로 API URL 탐지
```bash
scrapy crawl api_capture -a url="https://m.sports.naver.com/kbaseball/record/kbo?seasonCode=2024&tab=teamRank"
```

### 5단계 - 탐지한 API URL을 constants.py에 등록

### 6단계 - api_call 스파이더로 데이터 수집 및 파일 저장
```bash
scrapy crawl api_call -o output.json
```

---

## 현재 상태

### constants.py 등록 현황

| 탭 | 웹 URL | API 등록 여부 |
|----|--------|--------------|
| teamRank | `/kbaseball/record/kbo?tab=teamRank` | 완료 |
| teamRecord | `/kbaseball/record/kbo?tab=teamRecord` | 미등록 |
| hitter | `/kbaseball/record/kbo?tab=hitter` | 미등록 |
| pitcher | `/kbaseball/record/kbo?tab=pitcher` | 미등록 |

### 발견된 API URL (teamRank)

| API URL | 설명 |
|---------|------|
| `https://api-gw.sports.naver.com/statistics/categories/kbo/seasons/2024/teams` | 팀 순위 |
| `https://api-gw.sports.naver.com/statistics/categories/kbo/seasons/2024/teams/last-ten-games` | 최근 10경기 |

---

## 남은 작업

아래 3개 탭의 API URL을 탐지 후 constants.py에 추가 필요

```bash
scrapy crawl api_capture -a url="https://m.sports.naver.com/kbaseball/record/kbo?seasonCode=2024&tab=teamRecord"
scrapy crawl api_capture -a url="https://m.sports.naver.com/kbaseball/record/kbo?seasonCode=2024&tab=hitter"
scrapy crawl api_capture -a url="https://m.sports.naver.com/kbaseball/record/kbo?seasonCode=2024&tab=pitcher"
```