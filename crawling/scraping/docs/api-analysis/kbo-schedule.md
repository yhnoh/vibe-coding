# KBO 경기일정 API 분석

## 웹 페이지 URL

```
https://m.sports.naver.com/kbaseball/schedule/index?category=kbo&date=2026-03-12
```

---

## 탐지된 API 엔드포인트 목록

모두 `api-gw.sports.naver.com` 도메인에서 호출됨.

| No | 경로 | 유형 | 설명 |
|----|------|------|------|
| 1 | `/schedule/games` | XHR | **핵심** 월별 경기 목록 조회 |
| 2 | `/schedule/calendar` | XHR | **핵심** 월별 캘린더 (날짜별 경기 유무) |
| 3 | `/schedule/season` | XHR | 시즌 정보 및 팀 목록 |
| 4 | `/one/myTeam` | XHR | 로그인 사용자 즐겨찾기 팀 |
| 5 | `/one/notice` | XHR | 공지사항 |
| 6 | `/cms/templates/kbaseball_schedule_league_tab` | XHR | 리그 탭 CMS 설정 |
| 7 | `/cms/templates/kbaseball_schedule_post_season_image` | XHR | 포스트시즌 이미지 CMS 설정 |

---

## API 상세

### 1. `/schedule/games` - 경기 목록 (핵심)

**전체 URL:**
```
https://api-gw.sports.naver.com/schedule/games?fields=basic%2Cschedule%2Cbaseball%2CmanualRelayUrl&upperCategoryId=kbaseball&categoryId=kbo&fromDate=2026-03-01&toDate=2026-03-31&roundCodes=&size=500
```

**쿼리 파라미터:**

| 파라미터 | 값 예시 | 설명 |
|----------|---------|------|
| `fields` | `basic,schedule,baseball,manualRelayUrl` | 응답에 포함할 필드 그룹 (콤마 구분) |
| `upperCategoryId` | `kbaseball` | 상위 카테고리 (고정값) |
| `categoryId` | `kbo` | 하위 카테고리 (고정값) |
| `fromDate` | `2026-03-01` | 조회 시작일 (해당 월의 1일) |
| `toDate` | `2026-03-31` | 조회 종료일 (해당 월의 말일) |
| `roundCodes` | `` | 라운드 필터 (빈 문자열 = 전체) |
| `size` | `500` | 최대 결과 수 |

**응답 JSON 구조:**
```json
{
  "code": 200,
  "success": true,
  "result": {
    "gameTotalCount": 75,
    "games": [
      {
        "gameId": "20260312KTLT02026",
        "superCategoryId": "baseball",
        "categoryId": "kbo",
        "categoryName": "KBO리그",
        "gameDate": "2026-03-12",
        "gameDateTime": "2026-03-12T13:00:00",
        "timeTbd": false,
        "stadium": "사직",
        "title": null,
        "homeTeamCode": "LT",
        "homeTeamName": "롯데",
        "homeTeamScore": 4,
        "awayTeamCode": "KT",
        "awayTeamName": "KT",
        "awayTeamScore": 3,
        "winner": "HOME",
        "statusCode": "RESULT",
        "statusNum": 4,
        "statusInfo": "9회초",
        "cancel": false,
        "suspended": false,
        "hasVideo": true,
        "roundCode": "kbo_e",
        "manualRelayUrl": null,
        "reversedHomeAway": true,
        "homeTeamEmblemUrl": "https://sports-phinf.pstatic.net/team/kbo/default/LT.png",
        "awayTeamEmblemUrl": "https://sports-phinf.pstatic.net/team/kbo/default/KT.png",
        "gameOnAir": false,
        "widgetEnable": false,
        "specialMatchInfo": null,
        "seriesOutcome": null,
        "homeStarterName": "김진욱",
        "awayStarterName": "주권",
        "winPitcherName": "홍민기",
        "losePitcherName": "김민수",
        "homeCurrentPitcherName": "윤성빈",
        "awayCurrentPitcherName": "손동현",
        "seriesGameNo": 0,
        "broadChannel": "",
        "roundName": null,
        "roundGameNo": 0
      }
    ]
  }
}
```

**games 배열 주요 필드 설명:**

