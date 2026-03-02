import pytest
from httpx import AsyncClient
from app.main import app


@pytest.fixture
def client():
    return AsyncClient(app=app, base_url="http://test")


@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
