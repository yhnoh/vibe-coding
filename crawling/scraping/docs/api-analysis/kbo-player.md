# KBO 타자/투수 목록 API 분석

## 웹 페이지 URL

```
https://m.sports.naver.com/kbaseball/record/kbo?tab=hitter
https://m.sports.naver.com/kbaseball/record/kbo?tab=pitcher
https://m.sports.naver.com/kbaseball/record/kbo?tab=hitter&teamCode=HT
```

---

## 탐지된 API 엔드포인트 목록

모두 `api-gw.sports.naver.com` 도메인에서 호출됨.

| No | 경로 | 유형 | 설명 |
|----|------|------|------|
| 1 | `/statistics/categories/kbo/seasons/{seasonCode}/players` | XHR | **핵심** 선수 목록 (타자/투수 통합 엔드포인트) |
| 2 | `/statistics/categories/kbo/seasons/{seasonCode}/top-players` | XHR | 카테고리별 상위 선수 (랭킹 배너용) |
| 3 | `/statistics/categories/kbo/seasons` | XHR | 시즌 목록 |
| 4 | `/statistics/categories/kbo/seasons/{seasonCode}/teams` | XHR | 팀 목록 (팀 필터 드롭다운용) |
| 5 | `/one/myTeam` | XHR | 로그인 사용자 즐겨찾기 팀 (불필요) |
| 6 | `/one/notice` | XHR | 공지사항 (불필요) |

**핵심 발견:** 타자(`tab=hitter`)와 투수(`tab=pitcher`) 모두 동일한 `/statistics/categories/kbo/seasons/{seasonCode}/players` 엔드포인트를 사용하며, `playerType` 쿼리 파라미터로 구분함.

---

## API 상세

### 1. `/statistics/categories/kbo/seasons/{seasonCode}/players` - 선수 목록 (핵심)

#### 타자 목록

**전체 URL:**
```
https://api-gw.sports.naver.com/statistics/categories/kbo/seasons/2026/players?sortField=hitterHra&sortDirection=desc&playerType=HITTER
```

**쿼리 파라미터:**

| 파라미터 | 값 예시 | 필수 여부 | 설명 |
|----------|---------|----------|------|
| `playerType` | `HITTER` | 필수 | 선수 유형 (`HITTER` / `PITCHER`) |
| `sortField` | `hitterHra` | 선택 | 정렬 기준 필드 (기본값: `hitterHra`) |
| `sortDirection` | `desc` | 선택 | 정렬 방향 (`asc` / `desc`) |
| `teamCode` | `HT` | 선택 | 팀 코드로 필터 (생략 시 전체 팀) |
| `page` | `1` | 선택 | 페이지 번호 (기본값: `1`) |
| `pageSize` | `50` | 선택 | 페이지 크기 (기본값: `50`) |

#### 투수 목록

**전체 URL:**
```
https://api-gw.sports.naver.com/statistics/categories/kbo/seasons/2026/players?sortField=pitcherEra&sortDirection=asc&playerType=PITCHER
```

**쿼리 파라미터:**

| 파라미터 | 값 예시 | 설명 |
|----------|---------|------|
| `playerType` | `PITCHER` | 선수 유형 |
| `sortField` | `pitcherEra` | 정렬 기준 필드 |
| `sortDirection` | `asc` | ERA 정렬은 오름차순 |

#### 응답 JSON 구조

```json
{
  "code": 200,
  "success": true,
  "result": {
    "page": 1,
    "pageSize": 50,
    "gameType": "PRESEASON",
    "seasonPlayerStats": [
      {
        "ranking": 1,
        "playerId": "65653",
        "playerName": "김호령",
        "playerImageUrl": "https://sports-phinf.pstatic.net/player/kbo/default/65653.png",
        "weight": 85,
        "height": 178,
        "backNumber": 27,
        "isRetire": "N",
        "isPlayer": "Y",
        "osId": "2441854",
        "profile": "{...}",
        "enable": "Y",
        "teamId": "HT",
        "teamName": "KIA",
        "teamShortName": "KIA",
        "teamImageUrl": "https://sports-phinf.pstatic.net/team/kbo/default/HT.png?type=f92_88",
        "seasonId": "2026",
        "year": 2026,
        "upperCategoryId": "kbaseball",
        "categoryId": "kbo",
        "league": null,
        "division": null,
        "hitterHra": 0.4736842105263158,
        "hitterRbi": 3,
        "hitterRun": 3,
        "hitterHr": 0,
        "hitterHit": 9,
        "hitterH2": 4,
        "hitterH3": 0,
        "hitterGameCount": 7,
        "hitterAb": 19,
        "hitterSb": 0,
        "hitterCs": null,
        "hitterBb": 2,
        "hitterHp": 0,
        "hitterKk": 4,
        "hitterGd": null,
        "hitterObp": 0.524,
        "hitterSlg": 0.684,
        "hitterOps": 1.208,
        "hitterIsop": 0.21,
        "hitterBabip": 0.6,
        "hitterWoba": 0.519,
        "hitterWrcPlus": 0.0,
        "hitterWpa": 0.361,
        "hitterWar": null,
        "isQualified": true,
        "isKoreanPlayer": false
      }
    ]
  }
}
```

