import httpx

API_DOMAIN = "https://api-gw.sports.naver.com"


async def fetch_schedule_games(from_date: str, to_date: str) -> dict:
    """경기일정 조회"""
    params = {
        "fields": "basic,schedule,baseball,manualRelayUrl",
        "upperCategoryId": "kbaseball",
        "categoryId": "kbo",
        "fromDate": from_date,
        "toDate": to_date,
        "roundCodes": "",
        "size": "500",
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_DOMAIN}/schedule/games", params=params)
        response.raise_for_status()
        return response.json()


async def fetch_schedule_games_record(game_id: str) -> dict:
    """경기 기록 조회 (타자/투수 박스스코어)"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_DOMAIN}/schedule/games/{game_id}/record")
        response.raise_for_status()
        return response.json()


async def fetch_seasons_teams(season: str) -> dict:
    """팀 순위/기록 조회"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_DOMAIN}/statistics/categories/kbo/seasons/{season}/teams")
        response.raise_for_status()
        return response.json()


async def fetch_seasons_players_hitter(season: str, team_code: str) -> dict:
    """타자 선수 기록 조회"""
    params = {
        "sortField": "hitterHra",
        "sortDirection": "desc",
        "playerType": "HITTER",
        "pageSize": "500",
        "teamCode": team_code,
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_DOMAIN}/statistics/categories/kbo/seasons/{season}/players",
            params=params,
        )
        response.raise_for_status()
        return response.json()


async def fetch_seasons_players_pitcher(season: str, team_code: str) -> dict:
    """투수 선수 기록 조회"""
    params = {
        "sortField": "pitcherEra",
        "sortDirection": "asc",
        "playerType": "PITCHER",
        "pageSize": "500",
        "teamCode": team_code,
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_DOMAIN}/statistics/categories/kbo/seasons/{season}/players",
            params=params,
        )
        response.raise_for_status()
        return response.json()
