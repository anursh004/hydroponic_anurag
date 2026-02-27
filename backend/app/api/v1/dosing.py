"""Dosing pump and recipe management endpoints."""
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_active_user, require_role
from app.models.user import User
from app.schemas.common import PaginatedResponse
from app.schemas.dosing import (
    DosingPumpCreate, DosingPumpUpdate, DosingPumpResponse,
    DosingRecipeCreate, DosingRecipeUpdate, DosingRecipeResponse,
    ManualDoseRequest, DosingEventResponse,
)
from app.services.dosing_service import DosingService

router = APIRouter()


# --- Pumps ---
@router.post("/pumps", response_model=DosingPumpResponse, status_code=201)
async def create_pump(
    farm_id: UUID,
    data: DosingPumpCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("admin", "farm_manager")),
):
    service = DosingService(db)
    return await service.create_pump(farm_id, data)


@router.get("/pumps", response_model=list[DosingPumpResponse])
async def list_pumps(
    farm_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    service = DosingService(db)
    return await service.get_pumps(farm_id)


@router.get("/pumps/{pump_id}", response_model=DosingPumpResponse)
async def get_pump(
    farm_id: UUID,
    pump_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    service = DosingService(db)
    return await service.get_pump(pump_id)


@router.patch("/pumps/{pump_id}", response_model=DosingPumpResponse)
async def update_pump(
    farm_id: UUID,
    pump_id: UUID,
    data: DosingPumpUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("admin", "farm_manager")),
):
    service = DosingService(db)
    return await service.update_pump(pump_id, data)


# --- Manual dosing ---
@router.post("/pumps/{pump_id}/dose", response_model=DosingEventResponse, status_code=201)
async def trigger_manual_dose(
    farm_id: UUID,
    pump_id: UUID,
    data: ManualDoseRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "farm_manager", "operator")),
):
    service = DosingService(db)
    return await service.manual_dose(pump_id, data, current_user.id)


# --- Recipes ---
@router.post("/recipes", response_model=DosingRecipeResponse, status_code=201)
async def create_recipe(
    farm_id: UUID,
    data: DosingRecipeCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("admin", "farm_manager")),
):
    service = DosingService(db)
    return await service.create_recipe(farm_id, data)


@router.get("/recipes", response_model=list[DosingRecipeResponse])
async def list_recipes(
    farm_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    service = DosingService(db)
    return await service.get_recipes(farm_id)


@router.patch("/recipes/{recipe_id}", response_model=DosingRecipeResponse)
async def update_recipe(
    farm_id: UUID,
    recipe_id: UUID,
    data: DosingRecipeUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("admin", "farm_manager")),
):
    service = DosingService(db)
    return await service.update_recipe(recipe_id, data)


# --- Dosing Events ---
@router.get("/events", response_model=PaginatedResponse[DosingEventResponse])
async def list_dosing_events(
    farm_id: UUID,
    pump_id: UUID | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    service = DosingService(db)
    events, total = await service.get_events(farm_id, pump_id=pump_id, skip=skip, limit=limit)
    return PaginatedResponse(items=events, total=total, skip=skip, limit=limit)
