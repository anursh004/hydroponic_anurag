from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CropProfileCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    scientific_name: str | None = None
    category: str
    days_to_germination: int = Field(..., ge=1)
    days_to_harvest: int = Field(..., ge=1)
    ideal_ph_min: float = Field(..., ge=0, le=14)
    ideal_ph_max: float = Field(..., ge=0, le=14)
    ideal_ec_min: float = Field(..., ge=0)
    ideal_ec_max: float = Field(..., ge=0)
    ideal_temp_min: float = Field(..., ge=-10, le=60)
    ideal_temp_max: float = Field(..., ge=-10, le=60)
    ideal_humidity_min: float = Field(..., ge=0, le=100)
    ideal_humidity_max: float = Field(..., ge=0, le=100)
    ideal_co2_min: int | None = None
    ideal_co2_max: int | None = None
    ideal_light_hours: float | None = Field(None, ge=0, le=24)
    ideal_light_spectrum: dict | None = None
    nutrient_recipe: dict | None = None
    notes: str | None = None
    image_url: str | None = None

    @field_validator("ideal_ph_max")
    @classmethod
    def ph_max_gte_min(cls, v, info):
        if "ideal_ph_min" in info.data and v < info.data["ideal_ph_min"]:
            raise ValueError("ideal_ph_max must be >= ideal_ph_min")
        return v

    @field_validator("ideal_ec_max")
    @classmethod
    def ec_max_gte_min(cls, v, info):
        if "ideal_ec_min" in info.data and v < info.data["ideal_ec_min"]:
            raise ValueError("ideal_ec_max must be >= ideal_ec_min")
        return v

    @field_validator("ideal_temp_max")
    @classmethod
    def temp_max_gte_min(cls, v, info):
        if "ideal_temp_min" in info.data and v < info.data["ideal_temp_min"]:
            raise ValueError("ideal_temp_max must be >= ideal_temp_min")
        return v


class CropProfileUpdate(BaseModel):
    name: str | None = None
    scientific_name: str | None = None
    category: str | None = None
    days_to_germination: int | None = None
    days_to_harvest: int | None = None
    ideal_ph_min: float | None = None
    ideal_ph_max: float | None = None
    ideal_ec_min: float | None = None
    ideal_ec_max: float | None = None
    ideal_temp_min: float | None = None
    ideal_temp_max: float | None = None
    ideal_humidity_min: float | None = None
    ideal_humidity_max: float | None = None
    ideal_co2_min: int | None = None
    ideal_co2_max: int | None = None
    ideal_light_hours: float | None = None
    ideal_light_spectrum: dict | None = None
    nutrient_recipe: dict | None = None
    notes: str | None = None
    image_url: str | None = None


class CropProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    scientific_name: str | None = None
    category: str
    days_to_germination: int
    days_to_harvest: int
    ideal_ph_min: float
    ideal_ph_max: float
    ideal_ec_min: float
    ideal_ec_max: float
    ideal_temp_min: float
    ideal_temp_max: float
    ideal_humidity_min: float
    ideal_humidity_max: float
    ideal_co2_min: int | None = None
    ideal_co2_max: int | None = None
    ideal_light_hours: float | None = None
    ideal_light_spectrum: dict | None = None
    nutrient_recipe: dict | None = None
    notes: str | None = None
    image_url: str | None = None
    is_system_default: bool
    created_by: UUID | None = None
    created_at: datetime
    updated_at: datetime


class CropCycleCreate(BaseModel):
    crop_profile_id: UUID
    zone_id: UUID | None = None
    tray_id: UUID | None = None
    seed_source: str | None = None
    seed_lot_number: str | None = None
    quantity_planted: int = Field(..., ge=1)
    seeded_at: date
    notes: str | None = None


class CropCycleUpdate(BaseModel):
    zone_id: UUID | None = None
    tray_id: UUID | None = None
    seed_source: str | None = None
    seed_lot_number: str | None = None
    status: str | None = None
    notes: str | None = None
    germination_count: int | None = None
    expected_harvest_at: date | None = None
    actual_harvest_at: date | None = None


class CropCycleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    farm_id: UUID
    zone_id: UUID | None = None
    tray_id: UUID | None = None
    crop_profile_id: UUID
    batch_code: str
    seed_source: str | None = None
    seed_lot_number: str | None = None
    quantity_planted: int
    germination_count: int | None = None
    germination_rate: float | None = None
    seeded_at: date
    germinated_at: date | None = None
    transplanted_at: date | None = None
    expected_harvest_at: date | None = None
    actual_harvest_at: date | None = None
    status: str
    notes: str | None = None
    crop_profile: CropProfileResponse | None = None
    created_at: datetime
    updated_at: datetime


class GrowthLogCreate(BaseModel):
    log_date: date
    height_cm: float | None = Field(None, ge=0)
    leaf_count: int | None = Field(None, ge=0)
    health_rating: int = Field(..., ge=1, le=5)
    photo_url: str | None = None
    notes: str | None = None


class GrowthLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    crop_cycle_id: UUID
    logged_by: UUID
    log_date: date
    height_cm: float | None = None
    leaf_count: int | None = None
    health_rating: int
    photo_url: str | None = None
    notes: str | None = None
    created_at: datetime