#### 타자 주요 통계 필드

| 필드 | 타입 | 설명 |
|------|------|------|
| `ranking` | integer | 순위 |
| `playerId` | string | 선수 고유 ID |
| `playerName` | string | 선수 이름 |
| `playerImageUrl` | string | 선수 이미지 URL |
| `teamId` | string | 팀 코드 (예: `HT`, `LG`) |
| `teamName` | string | 팀 이름 |
| `isQualified` | boolean | 규정 타석 충족 여부 |
| `hitterHra` | float | 타율 |
| `hitterRbi` | integer | 타점 |
| `hitterRun` | integer | 득점 |
| `hitterHr` | integer | 홈런 |
| `hitterHit` | integer | 안타 |
| `hitterH2` | integer | 2루타 |
| `hitterH3` | integer | 3루타 |
| `hitterGameCount` | integer | 출장 경기 수 |
| `hitterAb` | integer | 타수 |
| `hitterSb` | integer | 도루 |
| `hitterBb` | integer | 볼넷 |
| `hitterHp` | integer | 사구 |
| `hitterKk` | integer | 삼진 |
| `hitterObp` | float | 출루율 |
| `hitterSlg` | float | 장타율 |
| `hitterOps` | float | OPS |
| `hitterIsop` | float | ISO (순장타율) |
| `hitterBabip` | float | BABIP |
| `hitterWoba` | float | wOBA |
| `hitterWrcPlus` | float | wRC+ |
| `hitterWpa` | float | WPA |
| `hitterWar` | float \| null | WAR (시범경기 중 null) |

#### 투수 주요 통계 필드

| 필드 | 타입 | 설명 |
|------|------|------|
| `pitcherEra` | float | 평균자책점 (ERA) |
| `pitcherWin` | integer | 승 |
| `pitcherLose` | integer | 패 |
| `pitcherSave` | integer | 세이브 |
| `pitcherHold` | integer | 홀드 |
| `pitcherGameCount` | integer | 등판 경기 수 |
| `pitcherInning` | string | 투구 이닝 (예: `"7 1/3"`) |
| `pitcherKk` | integer | 탈삼진 |
| `pitcherHit` | integer | 피안타 |
| `pitcherHr` | integer | 피홈런 |
| `pitcherR` | integer | 실점 |
| `pitcherEr` | integer | 자책점 |
| `pitcherBb` | integer | 볼넷 허용 |
| `pitcherHp` | integer | 사구 허용 |
| `pitcherWra` | float | 승률 |
| `pitcherQs` | integer | 퀄리티스타트 |
| `pitcherWhip` | float | WHIP |
| `pitcherInningKk` | float | 9이닝당 탈삼진 (K/9) |
| `pitcherInningBb` | float | 9이닝당 볼넷 (BB/9) |
| `pitcherKkBbRate` | float | K/BB 비율 |
| `pitcherPaKkRate` | float | 삼진률 (%) |
| `pitcherPaBbRate` | float | 볼넷률 (%) |
| `pitcherWpa` | float | WPA |
| `pitcherWar` | float \| null | WAR (시범경기 중 null) |
| `pitcherStart` | integer \| null | 선발 등판 수 (시범경기 중 null) |
| `pitcherPitchCount` | integer \| null | 투구 수 (시범경기 중 null) |

---

### 2. `/statistics/categories/kbo/seasons/{seasonCode}/top-players` - 상위 선수 (랭킹 배너)

**전체 URL:**
```
https://api-gw.sports.naver.com/statistics/categories/kbo/seasons/2026/top-players?limit=30&rankFlag=Y&playerType=HITTER
https://api-gw.sports.naver.com/statistics/categories/kbo/seasons/2026/top-players?limit=30&rankFlag=Y&playerType=PITCHER
```

**쿼리 파라미터:**

| 파라미터 | 값 예시 | 설명 |
|----------|---------|------|
| `playerType` | `HITTER` / `PITCHER` | 선수 유형 |
| `limit` | `30` | 각 카테고리별 상위 N명 |
| `rankFlag` | `Y` | 랭킹 필터 여부 |

