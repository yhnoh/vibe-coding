import scrapy
from scrapy_playwright.page import PageMethod
from urllib.parse import urlparse, parse_qs


class ApiCaptureSpider(scrapy.Spider):
    """
    웹 URL을 입력받아 해당 페이지에서 호출하는 API URL 목록을 출력하는 스파이더

    실행 방법:
        scrapy crawl api_capture -a url="https://example.com"

    동작 흐름:
        start() → Playwright로 브라우저 열고 페이지 로드
              ↓
        parse() → 페이지 새로고침하면서 XHR/Fetch 요청 감지
              ↓
        API URL 목록 출력
              ↓
        constants.py의 ApiUrl에 수동으로 추가
    """

    name = "api_capture"

    def __init__(self, url=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url = url  # -a url="..." 로 전달받은 웹 URL

    async def start(self):
        # Playwright 브라우저로 페이지 요청
        yield scrapy.Request(
            url=self.url,
            meta={
                "playwright": True,              # Playwright로 브라우저 열기
                "playwright_include_page": True, # parse()에서 page 객체 사용하기 위해 필요
                "playwright_page_methods": [
                    PageMethod("wait_for_timeout", 3000),  # JS 로딩 완료까지 3초 대기
                ],
            },
            callback=self.parse,
            errback=self.errback,  # 요청 실패 시 errback 호출
        )

    async def parse(self, response):
        # response.meta에서 Playwright 브라우저 page 객체 꺼내기
        page = response.meta["playwright_page"]
        captured = []

        def on_request(request):
            # fetch, xhr 타입만 캡처 (이미지, 스크립트, 폰트 등 제외)
            if request.resource_type in ["fetch", "xhr"]:
                captured.append(request.url)

        # 이벤트 핸들러 등록: 이후 발생하는 네트워크 요청을 on_request로 감지
        page.on("request", on_request)

        # 페이지 새로고침 → 등록된 핸들러가 API 요청을 캡처
        await page.reload()

        # 새로고침 후 API 응답이 완료될 때까지 3초 대기
        await page.wait_for_timeout(3000)

        self.logger.info(f"\n=== {self.url} 에서 호출되는 API 목록 ===")
        for api_url in captured:
            parsed = urlparse(api_url)
            query_params = parse_qs(parsed.query)

            self.logger.info(f"URL       : {api_url}")
            self.logger.info(f"Path      : {parsed.path}")
            self.logger.info(f"QueryString: {query_params}")
            self.logger.info("---")

        # 브라우저 페이지 닫기 (메모리 누수 방지)
        await page.close()

    async def errback(self, failure):
        # 요청 실패 시 에러 로그 출력 후 브라우저 페이지 닫기
        self.logger.error(f"요청 실패: {failure}")
        page = failure.request.meta.get("playwright_page")
        if page:
            await page.close()
