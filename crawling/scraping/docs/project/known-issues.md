# 알려진 이슈 및 제약사항

## 비공식 API 의존성

네이버 스포츠 API(`api-gw.sports.naver.com`)는 비공식 API이다.

| 리스크 | 영향 | 대응 방안 |
|--------|------|----------|
| API 엔드포인트 변경 | 모든 Spider + FastAPI 동작 불가 | 응답 스키마 검증으로 변경 감지 |
| API 인증 추가 | 직접 호출 불가 | Playwright Spider로 전환 |
| IP 차단 | 서버에서 요청 불가 | Decodo 프록시 도입 |
| Rate Limit 추가 | 대량 요청 실패 | 요청 간격 조절, 재시도 전략 |

현재 확인된 상태 (2026-03-21):
- 인증 불필요
- Rate Limit 헤더 없음
- User-Agent/Referer 제한 없음
- 연속 10회 요청 성공

## 라인업 데이터

- 라인업 전용 API가 없음
- Playwright로 HTML DOM을 파싱해야 함
- DOM 구조 변경 시 파싱 로직 수정 필요
- 서버에 chromium 설치 필요 (Dockerfile에 포함)
- 대안: `/schedule/games/{gameId}/record` API의 `battersBoxscore`에서 선발/교체 구분 가능

## Scrapy + FastAPI URL 중복

- 네이버 API URL과 params 조합 로직이 Scrapy Spider와 FastAPI client에 각각 존재
- `scrapying/` 디렉토리에서 실행하는 Scrapy와 프로젝트 루트에서 실행하는 FastAPI의 import 경로가 달라 공통 모듈화 어려움
- 현재는 중복을 허용하고 있음

## 데이터 저장소 부재

- 현재 LoggingPipeline만 있어서 데이터가 로그로만 출력됨
- S3, DB 등 실제 저장소 미구현
- FastAPI는 매 요청마다 네이버 API를 호출 (캐싱 없음)

## 투수 이닝 필드 형식

- `pitcherInning` 필드가 문자열로 반환됨 (예: `"7 1/3"`, `"10 2/3"`)
- 숫자 연산이 필요하면 별도 파싱 로직 필요

## 시범경기 중 null 필드

- `hitterWar`, `pitcherWar`, `pitcherStart`, `pitcherPitchCount` 등이 시범경기 중 null
- 정규시즌에는 채워질 것으로 예상
