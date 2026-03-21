from collections.abc import AsyncIterator, Iterator
from typing import Any

import scrapy
from scrapy.http import TextResponse

from scrapying.constants import API_DOMAIN
from scrapying.items import CrawledItem


class NaversportsKboScheduleGamesRecordSpider(scrapy.Spider):
    """KBO 경기별 기록(타자/투수 박스스코어)을 수집하는 스파이더.

    실행 방법:
        scrapy crawl naversports_kbo_schedule_games_record -a game_id=20260319HTHH02026

    동작 흐름:
        start() → /schedule/games/{game_id}/record API 호출
              ↓
        parse() → CrawledItem yield
              ↓
        LoggingPipeline → 로그 출력
    """

    name: str = "naversports_kbo_schedule_games_record"

    game_id: str

    def __init__(self, game_id: str | None = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        if not game_id:
            raise ValueError("game_id 파라미터가 필요합니다. (예: -a game_id=20260319HTHH02026)")
        self.game_id = game_id

    async def start(self) -> AsyncIterator[scrapy.Request]:
        url: str = f"{API_DOMAIN}/schedule/games/{self.game_id}/record"

        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response: TextResponse) -> Iterator[CrawledItem]:
        content_type: str = response.headers.get("Content-Type", b"").decode()

        if "json" not in content_type:
            self.logger.warning(f"예상하지 못한 Content-Type: {content_type}")
            return

        self.logger.info(f"경기 ID: {self.game_id}")

        item: CrawledItem = CrawledItem()
        item["source"] = "naversports"
        item["data_type"] = "naversports_kbo_schedule_games_record"
        item["content_type"] = "json"
        item["raw_data"] = response.text
        yield item