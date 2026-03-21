# Python(Scrapy) 크롤링 구현 계획

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Scrapy 크롤링 결과를 S3에 원본 업로드하는 파이프라인 완성 + Docker 컨테이너화

**Architecture:** Spider가 데이터를 yield → S3Pipeline이 원본을 S3에 업로드. Spider는 S3를 모르고, Pipeline이 업로드 책임. constants.py가 크롤링 대상 URL을 관리.

**Tech Stack:** Scrapy, scrapy-playwright, boto3 (S3 업로드), moto (S3 테스트 mock), pytest, Docker

**Spec:** `docs/superpowers/specs/2026-03-19-python-crawling-design.md`

---

## 구현 순서 개요

API 구조를 먼저 파악한 후 코드를 설계한다.

```
Phase 1: 환경 셋업
  Task 1: 테스트 환경 셋업

Phase 2: API 탐지 및 분석 (api_capture 활용)
  Task 2: 경기일정 API 탐지 및 분석
  Task 3: 팀정보/팀기록 API 탐지 및 분석
  Task 4: 타자/투수 목록 API 탐지 및 분석
  → 각 Task에서 API 엔드포인트, 응답 구조, 헤더, 페이지네이션 등을 문서화

Phase 3: 핵심 코드 구현 (Phase 2 결과 기반)
  Task 5: CrawledItem 정의
  Task 6: S3UploadPipeline 구현
  Task 7: constants.py 작성 (탐지된 API 기반)
  Task 8: api_call Spider 수정
  Task 9: html_crawl Spider 생성

Phase 4: 컨테이너화
  Task 10: Dockerfile 작성

Phase 5: 검증
  Task 11: 전체 테스트 실행 및 정리
```

---

## Phase 1: 환경 셋업

### Task 1: 테스트 환경 셋업

**Files:**
- Modify: `pyproject.toml`
- Create: `scrapying/tests/__init__.py`

- [ ] **Step 1: 의존성 추가**

```bash
cd /Users/yeonghonoh-jobis/work/yhnoh/vibe-coding/crawling/scraping
uv add boto3
uv add --dev pytest moto[s3]
```

- [ ] **Step 2: pytest pythonpath 설정 추가**

`pyproject.toml`에 추가:
```toml
[tool.pytest.ini_options]
pythonpath = ["scrapying"]
testpaths = ["scrapying/tests"]
```

이렇게 하면 `scrapying/` 디렉토리가 `sys.path`에 추가되어 `from scrapying.items import ...` 임포트가 동작한다.

- [ ] **Step 3: 테스트 디렉토리 생성**

```bash
mkdir -p scrapying/tests
touch scrapying/tests/__init__.py
```

- [ ] **Step 4: pytest 실행 확인**

Run: `uv run pytest -v`
Expected: "no tests ran" (에러 없이 종료)

- [ ] **Step 5: 커밋**

```bash
git add pyproject.toml uv.lock scrapying/tests/__init__.py
git commit -m "chore: 테스트 환경 셋업 (pytest, boto3, moto)"
```

---

## Phase 2: API 탐지 및 분석

각 페이지별로 api_capture를 실행하여 실제 API 엔드포인트를 탐지하고, 해당 API를 직접 호출하여 응답 구조를 파악한다.

**분석 결과는 `docs/api-analysis/` 디렉토리에 페이지별로 문서화한다.**

### Task 2: 경기일정 API 탐지 및 분석

**Files:**
- Create: `docs/api-analysis/kbo-schedule.md`

- [ ] **Step 1: api_capture 실행**

```bash
cd scrapying
uv run scrapy crawl api_capture -a url="https://m.sports.naver.com/kbaseball/schedule/index?category=kbo&date=2026-03-12"
```

- [ ] **Step 2: 탐지된 API를 직접 호출하여 응답 확인**

탐지된 API URL을 api_call로 호출:
```bash
uv run scrapy crawl api_call -a url="{탐지된_API_URL}" -o schedule_sample.json
```

- [ ] **Step 3: 분석 결과 문서화**

