from datetime import datetime, timezone, timedelta

import scrapy

from scrapying.constants import API_DOMAIN
from scrapying.items import CrawledItem


class NaversportsKboScheduleGameSpider(scrapy.Spider):
    """KBO 경기일정을 수집하는 스파이더.

    실행 방법:
        scrapy crawl naversports_kbo_schedule_game                                                  # 오늘 경기일정
        scrapy crawl naversports_kbo_schedule_game -a from_date=2026-03-21                         # 특정 날짜 경기일정
        scrapy crawl naversports_kbo_schedule_game -a from_date=2026-03-21 -a to_date=2026-03-25   # 날짜 범위 경기일정

    동작 흐름:
        start() → 날짜 범위 계산
              ↓
        parse() → /schedule/games API 호출 → CrawledItem yield
              ↓
        LoggingPipeline → 로그 출력
    """

    name = "naversports_kbo_schedule_game"

    def __init__(self, from_date=None, to_date=None, **kwargs):
        super().__init__(**kwargs)
        kst = timezone(timedelta(hours=9))
        today = datetime.now(kst).strftime("%Y-%m-%d")
        self.from_date = from_date or today
        self.to_date = to_date or self.from_date

    async def start(self):
        from_date = self.from_date
        to_date = self.to_date

        params = {
            "fields": "basic,schedule,baseball,manualRelayUrl",
            "upperCategoryId": "kbaseball",
            "categoryId": "kbo",
            "fromDate": from_date,
            "toDate": to_date,
            "roundCodes": "",
            "size": "500",
        }
        query = "&".join(f"{k}={v}" for k, v in params.items())
        url = f"{API_DOMAIN}/schedule/games?{query}"

        yield scrapy.Request(url=url, callback=self.parse, cb_kwargs={"from_date": from_date})

    def parse(self, response, from_date):
        content_type = response.headers.get("Content-Type", b"").decode()

        if "json" not in content_type:
            self.logger.warning(f"예상하지 못한 Content-Type: {content_type}")
            return

        period = from_date if from_date == self.to_date else f"{from_date} ~ {self.to_date}"
        self.logger.info(f"조회 기간: {period}")

        item = CrawledItem()
        item["source"] = "naversports"
        item["data_type"] = "naversports_kbo_schedule_game"
        item["content_type"] = "json"
        item["raw_data"] = response.text
        yield item
