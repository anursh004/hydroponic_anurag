"""Shared test fixtures for backend tests."""
import asyncio
from datetime import datetime
from decimal import Decimal
from typing import AsyncGenerator
from uuid import uuid4

import pytest
import pytest_asyncio
from sqlalchemy import event
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)

from app.core.config import settings
from app.models.base import Base
from app.models import *  # noqa: F401,F403 - Import all models for table creation


# Use SQLite for testing (in-memory)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def engine():
    """Create async engine for tests."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    # Enable foreign keys for SQLite
    @event.listens_for(engine.sync_engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a fresh database session for each test with rollback."""
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with session_factory() as session:
        async with session.begin():
            yield session
            await session.rollback()


@pytest_asyncio.fixture
async def sample_role(db_session: AsyncSession):
    """Create a sample role for testing."""
    from app.models.user import Role
    role = Role(id=uuid4(), name="admin", description="Admin role")
    db_session.add(role)
    await db_session.flush()
    return role


@pytest_asyncio.fixture
async def sample_user(db_session: AsyncSession, sample_role):
    """Create a sample user for testing."""
    from app.models.user import User
    from app.core.security import get_password_hash
    user = User(
        id=uuid4(),
        email="test@example.com",
        full_name="Test User",
        hashed_password=get_password_hash("TestPass123!"),
        role_id=sample_role.id,
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest_asyncio.fixture
async def sample_farm(db_session: AsyncSession, sample_user):
    """Create a sample farm for testing."""
    from app.models.farm import Farm
    from app.models.user import user_farms
    farm = Farm(
        id=uuid4(),
        name="Test Farm",
        location="Test Location",
        latitude=40.7128,
        longitude=-74.0060,
        timezone="America/New_York",
        owner_id=sample_user.id,
    )
    db_session.add(farm)
    await db_session.flush()

    # Add user-farm association
    await db_session.execute(
        user_farms.insert().values(user_id=sample_user.id, farm_id=farm.id)
    )
    await db_session.flush()
    return farm


@pytest_asyncio.fixture
async def sample_zone(db_session: AsyncSession, sample_farm):
    """Create a sample zone."""
    from app.models.farm import Zone
    from app.core.constants import ZoneType, EnvironmentType
    zone = Zone(
        id=uuid4(),
        name="Zone A",
        farm_id=sample_farm.id,
        zone_type=ZoneType.GROWING if hasattr(ZoneType, "GROWING") else "growing",
        environment_type=EnvironmentType.INDOOR if hasattr(EnvironmentType, "INDOOR") else "indoor",
        position=1,
    )
    db_session.add(zone)
    await db_session.flush()
    return zone


@pytest_asyncio.fixture
async def sample_sensor(db_session: AsyncSession, sample_farm, sample_zone):
    """Create a sample sensor."""
    from app.models.sensor import Sensor
    from app.core.constants import SensorType
    sensor = Sensor(
        id=uuid4(),
        name="pH Sensor 1",
        farm_id=sample_farm.id,
        zone_id=sample_zone.id,
        sensor_type=SensorType.PH,
        mqtt_topic=f"greenos/{sample_farm.id}/sensors/ph1/ph",
        is_active=True,
        calibration_offset=0.0,
    )
    db_session.add(sensor)
    await db_session.flush()
    return sensor


@pytest_asyncio.fixture
async def sample_crop_profile(db_session: AsyncSession):
    """Create a sample crop profile."""
    from app.models.crop import CropProfile
    profile = CropProfile(
        id=uuid4(),
        name="Test Lettuce",
        species="Lactuca sativa",
        variety="Butterhead",
        growth_days=35,
        germination_days=3,
        ideal_ph_min=5.5,
        ideal_ph_max=6.5,
        ideal_ec_min=Decimal("0.8"),
        ideal_ec_max=Decimal("1.2"),
        ideal_temp_min=15.0,
        ideal_temp_max=22.0,
        ideal_humidity_min=50.0,
        ideal_humidity_max=70.0,
        ideal_light_hours=16,
        nutrient_recipe={"n": 150, "p": 50, "k": 200},
        is_system_default=True,
    )
    db_session.add(profile)
    await db_session.flush()
    return profile


@pytest_asyncio.fixture
async def sample_crop_cycle(db_session: AsyncSession, sample_farm, sample_crop_profile):
    """Create a sample crop cycle."""
    from app.models.crop import CropCycle
    from app.core.constants import CropCycleStatus
    cycle = CropCycle(
        id=uuid4(),
        batch_code="LET-2025-0115-001",
        farm_id=sample_farm.id,
        crop_profile_id=sample_crop_profile.id,
        status=CropCycleStatus.VEGETATIVE,
        seeded_at=datetime.utcnow(),
        seed_batch="SEED-001",
        tray_count=10,
    )
    db_session.add(cycle)
    await db_session.flush()
    return cycle