`docs/api-analysis/kbo-schedule.md`에 다음 내용을 기록:
- 웹 페이지 URL
- 탐지된 API 엔드포인트 URL
- API 응답 JSON 구조 (주요 필드)
- 필수 헤더 (Referer 등)
- 페이지네이션 방식 (있는 경우)
- URL 파라미터 (date 등 동적 파라미터)
- 특이사항

- [ ] **Step 4: 커밋**

```bash
git add summary/api-analysis/kbo-schedule.md schedule_sample.json
git commit -m "docs: 경기일정 API 탐지 및 응답 구조 분석"
```

---

### Task 3: 팀정보/팀기록 API 탐지 및 분석

**Files:**
- Create: `docs/api-analysis/kbo-team.md`

- [ ] **Step 1: 팀정보(teamRank) api_capture 실행**

```bash
cd scrapying
uv run scrapy crawl api_capture -a url="https://m.sports.naver.com/kbaseball/record/kbo?tab=teamRank"
```

- [ ] **Step 2: 팀기록(teamRecord) api_capture 실행**

```bash
uv run scrapy crawl api_capture -a url="https://m.sports.naver.com/kbaseball/record/kbo?seasonCode=2026&tab=teamRecord"
```

- [ ] **Step 3: 탐지된 API를 직접 호출하여 응답 확인**

```bash
uv run scrapy crawl api_call -a url="{탐지된_API_URL}" -o team_sample.json
```

- [ ] **Step 4: 분석 결과 문서화**

`docs/api-analysis/kbo-team.md`에 기록:
- teamRank API 엔드포인트 + 응답 구조
- teamRecord API 엔드포인트 + 응답 구조
- **실제 팀 코드 목록 확인** (응답에서 teamCode 필드 추출)
- seasonCode 파라미터 동작 방식

- [ ] **Step 5: 커밋**

```bash
git add summary/api-analysis/kbo-team.md team_sample.json
git commit -m "docs: 팀정보/팀기록 API 탐지 및 응답 구조 분석"
```

---

### Task 4: 타자/투수 목록 API 탐지 및 분석

**Files:**
- Create: `docs/api-analysis/kbo-player.md`

- [ ] **Step 1: 타자목록 api_capture 실행**

```bash
cd scrapying
uv run scrapy crawl api_capture -a url="https://m.sports.naver.com/kbaseball/record/kbo?tab=hitter"
```

- [ ] **Step 2: 투수목록 api_capture 실행**

```bash
uv run scrapy crawl api_capture -a url="https://m.sports.naver.com/kbaseball/record/kbo?tab=pitcher"
```

- [ ] **Step 3: 팀별 목록 api_capture 실행 (1개 팀 샘플)**

```bash
uv run scrapy crawl api_capture -a url="https://m.sports.naver.com/kbaseball/record/kbo?tab=hitter&teamCode=KIA"
```

- [ ] **Step 4: 탐지된 API를 직접 호출하여 응답 확인**

```bash
uv run scrapy crawl api_call -a url="{탐지된_API_URL}" -o player_sample.json
```

- [ ] **Step 5: 분석 결과 문서화**

`docs/api-analysis/kbo-player.md`에 기록:
- 타자 API 엔드포인트 + 응답 구조
- 투수 API 엔드포인트 + 응답 구조
- **페이지네이션 확인** (전체 선수 수, 한 페이지 크기, 다음 페이지 파라미터)
- teamCode 파라미터 동작 방식 (팀별 필터 vs 전체)
- 전체 목록 vs 팀별 목록의 API 차이

- [ ] **Step 6: 커밋**

```bash
git add summary/api-analysis/kbo-player.md player_sample.json
git commit -m "docs: 타자/투수 목록 API 탐지 및 응답 구조 분석"
```

---

## Phase 3: 핵심 코드 구현

> Phase 2의 분석 결과를 기반으로 구현한다.
> 아래 코드는 **예시**이며, 실제 API 응답 구조에 맞게 수정해야 한다.

### Task 5: CrawledItem 정의

**Files:**
- Modify: `scrapying/scrapying/items.py`
- Create: `scrapying/tests/test_items.py`

