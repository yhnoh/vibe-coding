from collections.abc import AsyncIterator, Iterator
from typing import Any

import scrapy
from scrapy.http import TextResponse

from scrapying.constants import API_DOMAIN
from scrapying.items import CrawledItem


class NaversportsKboScheduleGamesSpider(scrapy.Spider):
    """KBO 경기일정을 수집하는 스파이더.

    실행 방법:
        scrapy crawl naversports_kbo_schedule_games -a from_date=2026-03-21 -a to_date=2026-03-21
        scrapy crawl naversports_kbo_schedule_games -a from_date=2026-03-21 -a to_date=2026-03-25

    동작 흐름:
        start() → 날짜 범위 계산
              ↓
        parse() → /schedule/games API 호출 → CrawledItem yield
              ↓
        LoggingPipeline → 로그 출력
    """

    name: str = "naversports_kbo_schedule_games"

    from_date: str
    to_date: str

    def __init__(self, from_date: str | None = None, to_date: str | None = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        if not from_date:
            raise ValueError("from_date 파라미터가 필요합니다. (예: -a from_date=2026-03-21)")
        if not to_date:
            raise ValueError("to_date 파라미터가 필요합니다. (예: -a to_date=2026-03-21)")
        self.from_date = from_date
        self.to_date = to_date

    async def start(self) -> AsyncIterator[scrapy.Request]:
        from_date: str = self.from_date
        to_date: str = self.to_date

        params: dict[str, str] = {
            "fields": "basic,schedule,baseball,manualRelayUrl",
            "upperCategoryId": "kbaseball",
            "categoryId": "kbo",
            "fromDate": from_date,
            "toDate": to_date,
            "roundCodes": "",
            "size": "500",
        }
        query: str = "&".join(f"{k}={v}" for k, v in params.items())
        url: str = f"{API_DOMAIN}/schedule/games?{query}"

        yield scrapy.Request(url=url, callback=self.parse, cb_kwargs={"from_date": from_date})

    def parse(self, response: TextResponse, from_date: str) -> Iterator[CrawledItem]:
        content_type: str = response.headers.get("Content-Type", b"").decode()

        if "json" not in content_type:
            self.logger.warning(f"예상하지 못한 Content-Type: {content_type}")
            return

        period: str = from_date if from_date == self.to_date else f"{from_date} ~ {self.to_date}"
        self.logger.info(f"조회 기간: {period}")

        item: CrawledItem = CrawledItem()
        item["source"] = "naversports"
        item["data_type"] = "naversports_kbo_schedule_games"
        item["content_type"] = "json"
        item["raw_data"] = response.text
        yield item
