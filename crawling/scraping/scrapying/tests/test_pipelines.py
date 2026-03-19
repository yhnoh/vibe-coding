import json
import re

import boto3
import pytest
from moto import mock_aws
from scrapying.items import CrawledItem
from scrapying.pipelines import S3UploadPipeline

BUCKET = "test-bucket"
REGION = "ap-northeast-2"


@pytest.fixture
def s3_env():
    """mock_aws 컨텍스트 안에서 S3 버킷 생성 + Pipeline + S3 client를 제공"""
    with mock_aws():
        conn = boto3.client("s3", region_name=REGION)
        conn.create_bucket(
            Bucket=BUCKET,
            CreateBucketConfiguration={"LocationConstraint": REGION},
        )
        pipeline = S3UploadPipeline(bucket_name=BUCKET, region_name=REGION)
        pipeline.open_spider(None)
        yield conn, pipeline


def test_s3_upload_json_item(s3_env):
    conn, pipeline = s3_env

    item = CrawledItem()
    item["source"] = "naver-sports"
    item["data_type"] = "kbo-team-rank"
    item["content_type"] = "json"
    item["raw_data"] = json.dumps({"teams": [{"name": "LG"}]})

    result = pipeline.process_item(item, None)

    assert result == item

    objects = conn.list_objects_v2(Bucket=BUCKET, Prefix="raw/naver-sports/kbo-team-rank/")
    assert objects["KeyCount"] == 1

    key = objects["Contents"][0]["Key"]
    assert key.endswith(".json")

    body = conn.get_object(Bucket=BUCKET, Key=key)["Body"].read().decode()
    assert json.loads(body) == {"teams": [{"name": "LG"}]}


def test_s3_upload_html_item(s3_env):
    conn, pipeline = s3_env

    item = CrawledItem()
    item["source"] = "naver-sports"
    item["data_type"] = "kbo-hitter"
    item["content_type"] = "html"
    item["raw_data"] = "<html><body>data</body></html>"

    pipeline.process_item(item, None)

    objects = conn.list_objects_v2(Bucket=BUCKET, Prefix="raw/naver-sports/kbo-hitter/")
    assert objects["KeyCount"] == 1

    key = objects["Contents"][0]["Key"]
    assert key.endswith(".html")


def test_s3_key_follows_path_convention(s3_env):
    """S3 경로가 raw/{source}/{data_type}/{yyyy}/{MM}/{dd}/{timestamp}.{ext} 형식인지 확인"""
    conn, pipeline = s3_env

    item = CrawledItem()
    item["source"] = "naver-sports"
    item["data_type"] = "kbo-team-rank"
    item["content_type"] = "json"
    item["raw_data"] = "{}"

    pipeline.process_item(item, None)

    objects = conn.list_objects_v2(Bucket=BUCKET, Prefix="raw/")
    key = objects["Contents"][0]["Key"]

    pattern = r"^raw/[\w-]+/[\w-]+/\d{4}/\d{2}/\d{2}/\d+\.\w+$"
    assert re.match(pattern, key), f"S3 key가 경로 규칙에 맞지 않음: {key}"