- [ ] **Step 1: 실패하는 테스트 작성**

`scrapying/tests/test_items.py`:
```python
from scrapying.items import CrawledItem


def test_crawled_item_has_required_fields():
    item = CrawledItem()
    item["source"] = "naver-sports"
    item["data_type"] = "kbo-team-rank"
    item["content_type"] = "json"
    item["raw_data"] = '{"teams": []}'

    assert item["source"] == "naver-sports"
    assert item["data_type"] == "kbo-team-rank"
    assert item["content_type"] == "json"
    assert item["raw_data"] == '{"teams": []}'
```

- [ ] **Step 2: 테스트 실패 확인**

Run: `uv run pytest scrapying/tests/test_items.py -v`
Expected: FAIL - `ImportError: cannot import name 'CrawledItem'`

- [ ] **Step 3: CrawledItem 구현**

`scrapying/scrapying/items.py`:
```python
import scrapy


class CrawledItem(scrapy.Item):
    """크롤링 결과를 담는 Item. S3Pipeline이 이 Item을 S3에 업로드한다."""
    source = scrapy.Field()        # 데이터 출처 (예: "naver-sports")
    data_type = scrapy.Field()     # 데이터 종류 (예: "kbo-team-rank")
    content_type = scrapy.Field()  # 응답 타입 ("json" 또는 "html")
    raw_data = scrapy.Field()      # 원본 데이터 (JSON 문자열 또는 HTML 문자열)
```

- [ ] **Step 4: 테스트 통과 확인**

Run: `uv run pytest scrapying/tests/test_items.py -v`
Expected: PASS

- [ ] **Step 5: 커밋**

```bash
git add scrapying/scrapying/items.py scrapying/tests/test_items.py
git commit -m "feat: CrawledItem 정의 (source, data_type, content_type, raw_data)"
```

---

### Task 6: S3UploadPipeline 구현

**Files:**
- Modify: `scrapying/scrapying/pipelines.py`
- Modify: `scrapying/scrapying/settings.py`
- Create: `scrapying/tests/test_pipelines.py`

- [ ] **Step 1: 실패하는 테스트 작성**

`scrapying/tests/test_pipelines.py`:
```python
import json
import re

import boto3
import pytest
from moto import mock_aws
from scrapying.items import CrawledItem
from scrapying.pipelines import S3UploadPipeline

BUCKET = "test-bucket"
REGION = "ap-northeast-2"


@pytest.fixture
def s3_env():
    """mock_aws 컨텍스트 안에서 S3 버킷 생성 + Pipeline + S3 client를 제공"""
    with mock_aws():
        conn = boto3.client("s3", region_name=REGION)
        conn.create_bucket(
            Bucket=BUCKET,
            CreateBucketConfiguration={"LocationConstraint": REGION},
        )
        pipeline = S3UploadPipeline(bucket_name=BUCKET, region_name=REGION)
        pipeline.open_spider(None)
        yield conn, pipeline


def test_s3_upload_json_item(s3_env):
    conn, pipeline = s3_env

    item = CrawledItem()
    item["source"] = "naver-sports"
    item["data_type"] = "kbo-team-rank"
    item["content_type"] = "json"
    item["raw_data"] = json.dumps({"teams": [{"name": "LG"}]})

    result = pipeline.process_item(item, None)

    # item이 그대로 반환되어야 함
    assert result == item

    # S3에 파일이 업로드되었는지 확인
    objects = conn.list_objects_v2(Bucket=BUCKET, Prefix="raw/naver-sports/kbo-team-rank/")
    assert objects["KeyCount"] == 1

    key = objects["Contents"][0]["Key"]
    assert key.endswith(".json")

    # 업로드된 내용이 원본과 동일한지 확인
    body = conn.get_object(Bucket=BUCKET, Key=key)["Body"].read().decode()
    assert json.loads(body) == {"teams": [{"name": "LG"}]}


def test_s3_upload_html_item(s3_env):
    conn, pipeline = s3_env

    item = CrawledItem()
    item["source"] = "naver-sports"
    item["data_type"] = "kbo-hitter"
    item["content_type"] = "html"
    item["raw_data"] = "<html><body>data</body></html>"

    pipeline.process_item(item, None)

    objects = conn.list_objects_v2(Bucket=BUCKET, Prefix="raw/naver-sports/kbo-hitter/")
    assert objects["KeyCount"] == 1

    key = objects["Contents"][0]["Key"]
    assert key.endswith(".html")


def test_s3_key_follows_path_convention(s3_env):
    """S3 경로가 raw/{source}/{data_type}/{yyyy}/{MM}/{dd}/{timestamp}.{ext} 형식인지 확인"""
    conn, pipeline = s3_env

    item = CrawledItem()
    item["source"] = "naver-sports"
    item["data_type"] = "kbo-team-rank"
    item["content_type"] = "json"
    item["raw_data"] = "{}"

    pipeline.process_item(item, None)

    objects = conn.list_objects_v2(Bucket=BUCKET, Prefix="raw/")
    key = objects["Contents"][0]["Key"]

    # raw/naver-sports/kbo-team-rank/2026/03/19/1710842400.json 패턴
    pattern = r"^raw/[\w-]+/[\w-]+/\d{4}/\d{2}/\d{2}/\d+\.\w+$"
    assert re.match(pattern, key), f"S3 key가 경로 규칙에 맞지 않음: {key}"
```

