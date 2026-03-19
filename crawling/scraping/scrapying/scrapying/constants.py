from dataclasses import dataclass, field


@dataclass(frozen=True)
class CrawlTarget:
    """크롤링 대상을 정의하는 데이터 클래스.

    source: 데이터 출처 (S3 경로의 첫 번째 세그먼트)
    data_type: 데이터 종류 (S3 경로의 두 번째 세그먼트)
    url_template: URL 템플릿 ({param} 형태의 플레이스홀더 포함 가능)
    content_type: 응답 타입 ("json" 또는 "html")
    default_params: URL 템플릿의 기본 파라미터 값
    """
    source: str
    data_type: str
    url_template: str
    content_type: str  # "json" or "html"
    default_params: dict = field(default_factory=dict)

    def build_url(self, params: dict | None = None) -> str:
        """URL 템플릿에 파라미터를 적용하여 최종 URL을 생성한다.
        params가 주어지면 default_params를 오버라이드한다.
        """
        merged = {**self.default_params, **(params or {})}
        return self.url_template.format(**merged) if merged else self.url_template


API_DOMAIN = "https://api-gw.sports.naver.com"
TARGETS: list[CrawlTarget] = [
    # === 경기일정 ===
    CrawlTarget(
        source="naver-sports",
        data_type="kbo-schedule",
        url_template=(
            API_DOMAIN + "/schedule/games?fields=basic%2Cschedule%2Cbaseball%2CmanualRelayUrl&upperCategoryId=kbaseball&categoryId=kbo&fromDate={fromDate}&toDate={toDate}&roundCodes=&size=500"),
        content_type="json",
        default_params={"fromDate": "2026-03-01", "toDate": "2026-03-31"},
    ),
    # === 팀 순위/기록 ===
    CrawlTarget(
        source="naver-sports",
        data_type="kbo-team-stats",
        url_template=(
              "%s/statistics/categories/kbo/seasons/{seasonCode}/teams" % API_DOMAIN),
        content_type="json",
        default_params={"seasonCode": "2026"},
    ),
    # === 팀 최근 10경기 ===
    CrawlTarget(
        source="naver-sports",
        data_type="kbo-team-last-ten",
        url_template=(
              "%s/statistics/categories/kbo/seasons/{seasonCode}/teams/last-ten-games" % API_DOMAIN),
        content_type="json",
        default_params={"seasonCode": "2026"},
    ),
    # === 타자 목록 ===
    CrawlTarget(
        source="naver-sports",
        data_type="kbo-hitter",
        url_template=(
              "%s/statistics/categories/kbo/seasons/{seasonCode}/players?sortField=hitterHra&sortDirection=desc&playerType=HITTER&pageSize=500" % API_DOMAIN),
        content_type="json",
        default_params={"seasonCode": "2026"},
    ),
    # === 투수 목록 ===
    CrawlTarget(
        source="naver-sports",
        data_type="kbo-pitcher",
        url_template=(
              "%s/statistics/categories/kbo/seasons/{seasonCode}/players?sortField=pitcherEra&sortDirection=asc&playerType=PITCHER&pageSize=500" % API_DOMAIN),
        content_type="json",
        default_params={"seasonCode": "2026"},
    ),
]

# 실제 네이버 스포츠 팀 코드 (api_capture로 확인됨)
TEAM_CODES: dict[str, str] = {
    "LT": "롯데 자이언츠",
    "OB": "두산 베어스",
    "SS": "삼성 라이온즈",
    "LG": "LG 트윈스",
    "NC": "NC 다이노스",
    "HH": "한화 이글스",
    "SK": "SSG 랜더스",
    "HT": "KIA 타이거즈",
    "WO": "키움 히어로즈",
    "KT": "KT 위즈",
}
