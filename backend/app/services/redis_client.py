from typing import Optional
import redis.asyncio as redis
from app.core.config import settings

_redis_client: Optional[redis.Redis] = None


async def get_redis() -> Optional[redis.Redis]:
    global _redis_client
    if _redis_client is None:
        try:
            _redis_client = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                max_connections=20,
            )
            # Test connection
            await _redis_client.ping()
        except Exception:
            _redis_client = None
    return _redis_client


async def close_redis() -> None:
    global _redis_client
    if _redis_client:
        await _redis_client.close()
        _redis_client = None