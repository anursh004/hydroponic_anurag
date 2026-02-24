import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.dosing import DosingEvent, DosingPump, DosingRecipe
from app.repositories.base import BaseRepository


class DosingService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.pump_repo = BaseRepository(DosingPump, db)
        self.recipe_repo = BaseRepository(DosingRecipe, db)
        self.event_repo = BaseRepository(DosingEvent, db)

    # Pumps
    async def create_pump(self, farm_id: uuid.UUID, data: dict) -> DosingPump:
        data["farm_id"] = farm_id
        return await self.pump_repo.create(data)

    async def update_pump(self, pump_id: uuid.UUID, data: dict) -> DosingPump:
        pump = await self.pump_repo.update(pump_id, data)
        if not pump:
            raise NotFoundException(detail="Dosing pump not found")
        return pump

    async def list_pumps(self, farm_id: uuid.UUID) -> list[DosingPump]:
        return await self.pump_repo.get_multi(limit=100, farm_id=farm_id)

    async def manual_dose(
        self, pump_id: uuid.UUID, volume_ml: float, user_id: uuid.UUID
    ) -> DosingEvent:
        pump = await self.pump_repo.get_by_id(pump_id)
        if not pump:
            raise NotFoundException(detail="Dosing pump not found")

        duration = volume_ml / float(pump.ml_per_second) if float(pump.ml_per_second) > 0 else 0
        event = await self.event_repo.create(
            {
                "pump_id": pump_id,
                "trigger": "manual",
                "volume_ml": volume_ml,
                "duration_seconds": round(duration, 2),
                "sensor_reading_before": 0,
                "status": "completed",
                "initiated_by": user_id,
            }
        )
        pump.last_dose_at = datetime.now(timezone.utc)
        await self.db.flush()
        return event

    # Recipes
    async def create_recipe(self, data: dict) -> DosingRecipe:
        return await self.recipe_repo.create(data)

    async def update_recipe(self, recipe_id: uuid.UUID, data: dict) -> DosingRecipe:
        recipe = await self.recipe_repo.update(recipe_id, data)
        if not recipe:
            raise NotFoundException(detail="Dosing recipe not found")
        return recipe

    async def delete_recipe(self, recipe_id: uuid.UUID) -> None:
        if not await self.recipe_repo.delete(recipe_id):
            raise NotFoundException(detail="Dosing recipe not found")

    async def list_recipes(self, skip: int = 0, limit: int = 100) -> list[DosingRecipe]:
        return await self.recipe_repo.get_multi(skip=skip, limit=limit)

    async def list_events(self, farm_id: uuid.UUID) -> list[DosingEvent]:
        return await self.event_repo.get_multi(limit=100)
