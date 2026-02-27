"""Finance and reporting endpoints."""
from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_active_user, require_role
from app.core.constants import CostCategory
from app.models.user import User
from app.schemas.common import PaginatedResponse
from app.schemas.finance import CostCreate, CostResponse
from app.services.finance_service import FinanceService

router = APIRouter()


@router.post("/costs", response_model=CostResponse, status_code=201)
async def create_cost(
    farm_id: UUID,
    data: CostCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("admin", "farm_manager")),
):
    service = FinanceService(db)
    return await service.create_cost(data)


@router.get("/costs", response_model=PaginatedResponse[CostResponse])
async def list_costs(
    farm_id: UUID,
    category: CostCategory | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    service = FinanceService(db)
    costs, total = await service.list_costs(
        farm_id, skip=skip, limit=limit,
        category=category, start_date=start_date, end_date=end_date,
    )
    return PaginatedResponse(items=costs, total=total, skip=skip, limit=limit)


@router.delete("/costs/{cost_id}", status_code=204)
async def delete_cost(
    farm_id: UUID,
    cost_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("admin")),
):
    service = FinanceService(db)
    await service.delete_cost(cost_id)


@router.get("/revenue-summary")
async def get_revenue_summary(
    farm_id: UUID,
    start_date: date | None = None,
    end_date: date | None = None,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("admin", "farm_manager")),
):
    service = FinanceService(db)
    return await service.get_revenue_summary(farm_id, start_date, end_date)


@router.get("/costs-by-category")
async def get_costs_by_category(
    farm_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("admin", "farm_manager")),
):
    service = FinanceService(db)
    return await service.get_costs_by_category(farm_id)


@router.get("/monthly-revenue")
async def get_monthly_revenue(
    farm_id: UUID,
    year: int = Query(..., ge=2020, le=2030),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("admin", "farm_manager")),
):
    service = FinanceService(db)
    return await service.get_monthly_revenue(farm_id, year)


@router.get("/profit-by-crop")
async def get_profit_by_crop(
    farm_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("admin", "farm_manager")),
):
    service = FinanceService(db)
    return await service.get_profit_by_crop(farm_id)
