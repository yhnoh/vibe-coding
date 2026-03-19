FROM python:3.14-slim

# uv 설치
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# 프로젝트 복사 (빌드 컨텍스트가 프로젝트 루트)
COPY . /app
WORKDIR /app

# 의존성 설치
RUN uv sync --frozen

# Playwright 브라우저 설치
RUN uv run playwright install chromium --with-deps

# scrapy.cfg가 있는 디렉토리로 이동
WORKDIR /app/scrapying

ENTRYPOINT ["uv", "run", "scrapy"]
CMD ["crawl", "api_call"]
