import uuid
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.sensor import Sensor, SensorReading
from app.repositories.sensor_repo import SensorRepository, SensorReadingRepository
from app.schemas.sensor import SensorSummaryResponse


class SensorService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.sensor_repo = SensorRepository(db)
        self.reading_repo = SensorReadingRepository(db)

    async def create_sensor(self, farm_id: uuid.UUID, data: dict) -> Sensor:
        data["farm_id"] = farm_id
        return await self.sensor_repo.create(data)

    async def get_sensor(self, sensor_id: uuid.UUID) -> Sensor:
        sensor = await self.sensor_repo.get_by_id(sensor_id)
        if not sensor:
            raise NotFoundException(detail="Sensor not found")
        return sensor

    async def update_sensor(self, sensor_id: uuid.UUID, data: dict) -> Sensor:
        sensor = await self.sensor_repo.update(sensor_id, data)
        if not sensor:
            raise NotFoundException(detail="Sensor not found")
        return sensor

    async def delete_sensor(self, sensor_id: uuid.UUID) -> None:
        sensor = await self.sensor_repo.update(sensor_id, {"is_active": False})
        if not sensor:
            raise NotFoundException(detail="Sensor not found")

    async def list_sensors(
        self,
        farm_id: uuid.UUID,
        zone_id: uuid.UUID | None = None,
        sensor_type: str | None = None,
    ) -> list[Sensor]:
        return await self.sensor_repo.get_farm_sensors(farm_id, zone_id, sensor_type)

    async def record_reading(
        self, sensor_id: uuid.UUID, data: dict
    ) -> SensorReading:
        sensor = await self.get_sensor(sensor_id)
        data["sensor_id"] = sensor_id

        reading = await self.reading_repo.create_reading(data)

        sensor.last_value = reading.value
        sensor.last_reading_at = reading.recorded_at
        await self.db.flush()

        return reading

    async def get_readings(
        self,
        sensor_id: uuid.UUID,
        start: datetime | None = None,
        end: datetime | None = None,
        limit: int = 100,
    ) -> list[SensorReading]:
        return await self.reading_repo.get_readings(sensor_id, start, end, limit)

    async def get_sensor_summary(self, farm_id: uuid.UUID) -> list[SensorSummaryResponse]:
        sensors = await self.sensor_repo.get_farm_sensors(farm_id)
        summaries = []
        for sensor in sensors:
            status = "normal"
            if sensor.last_value is None:
                status = "no_data"
            summaries.append(
                SensorSummaryResponse(
                    sensor_id=sensor.id,
                    sensor_type=sensor.sensor_type,
                    name=sensor.name,
                    latest_value=float(sensor.last_value) if sensor.last_value else None,
                    latest_reading_at=sensor.last_reading_at,
                    status=status,
                    zone_name=sensor.zone.name if sensor.zone else None,
                )
            )
        return summaries
