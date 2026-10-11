from typing import Optional
from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.services.redis_client import get_redis


class RateLimiter:
    def __init__(self, max_requests: int, window_seconds: int, prefix: str = "ratelimit"):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.prefix = prefix

    async def __call__(
        self,
        request: Request,
        db: AsyncSession = Depends(get_db),
    ) -> None:
        redis = await get_redis()
        if not redis:
            # If Redis unavailable, skip rate limiting (fail open for development)
            return

        # Get identifier from request (IP or user)
        if hasattr(request.state, "nim") and request.state.nim:
            identifier = f"user:{request.state.nim}"
        else:
            client_host = request.client.host if request.client else "unknown"
            identifier = f"ip:{client_host}"

        key = f"{self.prefix}:{identifier}"

        current = await redis.get(key)
        if current is None:
            await redis.setex(key, self.window_seconds, 1)
            return

        current_count = int(current)
        if current_count >= self.max_requests:
            ttl = await redis.ttl(key)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Try again in {ttl} seconds.",
                headers={"Retry-After": str(ttl)},
            )

        await redis.incr(key)


# Pre-configured rate limiters
rate_limit_login = RateLimiter(
    max_requests=settings.RATE_LIMIT_LOGIN,
    window_seconds=settings.RATE_LIMIT_LOGIN_WINDOW,
    prefix="ratelimit:login",
)

rate_limit_biometric = RateLimiter(
    max_requests=settings.RATE_LIMIT_BIOMETRIC,
    window_seconds=settings.RATE_LIMIT_BIOMETRIC_WINDOW,
    prefix="ratelimit:biometric",
)

rate_limit_voting = RateLimiter(
    max_requests=settings.RATE_LIMIT_VOTING,
    window_seconds=settings.RATE_LIMIT_VOTING_WINDOW,
    prefix="ratelimit:voting",
)


async def check_biometric_attempts(nim: str) -> int:
    """Check remaining biometric attempts for a student."""
    redis = await get_redis()
    if not redis:
        return settings.MAX_BIOMETRIC_ATTEMPTS

    key = f"biometric:attempts:{nim}"
    current = await redis.get(key)
    if current is None:
        return settings.MAX_BIOMETRIC_ATTEMPTS
    return max(0, settings.MAX_BIOMETRIC_ATTEMPTS - int(current))


async def increment_biometric_attempts(nim: str) -> int:
    """Increment biometric attempts and return remaining."""
    redis = await get_redis()
    if not redis:
        return settings.MAX_BIOMETRIC_ATTEMPTS - 1

    key = f"biometric:attempts:{nim}"
    current = await redis.incr(key)
    if current == 1:
        # Set expiry to 24 hours
        await redis.expire(key, 86400)
    return max(0, settings.MAX_BIOMETRIC_ATTEMPTS - current)


async def reset_biometric_attempts(nim: str) -> None:
    """Reset biometric attempts for a student."""
    redis = await get_redis()
    if redis:
        await redis.delete(f"biometric:attempts:{nim}")