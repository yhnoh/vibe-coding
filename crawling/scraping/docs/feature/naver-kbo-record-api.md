# 네이버 스포츠 KBO 기록 API 분석

> 분석 대상: `https://m.sports.naver.com/kbaseball/record/kbo?seasonCode=2026&tab=hitter&teamCode=OB`
> 분석 일시: 2026-03-20

## 개요

네이버 스포츠 KBO 기록/순위 페이지는 내부적으로 `api-gw.sports.naver.com` API를 호출하여 데이터를 렌더링한다.
모든 API가 **인증 없이 직접 HTTP GET 호출 가능**하므로, Playwright 없이 `scrapy.Request`만으로 데이터 수집이 가능하다.

---

## 발견된 API 엔드포인트 (4개)

| # | 엔드포인트 | 용도 |
|---|-----------|------|
| 1 | `/statistics/categories/kbo/seasons` | 시즌 목록 |
| 2 | `/statistics/categories/kbo/seasons/{year}/players` | 팀별 선수 기록 (타자/투수) |
| 3 | `/statistics/categories/kbo/seasons/{year}/top-players` | 부문별 리그 Top 랭킹 |
| 4 | `/statistics/categories/kbo/seasons/{year}/teams` | 팀 순위 및 공격/수비 기록 |

Base URL: `https://api-gw.sports.naver.com`

---

## 1. 시즌 목록 API

```
GET /statistics/categories/kbo/seasons
```

조회 가능한 KBO 시즌 목록을 반환한다 (2008~2026).

### 응답 구조

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
        "isSeason": "N",
        "isEnable": "Y",
        "currentGameType": "PRESEASON"
      }
    ]
  }
}
```

### 필드 설명

| 필드 | 의미 |
|------|------|
| `seasonCode` | 시즌 코드 (연도) |
| `startDate` / `endDate` | 시즌 시작/종료일 (yyyyMMdd) |
| `isSeason` | 현재 시즌 여부 |
| `isEnable` | 데이터 조회 가능 여부 |
| `currentGameType` | 현재 경기 유형 (`PRESEASON`, `REGULAR_SEASON`) |

---

## 2. 팀별 선수 기록 API

```
GET /statistics/categories/kbo/seasons/{year}/players
    ?teamCode=OB
    &sortField=hitterHra
    &sortDirection=desc
    &playerType=HITTER
```

특정 팀의 선수별 시즌 기록을 반환한다.

### 파라미터

| 파라미터 | 필수 | 설명 | 예시 |
|----------|------|------|------|
| `teamCode` | O | 팀 코드 | `OB` |
| `playerType` | O | 선수 유형 | `HITTER`, `PITCHER` |
| `sortField` | O | 정렬 기준 필드명 | `hitterHra` |
| `sortDirection` | O | 정렬 방향 | `asc`, `desc` |

### 응답 구조

```json
{
  "code": 200,
  "success": true,
  "result": {
    "page": 1,
    "pageSize": 50,
    "seasonPlayerStats": [...],
    "gameType": "PRESEASON"
  }
}
```

### 타자(HITTER) 기록 필드

| 필드 | 의미 | 비고 |
|------|------|------|
| `hitterHra` | 타율 (AVG) | 안타/타수 |
| `hitterGameCount` | 출장 경기수 (G) | |
| `hitterAb` | 타수 (AB) | |
| `hitterHit` | 안타 (H) | |
| `hitterH2` | 2루타 (2B) | |
| `hitterH3` | 3루타 (3B) | |
| `hitterHr` | 홈런 (HR) | |
| `hitterRbi` | 타점 (RBI) | |
| `hitterRun` | 득점 (R) | |
| `hitterSb` | 도루 (SB) | |
| `hitterCs` | 도루실패 (CS) | nullable |
| `hitterBb` | 볼넷 (BB) | |
| `hitterHp` | 사구 (HBP) | |
| `hitterKk` | 삼진 (SO) | |
| `hitterGd` | 병살타 (GDP) | nullable |
| `hitterObp` | 출루율 (OBP) | |
| `hitterSlg` | 장타율 (SLG) | |
| `hitterOps` | OPS | OBP + SLG |
| `hitterIsop` | IsoP | 순수장타력 (SLG - AVG) |
| `hitterBabip` | BABIP | 인플레이 타율 |
| `hitterWoba` | wOBA | 가중 출루율 |
| `hitterWrcPlus` | wRC+ | 조정된 득점 창출력 |
| `hitterWpa` | WPA | 승리 기여도 |
| `hitterWar` | WAR | 대체선수 대비 승리 기여 (nullable) |
| `isQualified` | 규정 타석 충족 여부 | boolean |

### 선수 프로필 필드

| 필드 | 의미 |
|------|------|
| `playerId` | 선수 고유 ID |
| `playerName` | 선수명 |
| `playerImageUrl` | 선수 사진 URL |
| `teamId` / `teamName` | 팀 코드 / 팀명 |
| `backNumber` | 등번호 |
| `height` / `weight` | 키(cm) / 몸무게(kg) |
| `profile` | JSON 문자열 (포지션, 풀네임 등 포함) |

---

## 3. 리그 순위별 선수 랭킹 API

```
GET /statistics/categories/kbo/seasons/{year}/top-players
    ?limit=30
    &rankFlag=Y
    &playerType=HITTER