- [ ] **Step 2: 테스트 실패 확인**

Run: `uv run pytest scrapying/tests/test_pipelines.py -v`
Expected: FAIL - `ImportError: cannot import name 'S3UploadPipeline'`

- [ ] **Step 3: S3UploadPipeline 구현**

`scrapying/scrapying/pipelines.py`:
```python
from datetime import datetime, timezone, timedelta

import boto3
from itemadapter import ItemAdapter

from scrapying.items import CrawledItem


class S3UploadPipeline:
    """CrawledItem을 S3에 원본 그대로 업로드하는 Pipeline.

    S3 경로 규칙: raw/{source}/{data_type}/{yyyy}/{MM}/{dd}/{timestamp}.{ext}
    """

    def __init__(self, bucket_name, region_name="ap-northeast-2"):
        self.bucket_name = bucket_name
        self.region_name = region_name
        self.s3_client = None

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            bucket_name=crawler.settings.get("S3_BUCKET_NAME"),
            region_name=crawler.settings.get("S3_REGION_NAME", "ap-northeast-2"),
        )

    def open_spider(self, spider):
        self.s3_client = boto3.client("s3", region_name=self.region_name)

    def process_item(self, item, spider):
        if not isinstance(item, CrawledItem):
            return item

        adapter = ItemAdapter(item)
        source = adapter["source"]
        data_type = adapter["data_type"]
        content_type = adapter["content_type"]
        raw_data = adapter["raw_data"]

        ext = "json" if content_type == "json" else "html"
        kst = timezone(timedelta(hours=9))
        now = datetime.now(kst)
        timestamp = int(now.timestamp())

        key = f"raw/{source}/{data_type}/{now.strftime('%Y/%m/%d')}/{timestamp}.{ext}"

        self.s3_client.put_object(
            Bucket=self.bucket_name,
            Key=key,
            Body=raw_data.encode("utf-8"),
            ContentType="application/json" if ext == "json" else "text/html",
        )

        if spider:
            spider.logger.info(f"S3 업로드 완료: s3://{self.bucket_name}/{key}")

        return item
```

- [ ] **Step 4: 테스트 통과 확인**

Run: `uv run pytest scrapying/tests/test_pipelines.py -v`
Expected: 3 tests PASS

- [ ] **Step 5: settings.py에 S3 설정 및 Pipeline 활성화**

`scrapying/scrapying/settings.py`에 추가:
```python
# S3 Upload 설정
S3_BUCKET_NAME = "your-bucket-name"  # 실제 버킷명으로 변경
S3_REGION_NAME = "ap-northeast-2"

# Pipeline 활성화
ITEM_PIPELINES = {
    "scrapying.pipelines.S3UploadPipeline": 300,
}
```

- [ ] **Step 6: 커밋**

