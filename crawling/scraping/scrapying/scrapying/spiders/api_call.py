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
