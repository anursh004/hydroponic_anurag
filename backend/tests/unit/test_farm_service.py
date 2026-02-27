"""Tests for farm service."""
import pytest
from uuid import uuid4

from app.core.exceptions import NotFoundException
from app.services.farm_service import FarmService
from app.schemas.farm import FarmCreate, FarmUpdate, ZoneCreate


class TestFarmService:
    """Test FarmService CRUD operations."""

    @pytest.mark.asyncio
    async def test_create_farm(self, db_session, sample_user):
        service = FarmService(db_session)
        data = FarmCreate(
            name="My Hydroponic Farm",
            location="Portland, OR",
            latitude=45.5155,
            longitude=-122.6789,
            timezone="America/Los_Angeles",
        )
        farm = await service.create_farm(data, sample_user.id)
        assert farm.name == "My Hydroponic Farm"
        assert farm.location == "Portland, OR"
        assert farm.owner_id == sample_user.id

    @pytest.mark.asyncio
    async def test_get_farm(self, db_session, sample_farm):
        service = FarmService(db_session)
        farm = await service.get_farm(sample_farm.id)
        assert farm.name == "Test Farm"
        assert farm.id == sample_farm.id

    @pytest.mark.asyncio
    async def test_get_farm_not_found(self, db_session):
        service = FarmService(db_session)
        with pytest.raises(NotFoundException):
            await service.get_farm(uuid4())

    @pytest.mark.asyncio
    async def test_update_farm(self, db_session, sample_farm):
        service = FarmService(db_session)
        data = FarmUpdate(name="Updated Farm Name")
        updated = await service.update_farm(sample_farm.id, data)
        assert updated.name == "Updated Farm Name"

    @pytest.mark.asyncio
    async def test_get_user_farms(self, db_session, sample_user, sample_farm):
        service = FarmService(db_session)
        farms, total = await service.get_user_farms(sample_user.id)
        assert total >= 1
        assert any(f.id == sample_farm.id for f in farms)

    @pytest.mark.asyncio
    async def test_delete_farm(self, db_session, sample_user):
        service = FarmService(db_session)
        data = FarmCreate(
            name="Temp Farm",
            location="Temp",
            timezone="UTC",
        )
        farm = await service.create_farm(data, sample_user.id)
        await service.delete_farm(farm.id)
        with pytest.raises(NotFoundException):
            await service.get_farm(farm.id)


class TestZoneService:
    """Test zone operations within FarmService."""

    @pytest.mark.asyncio
    async def test_create_zone(self, db_session, sample_farm):
        service = FarmService(db_session)
        data = ZoneCreate(
            name="New Growing Zone",
            zone_type="growing",
            environment_type="indoor",
            position=1,
        )
        zone = await service.create_zone(sample_farm.id, data)
        assert zone.name == "New Growing Zone"
        assert zone.farm_id == sample_farm.id

    @pytest.mark.asyncio
    async def test_get_zones(self, db_session, sample_farm, sample_zone):
        service = FarmService(db_session)
        zones = await service.get_zones(sample_farm.id)
        assert len(zones) >= 1
