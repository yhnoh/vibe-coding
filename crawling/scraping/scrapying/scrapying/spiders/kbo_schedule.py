import calendar
from datetime import datetime, timezone, timedelta

import scrapy

from scrapying.constants import API_DOMAIN
from scrapying.items import CrawledItem


class KboScheduleSpider(scrapy.Spider):
    """KBO 경기일정을 수집하는 스파이더.

    실행 방법:
        scrapy crawl kbo_schedule                          # 이번 달 경기일정
        scrapy crawl kbo_schedule -a month=2026-04         # 특정 월 경기일정
        scrapy crawl kbo_schedule -a from=2026-03&to=2026-05  # 월 범위 수집

    동작 흐름:
        start() → 날짜 범위 계산
              ↓
        parse() → /schedule/games API 호출 → CrawledItem yield
              ↓
        S3UploadPipeline → S3에 원본 업로드
    """

    name = "kbo_schedule"

    def __init__(self, month=None, **kwargs):
        super().__init__(**kwargs)
        self.month = month

    async def start(self):
        kst = timezone(timedelta(hours=9))
        now = datetime.now(kst)

        if self.month:
            year, mon = map(int, self.month.split("-"))
        else:
            year, mon = now.year, now.month

        last_day = calendar.monthrange(year, mon)[1]
        from_date = f"{year}-{mon:02d}-01"
        to_date = f"{year}-{mon:02d}-{last_day:02d}"

        url = (
            f"{API_DOMAIN}/schedule/games"
            f"?fields=basic%2Cschedule%2Cbaseball%2CmanualRelayUrl"
            f"&upperCategoryId=kbaseball&categoryId=kbo"
            f"&fromDate={from_date}&toDate={to_date}"
            f"&roundCodes=&size=500"
        )

        yield scrapy.Request(url=url, callback=self.parse, cb_kwargs={"from_date": from_date})

    def parse(self, response, from_date):
        content_type = response.headers.get("Content-Type", b"").decode()
        self.logger.info(f"\n=== 경기일정: {response.url} | Content-Type: {content_type} ===")

        if "json" in content_type:
            item = CrawledItem()
            item["source"] = "naver-sports"
            item["data_type"] = "kbo-schedule"
            item["content_type"] = "json"
            item["raw_data"] = response.text
            yield item
        else:
            self.logger.warning(f"예상하지 못한 Content-Type: {content_type}")
