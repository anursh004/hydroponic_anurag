"""Farm management endpoints."""
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_active_user, require_role
from app.models.user import User
from app.schemas.common import PaginatedResponse, MessageResponse
from app.schemas.farm import (
    FarmCreate, FarmUpdate, FarmResponse,
    ZoneCreate, ZoneUpdate, ZoneResponse,
    RackCreate, RackUpdate, RackResponse,
    TrayCreate, TrayUpdate, TrayResponse,
)
from app.services.farm_service import FarmService

router = APIRouter()


# --- Farms ---
@router.post("/", response_model=FarmResponse, status_code=201)
async def create_farm(
    data: FarmCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = FarmService(db)
    return await service.create_farm(data, current_user.id)


@router.get("/", response_model=PaginatedResponse[FarmResponse])
async def list_farms(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = FarmService(db)
    farms, total = await service.get_user_farms(current_user.id, skip, limit)
    return PaginatedResponse(items=farms, total=total, skip=skip, limit=limit)


@router.get("/{farm_id}", response_model=FarmResponse)
async def get_farm(
    farm_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    service = FarmService(db)
    return await service.get_farm(farm_id)


@router.patch("/{farm_id}", response_model=FarmResponse)
async def update_farm(
    farm_id: UUID,
    data: FarmUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("admin", "farm_manager")),
):
    service = FarmService(db)
    return await service.update_farm(farm_id, data)


@router.delete("/{farm_id}", status_code=204)
async def delete_farm(
    farm_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("admin")),
):
    service = FarmService(db)
    await service.delete_farm(farm_id)


# --- Zones ---
@router.post("/{farm_id}/zones", response_model=ZoneResponse, status_code=201)
async def create_zone(
    farm_id: UUID,
    data: ZoneCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("admin", "farm_manager")),
):
    service = FarmService(db)
    return await service.create_zone(farm_id, data)


@router.get("/{farm_id}/zones", response_model=list[ZoneResponse])
async def list_zones(
    farm_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    service = FarmService(db)
    return await service.get_zones(farm_id)


@router.patch("/{farm_id}/zones/{zone_id}", response_model=ZoneResponse)
async def update_zone(
    farm_id: UUID,
    zone_id: UUID,
    data: ZoneUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("admin", "farm_manager")),
):
    service = FarmService(db)
    return await service.update_zone(zone_id, data)


@router.delete("/{farm_id}/zones/{zone_id}", status_code=204)
async def delete_zone(
    farm_id: UUID,
    zone_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("admin", "farm_manager")),
):
    service = FarmService(db)
    await service.delete_zone(zone_id)


# --- Racks ---
@router.post("/{farm_id}/zones/{zone_id}/racks", response_model=RackResponse, status_code=201)
async def create_rack(
    farm_id: UUID,
    zone_id: UUID,
    data: RackCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("admin", "farm_manager")),
):
    service = FarmService(db)
    return await service.create_rack(zone_id, data)


@router.get("/{farm_id}/zones/{zone_id}/racks", response_model=list[RackResponse])
async def list_racks(
    farm_id: UUID,
    zone_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    service = FarmService(db)
    return await service.get_racks(zone_id)


# --- Trays ---
@router.post("/{farm_id}/racks/{rack_id}/trays", response_model=TrayResponse, status_code=201)
async def create_tray(
    farm_id: UUID,
    rack_id: UUID,
    data: TrayCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("admin", "farm_manager")),
):
    service = FarmService(db)
    return await service.create_tray(rack_id, data)
