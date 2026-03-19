from scrapying.constants import CrawlTarget, TARGETS


def test_crawl_target_with_url_template():
    target = CrawlTarget(
        source="naver-sports",
        data_type="kbo-schedule",
        url_template="https://api-gw.sports.naver.com/schedule/games?fromDate={fromDate}&toDate={toDate}",
        content_type="json",
        default_params={"fromDate": "2026-03-01", "toDate": "2026-03-31"},
    )
    assert target.source == "naver-sports"
    assert "fromDate=2026-03-01" in target.build_url()
    assert "toDate=2026-03-31" in target.build_url()


def test_crawl_target_build_url_with_override():
    target = CrawlTarget(
        source="naver-sports",
        data_type="kbo-schedule",
        url_template="https://api-gw.sports.naver.com/schedule/games?fromDate={fromDate}&toDate={toDate}",
        content_type="json",
        default_params={"fromDate": "2026-03-01", "toDate": "2026-03-31"},
    )
    url = target.build_url(params={"fromDate": "2026-04-01", "toDate": "2026-04-30"})
    assert "fromDate=2026-04-01" in url
    assert "toDate=2026-04-30" in url


def test_crawl_target_without_params():
    target = CrawlTarget(
        source="naver-sports",
        data_type="kbo-team-rank",
        url_template="https://api-gw.sports.naver.com/statistics/categories/kbo/seasons/2026/teams",
        content_type="json",
    )
    assert target.build_url() == "https://api-gw.sports.naver.com/statistics/categories/kbo/seasons/2026/teams"


def test_targets_is_list():
    assert isinstance(TARGETS, list)
    assert len(TARGETS) > 0
