from pydantic import BaseModel, Field


# === 공통 ===

class NaverApiResponse[T](BaseModel):
    """네이버 스포츠 API 공통 응답 구조"""
    code: int
    success: bool
    result: T


# === 1. 경기일정 (/schedule/games) ===

class Game(BaseModel):
    gameId: str = Field(description="경기 고유 ID (예: 20260321HHLT02026)")
    gameDate: str = Field(description="경기 날짜 (YYYY-MM-DD)")
    gameDateTime: str = Field(description="경기 일시 (ISO 8601)")
    stadium: str = Field(description="경기장")
    homeTeamCode: str = Field(description="홈팀 코드")
    homeTeamName: str = Field(description="홈팀 이름")
    homeTeamScore: int | None = Field(default=None, description="홈팀 점수")
    awayTeamCode: str = Field(description="원정팀 코드")
    awayTeamName: str = Field(description="원정팀 이름")
    awayTeamScore: int | None = Field(default=None, description="원정팀 점수")
    winner: str | None = Field(default=None, description="승자 (HOME/AWAY/DRAW)")
    statusCode: str = Field(description="경기 상태 (BEFORE/LIVE/RESULT/CANCEL)")
    statusInfo: str | None = Field(default=None, description="현재 이닝 정보")
    cancel: bool = Field(description="경기 취소 여부")
    suspended: bool = Field(description="경기 중단 여부")
    homeStarterName: str | None = Field(default=None, description="홈팀 선발투수")
    awayStarterName: str | None = Field(default=None, description="원정팀 선발투수")
    winPitcherName: str | None = Field(default=None, description="승리투수")
    losePitcherName: str | None = Field(default=None, description="패전투수")
    roundCode: str | None = Field(default=None, description="라운드 (kbo_e: 시범경기)")
    broadChannel: str | None = Field(default=None, description="중계 채널")

    model_config = {"extra": "allow"}


class ScheduleGamesResult(BaseModel):
    games: list[Game]
    gameTotalCount: int = Field(description="경기 총 수")


# === 2. 경기 기록 (/schedule/games/{gameId}/record) ===

class BatterBoxscore(BaseModel):
    playerCode: str = Field(description="선수 ID")
    name: str = Field(description="선수명")
    pos: str = Field(description="포지션")
    batOrder: int = Field(description="타순")
    ab: int = Field(description="타수")
    hit: int = Field(description="안타")
    rbi: int = Field(description="타점")
    run: int = Field(description="득점")
    hr: int = Field(description="홈런")
    bb: int = Field(description="볼넷")
    kk: int = Field(description="삼진")
    sb: int = Field(description="도루")
    hra: str = Field(description="타율")

    model_config = {"extra": "allow"}


class PitcherBoxscore(BaseModel):
    pcode: str = Field(description="선수 ID")
    name: str = Field(description="선수명")
    inn: str = Field(description="투구 이닝")
    hit: int = Field(description="피안타")
    r: int = Field(description="실점")
    er: int = Field(description="자책점")
    bb: int = Field(description="볼넷")
    kk: int = Field(description="탈삼진")
    hr: int = Field(description="피홈런")
    era: str = Field(description="평균자책점")
    w: int = Field(description="승")
    l: int = Field(description="패")
    s: int = Field(description="세이브")
    wls: str = Field(description="승패세 표시")

    model_config = {"extra": "allow"}


class TeamBoxscore(BaseModel):
    away: list[BatterBoxscore | PitcherBoxscore]
    home: list[BatterBoxscore | PitcherBoxscore]

    model_config = {"extra": "allow"}


class BattersBoxscore(BaseModel):
    away: list[BatterBoxscore]
    home: list[BatterBoxscore]


class PitchersBoxscore(BaseModel):
    away: list[PitcherBoxscore]
    home: list[PitcherBoxscore]


class EtcRecord(BaseModel):
    how: str = Field(description="기록 유형 (홈런, 도루, 결승타 등)")
    result: str = Field(description="기록 내용")


class PitchingResult(BaseModel):
    pCode: str = Field(description="선수 ID")
    name: str = Field(description="선수명")
    w: int = Field(description="승")
    l: int = Field(description="패")
    s: int = Field(description="세이브")
    wls: str = Field(description="승패세 표시 (W/L/S)")


