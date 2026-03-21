import json
from collections.abc import AsyncIterator, Iterator
from typing import Any

import scrapy
from scrapy.http import TextResponse
from scrapy_playwright.page import PageMethod

from scrapying.items import CrawledItem

LINEUP_JS = """
() => {
    const allLists = document.querySelectorAll('[role="list"], ul, ol');
    const result = [];
    for (const list of allLists) {
        const items = list.querySelectorAll('[role="listitem"], li');
        if (items.length < 5) continue;
        const firstStrong = items[0]?.querySelector('strong');
        if (!firstStrong) continue;

        const players = [];
        for (const item of items) {
            const img = item.querySelector('img[src*="player"]');
            const playerId = img ? img.src.match(/\\/(\\d+)\\.png/)?.[1] || null : null;
            const strong = item.querySelector('strong');
            const name = strong ? strong.textContent.trim() : '';
            const allText = item.textContent.trim();
            const posMatch = allText.match(/(중견수|좌익수|우익수|1루수|2루수|3루수|유격수|포수|지명타자|우투|좌투|우언|좌언)\\s*[,\\s]*(우타|좌타|양타)?/);
            const position = posMatch ? posMatch[0].trim() : '';
            const orderMatch = allText.match(/^(선발|\\d+)/);
            const order = orderMatch ? orderMatch[1] : '';
            players.push({ playerId, name, position, order });
        }
        result.push(players);
    }
    return result;
}
"""


class NaversportsKboScheduleGamesLineupSpider(scrapy.Spider):
    """KBO 경기별 라인업을 Playwright로 크롤링하는 스파이더.

    실행 방법:
        scrapy crawl naversports_kbo_schedule_games_lineup -a game_id=20260321HHLT02026

    동작 흐름:
        start() → Playwright로 라인업 페이지 렌더링
              ↓
        parse() → JavaScript로 DOM에서 라인업 추출 → CrawledItem yield
              ↓
        LoggingPipeline → 로그 출력
    """

    name: str = "naversports_kbo_schedule_games_lineup"

    game_id: str

    def __init__(self, game_id: str | None = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        if not game_id:
            raise ValueError("game_id 파라미터가 필요합니다. (예: -a game_id=20260321HHLT02026)")
        self.game_id = game_id

    async def start(self) -> AsyncIterator[scrapy.Request]:
        url: str = f"https://m.sports.naver.com/game/{self.game_id}/lineup"

        yield scrapy.Request(
            url=url,
            callback=self.parse,
            meta={
                "playwright": True,
                "playwright_include_page": True,
                "playwright_page_methods": [
                    PageMethod("wait_for_selector", "h4", timeout=15000),
                    PageMethod("wait_for_timeout", 2000),
                ],
            },
        )

    async def parse(self, response: TextResponse) -> AsyncIterator[CrawledItem]:
        page = response.meta.get("playwright_page")
        if not page:
            self.logger.warning("Playwright 페이지를 가져올 수 없습니다.")
            return

        try:
            lineup_data: list = await page.evaluate(LINEUP_JS)

            result: dict = {
                "gameId": self.game_id,
                "away": lineup_data[0] if len(lineup_data) > 0 else [],
                "home": lineup_data[1] if len(lineup_data) > 1 else [],
            }

            self.logger.info(f"경기 ID: {self.game_id} | 원정: {len(result['away'])}명 | 홈: {len(result['home'])}명")

            item: CrawledItem = CrawledItem()
            item["source"] = "naversports"
            item["data_type"] = "naversports_kbo_schedule_games_lineup"
            item["content_type"] = "json"
            item["raw_data"] = json.dumps(result, ensure_ascii=False)
            yield item
        finally:
            await page.close()
