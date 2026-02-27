"""Integration tests for auth API endpoints."""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, AsyncMock

from app.main import app
from app.core.database import get_db


class TestAuthEndpoints:
    """Test auth API integration."""

    @pytest_asyncio.fixture
    async def client(self, db_session):
        """Create test client with database override."""
        async def override_get_db():
            yield db_session

        app.dependency_overrides[get_db] = override_get_db
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield client
        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_register(self, client, sample_role):
        response = await client.post("/api/v1/auth/register", json={
            "email": "newuser@test.com",
            "password": "ValidPass123!",
            "full_name": "New User",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@test.com"
        assert "hashed_password" not in data

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client, sample_user, sample_role):
        response = await client.post("/api/v1/auth/register", json={
            "email": "test@example.com",
            "password": "ValidPass123!",
            "full_name": "Duplicate",
        })
        assert response.status_code == 409

    @pytest.mark.asyncio
    async def test_login_success(self, client, sample_user, sample_role):
        response = await client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "TestPass123!",
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client, sample_user, sample_role):
        response = await client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "WrongPassword!",
        })
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_user(self, client, sample_user, sample_role):
        # Login first
        login_resp = await client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "TestPass123!",
        })
        token = login_resp.json()["access_token"]

        # Get profile
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        assert response.json()["email"] == "test@example.com"

    @pytest.mark.asyncio
    async def test_health_check(self, client):
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
