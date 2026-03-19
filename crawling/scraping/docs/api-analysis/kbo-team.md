# KBO 팀정보/팀기록 API 분석

## 웹 페이지 URL

```
https://m.sports.naver.com/kbaseball/record/kbo?tab=teamRank
https://m.sports.naver.com/kbaseball/record/kbo?seasonCode=2026&tab=teamRecord
```

---

## 탐지된 API 엔드포인트 목록

모두 `api-gw.sports.naver.com` 도메인에서 호출됨.

| No | 경로 | 유형 | 설명 |
|----|------|------|------|
| 1 | `/statistics/categories/kbo/seasons` | XHR | 시즌 목록 (2008~현재) |
| 2 | `/statistics/categories/kbo/seasons/{seasonCode}/teams` | XHR | **핵심** 팀 순위 및 팀 기록 통합 |
| 3 | `/statistics/categories/kbo/seasons/{seasonCode}/teams/last-ten-games` | XHR | 팀별 최근 10경기 결과 |
| 4 | `/one/myTeam` | XHR | 로그인 사용자 즐겨찾기 팀 (불필요) |
| 5 | `/one/notice` | XHR | 공지사항 (불필요) |
| 6 | `/cms/templates/record_banner` | XHR | 기록 페이지 배너 CMS (불필요) |

**핵심 발견:** `teamRank`와 `teamRecord` 탭 모두 동일한 `/statistics/categories/kbo/seasons/{seasonCode}/teams` API를 사용함.
탭 구분은 프론트엔드에서 처리되며, 응답 데이터에 타격/투구 통계가 모두 포함되어 있음.

---

## API 상세

### 1. `/statistics/categories/kbo/seasons` - 시즌 목록

**전체 URL:**
```
https://api-gw.sports.naver.com/statistics/categories/kbo/seasons
```

**쿼리 파라미터:** 없음

**응답 JSON 구조:**
```json
{
  "code": 200,
  "success": true,
  "result": {
    "seasons": [
      {
        "category": "kbo",
        "year": 2026,
        "seasonCode": "2026",
        "title": "2026",
        "startDate": "20260328",
        "endDate": "20260906",
        "logoUrl": null,
        "isSeason": "N",
        "isEnable": "Y",
        "currentGameType": "PRESEASON",
        "desc": null
      }
    ]
  }
}
```

**seasons 배열 주요 필드:**

| 필드 | 타입 | 설명 |
|------|------|------|
| `seasonCode` | string | 시즌 코드 (연도, 예: `"2026"`) |
| `year` | integer | 연도 |
| `startDate` | string | 시즌 시작일 (`YYYYMMDD` 형식) |
| `endDate` | string | 시즌 종료일 (`YYYYMMDD` 형식) |
| `currentGameType` | string | 현재 경기 유형 (`PRESEASON` / `REGULAR_SEASON` / `POST_SEASON`) |
| `isEnable` | string | 조회 가능 여부 (`"Y"` / `"N"`) |

**지원 시즌 범위:** 2008년 ~ 현재 (2026)

---

### 2. `/statistics/categories/kbo/seasons/{seasonCode}/teams` - 팀 순위 및 기록 (핵심)

**전체 URL:**
```
https://api-gw.sports.naver.com/statistics/categories/kbo/seasons/2026/teams
```

**경로 파라미터:**

| 파라미터 | 값 예시 | 설명 |
|----------|---------|------|
| `seasonCode` | `2026` | 시즌 코드 (연도) |

**쿼리 파라미터:** 없음

