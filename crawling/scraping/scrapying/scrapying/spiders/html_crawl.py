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