```

주요 부문별 리그 Top 랭킹을 반환한다.

### 파라미터

| 파라미터 | 필수 | 설명 | 예시 |
|----------|------|------|------|
| `limit` | O | 순위 제한 | `30` |
| `rankFlag` | O | 랭킹 플래그 | `Y` |
| `playerType` | O | 선수 유형 | `HITTER`, `PITCHER` |

### 응답 구조

```json
{
  "code": 200,
  "success": true,
  "result": {
    "topPlayers": [
      {
        "type": "hitterHra",
        "rankings": [...]
      }
    ],
    "gameType": "PRESEASON"
  }
}
```

### 타자 랭킹 부문 (6개)

| type | 부문 |
|------|------|
| `hitterHra` | 타율 |
| `hitterHr` | 홈런 |
| `hitterRbi` | 타점 |
| `hitterHit` | 안타 |
| `hitterSb` | 도루 |
| `hitterRun` | 득점 |

`playerType=PITCHER`로 변경하면 투수 랭킹을 조회할 수 있다.

---

## 4. 팀 순위/기록 API

```
GET /statistics/categories/kbo/seasons/{year}/teams
```

전 구단 팀 순위 및 공격/수비 통합 기록을 반환한다.

### 응답 구조

```json
{
  "code": 200,
  "success": true,
  "result": {
    "seasonTeamStats": [...],
    "postSeason": null,
    "gameType": "PRESEASON"
  }
}
```

### 순위 필드

| 필드 | 의미 |
|------|------|
| `ranking` | 순위 |
| `wra` | 승률 |
| `gameCount` | 경기수 |
| `winGameCount` | 승 |
| `loseGameCount` | 패 |
| `drawnGameCount` | 무 |
| `gameBehind` | 게임차 |
| `continuousGameResult` | 연속 결과 (예: "5승") |

### 팀 공격 기록 필드

| 필드 | 의미 |
|------|------|
| `offenseHra` | 팀 타율 |
| `offenseRun` | 득점 |
| `offenseRbi` | 타점 |
| `offenseAb` | 타수 |
| `offenseHr` | 홈런 |
| `offenseHit` | 안타 |
| `offenseH2` | 2루타 |
| `offenseH3` | 3루타 |
| `offenseSb` | 도루 |
| `offenseBbhp` | 볼넷+사구 |
| `offenseKk` | 삼진 |
| `offenseGd` | 병살 |
| `offenseObp` | 출루율 |
| `offenseSlg` | 장타율 |
| `offenseOps` | OPS |

### 팀 수비 기록 필드

| 필드 | 의미 |
|------|------|
| `defenseEra` | 팀 평균자책점 (ERA) |
| `defenseR` | 실점 |
| `defenseEr` | 자책점 |
| `defenseInning` | 이닝 |
| `defenseHit` | 피안타 |
| `defenseHr` | 피홈런 |
| `defenseKk` | 탈삼진 |
| `defenseBbhp` | 볼넷+사구 허용 |
| `defenseErr` | 실책 |
| `defenseWhip` | WHIP |
| `defenseQs` | QS (퀄리티 스타트) |
| `defenseSave` | 세이브 |
| `defenseHold` | 홀드 |
| `defenseWp` | 폭투 |

---

## 팀 코드 매핑

| 코드 | 팀명 |
|------|------|
| `OB` | 두산 베어스 |
| `HT` | KIA 타이거즈 |
| `SS` | 삼성 라이온즈 |
| `LG` | LG 트윈스 |
| `NC` | NC 다이노스 |
| `KT` | KT 위즈 |
| `LT` | 롯데 자이언츠 |
| `SK` | SSG 랜더스 |
| `HH` | 한화 이글스 |
| `WO` | 키움 히어로즈 |

---

## 크롤링 활용 시 참고

- 모든 API는 인증 없이 직접 HTTP GET으로 호출 가능
- Playwright 없이 `scrapy.Request`만으로 데이터 수집 가능
- 응답 형식은 JSON
- `playerType` 파라미터로 타자(`HITTER`)/투수(`PITCHER`) 전환
- 시즌 데이터는 2008년부터 제공