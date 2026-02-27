"""Tests for sensor service."""
import pytest
from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from app.core.constants import SensorType
from app.core.exceptions import NotFoundException
from app.services.sensor_service import SensorService
from app.schemas.sensor import SensorCreate, SensorUpdate, SensorReadingCreate


class TestSensorService:
    """Test SensorService operations."""

    @pytest.mark.asyncio
    async def test_create_sensor(self, db_session, sample_farm, sample_zone):
        service = SensorService(db_session)
        data = SensorCreate(
            name="Temperature Sensor 1",
            sensor_type=SensorType.TEMPERATURE,
            zone_id=sample_zone.id,
            mqtt_topic=f"greenos/{sample_farm.id}/sensors/temp1/temperature",
        )
        sensor = await service.create_sensor(sample_farm.id, data)
        assert sensor.name == "Temperature Sensor 1"
        assert sensor.sensor_type == SensorType.TEMPERATURE
        assert sensor.farm_id == sample_farm.id

    @pytest.mark.asyncio
    async def test_get_sensor(self, db_session, sample_sensor):
        service = SensorService(db_session)
        sensor = await service.get_sensor(sample_sensor.id)
        assert sensor.id == sample_sensor.id
        assert sensor.name == "pH Sensor 1"

    @pytest.mark.asyncio
    async def test_get_sensor_not_found(self, db_session):
        service = SensorService(db_session)
        with pytest.raises(NotFoundException):
            await service.get_sensor(uuid4())

    @pytest.mark.asyncio
    async def test_update_sensor(self, db_session, sample_sensor):
        service = SensorService(db_session)
        data = SensorUpdate(name="Updated pH Sensor")
        updated = await service.update_sensor(sample_sensor.id, data)
        assert updated.name == "Updated pH Sensor"

    @pytest.mark.asyncio
    async def test_get_farm_sensors(self, db_session, sample_farm, sample_sensor):
        service = SensorService(db_session)
        sensors = await service.get_farm_sensors(sample_farm.id)
        assert len(sensors) >= 1
        assert any(s.id == sample_sensor.id for s in sensors)

    @pytest.mark.asyncio
    async def test_get_farm_sensors_by_type(self, db_session, sample_farm, sample_sensor):
        service = SensorService(db_session)
        sensors = await service.get_farm_sensors(
            sample_farm.id, sensor_type=SensorType.PH
        )
        assert all(s.sensor_type == SensorType.PH for s in sensors)

    @pytest.mark.asyncio
    async def test_record_reading(self, db_session, sample_sensor):
        service = SensorService(db_session)
        data = SensorReadingCreate(value=Decimal("6.5"))
        reading = await service.record_reading(sample_sensor.id, data)
        assert float(reading.value) == 6.5
        assert reading.sensor_id == sample_sensor.id

    @pytest.mark.asyncio
    async def test_record_reading_updates_sensor(self, db_session, sample_sensor):
        service = SensorService(db_session)
        data = SensorReadingCreate(value=Decimal("7.2"))
        await service.record_reading(sample_sensor.id, data)
        sensor = await service.get_sensor(sample_sensor.id)
        assert float(sensor.last_value) == 7.2

    @pytest.mark.asyncio
    async def test_delete_sensor(self, db_session, sample_farm, sample_zone):
        service = SensorService(db_session)
        data = SensorCreate(
            name="Temp Sensor",
            sensor_type=SensorType.EC,
            zone_id=sample_zone.id,
            mqtt_topic="test/topic",
        )
        sensor = await service.create_sensor(sample_farm.id, data)
        await service.delete_sensor(sensor.id)
        with pytest.raises(NotFoundException):
            await service.get_sensor(sensor.id)
