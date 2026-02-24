from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DosingPumpCreate(BaseModel):
    name: str = Field(..., min_length=1)
    pump_type: str
    zone_id: UUID | None = None
    mqtt_topic_command: str | None = None
    mqtt_topic_status: str | None = None
    ml_per_second: float = Field(..., gt=0)


class DosingPumpUpdate(BaseModel):
    name: str | None = None
    pump_type: str | None = None
    zone_id: UUID | None = None
    mqtt_topic_command: str | None = None
    mqtt_topic_status: str | None = None
    ml_per_second: float | None = Field(None, gt=0)
    is_active: bool | None = None


class DosingPumpResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    farm_id: UUID
    zone_id: UUID | None = None
    name: str
    pump_type: str
    mqtt_topic_command: str | None = None
    mqtt_topic_status: str | None = None
    ml_per_second: float
    is_active: bool
    last_dose_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class DosingRecipeCreate(BaseModel):
    name: str = Field(..., min_length=1)
    crop_profile_id: UUID | None = None
    growth_stage: str | None = None
    target_ph_min: float = Field(..., ge=0, le=14)
    target_ph_max: float = Field(..., ge=0, le=14)
    target_ec: float = Field(..., ge=0)
    nutrient_ratios: dict | None = None


class DosingRecipeUpdate(BaseModel):
    name: str | None = None
    crop_profile_id: UUID | None = None
    growth_stage: str | None = None
    target_ph_min: float | None = None
    target_ph_max: float | None = None
    target_ec: float | None = None
    nutrient_ratios: dict | None = None
    is_active: bool | None = None


class DosingRecipeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    crop_profile_id: UUID | None = None
    growth_stage: str | None = None
    target_ph_min: float
    target_ph_max: float
    target_ec: float
    nutrient_ratios: dict | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ManualDoseRequest(BaseModel):
    volume_ml: float = Field(..., gt=0)


class DosingEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    pump_id: UUID
    recipe_id: UUID | None = None
    trigger: str
    volume_ml: float
    duration_seconds: float
    sensor_reading_before: float
    sensor_reading_after: float | None = None
    status: str
    initiated_by: UUID | None = None
    created_at: datetime
