import scrapy

from scrapying.constants import API_DOMAIN, TEAM_CODES
from scrapying.items import CrawledItem


class KboHitterSpider(scrapy.Spider):
    """KBO 타자 목록을 수집하는 스파이더.

    실행 방법:
        scrapy crawl kbo_hitter                           # 전체 타자 목록
        scrapy crawl kbo_hitter -a season=2025            # 특정 시즌
        scrapy crawl kbo_hitter -a team=HT                # 특정 팀만
        scrapy crawl kbo_hitter -a all_teams=true         # 팀별로 각각 수집

    동작 흐름:
        start() → /statistics/.../players?playerType=HITTER API 호출
              ↓
        parse() → CrawledItem yield
              ↓
        S3UploadPipeline → S3에 원본 업로드
    """

    name = "kbo_hitter"

    def __init__(self, season="2026", team=None, all_teams=None, **kwargs):
        super().__init__(**kwargs)
        self.season = season
        self.team = team
        self.all_teams = all_teams == "true"

    async def start(self):
        base_url = (
            f"{API_DOMAIN}/statistics/categories/kbo/seasons/{self.season}/players"
            f"?sortField=hitterHra&sortDirection=desc&playerType=HITTER&pageSize=500"
        )

        if self.team:
            yield scrapy.Request(
                url=f"{base_url}&teamCode={self.team}",
                callback=self.parse,
                cb_kwargs={"team_code": self.team},
            )
        elif self.all_teams:
            for team_code in TEAM_CODES:
                yield scrapy.Request(
                    url=f"{base_url}&teamCode={team_code}",
                    callback=self.parse,
                    cb_kwargs={"team_code": team_code},
                )
        else:
            yield scrapy.Request(
                url=base_url,
                callback=self.parse,
                cb_kwargs={"team_code": None},
            )

    def parse(self, response, team_code):
        content_type = response.headers.get("Content-Type", b"").decode()
        label = f"팀({team_code})" if team_code else "전체"
        self.logger.info(f"\n=== 타자 목록 [{label}]: {response.url} ===")

        if "json" in content_type:
            item = CrawledItem()
            item["source"] = "naver-sports"
            item["data_type"] = f"kbo-hitter-{team_code}" if team_code else "kbo-hitter"
            item["content_type"] = "json"
            item["raw_data"] = response.text
            yield item
