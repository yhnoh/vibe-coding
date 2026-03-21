# 네이버 스포츠 KBO API 명세

## 기본 정보

- **Base URL**: `https://api-gw.sports.naver.com`
- **인증**: 불필요 (비인증 API)
- **응답 형식**: JSON
- **웹 페이지**: `https://m.sports.naver.com/kbaseball`

---

## 1. 경기일정 - `/schedule/games`

특정 기간의 KBO 경기 목록을 조회한다.

**URL**
```
GET /schedule/games?fields=basic,schedule,baseball,manualRelayUrl&upperCategoryId=kbaseball&categoryId=kbo&fromDate={fromDate}&toDate={toDate}&roundCodes=&size=500
```

**웹 페이지**
```
https://m.sports.naver.com/kbaseball/schedule/index?category=kbo&date=2026-03-21
```

**쿼리 파라미터**

| 파라미터 | 필수 | 설명 | 예시 |
|----------|------|------|------|
| `fields` | Y | 응답 필드 그룹 | `basic,schedule,baseball,manualRelayUrl` |
| `upperCategoryId` | Y | 상위 카테고리 (고정) | `kbaseball` |
| `categoryId` | Y | 카테고리 (고정) | `kbo` |
| `fromDate` | Y | 조회 시작일 | `2026-03-21` |
| `toDate` | Y | 조회 종료일 | `2026-03-21` |
| `roundCodes` | N | 라운드 필터 | (빈 문자열) |
| `size` | N | 최대 결과 수 | `500` |

**응답 주요 필드** (`result.games[]`)

| 필드 | 타입 | 설명 |
|------|------|------|
| `gameId` | string | 경기 고유 ID (예: `20260321HHLT02026`) |
| `gameDate` | string | 경기 날짜 (`YYYY-MM-DD`) |
| `gameDateTime` | string | 경기 일시 (ISO 8601) |
| `stadium` | string | 경기장 |
| `homeTeamCode` | string | 홈팀 코드 |
| `homeTeamName` | string | 홈팀 이름 |
| `homeTeamScore` | integer | 홈팀 점수 |
| `awayTeamCode` | string | 원정팀 코드 |
| `awayTeamName` | string | 원정팀 이름 |
| `awayTeamScore` | integer | 원정팀 점수 |
| `winner` | string | 승자 (`HOME` / `AWAY` / `DRAW`) |
| `statusCode` | string | 경기 상태 (`BEFORE` / `LIVE` / `RESULT` / `CANCEL`) |
| `homeStarterName` | string | 홈팀 선발투수 |
| `awayStarterName` | string | 원정팀 선발투수 |
| `winPitcherName` | string | 승리투수 |
| `losePitcherName` | string | 패전투수 |
| `roundCode` | string | 라운드 (`kbo_e`: 시범경기) |

---

## 2. 경기 기록 - `/schedule/games/{gameId}/record`

특정 경기의 타자/투수 박스스코어를 조회한다.

**URL**
```
GET /schedule/games/{gameId}/record
```

**웹 페이지**
```
https://m.sports.naver.com/game/{gameId}/record
```

**경로 파라미터**

| 파라미터 | 필수 | 설명 | 예시 |
|----------|------|------|------|
| `gameId` | Y | 경기 ID | `20260319HTHH02026` |

**응답 주요 필드** (`result.recordData`)

| 필드 | 타입 | 설명 |
|------|------|------|
| `battersBoxscore.away[]` | array | 원정팀 타자 박스스코어 |
| `battersBoxscore.home[]` | array | 홈팀 타자 박스스코어 |
| `pitchersBoxscore.away[]` | array | 원정팀 투수 박스스코어 |
| `pitchersBoxscore.home[]` | array | 홈팀 투수 박스스코어 |
| `scoreBoard` | object | 이닝별 스코어보드 |
| `etcRecords[]` | array | 기타 기록 (홈런, 도루, 결승타 등) |
| `pitchingResult[]` | array | 승/패/세 투수 정보 |
| `gameInfo` | object | 경기 기본 정보 |

