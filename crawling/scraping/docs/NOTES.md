# Scrapy 크롤링 프로젝트 정리

## 목표
네이버 스포츠(KBO) 페이지에서 데이터를 크롤링하기 위해 Scrapy + Playwright를 활용한 프로젝트

---

## Scrapy 철학

Scrapy는 **"요청을 던지면 엔진이 알아서 처리한다"** 는 철학을 가진 비동기 크롤링 프레임워크입니다.

- 개발자는 **"어디서 가져올지(URL)"** 와 **"어떻게 파싱할지(parse)"** 만 정의
- 요청 스케줄링, 중복 제거, 재시도, 속도 조절은 Scrapy 엔진이 자동 처리
- `yield` 로 요청/아이템을 엔진에 넘기는 방식으로 동작

```
Spider (yield Request)
    → Scrapy 엔진
    → Downloader (HTTP 요청)
    → Spider (parse 호출)
    → Pipeline (데이터 저장)
```

---

## 프로젝트 구조

```
scraping/
├── pyproject.toml          # 프로젝트 의존성 관리 (uv)
└── scrapying/              # Scrapy 프로젝트 루트 (scrapy.cfg 위치)
    ├── scrapy.cfg          # Scrapy 배포 설정
    └── scrapying/          # Scrapy 패키지
        ├── constants.py    # URL 목록 관리
        ├── items.py        # 수집할 데이터 구조 정의
        ├── middlewares.py  # 요청/응답 가로채기
        ├── pipelines.py    # 데이터 처리/저장
        ├── settings.py     # Scrapy 전역 설정
        └── spiders/        # 스파이더 모음
            ├── api_capture.py  # 웹페이지에서 API URL 자동 탐지
            └── api_call.py     # API 직접 호출
```

---

## Scrapy 핵심 컴포넌트

| 컴포넌트 | 파일 | 역할 |
|----------|------|------|
| Spider | `spiders/*.py` | 크롤링 로직 (URL, 파싱 방법 정의) |
| Item | `items.py` | 수집할 데이터 필드 정의 |
| Pipeline | `pipelines.py` | 수집된 데이터 처리 (DB 저장, 검증 등) |
| Middleware | `middlewares.py` | 요청/응답 가로채기 (프록시, 헤더 등) |
| Settings | `settings.py` | 전역 설정 (속도, 헤더, 파이프라인 등) |

---

## 사용 패키지

### scrapy
- **용도**: 웹 크롤링 프레임워크
- **역할**: HTTP 요청, 스케줄링, 파싱, 파이프라인 처리를 자동화

### scrapy-playwright
- **용도**: Scrapy에 Playwright 브라우저를 연동
- **역할**: JavaScript로 렌더링되는 페이지(네이버 쇼핑, 스포츠 등) 크롤링 가능
- **필요한 이유**: 일반 Scrapy는 HTML만 받아오기 때문에 JS 실행 후 나타나는 데이터를 못 가져옴

### playwright
- **용도**: 브라우저 자동화 도구
- **역할**: Chromium 브라우저를 코드로 제어, 네트워크 요청 캡처 가능

---

## settings.py 주요 설정

```python
# Playwright를 HTTP 요청 처리기로 등록 (필수)
DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}

# 비동기 처리 엔진 (Playwright 사용 시 필수)
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"

# robots.txt 무시 (네이버가 크롤링 차단하므로 False)
ROBOTSTXT_OBEY = False

# 같은 도메인에 동시 요청 수 제한
CONCURRENT_REQUESTS_PER_DOMAIN = 1

# 요청 간 대기 시간 (서버 부하 방지)
DOWNLOAD_DELAY = 1
```

---

## constants.py 구조

URL을 한 곳에서 관리하기 위한 설정 파일

