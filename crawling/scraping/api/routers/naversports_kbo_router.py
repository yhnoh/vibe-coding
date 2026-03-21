from fastapi import APIRouter, Query

from api.routers.naversports_kbo_client import (
    fetch_schedule_games,
    fetch_schedule_games_record,
    fetch_seasons_teams,
    fetch_seasons_players_hitter,
    fetch_seasons_players_pitcher,
)
from api.routers.naversports_kbo_schemas import (
    NaverApiResponse,
    ScheduleGamesResult,
    ScheduleGamesRecordResult,
    SeasonsTeamsResult,
    SeasonsPlayersHitterResult,
    SeasonsPlayersPitcherResult,
)

router = APIRouter(prefix="/kbo", tags=["KBO"])


@router.get("/schedule/games", response_model=NaverApiResponse[ScheduleGamesResult])
async def get_schedule_games(
    from_date: str = Query(..., description="조회 시작일 (예: 2026-03-21)"),
    to_date: str = Query(..., description="조회 종료일 (예: 2026-03-21)"),
) -> dict:
    """경기일정 조회"""
    return await fetch_schedule_games(from_date, to_date)


@router.get("/schedule/games/{game_id}/record", response_model=NaverApiResponse[ScheduleGamesRecordResult])
async def get_schedule_games_record(game_id: str) -> dict:
    """경기 기록 조회 (타자/투수 박스스코어)"""
    return await fetch_schedule_games_record(game_id)


@router.get("/seasons/{season}/teams", response_model=NaverApiResponse[SeasonsTeamsResult])
async def get_seasons_teams(season: str) -> dict:
    """팀 순위/기록 조회"""
    return await fetch_seasons_teams(season)


@router.get("/seasons/{season}/players/hitter", response_model=NaverApiResponse[SeasonsPlayersHitterResult])
async def get_seasons_players_hitter(
    season: str,
    team_code: str = Query(..., description="팀 코드 (예: OB)"),
) -> dict:
    """타자 선수 기록 조회"""
    return await fetch_seasons_players_hitter(season, team_code)


@router.get("/seasons/{season}/players/pitcher", response_model=NaverApiResponse[SeasonsPlayersPitcherResult])
async def get_seasons_players_pitcher(
    season: str,
    team_code: str = Query(..., description="팀 코드 (예: OB)"),
) -> dict:
    """투수 선수 기록 조회"""
    return await fetch_seasons_players_pitcher(season, team_code)
