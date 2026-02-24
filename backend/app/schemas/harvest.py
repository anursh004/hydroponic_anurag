from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class HarvestCreate(BaseModel):
    harvest_date: date
    weight_kg: float = Field(..., gt=0)
    grade: str = "A"
    quality_notes: str | None = None
    photo_url: str | None = None
    waste_kg: float = Field(0, ge=0)


class HarvestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    crop_cycle_id: UUID
    harvested_by: UUID
    harvest_date: date
    weight_kg: float
    grade: str
    quality_notes: str | None = None
    photo_url: str | None = None
    waste_kg: float
    created_at: datetime


class YieldTargetCreate(BaseModel):
    crop_profile_id: UUID
    zone_id: UUID | None = None
    expected_yield_kg_per_sqm: float = Field(..., gt=0)
    target_cycle_days: int = Field(..., ge=1)


class YieldTargetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    crop_profile_id: UUID
    zone_id: UUID | None = None
    expected_yield_kg_per_sqm: float
    target_cycle_days: int
    created_at: datetime
    updated_at: datetime


class YieldReportResponse(BaseModel):
    crop_name: str
    zone_name: str | None = None
    total_harvested_kg: float
    expected_kg: float
    variance_percent: float
    cycle_count: int


class HarvestCalendarEntry(BaseModel):
    date: date
    crop_name: str
    batch_code: str
    expected_kg: float | None = None
    is_actual: bool
    crop_cycle_id: UUID