**응답 JSON 구조:**
```json
{
  "code": 200,
  "success": true,
  "result": {
    "seasonTeamStats": [
      {
        "teamId": "LT",
        "teamName": "롯데",
        "teamShortName": "롯데",
        "teamImageUrl": "https://sports-phinf.pstatic.net/team/kbo/default/LT.png?type=f92_88",
        "seasonId": "2026",
        "year": 2026,
        "upperCategoryId": "kbaseball",
        "categoryId": "kbo",
        "league": "",
        "division": null,
        "gameType": "PRESEASON",
        "ranking": 1,
        "wcRanking": null,
        "orderNo": 7,
        "wra": 1.0,
        "gameCount": 7,
        "winGameCount": 5,
        "drawnGameCount": 2,
        "loseGameCount": 0,
        "gameBehind": 0.0,
        "wcGameBehind": null,
        "continuousGameResult": "5승",
        "lastFiveGames": "-----",
        "offenseHra": 0.32203,
        "offenseRun": 48,
        "offenseRbi": 45,
        "offenseAb": 236,
        "offenseHr": 5,
        "offenseHit": 76,
        "offenseH2": 14,
        "offenseH3": 2,
        "offenseSb": 9,
        "offenseBb": null,
        "offenseHp": null,
        "offenseBbhp": 29,
        "offenseKk": 51,
        "offenseGd": 5,
        "offenseObp": 0.39179,
        "offenseSlg": 0.46186,
        "offenseOps": 0.85365,
        "defenseEra": 3.2459,
        "defenseR": 24,
        "defenseEr": 22,
        "defenseInning": 61.0,
        "defenseHit": 53,
        "defenseHr": 3,
        "defenseKk": 47,
        "defenseBb": null,
        "defenseHp": null,
        "defenseBbhp": 28,
        "defenseErr": 4,
        "defenseWhip": 1.27869,
        "defenseQs": 0,
        "defenseSave": 3,
        "defenseHold": 5,
        "defenseWp": 6,
        "hasMyTeam": "Y",
        "myTeamCategoryId": "kbo",
        "nextScheduleGameId": "-",
        "opposingTeamImageUrl": null,
        "opposingTeamName": null,
        "keyword": "롯데 자이언츠",
        "osId": "2484094",
        "pkId": 146
      }
    ],
    "postSeason": {
      "pcImageUrl": null,
      "mobileImageUrl": null,
      "teamColors": null
    },
    "gameType": "PRESEASON"
  }
}
```

**seasonTeamStats 배열 주요 필드:**

| 필드 | 타입 | 설명 |
|------|------|------|
| `teamId` | string | **팀 코드** (예: `LT`, `OB`, `HT`) |
| `teamName` | string | 팀 이름 (예: `롯데`, `두산`, `KIA`) |
| `teamShortName` | string | 팀 약칭 |
| `teamImageUrl` | string | 팀 엠블럼 이미지 URL |
| `seasonId` | string | 시즌 코드 |
| `gameType` | string | 경기 유형 (`PRESEASON` / `REGULAR_SEASON`) |
| `ranking` | integer | 순위 |
| `wra` | float | 승률 |
| `gameCount` | integer | 경기 수 |
| `winGameCount` | integer | 승 |
| `drawnGameCount` | integer | 무 |
| `loseGameCount` | integer | 패 |
| `gameBehind` | float | 게임 차 |
| `continuousGameResult` | string | 연속 성적 (예: `5승`, `1패`) |
| `lastFiveGames` | string | 최근 5경기 결과 (`-----`는 시범경기 시 미제공) |
| `offenseHra` | float | 팀 타율 |
| `offenseRun` | integer | 득점 |
| `offenseRbi` | integer | 타점 |
| `offenseHr` | integer | 홈런 |
| `offenseHit` | integer | 안타 |
| `offenseH2` | integer | 2루타 |
| `offenseH3` | integer | 3루타 |
| `offenseSb` | integer | 도루 |
| `offenseBbhp` | integer | 볼넷+사구 합산 |
| `offenseKk` | integer | 삼진 |
| `offenseObp` | float | 출루율 |
| `offenseSlg` | float | 장타율 |
| `offenseOps` | float | OPS |
| `defenseEra` | float | 팀 평균자책점 (ERA) |
| `defenseR` | integer | 실점 |
| `defenseEr` | integer | 자책점 |
| `defenseInning` | float | 투구 이닝 |
| `defenseHit` | integer | 피안타 |
| `defenseHr` | integer | 피홈런 |
| `defenseKk` | integer | 탈삼진 |
| `defenseBbhp` | integer | 볼넷+사구 허용 합산 |
| `defenseErr` | integer | 실책 |
| `defenseWhip` | float | WHIP |
| `defenseSave` | integer | 세이브 |
| `defenseHold` | integer | 홀드 |
| `defenseWp` | integer | 폭투 |
| `keyword` | string | 팀 풀네임 (예: `롯데 자이언츠`) |
| `osId` | string | 내부 팀 식별자 (OS ID) |

---

### 3. `/statistics/categories/kbo/seasons/{seasonCode}/teams/last-ten-games` - 최근 10경기

**전체 URL:**
```
https://api-gw.sports.naver.com/statistics/categories/kbo/seasons/2026/teams/last-ten-games
https://api-gw.sports.naver.com/statistics/categories/kbo/seasons/2026/teams/last-ten-games?sortField=lastTenGameResult
```

