import uuid
from datetime import timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestException, NotFoundException
from app.models.crop import CropCycle, CropProfile, GrowthLog
from app.models.user import User
from app.repositories.crop_repo import (
    CropCycleRepository,
    CropProfileRepository,
    GrowthLogRepository,
)


class CropService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.profile_repo = CropProfileRepository(db)
        self.cycle_repo = CropCycleRepository(db)
        self.log_repo = GrowthLogRepository(db)

    # Profiles
    async def list_profiles(self, skip: int = 0, limit: int = 100) -> list[CropProfile]:
        return await self.profile_repo.get_all_profiles(skip, limit)

    async def get_profile(self, profile_id: uuid.UUID) -> CropProfile:
        profile = await self.profile_repo.get_by_id(profile_id)
        if not profile:
            raise NotFoundException(detail="Crop profile not found")
        return profile

    async def create_profile(self, data: dict, user: User) -> CropProfile:
        data["created_by"] = user.id
        data["is_system_default"] = False
        return await self.profile_repo.create(data)

    async def update_profile(self, profile_id: uuid.UUID, data: dict) -> CropProfile:
        profile = await self.profile_repo.update(profile_id, data)
        if not profile:
            raise NotFoundException(detail="Crop profile not found")
        return profile

    async def delete_profile(self, profile_id: uuid.UUID) -> None:
        profile = await self.profile_repo.get_by_id(profile_id)
        if not profile:
            raise NotFoundException(detail="Crop profile not found")
        if profile.is_system_default:
            raise BadRequestException(detail="Cannot delete system default profiles")
        await self.profile_repo.delete(profile_id)

    # Cycles
    async def create_cycle(self, farm_id: uuid.UUID, data: dict) -> CropCycle:
        profile = await self.get_profile(data["crop_profile_id"])

        batch_code = await self.cycle_repo.generate_batch_code(profile.name)
        data["farm_id"] = farm_id
        data["batch_code"] = batch_code
        data["expected_harvest_at"] = data["seeded_at"] + timedelta(days=profile.days_to_harvest)
        data["status"] = "seeded"

        return await self.cycle_repo.create(data)

    async def get_cycle(self, cycle_id: uuid.UUID) -> CropCycle:
        cycle = await self.cycle_repo.get_with_profile(cycle_id)
        if not cycle:
            raise NotFoundException(detail="Crop cycle not found")
        return cycle

    async def list_cycles(self, farm_id: uuid.UUID, status: str | None = None) -> list[CropCycle]:
        if status:
            return await self.cycle_repo.get_multi(limit=1000, farm_id=farm_id, status=status)
        return await self.cycle_repo.get_active_cycles(farm_id)

    async def update_cycle(self, cycle_id: uuid.UUID, data: dict) -> CropCycle:
        cycle = await self.cycle_repo.update(cycle_id, data)
        if not cycle:
            raise NotFoundException(detail="Crop cycle not found")
        return cycle

    async def log_germination(self, cycle_id: uuid.UUID, germination_count: int) -> CropCycle:
        cycle = await self.get_cycle(cycle_id)
        cycle.germination_count = germination_count
        if cycle.quantity_planted > 0:
            cycle.germination_rate = round(
                (germination_count / cycle.quantity_planted) * 100, 2
            )
        cycle.status = "germinating"
        await self.db.flush()
        await self.db.refresh(cycle)
        return cycle

    async def add_growth_log(
        self, cycle_id: uuid.UUID, data: dict, user: User
    ) -> GrowthLog:
        await self.get_cycle(cycle_id)  # Verify exists
        data["crop_cycle_id"] = cycle_id
        data["logged_by"] = user.id
        return await self.log_repo.create(data)

    async def get_growth_logs(self, cycle_id: uuid.UUID) -> list[GrowthLog]:
        return await self.log_repo.get_logs_for_cycle(cycle_id)
