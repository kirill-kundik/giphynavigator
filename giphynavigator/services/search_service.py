"""Search service module."""

import asyncio
from typing import Optional, List

from giphynavigator.models import Gif, SearchObject
from giphynavigator.services.giphy_service import GiphyService
from giphynavigator.services.redis_service import RedisService


class SearchService:

    def __init__(self, giphy_client: GiphyService, redis_service: RedisService):
        self._giphy_client = giphy_client
        self._redis_service = redis_service

    async def gif(self, id_: str) -> Optional[Gif]:
        gif = await self._redis_service.get(f"gif_{id_}")

        if gif:
            return Gif(**gif)
        return None

    async def search(self, query: str, limit: int = 25, offset: int = 0) -> SearchObject:
        """Search for gifs and return formatted data."""
        if not query:
            return SearchObject()

        results = await self._redis_service.get(f"search_{query}")

        if not results:
            results = await self._load(query, offset)

        if 2 * limit + offset > len(results):
            asyncio.create_task(self._load(query, len(results)))

        return SearchObject(
            gifs=[
                await self.gif(gif_id)
                for gif_id in results[offset:limit + offset]
            ]
        )

    async def _load(self, query: str, offset: int) -> List[str]:
        results = await self._giphy_client.search(query, offset=offset)

        ids = []

        for original_gif in results["data"]:
            gif_id = original_gif["id"]
            gif = {
                "id": original_gif["id"],
                "url": original_gif["url"],
                "embed_url": original_gif["embed_url"],
            }
            if "user" in original_gif:
                gif["author_username"] = original_gif["user"]["username"]
                gif["author_profile"] = original_gif["user"]["profile_url"]
                gif["author_avatar"] = original_gif["user"]["avatar_url"]

            ids.append(gif_id)

            await self._redis_service.set(f"gif_{gif_id}", gif)

        previous_results = await self._redis_service.get(f"search_{query}")

        if previous_results:
            ids_to_write = previous_results + ids
        else:
            ids_to_write = ids

        await self._redis_service.set(f"search_{query}", ids_to_write)

        return ids
