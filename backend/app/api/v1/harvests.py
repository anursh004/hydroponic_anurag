"""Harvest management endpoints."""
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_active_user, require_role
from app.models.user import User
from app.schemas.common import PaginatedResponse
from app.schemas.harvest import (
    HarvestCreate, HarvestResponse,
    YieldReportResponse, HarvestCalendarEntry,
)
from app.services.harvest_service import HarvestService

router = APIRouter()


@router.post("/", response_model=HarvestResponse, status_code=201)
async def create_harvest(
    farm_id: UUID,
    data: HarvestCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "farm_manager", "operator")),
):
    service = HarvestService(db)
    return await service.create_harvest(data, current_user.id)


@router.get("/", response_model=PaginatedResponse[HarvestResponse])
async def list_harvests(
    farm_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    service = HarvestService(db)
    harvests, total = await service.get_harvests(farm_id, skip=skip, limit=limit)
    return PaginatedResponse(items=harvests, total=total, skip=skip, limit=limit)


@router.get("/calendar", response_model=list[HarvestCalendarEntry])
async def get_harvest_calendar(
    farm_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    service = HarvestService(db)
    return await service.get_harvest_calendar(farm_id)


@router.get("/yield-report", response_model=list[YieldReportResponse])
async def get_yield_report(
    farm_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    service = HarvestService(db)
    return await service.get_yield_report(farm_id)


@router.get("/monthly-yield")
async def get_monthly_yield(
    farm_id: UUID,
    year: int = Query(..., ge=2020, le=2030),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    service = HarvestService(db)
    return await service.get_monthly_yield(farm_id, year)


@router.get("/{harvest_id}", response_model=HarvestResponse)
async def get_harvest(
    farm_id: UUID,
    harvest_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    service = HarvestService(db)
    return await service.get_harvest(harvest_id)
