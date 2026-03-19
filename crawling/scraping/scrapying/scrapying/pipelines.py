# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


from datetime import datetime, timezone, timedelta

import boto3
from itemadapter import ItemAdapter

from scrapying.items import CrawledItem


class S3UploadPipeline:
    """CrawledItem을 S3에 원본 그대로 업로드하는 Pipeline.

    S3 경로 규칙: raw/{source}/{data_type}/{yyyy}/{MM}/{dd}/{timestamp}.{ext}
    """

    def __init__(self, bucket_name, region_name="ap-northeast-2"):
        self.bucket_name = bucket_name
        self.region_name = region_name
        self.s3_client = None

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            bucket_name=crawler.settings.get("S3_BUCKET_NAME"),
            region_name=crawler.settings.get("S3_REGION_NAME", "ap-northeast-2"),
        )

    def open_spider(self, spider):
        self.s3_client = boto3.client("s3", region_name=self.region_name)

    def process_item(self, item, spider):
        if not isinstance(item, CrawledItem):
            return item

        adapter = ItemAdapter(item)
        source = adapter["source"]
        data_type = adapter["data_type"]
        content_type = adapter["content_type"]
        raw_data = adapter["raw_data"]

        ext = "json" if content_type == "json" else "html"
        kst = timezone(timedelta(hours=9))
        now = datetime.now(kst)
        timestamp = int(now.timestamp())

        key = f"raw/{source}/{data_type}/{now.strftime('%Y/%m/%d')}/{timestamp}.{ext}"

        self.s3_client.put_object(
            Bucket=self.bucket_name,
            Key=key,
            Body=raw_data.encode("utf-8"),
            ContentType="application/json" if ext == "json" else "text/html",
        )

        if spider:
            spider.logger.info(f"S3 업로드 완료: s3://{self.bucket_name}/{key}")

        return item
