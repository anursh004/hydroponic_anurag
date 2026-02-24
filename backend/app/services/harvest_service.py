import uuid
from datetime import date, timedelta

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.crop import CropCycle, CropProfile
from app.models.harvest import Harvest
from app.models.user import User
from app.repositories.base import BaseRepository
from app.schemas.harvest import HarvestCalendarEntry, YieldReportResponse


class HarvestService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.harvest_repo = BaseRepository(Harvest, db)

    async def create_harvest(
        self, cycle_id: uuid.UUID, data: dict, user: User
    ) -> Harvest:
        result = await self.db.execute(
            select(CropCycle).where(CropCycle.id == cycle_id)
        )
        cycle = result.scalar_one_or_none()
        if not cycle:
            raise NotFoundException(detail="Crop cycle not found")

        data["crop_cycle_id"] = cycle_id
        data["harvested_by"] = user.id
        harvest = await self.harvest_repo.create(data)

        cycle.status = "harvested"
        cycle.actual_harvest_at = data["harvest_date"]
        await self.db.flush()
        return harvest

    async def list_harvests(self, farm_id: uuid.UUID) -> list[Harvest]:
        result = await self.db.execute(
            select(Harvest)
            .join(CropCycle, Harvest.crop_cycle_id == CropCycle.id)
            .where(CropCycle.farm_id == farm_id)
            .order_by(Harvest.harvest_date.desc())
            .limit(100)
        )
        return list(result.scalars().all())

    async def get_harvest(self, harvest_id: uuid.UUID) -> Harvest:
        harvest = await self.harvest_repo.get_by_id(harvest_id)
        if not harvest:
            raise NotFoundException(detail="Harvest not found")
        return harvest

    async def get_harvest_calendar(self, farm_id: uuid.UUID) -> list[HarvestCalendarEntry]:
        entries = []
        result = await self.db.execute(
            select(CropCycle, CropProfile)
            .join(CropProfile, CropCycle.crop_profile_id == CropProfile.id)
            .where(
                CropCycle.farm_id == farm_id,
                CropCycle.status.notin_(["failed"]),
            )
        )
        for cycle, profile in result.all():
            if cycle.expected_harvest_at:
                entries.append(
                    HarvestCalendarEntry(
                        date=cycle.expected_harvest_at,
                        crop_name=profile.name,
                        batch_code=cycle.batch_code,
                        expected_kg=None,
                        is_actual=cycle.status == "harvested",
                        crop_cycle_id=cycle.id,
                    )
                )
        return sorted(entries, key=lambda e: e.date)

    async def get_yield_report(self, farm_id: uuid.UUID) -> list[YieldReportResponse]:
        result = await self.db.execute(
            select(
                CropProfile.name,
                func.sum(Harvest.weight_kg).label("total_kg"),
                func.count(Harvest.id).label("count"),
            )
            .join(CropCycle, Harvest.crop_cycle_id == CropCycle.id)
            .join(CropProfile, CropCycle.crop_profile_id == CropProfile.id)
            .where(CropCycle.farm_id == farm_id)
            .group_by(CropProfile.name)
        )
        reports = []
        for row in result.all():
            reports.append(
                YieldReportResponse(
                    crop_name=row[0],
                    zone_name=None,
                    total_harvested_kg=float(row[1] or 0),
                    expected_kg=0,
                    variance_percent=0,
                    cycle_count=row[2] or 0,
                )
            )
        return reports

    async def get_monthly_yield(self, farm_id: uuid.UUID) -> float:
        today = date.today()
        month_start = today.replace(day=1)
        result = await self.db.execute(
            select(func.sum(Harvest.weight_kg))
            .join(CropCycle, Harvest.crop_cycle_id == CropCycle.id)
            .where(
                CropCycle.farm_id == farm_id,
                Harvest.harvest_date >= month_start,
            )
        )
        return float(result.scalar() or 0)
