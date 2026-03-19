

### 버전
- Python: 3.14.3
- uv: 0.10.11


```
├── scrapy.cfg              # 배포 설정 파일
└── myproject/
  ├── __init__.py
  ├── items.py            # 스크래핑할 데이터 구조 정의
  ├── middlewares.py      # 다운로더/스파이더 미들웨어
  ├── pipelines.py        # 아이템 파이프라인 (데이터 처리/저장)
  ├── settings.py         # 프로젝트 설정
  └── spiders/            # 스파이더 디렉토리
      ├── __init__.py
      └── my_spider.py    # 실제 크롤링 로직

```

```shell
## 프로젝트 생성
uv run scrapy startproject [프로젝트명]

## 스파이더 생성
uv run scrapy genspider [스파이더명] [도메인]

## 
uv run scrapy crawl [스파이더명]

## scrapy-playwright 프로젝트 패키지 추가 (동적 웹사이트 크롤링 지원)
uv add scrapy-playwright

## playwright 
uv run playwright install chromium

```

### 네이버 스포츠
- 경기일정: https://m.sports.naver.com/kbaseball/schedule/index?category=kbo&date=2026-03-12
- 팀정보: https://m.sports.naver.com/kbaseball/record/kbo?tab=teamRank
- 팀기록: https://m.sports.naver.com/kbaseball/record/kbo?seasonCode=2026&tab=teamRecord
- 타자목록: https://m.sports.naver.com/kbaseball/record/kbo?tab=hitter
- 팀별 타자목록: https://m.sports.naver.com/kbaseball/record/kbo?tab=hitter&teamCode=KIA
- 투수목록: https://m.sports.naver.com/kbaseball/record/kbo?tab=pitcher
- 팀별 투수목록: https://m.sports.naver.com/kbaseball/record/kbo?tab=pitcher&teamCode=KIA


> [Spyder > Docs](https://docs.scrapy.org/en/latest/index.html)

> 
> 