| 필드 | 타입 | 설명 |
|------|------|------|
| `gameId` | string | 경기 고유 ID (형식: `YYYYMMDD{원정팀코드}{홈팀코드}0{년도}`) |
| `gameDate` | string | 경기 날짜 (`YYYY-MM-DD`) |
| `gameDateTime` | string | 경기 일시 (ISO 8601) |
| `stadium` | string | 경기장 이름 |
| `homeTeamCode` | string | 홈팀 코드 |
| `homeTeamName` | string | 홈팀 이름 |
| `homeTeamScore` | integer | 홈팀 점수 |
| `awayTeamCode` | string | 원정팀 코드 |
| `awayTeamName` | string | 원정팀 이름 |
| `awayTeamScore` | integer | 원정팀 점수 |
| `winner` | string | 승자 (`HOME` / `AWAY` / `DRAW`) |
| `statusCode` | string | 경기 상태 (`BEFORE` / `LIVE` / `RESULT` / `CANCEL`) |
| `statusInfo` | string | 현재 이닝 정보 (예: `9회초`) |
| `cancel` | boolean | 경기 취소 여부 |
| `suspended` | boolean | 경기 중단 여부 |
| `homeStarterName` | string | 홈팀 선발투수 |
| `awayStarterName` | string | 원정팀 선발투수 |
| `winPitcherName` | string | 승리투수 |
| `losePitcherName` | string | 패전투수 |
| `roundCode` | string | 라운드 코드 (예: `kbo_e` = 시범경기) |
| `reversedHomeAway` | boolean | 홈/원정 표기가 반전된 경우 |

---

### 2. `/schedule/calendar` - 월별 캘린더

**전체 URL:**
```
https://api-gw.sports.naver.com/schedule/calendar?upperCategoryId=kbaseball&categoryIds=kbo&date=2026-03-12
```

**쿼리 파라미터:**

| 파라미터 | 값 예시 | 설명 |
|----------|---------|------|
| `upperCategoryId` | `kbaseball` | 상위 카테고리 (고정값) |
| `categoryIds` | `kbo` | 카테고리 ID (복수 지정 가능, 콤마 구분) |
| `date` | `2026-03-12` | 조회 기준 날짜 (해당 월 전체 반환) |

**응답 JSON 구조:**
```json
{
  "code": 200,
  "success": true,
  "result": {
    "month": 3,
    "today": "2026-03-19",
    "selectedDate": "2026-03-12",
    "dayOfPrevMonth": "2025-10-31",
    "dayOfNextMonth": "2026-04-01",
    "beforeDate": null,
    "afterDate": null,
    "scheduleRecentDate": "2026-03-19",
    "years": [2008, 2009, "..."],
    "dates": [
      {
        "ymd": "2026-03-12",
        "dayOfWeek": "목",
        "contentsCount": 1,
        "gameCount": 5,
        "gameIds": ["20260312KTLT02026", "..."],
        "gameInfos": [
          {
            "gameId": "20260312KTLT02026",
            "homeTeamCode": "LT",
            "awayTeamCode": "KT",
            "statusCode": "RESULT",
            "winner": "HOME"
          }
        ],
        "isKoreaGameExisted": false
      }
    ]
  }
}
```

**dates 배열 주요 필드:**

| 필드 | 타입 | 설명 |
|------|------|------|
| `ymd` | string | 날짜 (`YYYY-MM-DD`) |
| `dayOfWeek` | string | 요일 (한국어: 월/화/수/목/금/토/일) |
| `gameCount` | integer | 해당 날짜 경기 수 |
| `gameIds` | array | 경기 ID 목록 |
| `gameInfos` | array \| null | 경기 요약 정보 (gameCount=0이면 null) |

---

### 3. `/schedule/season` - 시즌 정보

**전체 URL:**
```
https://api-gw.sports.naver.com/schedule/season?categoryId=kbo&date=2026-03-12&hasTeams=true&tournament=false
```

**쿼리 파라미터:**

| 파라미터 | 값 예시 | 설명 |
|----------|---------|------|
| `categoryId` | `kbo` | 카테고리 ID |
| `date` | `2026-03-12` | 기준 날짜 |
| `hasTeams` | `true` | 팀 목록 포함 여부 |
| `tournament` | `false` | 토너먼트 방식 여부 |

