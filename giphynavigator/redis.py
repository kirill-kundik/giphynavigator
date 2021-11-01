"""Redis client module."""

import aioredis


def init_redis(host: str, password: str) -> aioredis.Redis:
    return aioredis.from_url(
        f"redis://{host}",
        password=password,
        encoding="utf-8",
        decode_responses=True
    )
