import scrapy

from scrapying.constants import API_DOMAIN
from scrapying.items import CrawledItem


class KboTeamStatsSpider(scrapy.Spider):
    """KBO 팀 순위 및 팀 기록을 수집하는 스파이더.

    실행 방법:
        scrapy crawl kbo_team_stats                       # 2026 시즌 (기본)
        scrapy crawl kbo_team_stats -a season=2025        # 특정 시즌

    동작 흐름:
        start() → /statistics/.../teams API 호출 (팀 순위 + 기록 통합)
                → /statistics/.../teams/last-ten-games API 호출 (최근 10경기)
              ↓
        parse_teams() / parse_last_ten() → CrawledItem yield
              ↓
        S3UploadPipeline → S3에 원본 업로드
    """

    name = "kbo_team_stats"

    def __init__(self, season="2026", **kwargs):
        super().__init__(**kwargs)
        self.season = season

    async def start(self):
        base = f"{API_DOMAIN}/statistics/categories/kbo/seasons/{self.season}"

        yield scrapy.Request(
            url=f"{base}/teams",
            callback=self.parse_teams,
        )
        yield scrapy.Request(
            url=f"{base}/teams/last-ten-games",
            callback=self.parse_last_ten,
        )

    def parse_teams(self, response):
        content_type = response.headers.get("Content-Type", b"").decode()
        self.logger.info(f"\n=== 팀 순위/기록: {response.url} ===")

        if "json" in content_type:
            item = CrawledItem()
            item["source"] = "naver-sports"
            item["data_type"] = "kbo-team-stats"
            item["content_type"] = "json"
            item["raw_data"] = response.text
            yield item

    def parse_last_ten(self, response):
        content_type = response.headers.get("Content-Type", b"").decode()
        self.logger.info(f"\n=== 팀 최근 10경기: {response.url} ===")

        if "json" in content_type:
            item = CrawledItem()
            item["source"] = "naver-sports"
            item["data_type"] = "kbo-team-last-ten"
            item["content_type"] = "json"
            item["raw_data"] = response.text
            yield item