```python
@dataclass
class ApiUrl:
    url: str                        # API URL

    def build_url(self, **kwargs):  # {변수} 자리에 값을 채워 URL 생성
        return self.url.format(**kwargs)


@dataclass
class WebUrl:
    url: str                        # 브라우저에서 여는 HTML 페이지 URL
    api_urls: list[ApiUrl]          # 해당 페이지에서 호출하는 API 목록

    def build_url(self, **kwargs):
        return self.url.format(**kwargs)
```

- `{{변수명}}` → `build_url(변수명=값)` 호출 시 치환됨
- f-string 안에서 `{변수}`는 즉시 치환, `{{변수}}`는 나중에 치환용으로 보존

---

## 스파이더 설명

### api_capture - 웹페이지에서 API URL 탐지

웹 URL을 입력하면 해당 페이지가 내부적으로 호출하는 API URL 목록을 출력

```
브라우저로 페이지 열기
    → 페이지 새로고침
    → XHR/Fetch 요청 감지
    → API URL 목록 출력
```

**실행:**
```bash
scrapy crawl api_capture -a url="https://m.sports.naver.com/kbaseball/record/kbo?seasonCode=2024&tab=teamRank"
```

**주요 코드 개념:**

| 키워드 | 설명 |
|--------|------|
| `async def` | 비동기 함수 선언. 네트워크 대기 중 다른 작업 처리 가능 |
| `yield` | 값을 하나씩 엔진에 전달. return과 달리 함수가 끝나지 않음 |
| `playwright_include_page: True` | 브라우저 page 객체를 response.meta로 받기 |
| `page.on("request", ...)` | 브라우저의 네트워크 요청을 이벤트로 감지 |
| `resource_type in ["fetch", "xhr"]` | API 요청만 필터링 (이미지, 스크립트 등 제외) |

---

### api_call - API 직접 호출

`constants.py`에 등록된 API URL로 직접 HTTP 요청을 보내고 JSON 응답을 출력

**실행:**
```bash
# constants.py의 모든 API URL 호출
scrapy crawl api_call

# 특정 URL 하나만 호출
scrapy crawl api_call -a url="https://api-gw.sports.naver.com/statistics/categories/kbo/seasons/2024/teams"
```

---

## 주요 명령어

```bash
# 프로젝트 생성 (현재 디렉토리에)
uv run scrapy startproject <프로젝트명> .

# 스파이더 생성
uv run scrapy genspider <스파이더명> <도메인>

# 스파이더 실행
uv run scrapy crawl <스파이더명>

# 스파이더 실행 + 인자 전달
uv run scrapy crawl <스파이더명> -a <키>=<값>

# 등록된 스파이더 목록 확인
uv run scrapy list

# Playwright 브라우저 설치
uv run playwright install chromium

# 패키지 추가
uv add <패키지명>
```

> **주의**: `scrapy crawl` 명령은 `scrapy.cfg`가 있는 디렉토리에서 실행해야 함

---

## 작업 흐름

```
1. api_capture 스파이더로 웹페이지에서 API URL 탐지
        ↓
2. 탐지된 API URL 중 필요한 것을 constants.py에 추가
        ↓
3. api_call 스파이더로 API 직접 호출하여 데이터 수집
```

---

## Scrapy에서 API 호출 가능 여부

### 기본 Scrapy로 가능한 경우

서버가 HTML을 바로 응답하거나, API가 JSON을 직접 응답하는 경우 일반 Scrapy로 충분합니다.

```
요청 → 서버 → HTML 또는 JSON 응답
```

```python
# 일반 API 호출 (JavaScript 렌더링 불필요)
yield scrapy.Request(
    url="https://api.example.com/data",
    callback=self.parse,
)

def parse(self, response):
    data = response.json()  # JSON 바로 파싱 가능
```

### Playwright가 필요한 경우

페이지가 JavaScript로 렌더링되는 경우 일반 Scrapy로는 빈 데이터만 받게 됩니다.

