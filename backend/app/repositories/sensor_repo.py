import uuid
from datetime import datetime

from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sensor import Sensor, SensorReading
from app.repositories.base import BaseRepository


class SensorRepository(BaseRepository[Sensor]):
    def __init__(self, db: AsyncSession):
        super().__init__(Sensor, db)

    async def get_farm_sensors(
        self,
        farm_id: uuid.UUID,
        zone_id: uuid.UUID | None = None,
        sensor_type: str | None = None,
    ) -> list[Sensor]:
        query = select(Sensor).where(Sensor.farm_id == farm_id, Sensor.is_active.is_(True))
        if zone_id:
            query = query.where(Sensor.zone_id == zone_id)
        if sensor_type:
            query = query.where(Sensor.sensor_type == sensor_type)
        result = await self.db.execute(query.order_by(Sensor.name))
        return list(result.scalars().all())


class SensorReadingRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_reading(self, data: dict) -> SensorReading:
        reading = SensorReading(**data)
        self.db.add(reading)
        await self.db.flush()
        await self.db.refresh(reading)
        return reading

    async def get_readings(
        self,
        sensor_id: uuid.UUID,
        start: datetime | None = None,
        end: datetime | None = None,
        limit: int = 100,
    ) -> list[SensorReading]:
        query = (
            select(SensorReading)
            .where(SensorReading.sensor_id == sensor_id)
        )
        if start:
            query = query.where(SensorReading.recorded_at >= start)
        if end:
            query = query.where(SensorReading.recorded_at <= end)
        query = query.order_by(desc(SensorReading.recorded_at)).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_latest_reading(self, sensor_id: uuid.UUID) -> SensorReading | None:
        result = await self.db.execute(
            select(SensorReading)
            .where(SensorReading.sensor_id == sensor_id)
            .order_by(desc(SensorReading.recorded_at))
            .limit(1)
        )
        return result.scalar_one_or_none()
