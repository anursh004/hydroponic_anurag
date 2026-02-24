from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class InventoryItemCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    category: str
    sku: str | None = None
    unit: str
    current_stock: float = 0
    reorder_threshold: float | None = None
    reorder_quantity: float | None = None
    unit_cost: float | None = None
    supplier: str | None = None
    notes: str | None = None


class InventoryItemUpdate(BaseModel):
    name: str | None = None
    category: str | None = None
    sku: str | None = None
    unit: str | None = None
    reorder_threshold: float | None = None
    reorder_quantity: float | None = None
    unit_cost: float | None = None
    supplier: str | None = None
    notes: str | None = None


class InventoryItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    farm_id: UUID
    name: str
    category: str
    sku: str | None = None
    unit: str
    current_stock: float
    reorder_threshold: float | None = None
    reorder_quantity: float | None = None
    unit_cost: float | None = None
    supplier: str | None = None
    notes: str | None = None
    created_at: datetime
    updated_at: datetime


class StockTransactionCreate(BaseModel):
    transaction_type: str
    quantity: float
    reference: str | None = None


class StockTransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    inventory_item_id: UUID
    transaction_type: str
    quantity: float
    reference: str | None = None
    performed_by: UUID
    created_at: datetime
