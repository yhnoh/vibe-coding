import scrapy

from scrapying.items import CrawledItem


class ApiCallSpider(scrapy.Spider):
    """단건 API URL을 직접 호출하여 응답을 확인하는 테스트용 스파이더.

    실행 방법:
        scrapy crawl api_call -a url="https://api.example.com/data"
        scrapy crawl api_call -a url="https://api.example.com/data" -o output.json
    """

    name = "api_call"

    def __init__(self, url=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url = url

    async def start(self):
        yield scrapy.Request(
            url=self.url,
            callback=self.parse,
        )

    def parse(self, response):
        content_type = response.headers.get("Content-Type", b"").decode()
        self.logger.info(f"\n=== API: {response.url} | Content-Type: {content_type} ===")

        if "json" in content_type:
            yield {"url": response.url, "data": response.json()}
        elif "xml" in content_type:
            yield {"url": response.url, "data": response.xpath("/*").get()}
        else:
            self.logger.warning(f"지원하지 않는 Content-Type: {content_type}")
