"""Inventory management endpoints."""
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_active_user, require_role
from app.core.constants import InventoryCategory
from app.models.user import User
from app.schemas.common import PaginatedResponse
from app.schemas.inventory import (
    InventoryItemCreate, InventoryItemUpdate, InventoryItemResponse,
    StockTransactionCreate, StockTransactionResponse,
)
from app.services.inventory_service import InventoryService

router = APIRouter()


@router.post("/items", response_model=InventoryItemResponse, status_code=201)
async def create_item(
    farm_id: UUID,
    data: InventoryItemCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("admin", "farm_manager")),
):
    service = InventoryService(db)
    return await service.create_item(farm_id, data)


@router.get("/items", response_model=PaginatedResponse[InventoryItemResponse])
async def list_items(
    farm_id: UUID,
    category: InventoryCategory | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    service = InventoryService(db)
    items, total = await service.get_items(farm_id, category=category, skip=skip, limit=limit)
    return PaginatedResponse(items=items, total=total, skip=skip, limit=limit)


@router.get("/items/low-stock", response_model=list[InventoryItemResponse])
async def get_low_stock(
    farm_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    service = InventoryService(db)
    return await service.get_low_stock(farm_id)


@router.get("/items/{item_id}", response_model=InventoryItemResponse)
async def get_item(
    farm_id: UUID,
    item_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    service = InventoryService(db)
    return await service.get_item(item_id)


@router.patch("/items/{item_id}", response_model=InventoryItemResponse)
async def update_item(
    farm_id: UUID,
    item_id: UUID,
    data: InventoryItemUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("admin", "farm_manager")),
):
    service = InventoryService(db)
    return await service.update_item(item_id, data)


@router.delete("/items/{item_id}", status_code=204)
async def delete_item(
    farm_id: UUID,
    item_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("admin")),
):
    service = InventoryService(db)
    await service.delete_item(item_id)


# --- Transactions ---
@router.post("/items/{item_id}/transactions", response_model=StockTransactionResponse, status_code=201)
async def create_transaction(
    farm_id: UUID,
    item_id: UUID,
    data: StockTransactionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "farm_manager", "operator")),
):
    service = InventoryService(db)
    return await service.create_transaction(item_id, data, current_user.id)


@router.get("/items/{item_id}/transactions", response_model=list[StockTransactionResponse])
async def list_transactions(
    farm_id: UUID,
    item_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    service = InventoryService(db)
    return await service.get_transactions(item_id, skip=skip, limit=limit)
