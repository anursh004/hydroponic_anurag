import uuid
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Date, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.crop import CropCycle, CropProfile
    from app.models.farm import Zone
    from app.models.user import User


class Harvest(BaseModel):
    __tablename__ = "harvests"

    crop_cycle_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("crop_cycles.id", ondelete="CASCADE"), nullable=False
    )
    harvested_by: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    harvest_date: Mapped[date] = mapped_column(Date, nullable=False)
    weight_kg: Mapped[Decimal] = mapped_column(Numeric(8, 3), nullable=False)
    grade: Mapped[str] = mapped_column(String(20), default="A", nullable=False)
    quality_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    photo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    waste_kg: Mapped[Decimal] = mapped_column(Numeric(8, 3), default=0, nullable=False)

    crop_cycle: Mapped["CropCycle"] = relationship(back_populates="harvests")
    harvester: Mapped["User"] = relationship(foreign_keys=[harvested_by])


class YieldTarget(BaseModel):
    __tablename__ = "yield_targets"

    crop_profile_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("crop_profiles.id", ondelete="CASCADE"), nullable=False
    )
    zone_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("zones.id", ondelete="SET NULL"), nullable=True
    )
    expected_yield_kg_per_sqm: Mapped[Decimal] = mapped_column(Numeric(8, 3), nullable=False)
    target_cycle_days: Mapped[int] = mapped_column(Integer, nullable=False)

    crop_profile: Mapped["CropProfile"] = relationship(foreign_keys=[crop_profile_id])
    zone: Mapped[Optional["Zone"]] = relationship(foreign_keys=[zone_id])
