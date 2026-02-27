"""Order, customer, subscription, and invoice endpoints."""
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_active_user, require_role
from app.core.constants import OrderStatus
from app.models.user import User
from app.schemas.common import PaginatedResponse
from app.schemas.order import (
    CustomerCreate, CustomerUpdate, CustomerResponse,
    OrderCreate, OrderUpdate, OrderResponse,
    SubscriptionCreate, SubscriptionUpdate, SubscriptionResponse,
    InvoiceResponse, TraceabilityResponse,
)
from app.services.order_service import OrderService

router = APIRouter()


# --- Customers ---
@router.post("/customers", response_model=CustomerResponse, status_code=201)
async def create_customer(
    farm_id: UUID,
    data: CustomerCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("admin", "farm_manager")),
):
    service = OrderService(db)
    return await service.create_customer(farm_id, data)


@router.get("/customers", response_model=PaginatedResponse[CustomerResponse])
async def list_customers(
    farm_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    service = OrderService(db)
    customers, total = await service.get_customers(farm_id, skip=skip, limit=limit)
    return PaginatedResponse(items=customers, total=total, skip=skip, limit=limit)


@router.get("/customers/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    farm_id: UUID,
    customer_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    service = OrderService(db)
    return await service.get_customer(customer_id)


@router.patch("/customers/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    farm_id: UUID,
    customer_id: UUID,
    data: CustomerUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("admin", "farm_manager")),
):
    service = OrderService(db)
    return await service.update_customer(customer_id, data)


# --- Orders ---
@router.post("/", response_model=OrderResponse, status_code=201)
async def create_order(
    farm_id: UUID,
    data: OrderCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "farm_manager", "operator")),
):
    service = OrderService(db)
    return await service.create_order(farm_id, data, current_user.id)


@router.get("/", response_model=PaginatedResponse[OrderResponse])
async def list_orders(
    farm_id: UUID,
    status: OrderStatus | None = None,
    customer_id: UUID | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    service = OrderService(db)
    orders, total = await service.get_orders(
        farm_id, status=status, customer_id=customer_id, skip=skip, limit=limit
    )
    return PaginatedResponse(items=orders, total=total, skip=skip, limit=limit)


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    farm_id: UUID,
    order_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    service = OrderService(db)
    return await service.get_order(order_id)


@router.patch("/{order_id}", response_model=OrderResponse)
async def update_order(
    farm_id: UUID,
    order_id: UUID,
    data: OrderUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("admin", "farm_manager")),
):
    service = OrderService(db)
    return await service.update_order(order_id, data)


@router.get("/{order_id}/traceability", response_model=list[TraceabilityResponse])
async def get_traceability(
    farm_id: UUID,
    order_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    service = OrderService(db)
    return await service.get_traceability(order_id)


# --- Subscriptions ---
@router.post("/subscriptions", response_model=SubscriptionResponse, status_code=201)
async def create_subscription(
    farm_id: UUID,
    data: SubscriptionCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("admin", "farm_manager")),
):
    service = OrderService(db)
    return await service.create_subscription(farm_id, data)


@router.get("/subscriptions", response_model=list[SubscriptionResponse])
async def list_subscriptions(
    farm_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    service = OrderService(db)
    return await service.get_subscriptions(farm_id)


@router.patch("/subscriptions/{sub_id}", response_model=SubscriptionResponse)
async def update_subscription(
    farm_id: UUID,
    sub_id: UUID,
    data: SubscriptionUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("admin", "farm_manager")),
):
    service = OrderService(db)
    return await service.update_subscription(sub_id, data)


# --- Invoices ---
@router.post("/{order_id}/invoices", response_model=InvoiceResponse, status_code=201)
async def create_invoice(
    farm_id: UUID,
    order_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("admin", "farm_manager")),
):
    service = OrderService(db)
    return await service.create_invoice(order_id)


@router.get("/{order_id}/invoices", response_model=list[InvoiceResponse])
async def list_invoices(
    farm_id: UUID,
    order_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    service = OrderService(db)
    return await service.get_invoices(order_id)