```
요청 → 서버 → HTML 응답 (데이터 없음)
                → 브라우저가 JS 실행
                → API 호출
                → 데이터 렌더링
```

| 상황 | 방법 |
|------|------|
| API가 JSON 직접 응답 | 기본 Scrapy로 직접 호출 |
| HTML 페이지에서 데이터 추출 (JS 없음) | 기본 Scrapy로 CSS/XPath 파싱 |
| JS 렌더링 후 데이터가 보임 | Playwright 필요 |
| 내부 API URL을 모름 | Playwright로 탐지 후 직접 호출 |

### 이 프로젝트의 전략

네이버 스포츠는 JS 렌더링 페이지이지만, 내부 API를 직접 호출하는 방식을 사용합니다.

```
1단계: Playwright로 페이지를 열어 내부 API URL 탐지 (api_capture)
    ↓
2단계: 탐지한 API URL을 기본 Scrapy로 직접 호출 (api_call)
```

Playwright 없이 API를 직접 호출하므로 속도가 빠르고 자원 소모가 적습니다.

---

## 웹 크롤링 주의사항

### 1. 법적/윤리적 주의사항

- **robots.txt 확인**: 사이트가 크롤링을 허용하는지 확인 (`/robots.txt` 경로)
  - `ROBOTSTXT_OBEY = True` 가 기본값이며, 이를 무시하면 법적 문제가 생길 수 있음
- **이용약관 확인**: 대부분의 사이트는 이용약관에 크롤링 금지 조항이 있음
- **상업적 사용 금지**: 수집한 데이터를 무단으로 상업적으로 사용하면 저작권법 위반
- **개인정보 수집 금지**: 타인의 개인정보를 무단 수집하면 개인정보보호법 위반

### 2. 서버 부하 관련

- **요청 간격 설정**: `DOWNLOAD_DELAY = 1` 처럼 요청 사이에 대기 시간을 줘야 함
  - 너무 빠른 요청은 서버에 DoS 공격과 같은 부하를 줄 수 있음
- **동시 요청 제한**: `CONCURRENT_REQUESTS_PER_DOMAIN = 1` 로 한 번에 하나씩만 요청
- **AutoThrottle 활용**: Scrapy의 AutoThrottle 기능으로 서버 응답 속도에 맞게 자동 조절 가능

```python
# settings.py
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 10
```

### 3. IP 차단 대응

- 같은 IP로 너무 많은 요청을 보내면 사이트에서 IP를 차단할 수 있음
- 차단 징후: 응답 코드 `403 Forbidden`, `429 Too Many Requests`
- 대응 방법:
  - `DOWNLOAD_DELAY` 값을 늘려서 요청 속도 줄이기
  - User-Agent 설정으로 일반 브라우저처럼 위장

```python
# settings.py
DEFAULT_REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
}
```

### 4. API 변경 대응

- 사이트의 내부 API는 공식 API가 아니기 때문에 언제든지 변경될 수 있음
- URL 구조, 파라미터, 응답 형식이 바뀌면 크롤러가 동작하지 않음
- `constants.py` 처럼 URL을 한 곳에서 관리하면 변경 시 빠르게 대응 가능

### 5. 데이터 신뢰성

- 크롤링한 데이터는 사이트 구조 변경으로 인해 갑자기 깨질 수 있음
- 수집된 데이터의 형식/타입을 항상 검증하는 코드 작성 권장

---

## 발견된 네이버 KBO API

| API | 설명 |
|-----|------|
| `https://api-gw.sports.naver.com/statistics/categories/kbo/seasons` | 시즌 목록 |
| `https://api-gw.sports.naver.com/statistics/categories/kbo/seasons/2024/teams` | 팀 순위 |
| `https://api-gw.sports.naver.com/statistics/categories/kbo/seasons/2024/teams/last-ten-games` | 최근 10경기 |
| `https://api-gw.sports.naver.com/schedule/games` | 경기 일정 |