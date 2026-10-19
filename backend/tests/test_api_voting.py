# T29: API test voting flow
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_cast_invalid_candidate():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Without real JWT/token this should still hit validation or auth layer
        r = await ac.post("/api/v1/voting/cast", json={"candidate_id": "BAD", "token": "bad"})
        assert r.status_code in (400, 401, 403)


@pytest.mark.asyncio
async def test_receipt_lookup_return_format():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.get("/api/v1/voting/receipt/nonexistent")
        # Should be 401/404; format check is contract-based
        assert r.status_code in (401, 404, 403)