**쿼리 파라미터:**

| 파라미터 | 값 예시 | 설명 |
|----------|---------|------|
| `sortField` | `lastTenGameResult` | 정렬 기준 (optional) |

**응답 JSON 구조:**
```json
{
  "code": 200,
  "success": true,
  "result": {
    "seasonTeamLastTenGameStats": [],
    "gameType": "PRESEASON"
  }
}
```

**비고:** 시범경기 중에는 `seasonTeamLastTenGameStats`가 빈 배열로 반환됨. 정규시즌 중에는 팀별 최근 10경기 결과가 포함될 것으로 예상.

---

## 실제 팀 코드 목록

`/statistics/categories/kbo/seasons/2026/teams` 응답에서 확인된 전체 팀 코드:

| 팀명 (teamName) | 풀네임 (keyword) | 팀 코드 (teamId) | OS ID (osId) |
|-----------------|-----------------|-----------------|-------------|
| 롯데 | 롯데 자이언츠 | `LT` | 2484094 |
| 두산 | 두산 베어스 | `OB` | 2484102 |
| 삼성 | 삼성 라이온즈 | `SS` | 2484087 |
| LG | LG 트윈스 | `LG` | 2484009 |
| NC | NC 다이노스 | `NC` | 2483999 |
| 한화 | 한화 이글스 | `HH` | 2484093 |
| SSG | SSG 랜더스 | `SK` | 2484084 |
| KIA | 기아 타이거즈 | `HT` | 2484078 |
| 키움 | 키움 히어로즈 | `WO` | 2484088 |
| KT | KT 위즈 | `KT` | 2479938 |

**주의:** `teamId` 필드가 팀 코드로, `/schedule/games` API의 `homeTeamCode`/`awayTeamCode` 값과 동일함.
SSG 랜더스의 팀 코드는 과거 SK 와이번스 시절 코드인 `SK`를 계속 사용 중.
KIA 타이거즈의 팀 코드는 해태 타이거즈 시절 코드인 `HT`를 계속 사용 중.
두산 베어스의 팀 코드는 OB 베어스 시절 코드인 `OB`를 계속 사용 중.

---

## seasonCode 파라미터 동작 방식

- URL 경로의 `{seasonCode}` 부분에 연도(4자리 숫자 문자열)를 지정
- 예: `/statistics/categories/kbo/seasons/2026/teams`, `/statistics/categories/kbo/seasons/2025/teams`
- 지원 범위: 2008 ~ 현재 (2026)
- `/statistics/categories/kbo/seasons` API로 사용 가능한 시즌 목록 확인 가능

---

## 필수 헤더

직접 API 호출 시 별도 인증 헤더나 토큰 없이 응답이 정상 반환됨.

| 헤더 | 필수 여부 | 비고 |
|------|----------|------|
| `Referer` | 불필요 | 없어도 동작 |
| `Authorization` | 불필요 | 비인증 API |
| `Cookie` | 불필요 | 로그인 관련 데이터(`/one/myTeam`)는 제외 |

---

## 특이사항

- **탭 통합:** `teamRank`(팀 순위)와 `teamRecord`(팀 기록) 탭은 동일한 API 엔드포인트를 사용. 응답 데이터에 순위 정보(ranking, wra, gameBehind)와 타격/투구 기록이 모두 포함되어 있어 단일 호출로 두 탭의 데이터를 모두 수집 가능.
- **시즌 진행 상태:** `gameType` 필드로 현재 경기 유형 확인 가능 (`PRESEASON` → `REGULAR_SEASON` → `POST_SEASON`)
- **시범경기 중 `lastFiveGames`:** 시범경기 중에는 `"-----"` 값으로 반환됨
- **시범경기 중 `last-ten-games`:** 시범경기 중에는 빈 배열 반환, 정규시즌 개막 후 데이터 채워짐
- **팀 코드 역사성:** 일부 팀은 구단명 변경 이전의 코드를 현재도 사용 (SK→SSG, HT→KIA, OB→두산)
- **정렬 순서:** API 응답의 팀 순서는 순위 기준이며, 동순위 팀은 임의 순서
- **데이터 수집 핵심 API:** `/statistics/categories/kbo/seasons/{seasonCode}/teams` 단일 호출로 팀 순위와 팀 기록을 모두 수집 가능
