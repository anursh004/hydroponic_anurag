"""Crop profile and cycle management endpoints."""
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_active_user, require_role
from app.core.constants import CropCycleStatus
from app.models.user import User
from app.schemas.common import PaginatedResponse
from app.schemas.crop import (
    CropProfileCreate, CropProfileUpdate, CropProfileResponse,
    CropCycleCreate, CropCycleUpdate, CropCycleResponse,
    GrowthLogCreate, GrowthLogResponse,
)
from app.services.crop_service import CropService

router = APIRouter()


# --- Crop Profiles ---
@router.post("/profiles", response_model=CropProfileResponse, status_code=201)
async def create_profile(
    data: CropProfileCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("admin", "farm_manager")),
):
    service = CropService(db)
    return await service.create_profile(data)


@router.get("/profiles", response_model=list[CropProfileResponse])
async def list_profiles(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    service = CropService(db)
    return await service.get_all_profiles()


@router.get("/profiles/{profile_id}", response_model=CropProfileResponse)
async def get_profile(
    profile_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    service = CropService(db)
    return await service.get_profile(profile_id)


@router.patch("/profiles/{profile_id}", response_model=CropProfileResponse)
async def update_profile(
    profile_id: UUID,
    data: CropProfileUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("admin", "farm_manager")),
):
    service = CropService(db)
    return await service.update_profile(profile_id, data)


@router.delete("/profiles/{profile_id}", status_code=204)
async def delete_profile(
    profile_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("admin")),
):
    service = CropService(db)
    await service.delete_profile(profile_id)


# --- Crop Cycles ---
@router.post("/cycles", response_model=CropCycleResponse, status_code=201)
async def create_cycle(
    data: CropCycleCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("admin", "farm_manager", "operator")),
):
    service = CropService(db)
    return await service.create_cycle(data)


@router.get("/cycles", response_model=PaginatedResponse[CropCycleResponse])
async def list_cycles(
    farm_id: UUID,
    status: CropCycleStatus | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    service = CropService(db)
    cycles, total = await service.get_cycles(farm_id, status=status, skip=skip, limit=limit)
    return PaginatedResponse(items=cycles, total=total, skip=skip, limit=limit)


@router.get("/cycles/{cycle_id}", response_model=CropCycleResponse)
async def get_cycle(
    cycle_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    service = CropService(db)
    return await service.get_cycle(cycle_id)


@router.patch("/cycles/{cycle_id}", response_model=CropCycleResponse)
async def update_cycle(
    cycle_id: UUID,
    data: CropCycleUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("admin", "farm_manager", "operator")),
):
    service = CropService(db)
    return await service.update_cycle(cycle_id, data)


# --- Growth Logs ---
@router.post("/cycles/{cycle_id}/growth-logs", response_model=GrowthLogResponse, status_code=201)
async def add_growth_log(
    cycle_id: UUID,
    data: GrowthLogCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "farm_manager", "operator")),
):
    service = CropService(db)
    return await service.add_growth_log(cycle_id, data, current_user.id)


@router.get("/cycles/{cycle_id}/growth-logs", response_model=list[GrowthLogResponse])
async def list_growth_logs(
    cycle_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    service = CropService(db)
    return await service.get_growth_logs(cycle_id)
