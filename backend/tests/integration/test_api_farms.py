"""Integration tests for farm API endpoints."""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.core.database import get_db
from app.core.security import create_access_token


class TestFarmEndpoints:
    """Test farm API integration."""

    @pytest_asyncio.fixture
    async def client(self, db_session):
        async def override_get_db():
            yield db_session

        app.dependency_overrides[get_db] = override_get_db
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield client
        app.dependency_overrides.clear()

    @pytest_asyncio.fixture
    async def auth_headers(self, sample_user):
        token = create_access_token(data={"sub": sample_user.email, "type": "access"})
        return {"Authorization": f"Bearer {token}"}

    @pytest.mark.asyncio
    async def test_create_farm(self, client, auth_headers, sample_user):
        response = await client.post(
            "/api/v1/farms/",
            json={
                "name": "API Test Farm",
                "location": "Test City",
                "timezone": "UTC",
            },
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "API Test Farm"

    @pytest.mark.asyncio
    async def test_list_farms(self, client, auth_headers, sample_farm):
        response = await client.get("/api/v1/farms/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert data["total"] >= 1

    @pytest.mark.asyncio
    async def test_get_farm(self, client, auth_headers, sample_farm):
        response = await client.get(
            f"/api/v1/farms/{sample_farm.id}", headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Test Farm"

    @pytest.mark.asyncio
    async def test_update_farm(self, client, auth_headers, sample_farm):
        response = await client.patch(
            f"/api/v1/farms/{sample_farm.id}",
            json={"name": "Updated Farm"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Updated Farm"

    @pytest.mark.asyncio
    async def test_unauthorized_access(self, client):
        response = await client.get("/api/v1/farms/")
        assert response.status_code in [401, 403]
