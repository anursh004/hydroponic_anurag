from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class PlantScanCreate(BaseModel):
    crop_cycle_id: UUID | None = None
    zone_id: UUID | None = None
    image_url: str
    scan_type: str = "manual"


class PlantScanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    farm_id: UUID
    crop_cycle_id: UUID | None = None
    zone_id: UUID | None = None
    image_url: str
    scan_type: str
    scanned_by: UUID | None = None
    analysis_status: str
    analysis_result: dict | None = None
    created_at: datetime


class AnomalyDetectionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    plant_scan_id: UUID
    anomaly_type: str
    confidence: float
    bounding_box: dict | None = None
    severity: str
    recommendation: str | None = None
    created_at: datetime


class AIAdvisoryResponse(BaseModel):
    recommendations: list[dict]
    yield_predictions: list[dict]
    environmental_suggestions: list[dict]
