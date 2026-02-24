from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SensorCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    sensor_type: str = Field(..., min_length=1)
    unit: str | None = None
    zone_id: UUID | None = None
    mqtt_topic: str | None = None
    hardware_id: str | None = None
    calibration_offset: float = 0
    metadata: dict | None = None


class SensorUpdate(BaseModel):
    name: str | None = None
    sensor_type: str | None = None
    unit: str | None = None
    zone_id: UUID | None = None
    mqtt_topic: str | None = None
    calibration_offset: float | None = None
    is_active: bool | None = None
    metadata: dict | None = None


class SensorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    farm_id: UUID
    zone_id: UUID | None = None
    name: str
    sensor_type: str
    unit: str | None = None
    mqtt_topic: str | None = None
    hardware_id: str | None = None
    calibration_offset: float
    is_active: bool
    last_reading_at: datetime | None = None
    last_value: float | None = None
    created_at: datetime
    updated_at: datetime


class SensorReadingCreate(BaseModel):
    value: float
    raw_value: float | None = None
    recorded_at: datetime


class SensorReadingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sensor_id: UUID
    value: float
    raw_value: float | None = None
    recorded_at: datetime
    received_at: datetime


class SensorSummaryResponse(BaseModel):
    sensor_id: UUID
    sensor_type: str
    name: str
    latest_value: float | None = None
    latest_reading_at: datetime | None = None
    status: str = "normal"
    zone_name: str | None = None
