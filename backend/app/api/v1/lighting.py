"""Lighting control endpoints."""
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_active_user, require_role
from app.models.user import User
from app.schemas.lighting import (
    LightZoneCreate, LightZoneUpdate, LightZoneResponse,
    LightScheduleCreate, LightScheduleUpdate, LightScheduleResponse,
    LightCommandRequest,
)
from app.schemas.common import MessageResponse
from app.services.lighting_service import LightingService

router = APIRouter()


# --- Light Zones ---
@router.post("/zones", response_model=LightZoneResponse, status_code=201)
async def create_light_zone(
    farm_id: UUID,
    data: LightZoneCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("admin", "farm_manager")),
):
    service = LightingService(db)
    return await service.create_light_zone(farm_id, data)


@router.get("/zones", response_model=list[LightZoneResponse])
async def list_light_zones(
    farm_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    service = LightingService(db)
    return await service.get_light_zones(farm_id)


@router.get("/zones/{zone_id}", response_model=LightZoneResponse)
async def get_light_zone(
    farm_id: UUID,
    zone_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    service = LightingService(db)
    return await service.get_light_zone(zone_id)


@router.patch("/zones/{zone_id}", response_model=LightZoneResponse)
async def update_light_zone(
    farm_id: UUID,
    zone_id: UUID,
    data: LightZoneUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("admin", "farm_manager")),
):
    service = LightingService(db)
    return await service.update_light_zone(zone_id, data)


@router.post("/zones/{zone_id}/command", response_model=MessageResponse)
async def send_light_command(
    farm_id: UUID,
    zone_id: UUID,
    data: LightCommandRequest,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("admin", "farm_manager", "operator")),
):
    service = LightingService(db)
    await service.send_command(zone_id, data)
    return MessageResponse(message=f"Light command '{data.action}' sent successfully")


# --- Schedules ---
@router.post("/schedules", response_model=LightScheduleResponse, status_code=201)
async def create_schedule(
    farm_id: UUID,
    data: LightScheduleCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("admin", "farm_manager")),
):
    service = LightingService(db)
    return await service.create_schedule(farm_id, data)


@router.get("/schedules", response_model=list[LightScheduleResponse])
async def list_schedules(
    farm_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    service = LightingService(db)
    return await service.get_schedules(farm_id)


@router.patch("/schedules/{schedule_id}", response_model=LightScheduleResponse)
async def update_schedule(
    farm_id: UUID,
    schedule_id: UUID,
    data: LightScheduleUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("admin", "farm_manager")),
):
    service = LightingService(db)
    return await service.update_schedule(schedule_id, data)
