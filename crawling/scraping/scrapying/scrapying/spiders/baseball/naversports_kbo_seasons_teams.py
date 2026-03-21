from collections.abc import AsyncIterator, Iterator
from typing import Any

import scrapy
from scrapy.http import TextResponse

from scrapying.constants import API_DOMAIN
from scrapying.items import CrawledItem


class NaversportsKboSeasonsTeamsSpider(scrapy.Spider):
    """KBO 팀 순위 및 기록을 수집하는 스파이더.

    실행 방법:
        scrapy crawl naversports_kbo_seasons_teams -a season=2026

    동작 흐름:
        start() → /statistics/categories/kbo/seasons/{season}/teams API 호출
              ↓
        parse() → CrawledItem yield
              ↓
        LoggingPipeline → 로그 출력
    """

    name: str = "naversports_kbo_seasons_teams"

    season: str

    def __init__(self, season: str | None = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        if not season:
            raise ValueError("season 파라미터가 필요합니다. (예: -a season=2026)")
        self.season = season

    async def start(self) -> AsyncIterator[scrapy.Request]:
        url: str = f"{API_DOMAIN}/statistics/categories/kbo/seasons/{self.season}/teams"

        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response: TextResponse) -> Iterator[CrawledItem]:
        content_type: str = response.headers.get("Content-Type", b"").decode()

        if "json" not in content_type:
            self.logger.warning(f"예상하지 못한 Content-Type: {content_type}")
            return

        self.logger.info(f"시즌: {self.season}")

        item: CrawledItem = CrawledItem()
        item["source"] = "naversports"
        item["data_type"] = "naversports_kbo_seasons_teams"
        item["content_type"] = "json"
        item["raw_data"] = response.text
        yield item