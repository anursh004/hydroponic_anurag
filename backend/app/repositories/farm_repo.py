import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.farm import Farm, Zone, Rack, Tray
from app.models.user import user_farms
from app.repositories.base import BaseRepository


class FarmRepository(BaseRepository[Farm]):
    def __init__(self, db: AsyncSession):
        super().__init__(Farm, db)

    async def get_user_farms(self, user_id: uuid.UUID) -> list[Farm]:
        result = await self.db.execute(
            select(Farm)
            .join(user_farms, user_farms.c.farm_id == Farm.id)
            .where(user_farms.c.user_id == user_id)
            .where(Farm.is_active.is_(True))
        )
        return list(result.scalars().all())

    async def get_farm_with_zones(self, farm_id: uuid.UUID) -> Farm | None:
        result = await self.db.execute(
            select(Farm)
            .options(selectinload(Farm.zones))
            .where(Farm.id == farm_id)
        )
        return result.scalar_one_or_none()


class ZoneRepository(BaseRepository[Zone]):
    def __init__(self, db: AsyncSession):
        super().__init__(Zone, db)


class RackRepository(BaseRepository[Rack]):
    def __init__(self, db: AsyncSession):
        super().__init__(Rack, db)


class TrayRepository(BaseRepository[Tray]):
    def __init__(self, db: AsyncSession):
        super().__init__(Tray, db)