**응답 JSON 구조:**
```json
{
  "code": 200,
  "success": true,
  "result": {
    "gameType": "PRESEASON",
    "topPlayers": [
      {
        "type": "hitterHra",
        "rankings": [
          {
            "ranking": 1,
            "playerId": "65653",
            "playerName": "김호령",
            ...
          }
        ]
      }
    ]
  }
}
```

**비고:** 시범경기 중에는 `topPlayers` 배열이 6개 항목만 반환됨 (타율, 홈런, 타점, ERA, 탈삼진, 세이브 등 주요 카테고리). 단순 배너 표시용 API로, 전체 선수 목록 수집에는 부적합.

---

## 페이지네이션 분석

### 파라미터

| 파라미터 | 기본값 | 설명 |
|----------|--------|------|
| `page` | `1` | 페이지 번호 |
| `pageSize` | `50` | 페이지당 선수 수 |

### 동작 방식

- `page`와 `pageSize` 쿼리 파라미터로 페이지네이션 제어
- 응답 JSON의 `result.page`와 `result.pageSize` 필드로 현재 페이지 상태 확인 가능
- **응답에 총 선수 수(`total`) 필드가 없음** - 마지막 페이지 여부 판단이 어려움
- `pageSize`를 크게 설정하면 한 번에 전체 선수를 조회할 수 있음

### 실제 선수 수 (2026 시범경기 기준)

| 구분 | 전체 선수 수 |
|------|------------|
| 타자 (HITTER) | 227명 |
| 투수 (PITCHER) | 199명 |

### 권장 수집 전략

**옵션 1 - 단일 요청 (권장):**
```
pageSize=500
```
한 번에 전체 선수를 가져옴. 정규시즌에도 팀당 30~40명 × 10팀 = 최대 300~400명 수준으로 예상.

**옵션 2 - 페이지 순환 (안전):**
반환된 `seasonPlayerStats` 길이가 `pageSize`보다 작아질 때까지 `page` 증가.

---

## teamCode 파라미터 동작 방식

- `teamCode` 파라미터를 추가하면 해당 팀 선수만 필터링됨
- 생략 시 전체 팀 대상
- 동일한 `/players` 엔드포인트를 사용하며 `teamCode` 유무만 다름

**전체 목록 vs 팀별 목록 비교:**

| 구분 | URL 예시 | 반환 수 (2026 시범경기) |
|------|----------|----------------------|
| 전체 타자 | `...?playerType=HITTER&pageSize=500` | 227명 |
| 팀별 타자 (HT) | `...?playerType=HITTER&teamCode=HT&pageSize=50` | 21명 |

**팀 코드는 Task 3에서 확인된 코드와 동일:**
`LT`, `OB`, `SS`, `LG`, `NC`, `HH`, `SK`, `HT`, `WO`, `KT`

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

- **단일 엔드포인트 통합:** 타자/투수가 동일한 `/players` 엔드포인트를 사용하며, `playerType=HITTER` 또는 `playerType=PITCHER`로 구분. 단, 응답 통계 필드는 `hitter*` 또는 `pitcher*` 접두사로 구분됨
- **총 건수 미제공:** API 응답에 `total` 또는 `totalCount` 필드가 없음. 전체 수집을 위해서는 `pageSize`를 크게 설정(예: 500)하거나 반환 레코드 수가 `pageSize`보다 적어질 때까지 순환 필요
- **`pitcherInning` 필드 형식:** 이닝 수가 정수가 아닌 문자열로 반환됨 (예: `"7 1/3"`, `"10 2/3"`). 파싱 시 주의 필요
- **시범경기 중 null 필드:** `hitterWar`, `hitterCs`, `pitcherWar`, `pitcherStart`, `pitcherPitchCount` 등 일부 필드가 시범경기 중 `null`로 반환됨. 정규시즌에는 채워질 것으로 예상
- **`isQualified` 필드:** 규정 타석/이닝 충족 여부. 기록 랭킹 집계 시 활용
- **`profile` 필드:** 선수 상세 프로필 정보가 JSON 문자열로 내포되어 있음 (이중 직렬화). 필요 시 추가 파싱 필요
- **`gameType`:** `PRESEASON`(시범경기), `REGULAR_SEASON`(정규시즌) 등 현재 경기 유형 표시
- **정렬:** 타자 기본 정렬은 `hitterHra`(타율) 내림차순, 투수 기본 정렬은 `pitcherEra`(ERA) 오름차순