**응답 JSON 구조 (주요 필드):**
```json
{
  "code": 200,
  "success": true,
  "result": {
    "seasonYear": 2026,
    "season": "2026",
    "categoryId": "kbo",
    "startDate": "2026-03-12",
    "endDate": "2026-09-06",
    "teams": [
      {"teamName": "LG", "teamCode": "LG", "teamShortName": "LG", "rank": 1},
      {"teamName": "한화", "teamCode": "HH", "teamShortName": "한화", "rank": 2}
    ],
    "months": [
      {"yearMonth": "2026-03", "gameCount": 15},
      {"yearMonth": "2026-04", "gameCount": 26}
    ],
    "postSeasons": [
      {"phaseCode": "kbo_ps_wd", "gameCount": 0},
      {"phaseCode": "kbo_ps_sp", "gameCount": 0},
      {"phaseCode": "kbo_ps_po", "gameCount": 0},
      {"phaseCode": "kbo_ps_ks", "gameCount": 0}
    ]
  }
}
```

---

## 필수 헤더

직접 API 호출 시 별도 인증 헤더나 토큰 없이 응답이 정상 반환됨.
브라우저에서는 `Referer: https://m.sports.naver.com/kbaseball/schedule/index?category=kbo&date=...` 헤더가 자동으로 전송되나,
Scrapy로 직접 호출 시에도 Referer 없이 200 응답을 받음.

| 헤더 | 필수 여부 | 비고 |
|------|----------|------|
| `Referer` | 불필요 | 브라우저에서는 자동 전송, 없어도 동작 |
| `Authorization` | 불필요 | 비인증 API |
| `Cookie` | 불필요 | 로그인 관련 데이터(`/one/myTeam`)는 제외 |

---

## 페이지네이션 방식

`/schedule/games` API는 페이지네이션 없음. `size=500` 파라미터로 단일 요청에 전체 월 경기를 가져옴.
월별 최대 경기 수는 약 130경기 (26일 x 5경기) 이하이므로 size=500으로 충분함.

---

## URL 파라미터 (동적 파라미터)

크롤링 시 변경이 필요한 파라미터:

| API | 파라미터 | 변경 방법 |
|-----|----------|-----------|
| `/schedule/games` | `fromDate`, `toDate` | 수집 대상 월에 맞게 변경 (예: `2026-04-01` ~ `2026-04-30`) |
| `/schedule/calendar` | `date` | 수집 대상 월의 임의 날짜 지정 |
| `/schedule/season` | `date` | 수집 대상 월의 임의 날짜 지정 |

---

## 팀 코드 목록

시즌 API 응답에서 확인된 팀 코드:

| 팀명 | 코드 |
|------|------|
| LG 트윈스 | `LG` |
| 한화 이글스 | `HH` |
| SSG 랜더스 | `SK` |
| 삼성 라이온즈 | `SS` |
| NC 다이노스 | `NC` |
| KT 위즈 | `KT` |
| 롯데 자이언츠 | `LT` |
| KIA 타이거즈 | `HT` |
| 두산 베어스 | `OB` |
| 키움 히어로즈 | `WO` |

---

## 특이사항

- **gameId 형식**: `YYYYMMDD{원정팀코드}{홈팀코드}0{년도}` (예: `20260312KTLT02026`)
  - 원정팀 코드가 앞에 오고 홈팀 코드가 뒤에 오는 구조
  - `reversedHomeAway: true`인 경우 gameId의 팀 코드 순서가 실제 홈/원정과 반전될 수 있음
- **statusCode 값**: `BEFORE`(경기 전), `LIVE`(진행 중), `RESULT`(종료), `CANCEL`(취소)
- **roundCode**: 시범경기는 `kbo_e`, 정규시즌은 `kbo_regular` 예상
- `/one/myTeam`과 `/one/notice`는 로그인/서비스 UI용 API로 경기 데이터 수집에 불필요
- `/cms/templates/*` API는 UI CMS 설정 데이터로 경기 데이터 수집에 불필요
- `nam.veta.naver.com` 도메인 API는 광고 관련으로 경기 데이터 수집에 불필요
- 데이터 수집에 필요한 핵심 API는 `/schedule/games`와 `/schedule/calendar` 두 가지