class GameRecordData(BaseModel):
    battersBoxscore: BattersBoxscore = Field(description="타자 박스스코어")
    pitchersBoxscore: PitchersBoxscore = Field(description="투수 박스스코어")
    etcRecords: list[EtcRecord] = Field(description="기타 기록")
    pitchingResult: list[PitchingResult] = Field(description="승/패/세 투수 정보")

    model_config = {"extra": "allow"}


class ScheduleGamesRecordResult(BaseModel):
    recordData: GameRecordData


# === 3. 팀 순위/기록 (/statistics/.../teams) ===

class SeasonTeamStats(BaseModel):
    teamId: str = Field(description="팀 코드")
    teamName: str = Field(description="팀 이름")
    teamImageUrl: str | None = Field(default=None, description="팀 엠블럼 이미지")
    ranking: int = Field(description="순위")
    wra: float = Field(description="승률")
    gameCount: int = Field(description="경기 수")
    winGameCount: int = Field(description="승")
    drawnGameCount: int = Field(description="무")
    loseGameCount: int = Field(description="패")
    gameBehind: float = Field(description="게임 차")
    continuousGameResult: str | None = Field(default=None, description="연속 성적")
    offenseHra: float = Field(description="팀 타율")
    offenseRun: int = Field(description="득점")
    offenseHr: int = Field(description="홈런")
    offenseOps: float = Field(description="OPS")
    defenseEra: float = Field(description="팀 ERA")
    defenseKk: int = Field(description="탈삼진")
    defenseWhip: float = Field(description="WHIP")

    model_config = {"extra": "allow"}


class SeasonsTeamsResult(BaseModel):
    seasonTeamStats: list[SeasonTeamStats]
    gameType: str = Field(description="경기 유형 (PRESEASON/REGULAR_SEASON)")

    model_config = {"extra": "allow"}


# === 4. 타자 선수 기록 ===

class HitterStats(BaseModel):
    playerId: str = Field(description="선수 ID")
    playerName: str = Field(description="선수명")
    playerImageUrl: str | None = Field(default=None, description="선수 이미지")
    teamId: str = Field(description="팀 코드")
    teamName: str = Field(description="팀 이름")
    ranking: int | None = Field(default=None, description="순위")
    hitterHra: float = Field(description="타율")
    hitterRbi: int = Field(description="타점")
    hitterRun: int = Field(description="득점")
    hitterHr: int = Field(description="홈런")
    hitterHit: int = Field(description="안타")
    hitterAb: int = Field(description="타수")
    hitterGameCount: int = Field(description="출장 경기 수")
    hitterBb: int = Field(description="볼넷")
    hitterKk: int = Field(description="삼진")
    hitterObp: float = Field(description="출루율")
    hitterSlg: float = Field(description="장타율")
    hitterOps: float = Field(description="OPS")
    isQualified: bool = Field(description="규정 타석 충족 여부")

    model_config = {"extra": "allow"}


class SeasonsPlayersHitterResult(BaseModel):
    page: int
    pageSize: int
    seasonPlayerStats: list[HitterStats]
    gameType: str


# === 5. 투수 선수 기록 ===

class PitcherStats(BaseModel):
    playerId: str = Field(description="선수 ID")
    playerName: str = Field(description="선수명")
    playerImageUrl: str | None = Field(default=None, description="선수 이미지")
    teamId: str = Field(description="팀 코드")
    teamName: str = Field(description="팀 이름")
    ranking: int | None = Field(default=None, description="순위")
    pitcherEra: float = Field(description="평균자책점 (ERA)")
    pitcherWin: int = Field(description="승")
    pitcherLose: int = Field(description="패")
    pitcherSave: int = Field(description="세이브")
    pitcherHold: int = Field(description="홀드")
    pitcherGameCount: int = Field(description="등판 경기 수")
    pitcherInning: str = Field(description="투구 이닝")
    pitcherKk: int = Field(description="탈삼진")
    pitcherWhip: float = Field(description="WHIP")
    isQualified: bool = Field(description="규정 이닝 충족 여부")

    model_config = {"extra": "allow"}


class SeasonsPlayersPitcherResult(BaseModel):
    page: int
    pageSize: int
    seasonPlayerStats: list[PitcherStats]
    gameType: str
