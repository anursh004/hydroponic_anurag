from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class LightZoneCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    mqtt_topic_command: str | None = None
    fixture_type: str | None = None
    max_intensity_percent: int = Field(100, ge=0, le=100)


class LightZoneUpdate(BaseModel):
    name: str | None = None
    mqtt_topic_command: str | None = None
    fixture_type: str | None = None
    max_intensity_percent: int | None = Field(None, ge=0, le=100)
    is_active: bool | None = None
    current_state: dict | None = None


class LightZoneResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    zone_id: UUID
    name: str
    mqtt_topic_command: str | None = None
    fixture_type: str | None = None
    max_intensity_percent: int
    current_state: dict | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class LightScheduleCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    crop_profile_id: UUID | None = None
    schedule: list[dict]
    spectrum_config: dict | None = None


class LightScheduleUpdate(BaseModel):
    name: str | None = None
    crop_profile_id: UUID | None = None
    schedule: list[dict] | None = None
    spectrum_config: dict | None = None
    is_active: bool | None = None


class LightScheduleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    light_zone_id: UUID
    crop_profile_id: UUID | None = None
    name: str
    schedule: list | dict
    spectrum_config: dict | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class LightCommandRequest(BaseModel):
    action: str  # on, off, set_intensity
    intensity: int | None = Field(None, ge=0, le=100)
    spectrum: dict | None = None
