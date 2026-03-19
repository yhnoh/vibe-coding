# 웹 크롤링 아키텍처 설계: Java 방식

## 개요

Spring 단일 스택으로 크롤링부터 데이터 가공/서빙까지 처리하는 아키텍처.
핵심 원칙: **기존 Spring 인프라에 크롤링을 통합** — 별도 언어/배포 없음.

## 전체 아키텍처

```
[데이터 수집 + 가공/서빙 — Spring 단일 스택]

Spring Batch (크롤링 Job)  ──→  S3 (원본)  ──→  Spring Batch (파싱 Job → DB 저장)
                                                Spring API (데이터 서빙)
```

## 역할 분리

| 계층 | 역할 | 하지 않는 것 |
|------|------|-------------|
| Spring Batch (크롤링 Job) | 웹 크롤링 → 원본 그대로 S3 업로드 | 파싱, 가공, 비즈니스 로직 |
| S3 | 원본 데이터 보관 (JSON/HTML) | - |
| Spring Batch (파싱 Job) | S3에서 원본 읽기 → 파싱 → DB 저장 | 크롤링 |
| Spring API | DB 데이터 조회/서빙 | 크롤링, 파싱 |

## S3 경로 규칙

Python 방식과 동일:
```
s3://bucket/raw/{source}/{data-type}/{yyyy}/{MM}/{dd}/{timestamp}.json
```

## 기술 스택

| 용도 | 라이브러리 |
|------|-----------|
| HTML 파싱 (정적 페이지) | Jsoup |
| API 호출 (JSON 응답) | RestTemplate / WebClient |
| JS 렌더링 (동적 페이지) | Playwright for Java |
| 네트워크 요청 가로채기 | Playwright for Java (route, intercept) |
| S3 업로드 | AWS SDK for Java |

## 프로젝트 구조

기존 Spring Batch 서버에 크롤링 모듈 추가:

```
spring-batch/
├── src/main/java/
│   ├── crawling/                    # 크롤링 모듈
│   │   ├── job/
│   │   │   ├── ApiCaptureJob.java   # API URL 탐지 Job
│   │   │   ├── ApiCallJob.java      # API 직접 호출 Job
│   │   │   └── HtmlCrawlJob.java    # HTML 크롤링 Job
│   │   ├── service/
│   │   │   ├── PlaywrightService.java   # Playwright 브라우저 관리
│   │   │   ├── CrawlingService.java     # 크롤링 공통 로직
│   │   │   └── S3UploadService.java     # S3 업로드
│   │   └── config/
│   │       ├── CrawlingConfig.java      # 크롤링 설정 (rate limit, retry 등)
│   │       └── PlaywrightConfig.java    # Playwright 설정
│   ├── parsing/                     # 파싱 모듈 (S3 → DB)
│   │   ├── job/
│   │   │   └── DataParsingJob.java
│   │   └── parser/
│   │       ├── KboTeamRankParser.java
│   │       └── ...
│   └── api/                         # API 서빙 (별도 서버)
```

## JS 렌더링: Playwright for Java

### API URL 탐지 (Python api_capture와 동일한 역할)

```java
@Component
public class ApiCaptureService {

    public List<String> captureApiUrls(String targetUrl) {
        List<String> capturedUrls = new ArrayList<>();

        try (Playwright playwright = Playwright.create()) {
            Browser browser = playwright.chromium().launch();
            Page page = browser.newPage();

            page.onRequest(request -> {
                String type = request.resourceType();
                if ("fetch".equals(type) || "xhr".equals(type)) {
                    capturedUrls.add(request.url());
                }
            });

            page.navigate(targetUrl);
            page.waitForTimeout(3000);
        }

        return capturedUrls;
    }
}
```

### HTML 크롤링

