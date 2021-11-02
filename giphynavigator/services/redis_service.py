"""Redis service module."""

import json
from typing import Union, Optional

from aioredis import Redis


class RedisService:
    def __init__(self, redis: Redis) -> None:
        self._redis = redis

    async def set(self, key: str, value: Optional[Union[str, dict, list]]) -> None:
        await self._redis.set(key, json.dumps(value))

    async def get(self, key: str) -> Optional[Union[str, dict, list]]:
        value = await self._redis.get(key)

        try:
            value = json.loads(value)
        except (TypeError, json.JSONDecodeError):
            pass

        return value