**타자 박스스코어 필드** (`battersBoxscore.away/home[]`)

| 필드 | 타입 | 설명 |
|------|------|------|
| `playerCode` | string | 선수 ID |
| `name` | string | 선수명 |
| `pos` | string | 포지션 (유, 중, 우, 좌, 1, 2, 3, 포, 지) |
| `batOrder` | integer | 타순 |
| `ab` | integer | 타수 |
| `hit` | integer | 안타 |
| `rbi` | integer | 타점 |
| `run` | integer | 득점 |
| `hr` | integer | 홈런 |
| `bb` | integer | 볼넷 |
| `kk` | integer | 삼진 |
| `sb` | integer | 도루 |
| `hra` | string | 타율 |
| `inn1`~`inn25` | string | 이닝별 결과 |

**투수 박스스코어 필드** (`pitchersBoxscore.away/home[]`)

| 필드 | 타입 | 설명 |
|------|------|------|
| `pcode` | string | 선수 ID |
| `name` | string | 선수명 |
| `inn` | string | 투구 이닝 (예: `"7 1/3"`) |
| `hit` | integer | 피안타 |
| `r` | integer | 실점 |
| `er` | integer | 자책점 |
| `bb` | integer | 볼넷 |
| `kk` | integer | 탈삼진 |
| `hr` | integer | 피홈런 |
| `era` | string | 평균자책점 |
| `w` | integer | 해당 경기 승 |
| `l` | integer | 해당 경기 패 |
| `s` | integer | 해당 경기 세이브 |
| `wls` | string | 승패세 표시 (`W`/`L`/`S`/빈값) |

---

## 3. 팀 순위/기록 - `/statistics/categories/kbo/seasons/{seasonCode}/teams`

시즌별 팀 순위 및 공격/수비 기록을 조회한다.

**URL**
```
GET /statistics/categories/kbo/seasons/{seasonCode}/teams
```

**웹 페이지**
```
https://m.sports.naver.com/kbaseball/record/kbo?seasonCode=2026&tab=teamRank
https://m.sports.naver.com/kbaseball/record/kbo?seasonCode=2026&tab=teamRecord
```

**경로 파라미터**

| 파라미터 | 필수 | 설명 | 예시 |
|----------|------|------|------|
| `seasonCode` | Y | 시즌 코드 (연도) | `2026` |

**응답 주요 필드** (`result.seasonTeamStats[]`)

| 필드 | 타입 | 설명 |
|------|------|------|
| `teamId` | string | 팀 코드 |
| `teamName` | string | 팀 이름 |
| `ranking` | integer | 순위 |
| `wra` | float | 승률 |
| `gameCount` | integer | 경기 수 |
| `winGameCount` | integer | 승 |
| `drawnGameCount` | integer | 무 |
| `loseGameCount` | integer | 패 |
| `gameBehind` | float | 게임 차 |
| `offenseHra` | float | 팀 타율 |
| `offenseRun` | integer | 득점 |
| `offenseHr` | integer | 홈런 |
| `offenseOps` | float | OPS |
| `defenseEra` | float | 팀 ERA |
| `defenseKk` | integer | 탈삼진 |
| `defenseWhip` | float | WHIP |

---

## 4. 타자 선수 기록 - `/statistics/categories/kbo/seasons/{seasonCode}/players`

시즌별 타자 선수 기록을 조회한다.

**URL**
```
GET /statistics/categories/kbo/seasons/{seasonCode}/players?sortField=hitterHra&sortDirection=desc&playerType=HITTER&pageSize=500&teamCode={teamCode}
```

**웹 페이지**
```
https://m.sports.naver.com/kbaseball/record/kbo?seasonCode=2026&tab=hitter&teamCode=OB
```

**파라미터**

