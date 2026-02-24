import uuid

from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.farm import Farm, Zone, Rack, Tray
from app.models.user import User, user_farms
from app.repositories.farm_repo import FarmRepository, ZoneRepository, RackRepository, TrayRepository


class FarmService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.farm_repo = FarmRepository(db)
        self.zone_repo = ZoneRepository(db)
        self.rack_repo = RackRepository(db)
        self.tray_repo = TrayRepository(db)

    async def create_farm(self, data: dict, owner: User) -> Farm:
        data["owner_id"] = owner.id
        farm = await self.farm_repo.create(data)
        await self.db.execute(
            insert(user_farms).values(user_id=owner.id, farm_id=farm.id)
        )
        await self.db.flush()
        return farm

    async def get_user_farms(self, user: User) -> list[Farm]:
        if user.is_superuser:
            return await self.farm_repo.get_multi(limit=1000)
        return await self.farm_repo.get_user_farms(user.id)

    async def get_farm(self, farm_id: uuid.UUID) -> Farm:
        farm = await self.farm_repo.get_farm_with_zones(farm_id)
        if not farm:
            raise NotFoundException(detail="Farm not found")
        return farm

    async def update_farm(self, farm_id: uuid.UUID, data: dict) -> Farm:
        farm = await self.farm_repo.update(farm_id, data)
        if not farm:
            raise NotFoundException(detail="Farm not found")
        return farm

    async def delete_farm(self, farm_id: uuid.UUID) -> None:
        farm = await self.farm_repo.update(farm_id, {"is_active": False})
        if not farm:
            raise NotFoundException(detail="Farm not found")

    # Zones
    async def create_zone(self, farm_id: uuid.UUID, data: dict) -> Zone:
        data["farm_id"] = farm_id
        return await self.zone_repo.create(data)

    async def get_zones(self, farm_id: uuid.UUID) -> list[Zone]:
        return await self.zone_repo.get_multi(limit=1000, farm_id=farm_id)

    async def get_zone(self, zone_id: uuid.UUID) -> Zone:
        zone = await self.zone_repo.get_by_id(zone_id)
        if not zone:
            raise NotFoundException(detail="Zone not found")
        return zone

    async def update_zone(self, zone_id: uuid.UUID, data: dict) -> Zone:
        zone = await self.zone_repo.update(zone_id, data)
        if not zone:
            raise NotFoundException(detail="Zone not found")
        return zone

    async def delete_zone(self, zone_id: uuid.UUID) -> None:
        if not await self.zone_repo.delete(zone_id):
            raise NotFoundException(detail="Zone not found")

    # Racks
    async def create_rack(self, zone_id: uuid.UUID, data: dict) -> Rack:
        data["zone_id"] = zone_id
        return await self.rack_repo.create(data)

    async def get_racks(self, zone_id: uuid.UUID) -> list[Rack]:
        return await self.rack_repo.get_multi(limit=1000, zone_id=zone_id)

    async def update_rack(self, rack_id: uuid.UUID, data: dict) -> Rack:
        rack = await self.rack_repo.update(rack_id, data)
        if not rack:
            raise NotFoundException(detail="Rack not found")
        return rack

    async def delete_rack(self, rack_id: uuid.UUID) -> None:
        if not await self.rack_repo.delete(rack_id):
            raise NotFoundException(detail="Rack not found")

    # Trays
    async def create_tray(self, rack_id: uuid.UUID, data: dict) -> Tray:
        data["rack_id"] = rack_id
        return await self.tray_repo.create(data)

    async def get_trays(self, rack_id: uuid.UUID) -> list[Tray]:
        return await self.tray_repo.get_multi(limit=1000, rack_id=rack_id)

    async def update_tray(self, tray_id: uuid.UUID, data: dict) -> Tray:
        tray = await self.tray_repo.update(tray_id, data)
        if not tray:
            raise NotFoundException(detail="Tray not found")
        return tray
