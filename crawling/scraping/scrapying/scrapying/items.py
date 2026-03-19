import scrapy


class CrawledItem(scrapy.Item):
    """크롤링 결과를 담는 Item. S3Pipeline이 이 Item을 S3에 업로드한다."""
    source = scrapy.Field()        # 데이터 출처 (예: "naver-sports")
    data_type = scrapy.Field()     # 데이터 종류 (예: "kbo-team-rank")
    content_type = scrapy.Field()  # 응답 타입 ("json" 또는 "html")
    raw_data = scrapy.Field()      # 원본 데이터 (JSON 문자열 또는 HTML 문자열)
