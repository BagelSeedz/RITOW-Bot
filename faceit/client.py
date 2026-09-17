import aiohttp


class FaceitClient:
    BASE_URL = "https://open.faceit.com/data/v4"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session: aiohttp.ClientSession | None = None

    async def start(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Accept": "application/json",
                }
            )

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()

    async def get_team(self, team_id: str):
        async with self.session.get(
            f"{self.BASE_URL}/teams/{team_id}"
        ) as response:
            response.raise_for_status()
            return await response.json()

    async def get_match(self, match_id: str):
        async with self.session.get(
            f"{self.BASE_URL}/matches/{match_id}"
        ) as response:
            response.raise_for_status()
            return await response.json()

    async def get_match_stats(self, match_id: str):
        async with self.session.get(
            f"{self.BASE_URL}/matches/{match_id}/stats"
        ) as response:
            response.raise_for_status()
            return await response.json()
    
    async def search_player(self, nickname: str):
        async with self.session.get(
            f"{self.BASE_URL}/search/players",
            params={"nickname": nickname}
        ) as response:
            response.raise_for_status()
            return await response.json()

