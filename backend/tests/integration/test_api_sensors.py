"""Integration tests for sensor API endpoints."""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.core.database import get_db
from app.core.security import create_access_token
from app.core.constants import SensorType


class TestSensorEndpoints:
    """Test sensor API integration."""

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
    async def test_create_sensor(self, client, auth_headers, sample_farm, sample_zone):
        response = await client.post(
            f"/api/v1/farms/{sample_farm.id}/sensors/",
            json={
                "name": "New Temp Sensor",
                "sensor_type": SensorType.TEMPERATURE.value,
                "zone_id": str(sample_zone.id),
                "mqtt_topic": "test/temp",
            },
            headers=auth_headers,
        )
        assert response.status_code == 201
        assert response.json()["name"] == "New Temp Sensor"

    @pytest.mark.asyncio
    async def test_list_sensors(self, client, auth_headers, sample_farm, sample_sensor):
        response = await client.get(
            f"/api/v1/farms/{sample_farm.id}/sensors/",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    @pytest.mark.asyncio
    async def test_record_reading(self, client, auth_headers, sample_farm, sample_sensor):
        response = await client.post(
            f"/api/v1/farms/{sample_farm.id}/sensors/{sample_sensor.id}/readings",
            json={"value": 6.8},
            headers=auth_headers,
        )
        assert response.status_code == 201
        assert float(response.json()["value"]) == 6.8

    @pytest.mark.asyncio
    async def test_get_readings(self, client, auth_headers, sample_farm, sample_sensor):
        # Record a reading first
        await client.post(
            f"/api/v1/farms/{sample_farm.id}/sensors/{sample_sensor.id}/readings",
            json={"value": 7.0},
            headers=auth_headers,
        )
        response = await client.get(
            f"/api/v1/farms/{sample_farm.id}/sensors/{sample_sensor.id}/readings",
            headers=auth_headers,
        )
        assert response.status_code == 200
