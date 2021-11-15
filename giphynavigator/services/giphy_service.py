"""Giphy client module."""

from aiohttp import ClientSession, ClientTimeout, ClientResponseError


class GiphyServiceException(Exception):
    pass


class GiphyService:
    API_URL = "https://api.giphy.com/v1"

    def __init__(self, api_key: str, timeout: float):
        self._api_key = api_key
        self._timeout = ClientTimeout(timeout)

    async def trending(self, limit, offset) -> dict:
        params = {"limit": limit, "offset": offset}

        return await self._fetch(f"{self.API_URL}/gifs/trending", params)

    async def gif(self, id_: str) -> dict:
        try:
            return await self._fetch(f"{self.API_URL}/gifs/{id_}", {})

        except ClientResponseError as e:
            raise GiphyServiceException(f"cannot load gif: {e.message}") from e

    async def search(self, query: str, limit: int = 50, offset: int = 0) -> dict:
        """Make search API call and return result."""
        url = f"{self.API_URL}/gifs/search"
        params = {
            "q": query,
            "limit": limit,
            "offset": offset,
        }
        return await self._fetch(url, params)

    async def _fetch(self, url: str, params: dict) -> dict:
        params["api_key"] = self._api_key
        async with ClientSession(timeout=self._timeout) as session:
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    response.raise_for_status()
                return await response.json()
