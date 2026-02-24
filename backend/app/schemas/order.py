from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CustomerCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    company: str | None = None
    email: str | None = None
    phone: str | None = None
    address: str | None = None
    customer_type: str
    notes: str | None = None


class CustomerUpdate(BaseModel):
    name: str | None = None
    company: str | None = None
    email: str | None = None
    phone: str | None = None
    address: str | None = None
    customer_type: str | None = None
    notes: str | None = None
    is_active: bool | None = None


class CustomerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    farm_id: UUID
    name: str
    company: str | None = None
    email: str | None = None
    phone: str | None = None
    address: str | None = None
    customer_type: str
    notes: str | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class OrderItemCreate(BaseModel):
    crop_profile_id: UUID
    quantity_kg: float = Field(..., gt=0)
    unit_price: float = Field(..., ge=0)


class OrderItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    order_id: UUID
    crop_profile_id: UUID
    quantity_kg: float
    unit_price: float
    total_price: float
    harvest_id: UUID | None = None
    crop_cycle_id: UUID | None = None


class OrderCreate(BaseModel):
    customer_id: UUID
    order_date: date
    delivery_date: date | None = None
    items: list[OrderItemCreate]
    notes: str | None = None


class OrderUpdate(BaseModel):
    status: str | None = None
    delivery_date: date | None = None
    notes: str | None = None


class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    farm_id: UUID
    customer_id: UUID
    order_number: str
    status: str
    order_date: date
    delivery_date: date | None = None
    total_amount: float
    notes: str | None = None
    subscription_id: UUID | None = None
    items: list[OrderItemResponse] = []
    created_at: datetime
    updated_at: datetime


class SubscriptionCreate(BaseModel):
    customer_id: UUID
    frequency: str
    day_of_week: int | None = Field(None, ge=0, le=6)
    items: list[dict]
    start_date: date
    end_date: date | None = None


class SubscriptionUpdate(BaseModel):
    frequency: str | None = None
    day_of_week: int | None = None
    items: list[dict] | None = None
    end_date: date | None = None
    is_active: bool | None = None


class SubscriptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    customer_id: UUID
    frequency: str
    day_of_week: int | None = None
    items: list | dict
    start_date: date
    end_date: date | None = None
    is_active: bool
    next_delivery_date: date
    created_at: datetime
    updated_at: datetime


class InvoiceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    order_id: UUID
    invoice_number: str
    amount: float
    tax_amount: float
    status: str
    due_date: date
    paid_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class TraceabilityResponse(BaseModel):
    order_id: UUID
    order_number: str
    items: list[dict]
