"""Redis client module."""

import aioredis


def init_redis(host: str) -> aioredis.Redis:
    return aioredis.from_url(
        f"redis://{host}",
        encoding="utf-8",
        decode_responses=True
    )
