"""Search service module."""

import asyncio
import logging
from typing import Optional, List

from giphynavigator.models import Gif, SearchObject
from giphynavigator.services.giphy_service import GiphyService, GiphyServiceException
from giphynavigator.services.redis_service import RedisService


class SearchService:
    def __init__(self, giphy_client: GiphyService, redis_service: RedisService):
        self._giphy_client = giphy_client
        self._redis_service = redis_service

    @staticmethod
    def _parse_gif(gif_object: dict) -> Gif:
        gif = {
            "id": gif_object["id"],
            "url": gif_object["url"],
            "embed_url": gif_object["embed_url"],
        }
        if "user" in gif_object:
            gif["author_username"] = gif_object["user"]["username"]
            gif["author_profile"] = gif_object["user"]["profile_url"]
            gif["author_avatar"] = gif_object["user"]["avatar_url"]
        return Gif(**gif)

    async def _load(self, query: str, offset: int) -> List[str]:
        results = await self._giphy_client.search(query, offset=offset)

        ids = []

        for original_gif in results["data"]:
            gif = self._parse_gif(original_gif)
            ids.append(gif.id)

            await self._redis_service.set(f"gif_{gif.id}", gif.dict())

        previous_results = await self._redis_service.get(f"search_{query}")

        if previous_results:
            ids_to_write = previous_results + ids
        else:
            ids_to_write = ids

        await self._redis_service.set(f"search_{query}", ids_to_write)

        return ids

    async def gif(self, id_: str) -> Optional[Gif]:
        gif = await self._redis_service.get(f"gif_{id_}")

        if gif:
            return Gif(**gif)

        try:
            result = await self._giphy_client.gif(id_)

        except GiphyServiceException as e:
            logging.error(repr(e))
            return None

        gif = self._parse_gif(result["data"])

        await self._redis_service.set(f"gif_{gif.id}", gif.dict())

        return gif

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
