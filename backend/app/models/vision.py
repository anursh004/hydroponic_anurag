import uuid
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, JSON, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.crop import CropCycle
    from app.models.farm import Farm, Zone
    from app.models.user import User


class PlantScan(BaseModel):
    __tablename__ = "plant_scans"

    farm_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("farms.id", ondelete="CASCADE"), nullable=False
    )
    crop_cycle_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("crop_cycles.id", ondelete="SET NULL"), nullable=True
    )
    zone_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("zones.id", ondelete="SET NULL"), nullable=True
    )
    image_url: Mapped[str] = mapped_column(String(500), nullable=False)
    scan_type: Mapped[str] = mapped_column(String(50), default="manual", nullable=False)
    scanned_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    analysis_status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)
    analysis_result: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    farm: Mapped["Farm"] = relationship(foreign_keys=[farm_id])
    anomalies: Mapped[list["AnomalyDetection"]] = relationship(
        back_populates="plant_scan", cascade="all, delete-orphan"
    )


class AnomalyDetection(BaseModel):
    __tablename__ = "anomaly_detections"

    plant_scan_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("plant_scans.id", ondelete="CASCADE"), nullable=False
    )
    anomaly_type: Mapped[str] = mapped_column(String(50), nullable=False)
    confidence: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False)
    bounding_box: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    recommendation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    plant_scan: Mapped["PlantScan"] = relationship(back_populates="anomalies")
