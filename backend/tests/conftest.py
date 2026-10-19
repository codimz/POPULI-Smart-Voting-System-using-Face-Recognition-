# T30 / Fixture: Mock Redis for API tests (fail-open)
import pytest
from unittest.mock import AsyncMock


@pytest.fixture(autouse=True)
def mock_redis_for_tests(monkeypatch):
    # Rate limit & attempt counter should fail-open when Redis unavailable
    import app.dependencies.rate_limit as rl
    async def fake_get_redis():
        m = AsyncMock()
        m.get = AsyncMock(return_value=None)
        m.set = AsyncMock(return_value=True)
        return m
    monkeypatch.setattr(rl, "get_redis", fake_get_redis)
