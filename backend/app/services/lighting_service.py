import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.lighting import LightSchedule, LightZone
from app.repositories.base import BaseRepository


class LightingService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.zone_repo = BaseRepository(LightZone, db)
        self.schedule_repo = BaseRepository(LightSchedule, db)

    async def create_light_zone(self, zone_id: uuid.UUID, data: dict) -> LightZone:
        data["zone_id"] = zone_id
        return await self.zone_repo.create(data)

    async def update_light_zone(self, lz_id: uuid.UUID, data: dict) -> LightZone:
        lz = await self.zone_repo.update(lz_id, data)
        if not lz:
            raise NotFoundException(detail="Light zone not found")
        return lz

    async def list_light_zones(self, zone_id: uuid.UUID) -> list[LightZone]:
        return await self.zone_repo.get_multi(limit=100, zone_id=zone_id)

    async def send_command(self, lz_id: uuid.UUID, command: dict) -> LightZone:
        lz = await self.zone_repo.get_by_id(lz_id)
        if not lz:
            raise NotFoundException(detail="Light zone not found")
        lz.current_state = command
        await self.db.flush()
        await self.db.refresh(lz)
        return lz

    async def create_schedule(self, lz_id: uuid.UUID, data: dict) -> LightSchedule:
        data["light_zone_id"] = lz_id
        return await self.schedule_repo.create(data)

    async def update_schedule(self, schedule_id: uuid.UUID, data: dict) -> LightSchedule:
        schedule = await self.schedule_repo.update(schedule_id, data)
        if not schedule:
            raise NotFoundException(detail="Light schedule not found")
        return schedule

    async def delete_schedule(self, schedule_id: uuid.UUID) -> None:
        if not await self.schedule_repo.delete(schedule_id):
            raise NotFoundException(detail="Light schedule not found")

    async def list_schedules(self, lz_id: uuid.UUID) -> list[LightSchedule]:
        return await self.schedule_repo.get_multi(limit=100, light_zone_id=lz_id)
