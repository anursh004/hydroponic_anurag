from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CostCreate(BaseModel):
    category: str
    description: str = Field(..., min_length=1, max_length=255)
    amount: float = Field(..., gt=0)
    date: date
    crop_cycle_id: UUID | None = None
    zone_id: UUID | None = None


class CostUpdate(BaseModel):
    category: str | None = None
    description: str | None = None
    amount: float | None = Field(None, gt=0)
    date: date | None = None
    crop_cycle_id: UUID | None = None
    zone_id: UUID | None = None


class CostResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    farm_id: UUID
    category: str
    description: str
    amount: float
    date: date
    crop_cycle_id: UUID | None = None
    zone_id: UUID | None = None
    created_by: UUID
    created_at: datetime


class RevenueDashboardResponse(BaseModel):
    total_revenue: float
    total_costs: float
    net_profit: float
    profit_margin: float
    revenue_by_month: list[dict]
    costs_by_category: list[dict]
    profit_by_crop: list[dict]


class ProfitByCropResponse(BaseModel):
    crop_name: str
    revenue: float
    costs: float
    profit: float
    margin: float
    cycles: int
