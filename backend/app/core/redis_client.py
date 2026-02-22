from typing import AsyncGenerator

import redis.asyncio as aioredis

from app.core.config import settings

redis_client: aioredis.Redis | None = None


async def init_redis() -> None:
    global redis_client
    redis_client = aioredis.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True,
    )


async def close_redis() -> None:
    global redis_client
    if redis_client:
        await redis_client.close()
        redis_client = None


async def get_redis() -> AsyncGenerator[aioredis.Redis, None]:
    if redis_client is None:
        raise RuntimeError("Redis not initialized. Call init_redis() first.")
    yield redis_client
