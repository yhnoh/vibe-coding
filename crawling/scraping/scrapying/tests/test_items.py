from scrapying.items import CrawledItem


def test_crawled_item_has_required_fields():
    item = CrawledItem()
    item["source"] = "naver-sports"
    item["data_type"] = "kbo-team-rank"
    item["content_type"] = "json"
    item["raw_data"] = '{"teams": []}'

    assert item["source"] == "naver-sports"
    assert item["data_type"] == "kbo-team-rank"
    assert item["content_type"] == "json"
    assert item["raw_data"] == '{"teams": []}'
