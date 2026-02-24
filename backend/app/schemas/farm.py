from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class FarmCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    location: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    timezone: str = "UTC"
    settings: dict | None = None


class FarmUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    location: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    timezone: str | None = None
    settings: dict | None = None
    is_active: bool | None = None


class FarmResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    location: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    timezone: str
    owner_id: UUID
    settings: dict | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ZoneCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    zone_type: str | None = None
    position_x: int = 0
    position_y: int = 0
    width: int = 100
    height: int = 100
    environment_type: str | None = None


class ZoneUpdate(BaseModel):
    name: str | None = None
    zone_type: str | None = None
    position_x: int | None = None
    position_y: int | None = None
    width: int | None = None
    height: int | None = None
    environment_type: str | None = None


class ZoneResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    farm_id: UUID
    name: str
    zone_type: str | None = None
    position_x: int
    position_y: int
    width: int
    height: int
    environment_type: str | None = None
    created_at: datetime
    updated_at: datetime


class RackCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    levels: int = Field(1, ge=1)
    position_index: int | None = None


class RackUpdate(BaseModel):
    name: str | None = None
    levels: int | None = Field(None, ge=1)
    position_index: int | None = None


class RackResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    zone_id: UUID
    name: str
    levels: int
    position_index: int | None = None
    created_at: datetime
    updated_at: datetime


class TrayCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    level: int
    capacity: int = Field(..., ge=1)
    current_crop_cycle_id: UUID | None = None


class TrayUpdate(BaseModel):
    name: str | None = None
    level: int | None = None
    capacity: int | None = Field(None, ge=1)
    current_crop_cycle_id: UUID | None = None


class TrayResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    rack_id: UUID
    name: str
    level: int
    capacity: int
    current_crop_cycle_id: UUID | None = None
    created_at: datetime
    updated_at: datetime