```java
@Component
public class HtmlCrawlService {

    public String crawlRenderedHtml(String targetUrl) {
        try (Playwright playwright = Playwright.create()) {
            Browser browser = playwright.chromium().launch();
            Page page = browser.newPage();
            page.navigate(targetUrl);
            page.waitForTimeout(3000);
            return page.content(); // JS 렌더링 완료된 HTML
        }
    }
}
```

## 직접 구현해야 하는 것들

Scrapy가 기본 제공하지만 Java에서는 직접 만들어야 하는 기능:

### 1. Rate Limiting (요청 간격 제어)

```java
@Component
public class RateLimiter {
    private final Map<String, Long> lastRequestTime = new ConcurrentHashMap<>();
    private final long delayMs = 1000; // 1초 간격

    public void waitIfNeeded(String domain) throws InterruptedException {
        Long last = lastRequestTime.get(domain);
        if (last != null) {
            long elapsed = System.currentTimeMillis() - last;
            if (elapsed < delayMs) {
                Thread.sleep(delayMs - elapsed);
            }
        }
        lastRequestTime.put(domain, System.currentTimeMillis());
    }
}
```

### 2. Retry 로직

```java
@Retryable(maxAttempts = 3, backoff = @Backoff(delay = 2000))
public String fetchUrl(String url) {
    // Spring Retry 활용
}
```

### 3. URL 중복 제거

```java
private final Set<String> visitedUrls = ConcurrentHashMap.newKeySet();

public boolean shouldVisit(String url) {
    return visitedUrls.add(url);
}
```

### 4. User-Agent 관리

```java
@Component
public class UserAgentRotator {
    private final List<String> agents = List.of(
        "Mozilla/5.0 ...",
        "Mozilla/5.0 ..."
    );
    private final AtomicInteger index = new AtomicInteger(0);

    public String next() {
        return agents.get(index.getAndIncrement() % agents.size());
    }
}
```

## 배포

기존 Spring Batch 서버에 통합:
- 별도 인프라 불필요
- Playwright 브라우저만 서버에 추가 설치 필요 (`mvn exec:java -e -D exec.mainClass=com.microsoft.playwright.CLI -D exec.args="install chromium"`)
- 기존 배치 스케줄러로 크롤링 Job 실행

## 실행 방식

| 실행 주체 | 방식 |
|-----------|------|
| Spring 스케줄러 | `@Scheduled` 또는 Batch 스케줄러로 Job 실행 |
| Spring API | API 호출로 Job 수동 실행 |
| 수동 | Spring Batch CLI 또는 관리자 API |

## Spring Batch 파싱 흐름

크롤링 Job과 동일한 구조:
```
1. 스케줄러 실행 (또는 수동)
2. S3에서 미처리 파일 목록 조회
3. 원본 파일 읽기 (JSON/HTML)
4. source/data-type에 맞는 파서로 가공
5. DB 저장
6. 처리 완료 기록
```

## 데이터 소스 확장

외부 API 업체를 사용하게 될 경우:
- 새 Batch Job 추가 (API 호출 → S3 업로드)
- S3에 같은 경로 규칙으로 저장
- 파싱 Job은 새 파서만 추가

## 트레이드오프

### 장점
- 단일 스택 (Java/Spring) — 별도 언어, 배포 파이프라인 불필요
- 기존 Spring 인프라에 통합 — 추가 인프라 비용 없음
- 팀 전원이 유지보수 가능 (Spring 개발자)
- 익숙한 환경에서 디버깅
- Spring Retry, Scheduler 등 기존 도구 활용 가능

### 단점
- 크롤링 프레임워크가 없어 Rate Limiting, Retry, URL 중복 제거 등 직접 구현 필요
- Playwright Java가 scrapy-playwright보다 통합 경험이 부족
- 크롤링 대상이 많아지면 직접 구현한 코드의 관리 부담 증가
- 크롤링 작업이 Batch 서버 리소스에 영향을 줄 수 있음 (Playwright는 메모리를 많이 사용)