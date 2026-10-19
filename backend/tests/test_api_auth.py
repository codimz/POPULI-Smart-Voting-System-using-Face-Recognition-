# T28: API test auth / login
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_login_wrong_nim_format():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.post("/api/v1/auth/login", json={"nim": "", "password": ""})
        assert r.status_code == 400
        data = r.json()
        assert data["success"] is False
        assert "error" in data


@pytest.mark.asyncio
async def test_login_invalid_password_format():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.post("/api/v1/auth/login", json={"nim": "0000000000", "password": "bad"})
        # Should be unauthorized (401) or 400 depending on validation
        assert r.status_code in (401, 400)
        data = r.json()
        assert data.get("success") is False
