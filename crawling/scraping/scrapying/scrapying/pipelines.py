# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


import json
import logging

from itemadapter import ItemAdapter

from scrapying.items import CrawledItem

logger = logging.getLogger(__name__)


class LoggingPipeline:
    """CrawledItem을 로그로 출력하는 Pipeline.

    JSON 데이터는 파싱하여 요약 정보를 로그로 출력한다.
    나중에 S3UploadPipeline 등으로 교체 가능.
    """

    def process_item(self, item, spider):
        if not isinstance(item, CrawledItem):
            return item

        # Spyder에서 수집된 CrawledItem을 로그로 출력
        adapter = ItemAdapter(item)
        source = adapter["source"]
        data_type = adapter["data_type"]
        content_type = adapter["content_type"]
        raw_data = adapter["raw_data"]

        if content_type == "json":
            data = json.loads(raw_data)
            spider.logger.info(
                f"[{source}/{data_type}] JSON 수집 완료 | "
                f"keys={list(data.get('result', data).keys())}"
            )
            # raw_data 전체를 DEBUG 레벨로 출력
            spider.logger.debug(f"[{source}/{data_type}] raw_data:\n{json.dumps(data, indent=2, ensure_ascii=False)[:2000]}")
        else:
            spider.logger.info(
                f"[{source}/{data_type}] HTML 수집 완료 | "
                f"length={len(raw_data)}"
            )

        return item
