from collections.abc import AsyncIterator, Iterator
from typing import Any

import scrapy
from scrapy.http import TextResponse

from scrapying.constants import API_DOMAIN
from scrapying.items import CrawledItem


class NaversportsKboSeasonsPlayersHitterSpider(scrapy.Spider):
    """KBO 타자 선수 기록을 수집하는 스파이더.

    실행 방법:
        scrapy crawl naversports_kbo_seasons_players_hitter -a season=2026 -a team_code=OB

    동작 흐름:
        start() → /statistics/categories/kbo/seasons/{season}/players API 호출
              ↓
        parse() → CrawledItem yield
              ↓
        LoggingPipeline → 로그 출력
    """

    name: str = "naversports_kbo_seasons_players_hitter"

    season: str
    team_code: str | None

    def __init__(self, season: str | None = None, team_code: str | None = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        if not season:
            raise ValueError("season 파라미터가 필요합니다. (예: -a season=2026)")
        if not team_code:
            raise ValueError("team_code 파라미터가 필요합니다. (예: -a team_code=OB)")
        self.season = season
        self.team_code = team_code

    async def start(self) -> AsyncIterator[scrapy.Request]:
        params: dict[str, str] = {
            "sortField": "hitterHra",
            "sortDirection": "desc",
            "playerType": "HITTER",
            "pageSize": "500",
            "teamCode": self.team_code,
        }

        query: str = "&".join(f"{k}={v}" for k, v in params.items())
        url: str = f"{API_DOMAIN}/statistics/categories/kbo/seasons/{self.season}/players?{query}"

        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response: TextResponse) -> Iterator[CrawledItem]:
        content_type: str = response.headers.get("Content-Type", b"").decode()

        if "json" not in content_type:
            self.logger.warning(f"예상하지 못한 Content-Type: {content_type}")
            return

        self.logger.info(f"시즌: {self.season} | 팀: {self.team_code}")

        item: CrawledItem = CrawledItem()
        item["source"] = "naversports"
        item["data_type"] = "naversports_kbo_seasons_players_hitter"
        item["content_type"] = "json"
        item["raw_data"] = response.text
        yield item