```bash
git add scrapying/scrapying/pipelines.py scrapying/scrapying/settings.py scrapying/tests/test_pipelines.py
git commit -m "feat: S3UploadPipeline 구현 (CrawledItem → S3 원본 업로드)"
```

---

### Task 7: constants.py 작성 (Phase 2 탐지 결과 기반)

**Files:**
- Create: `scrapying/scrapying/constants.py`
- Create: `scrapying/tests/test_constants.py`

> **중요:** 아래 코드는 예시이며, Phase 2에서 탐지된 실제 API URL과 파라미터로 교체해야 한다.

- [ ] **Step 1: 실패하는 테스트 작성**

`scrapying/tests/test_constants.py`:
```python
from scrapying.constants import CrawlTarget, TARGETS


def test_crawl_target_with_url_template():
    target = CrawlTarget(
        source="naver-sports",
        data_type="kbo-schedule",
        url_template="https://api-gw.sports.naver.com/schedule?date={date}",
        content_type="json",
        default_params={"date": "2026-03-12"},
    )
    assert target.source == "naver-sports"
    assert target.build_url() == "https://api-gw.sports.naver.com/schedule?date=2026-03-12"


def test_crawl_target_build_url_with_override():
    target = CrawlTarget(
        source="naver-sports",
        data_type="kbo-schedule",
        url_template="https://api-gw.sports.naver.com/schedule?date={date}",
        content_type="json",
        default_params={"date": "2026-03-12"},
    )
    url = target.build_url(params={"date": "2026-04-01"})
    assert url == "https://api-gw.sports.naver.com/schedule?date=2026-04-01"


def test_crawl_target_without_params():
    target = CrawlTarget(
        source="naver-sports",
        data_type="kbo-team-rank",
        url_template="https://api-gw.sports.naver.com/teams",
        content_type="json",
    )
    assert target.build_url() == "https://api-gw.sports.naver.com/teams"


def test_targets_is_list():
    assert isinstance(TARGETS, list)
    assert len(TARGETS) > 0
```

- [ ] **Step 2: 테스트 실패 확인**

Run: `uv run pytest scrapying/tests/test_constants.py -v`
Expected: FAIL - `ImportError: cannot import name 'CrawlTarget'`

- [ ] **Step 3: constants.py 구현**

`scrapying/scrapying/constants.py`:
```python
from dataclasses import dataclass, field


@dataclass(frozen=True)
class CrawlTarget:
    """크롤링 대상을 정의하는 데이터 클래스.

    source: 데이터 출처 (S3 경로의 첫 번째 세그먼트)
    data_type: 데이터 종류 (S3 경로의 두 번째 세그먼트)
    url_template: URL 템플릿 ({param} 형태의 플레이스홀더 포함 가능)
    content_type: 응답 타입 ("json" 또는 "html")
    default_params: URL 템플릿의 기본 파라미터 값
    """
    source: str
    data_type: str
    url_template: str
    content_type: str  # "json" or "html"
    default_params: dict = field(default_factory=dict)

    def build_url(self, params: dict | None = None) -> str:
        """URL 템플릿에 파라미터를 적용하여 최종 URL을 생성한다.
        params가 주어지면 default_params를 오버라이드한다.
        """
        merged = {**self.default_params, **(params or {})}
        return self.url_template.format(**merged) if merged else self.url_template


# Phase 2에서 탐지된 실제 API URL로 교체할 것
# 아래는 예시이며 api_capture 실행 결과에 따라 변경됨
TARGETS: list[CrawlTarget] = [
    # === Naver Sports KBO (api_capture로 탐지된 API 엔드포인트) ===
    CrawlTarget(
        source="naver-sports",
        data_type="kbo-team-rank",
        url_template="https://api-gw.sports.naver.com/statistics/categories/kbo/seasons/2024/teams",
        content_type="json",
    ),
    CrawlTarget(
        source="naver-sports",
        data_type="kbo-last-ten-games",
        url_template="https://api-gw.sports.naver.com/statistics/categories/kbo/seasons/2024/teams/last-ten-games",
        content_type="json",
    ),
    # TODO: Phase 2 완료 후 경기일정, 팀기록, 타자/투수 목록 API 추가
]
```