| 파라미터 | 위치 | 필수 | 설명 | 예시 |
|----------|------|------|------|------|
| `seasonCode` | path | Y | 시즌 코드 | `2026` |
| `playerType` | query | Y | 선수 유형 (고정) | `HITTER` |
| `teamCode` | query | Y | 팀 코드 | `OB` |
| `sortField` | query | N | 정렬 기준 | `hitterHra` |
| `sortDirection` | query | N | 정렬 방향 | `desc` |
| `pageSize` | query | N | 페이지 크기 | `500` |

**응답 주요 필드** (`result.seasonPlayerStats[]`)

| 필드 | 타입 | 설명 |
|------|------|------|
| `playerId` | string | 선수 ID |
| `playerName` | string | 선수명 |
| `teamId` | string | 팀 코드 |
| `teamName` | string | 팀 이름 |
| `ranking` | integer | 순위 |
| `hitterHra` | float | 타율 |
| `hitterRbi` | integer | 타점 |
| `hitterRun` | integer | 득점 |
| `hitterHr` | integer | 홈런 |
| `hitterHit` | integer | 안타 |
| `hitterAb` | integer | 타수 |
| `hitterBb` | integer | 볼넷 |
| `hitterKk` | integer | 삼진 |
| `hitterObp` | float | 출루율 |
| `hitterSlg` | float | 장타율 |
| `hitterOps` | float | OPS |

---

## 5. 투수 선수 기록 - `/statistics/categories/kbo/seasons/{seasonCode}/players`

시즌별 투수 선수 기록을 조회한다. 타자와 동일한 엔드포인트를 사용하며 `playerType`으로 구분한다.

**URL**
```
GET /statistics/categories/kbo/seasons/{seasonCode}/players?sortField=pitcherEra&sortDirection=asc&playerType=PITCHER&pageSize=500&teamCode={teamCode}
```

**웹 페이지**
```
https://m.sports.naver.com/kbaseball/record/kbo?seasonCode=2026&tab=pitcher&teamCode=OB
```

**파라미터**

| 파라미터 | 위치 | 필수 | 설명 | 예시 |
|----------|------|------|------|------|
| `seasonCode` | path | Y | 시즌 코드 | `2026` |
| `playerType` | query | Y | 선수 유형 (고정) | `PITCHER` |
| `teamCode` | query | Y | 팀 코드 | `OB` |
| `sortField` | query | N | 정렬 기준 | `pitcherEra` |
| `sortDirection` | query | N | 정렬 방향 | `asc` |
| `pageSize` | query | N | 페이지 크기 | `500` |

**응답 주요 필드** (`result.seasonPlayerStats[]`)

| 필드 | 타입 | 설명 |
|------|------|------|
| `playerId` | string | 선수 ID |
| `playerName` | string | 선수명 |
| `teamId` | string | 팀 코드 |
| `teamName` | string | 팀 이름 |
| `ranking` | integer | 순위 |
| `pitcherEra` | float | 평균자책점 (ERA) |
| `pitcherWin` | integer | 승 |
| `pitcherLose` | integer | 패 |
| `pitcherSave` | integer | 세이브 |
| `pitcherHold` | integer | 홀드 |
| `pitcherInning` | string | 투구 이닝 (예: `"7 1/3"`) |
| `pitcherKk` | integer | 탈삼진 |
| `pitcherWhip` | float | WHIP |

---

## 팀 코드 목록

| 팀명 | 코드 | 비고 |
|------|------|------|
| LG 트윈스 | `LG` | |
| 한화 이글스 | `HH` | |
| SSG 랜더스 | `SK` | 구 SK 와이번스 코드 |
| 삼성 라이온즈 | `SS` | |
| NC 다이노스 | `NC` | |
| KT 위즈 | `KT` | |
| 롯데 자이언츠 | `LT` | |
| KIA 타이거즈 | `HT` | 구 해태 타이거즈 코드 |
| 두산 베어스 | `OB` | 구 OB 베어스 코드 |
| 키움 히어로즈 | `WO` | |

---

## gameId 형식

```
YYYYMMDD{원정팀코드}{홈팀코드}0{연도}
```

예: `20260321HHLT02026` → 2026-03-21, 한화(원정) vs 롯데(홈)