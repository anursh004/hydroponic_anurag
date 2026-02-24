import uuid
from datetime import date

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.crop import CropProfile, CropCycle, GrowthLog
from app.repositories.base import BaseRepository


class CropProfileRepository(BaseRepository[CropProfile]):
    def __init__(self, db: AsyncSession):
        super().__init__(CropProfile, db)

    async def get_all_profiles(self, skip: int = 0, limit: int = 100) -> list[CropProfile]:
        result = await self.db.execute(
            select(CropProfile).order_by(CropProfile.name).offset(skip).limit(limit)
        )
        return list(result.scalars().all())


class CropCycleRepository(BaseRepository[CropCycle]):
    def __init__(self, db: AsyncSession):
        super().__init__(CropCycle, db)

    async def get_active_cycles(self, farm_id: uuid.UUID) -> list[CropCycle]:
        result = await self.db.execute(
            select(CropCycle)
            .options(selectinload(CropCycle.crop_profile))
            .where(
                CropCycle.farm_id == farm_id,
                CropCycle.status.notin_(["harvested", "failed"]),
            )
            .order_by(CropCycle.seeded_at.desc())
        )
        return list(result.scalars().all())

    async def get_with_profile(self, cycle_id: uuid.UUID) -> CropCycle | None:
        result = await self.db.execute(
            select(CropCycle)
            .options(selectinload(CropCycle.crop_profile))
            .where(CropCycle.id == cycle_id)
        )
        return result.scalar_one_or_none()

    async def generate_batch_code(self, crop_name: str) -> str:
        prefix = "".join(w[0] for w in crop_name.split()[:3]).upper()
        today = date.today()
        date_part = today.strftime("%Y-%m%d")
        count = await self.db.execute(
            select(func.count()).select_from(CropCycle).where(
                CropCycle.batch_code.like(f"{prefix}-{date_part}%")
            )
        )
        seq = (count.scalar() or 0) + 1
        return f"{prefix}-{date_part}-{seq:03d}"


class GrowthLogRepository(BaseRepository[GrowthLog]):
    def __init__(self, db: AsyncSession):
        super().__init__(GrowthLog, db)

    async def get_logs_for_cycle(self, cycle_id: uuid.UUID) -> list[GrowthLog]:
        result = await self.db.execute(
            select(GrowthLog)
            .where(GrowthLog.crop_cycle_id == cycle_id)
            .order_by(GrowthLog.log_date.desc())
        )
        return list(result.scalars().all())