- [ ] **Step 4: 테스트 통과 확인**

Run: `uv run pytest scrapying/tests/test_constants.py -v`
Expected: 4 tests PASS

- [ ] **Step 5: 커밋**

```bash
git add scrapying/scrapying/constants.py scrapying/tests/test_constants.py
git commit -m "feat: constants.py 작성 (CrawlTarget + url_template + KBO URL 목록)"
```

---

### Task 8: api_call Spider 수정 (CrawledItem + constants 연동)

**Files:**
- Modify: `scrapying/scrapying/spiders/api_call.py`

- [ ] **Step 1: api_call Spider를 CrawledItem과 constants 기반으로 수정**

`scrapying/scrapying/spiders/api_call.py`:
```python
import scrapy

from scrapying.constants import TARGETS
from scrapying.items import CrawledItem


class ApiCallSpider(scrapy.Spider):
    """constants.py에 등록된 API URL들을 호출하여 데이터를 수집하는 스파이더.

    실행 방법:
        scrapy crawl api_call                           # TARGETS의 모든 json 타입 URL 호출
        scrapy crawl api_call -a source=naver-sports    # 특정 source만 필터링

    동작 흐름:
        start() → constants.TARGETS에서 json 타입 URL 추출
              ↓
        parse() → 응답을 CrawledItem으로 yield
              ↓
        S3UploadPipeline → S3에 원본 업로드
    """

    name = "api_call"

    def __init__(self, source=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.source_filter = source

    async def start(self):
        targets = [t for t in TARGETS if t.content_type == "json"]
        if self.source_filter:
            targets = [t for t in targets if t.source == self.source_filter]

        for target in targets:
            yield scrapy.Request(
                url=target.build_url(),
                callback=self.parse,
                cb_kwargs={"target": target},
            )

    def parse(self, response, target):
        content_type = response.headers.get("Content-Type", b"").decode()
        self.logger.info(f"\n=== API: {response.url} | Content-Type: {content_type} ===")

        if "json" in content_type:
            item = CrawledItem()
            item["source"] = target.source
            item["data_type"] = target.data_type
            item["content_type"] = "json"
            item["raw_data"] = response.text
            yield item
        else:
            self.logger.warning(f"예상하지 못한 Content-Type: {content_type}")
```

- [ ] **Step 2: 로컬 실행 테스트**

Run: `cd scrapying && uv run scrapy crawl api_call 2>&1 | tail -20` (scrapy 명령어는 scrapy.cfg가 있는 디렉토리에서 실행)
Expected: S3 업로드 로그 출력 (실제 S3 버킷이 없으면 에러 — 정상. Spider 자체 실행은 확인)

- [ ] **Step 3: 커밋**

```bash
git add scrapying/scrapying/spiders/api_call.py
git commit -m "feat: api_call Spider를 CrawledItem + constants 기반으로 수정"
```

---

### Task 9: html_crawl Spider 생성

**Files:**
- Create: `scrapying/scrapying/spiders/html_crawl.py`

- [ ] **Step 1: html_crawl Spider 구현**

