"""Sensor management and reading endpoints."""
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_active_user, require_role
from app.core.constants import SensorType
from app.models.user import User
from app.schemas.common import PaginatedResponse
from app.schemas.sensor import (
    SensorCreate, SensorUpdate, SensorResponse,
    SensorReadingCreate, SensorReadingResponse, SensorSummaryResponse,
)
from app.services.sensor_service import SensorService

router = APIRouter()


@router.post("/", response_model=SensorResponse, status_code=201)
async def create_sensor(
    farm_id: UUID,
    data: SensorCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("admin", "farm_manager")),
):
    service = SensorService(db)
    return await service.create_sensor(farm_id, data)


@router.get("/", response_model=list[SensorResponse])
async def list_sensors(
    farm_id: UUID,
    zone_id: UUID | None = None,
    sensor_type: SensorType | None = None,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    service = SensorService(db)
    return await service.get_farm_sensors(farm_id, zone_id=zone_id, sensor_type=sensor_type)


@router.get("/summary", response_model=list[SensorSummaryResponse])
async def get_sensor_summary(
    farm_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    service = SensorService(db)
    return await service.get_sensor_summary(farm_id)


@router.get("/{sensor_id}", response_model=SensorResponse)
async def get_sensor(
    farm_id: UUID,
    sensor_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    service = SensorService(db)
    return await service.get_sensor(sensor_id)


@router.patch("/{sensor_id}", response_model=SensorResponse)
async def update_sensor(
    farm_id: UUID,
    sensor_id: UUID,
    data: SensorUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("admin", "farm_manager")),
):
    service = SensorService(db)
    return await service.update_sensor(sensor_id, data)


@router.delete("/{sensor_id}", status_code=204)
async def delete_sensor(
    farm_id: UUID,
    sensor_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("admin")),
):
    service = SensorService(db)
    await service.delete_sensor(sensor_id)


# --- Readings ---
@router.post("/{sensor_id}/readings", response_model=SensorReadingResponse, status_code=201)
async def record_reading(
    farm_id: UUID,
    sensor_id: UUID,
    data: SensorReadingCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    service = SensorService(db)
    return await service.record_reading(sensor_id, data)


@router.get("/{sensor_id}/readings", response_model=list[SensorReadingResponse])
async def get_readings(
    farm_id: UUID,
    sensor_id: UUID,
    start: datetime | None = None,
    end: datetime | None = None,
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    service = SensorService(db)
    return await service.get_readings(sensor_id, start=start, end=end, limit=limit)
