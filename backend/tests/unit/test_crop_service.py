"""Tests for crop service."""
import pytest
from uuid import uuid4
from decimal import Decimal

from app.core.constants import CropCycleStatus
from app.core.exceptions import NotFoundException, BadRequestException
from app.services.crop_service import CropService
from app.schemas.crop import CropProfileCreate, CropCycleCreate, GrowthLogCreate


class TestCropProfileService:
    """Test crop profile operations."""

    @pytest.mark.asyncio
    async def test_create_profile(self, db_session):
        service = CropService(db_session)
        data = CropProfileCreate(
            name="Test Basil",
            species="Ocimum basilicum",
            variety="Genovese",
            growth_days=28,
            germination_days=5,
            ideal_ph_min=5.5,
            ideal_ph_max=6.5,
            ideal_ec_min=Decimal("1.0"),
            ideal_ec_max=Decimal("1.6"),
            ideal_temp_min=18.0,
            ideal_temp_max=27.0,
            ideal_humidity_min=40.0,
            ideal_humidity_max=60.0,
            ideal_light_hours=16,
        )
        profile = await service.create_profile(data)
        assert profile.name == "Test Basil"
        assert profile.growth_days == 28

    @pytest.mark.asyncio
    async def test_get_profile(self, db_session, sample_crop_profile):
        service = CropService(db_session)
        profile = await service.get_profile(sample_crop_profile.id)
        assert profile.id == sample_crop_profile.id

    @pytest.mark.asyncio
    async def test_get_all_profiles(self, db_session, sample_crop_profile):
        service = CropService(db_session)
        profiles = await service.get_all_profiles()
        assert len(profiles) >= 1

    @pytest.mark.asyncio
    async def test_delete_system_default_profile_fails(self, db_session, sample_crop_profile):
        service = CropService(db_session)
        with pytest.raises(BadRequestException):
            await service.delete_profile(sample_crop_profile.id)


class TestCropCycleService:
    """Test crop cycle operations."""

    @pytest.mark.asyncio
    async def test_create_cycle(self, db_session, sample_farm, sample_crop_profile):
        service = CropService(db_session)
        data = CropCycleCreate(
            farm_id=sample_farm.id,
            crop_profile_id=sample_crop_profile.id,
            seed_batch="SEED-TEST-001",
            tray_count=5,
        )
        cycle = await service.create_cycle(data)
        assert cycle.farm_id == sample_farm.id
        assert cycle.status == CropCycleStatus.SEEDED
        assert cycle.batch_code is not None
        assert "LET" in cycle.batch_code or len(cycle.batch_code) > 0

    @pytest.mark.asyncio
    async def test_get_cycle(self, db_session, sample_crop_cycle):
        service = CropService(db_session)
        cycle = await service.get_cycle(sample_crop_cycle.id)
        assert cycle.id == sample_crop_cycle.id
        assert cycle.batch_code == "LET-2025-0115-001"

    @pytest.mark.asyncio
    async def test_get_active_cycles(self, db_session, sample_farm, sample_crop_cycle):
        service = CropService(db_session)
        cycles, total = await service.get_cycles(sample_farm.id)
        assert total >= 1

    @pytest.mark.asyncio
    async def test_add_growth_log(self, db_session, sample_crop_cycle, sample_user):
        service = CropService(db_session)
        data = GrowthLogCreate(
            health_rating=4,
            height_cm=12.5,
            leaf_count=8,
            notes="Looking healthy",
        )
        log = await service.add_growth_log(sample_crop_cycle.id, data, sample_user.id)
        assert log.health_rating == 4
        assert float(log.height_cm) == 12.5


class TestCropProfileValidation:
    """Test crop profile schema validations."""

    def test_ph_range_validation(self):
        """pH must be between 0 and 14."""
        with pytest.raises(Exception):
            CropProfileCreate(
                name="Bad pH",
                species="Test",
                growth_days=30,
                ideal_ph_min=-1.0,
                ideal_ph_max=15.0,
                ideal_temp_min=18.0,
                ideal_temp_max=25.0,
                ideal_humidity_min=50.0,
                ideal_humidity_max=70.0,
                ideal_light_hours=16,
            )

    def test_growth_log_health_rating_range(self):
        """Health rating must be 1-5."""
        with pytest.raises(Exception):
            GrowthLogCreate(health_rating=0)
        with pytest.raises(Exception):
            GrowthLogCreate(health_rating=6)