`scrapying/scrapying/spiders/html_crawl.py`:
```python
import scrapy
from scrapy_playwright.page import PageMethod

from scrapying.constants import TARGETS
from scrapying.items import CrawledItem


class HtmlCrawlSpider(scrapy.Spider):
    """constants.py에 등록된 HTML URL들을 Playwright로 크롤링하여 렌더링된 HTML을 수집하는 스파이더.

    실행 방법:
        scrapy crawl html_crawl                           # TARGETS의 모든 html 타입 URL 크롤링
        scrapy crawl html_crawl -a source=naver-sports    # 특정 source만 필터링

    동작 흐름:
        start() → constants.TARGETS에서 html 타입 URL 추출
              ↓
        parse() → Playwright로 JS 렌더링 후 HTML 수집 → CrawledItem으로 yield
              ↓
        S3UploadPipeline → S3에 원본 업로드
    """

    name = "html_crawl"

    def __init__(self, source=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.source_filter = source

    async def start(self):
        targets = [t for t in TARGETS if t.content_type == "html"]
        if self.source_filter:
            targets = [t for t in targets if t.source == self.source_filter]

        for target in targets:
            yield scrapy.Request(
                url=target.build_url(),
                meta={
                    "playwright": True,
                    "playwright_include_page": True,
                    "playwright_page_methods": [
                        PageMethod("wait_for_timeout", 3000),
                    ],
                },
                callback=self.parse,
                cb_kwargs={"target": target},
                errback=self.errback,
            )

    async def parse(self, response, target):
        page = response.meta["playwright_page"]

        html_content = await page.content()
        await page.close()

        self.logger.info(f"\n=== HTML 크롤링 완료: {response.url} ({len(html_content)} bytes) ===")

        item = CrawledItem()
        item["source"] = target.source
        item["data_type"] = target.data_type
        item["content_type"] = "html"
        item["raw_data"] = html_content
        yield item

    async def errback(self, failure):
        self.logger.error(f"요청 실패: {failure}")
        page = failure.request.meta.get("playwright_page")
        if page:
            await page.close()
```

- [ ] **Step 2: 커밋**

```bash
git add scrapying/scrapying/spiders/html_crawl.py
git commit -m "feat: html_crawl Spider 생성 (Playwright로 HTML 크롤링 → CrawledItem)"
```

---

## Phase 4: 컨테이너화

### Task 10: Dockerfile 작성

**Files:**
- Create: `scrapying/Dockerfile`

- [ ] **Step 1: Dockerfile 작성**

`scrapying/Dockerfile`:
```dockerfile
FROM python:3.14-slim

# uv 설치
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# 프로젝트 복사 (빌드 컨텍스트가 프로젝트 루트)
COPY . /app
WORKDIR /app

# 의존성 설치
RUN uv sync --frozen

# Playwright 브라우저 설치
RUN uv run playwright install chromium --with-deps

# scrapy.cfg가 있는 디렉토리로 이동
WORKDIR /app/scrapying

ENTRYPOINT ["uv", "run", "scrapy"]
CMD ["crawl", "api_call"]
```

- [ ] **Step 2: Docker 빌드 테스트**

Run: `cd /Users/yeonghonoh-jobis/work/yhnoh/vibe-coding/crawling/scraping && docker build -f scrapying/Dockerfile -t scraping:test .`
Expected: 빌드 성공

- [ ] **Step 3: Docker 실행 테스트**

Run: `docker run --rm scraping:test list`
Expected: Spider 목록 출력 (api_call, api_capture, html_crawl)

- [ ] **Step 4: 커밋**

```bash
git add scrapying/Dockerfile
git commit -m "feat: Dockerfile 작성 (Scrapy + Playwright + uv)"
```

---

## Phase 5: 검증

### Task 11: 전체 테스트 실행 및 정리

- [ ] **Step 1: 전체 테스트 실행**

Run: `uv run pytest -v`
Expected: 모든 테스트 PASS

- [ ] **Step 2: Spider 목록 확인**

Run: `cd scrapying && uv run scrapy list` (scrapy 명령어는 scrapy.cfg가 있는 디렉토리에서 실행)
Expected:
```
api_call
api_capture
html_crawl
```

- [ ] **Step 3: CLAUDE.md 업데이트**

`CLAUDE.md`에 새로 추가된 파일들 반영:
- `scrapying/scrapying/pipelines.py` - S3 업로드 파이프라인
- `scrapying/scrapying/constants.py` - 크롤링 URL 목록 관리 (CrawlTarget + url_template)
- `scrapying/scrapying/spiders/html_crawl.py` - HTML 크롤링 Spider
- `scrapying/Dockerfile` - Docker 이미지 빌드
- `scrapying/tests/` - 테스트 코드
- `docs/api-analysis/` - API 탐지 및 응답 구조 분석 문서

- [ ] **Step 4: 최종 커밋**

```bash
git add CLAUDE.md
git commit -m "docs: CLAUDE.md 업데이트 (새 파일 목록 반영)"
```
