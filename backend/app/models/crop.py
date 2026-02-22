import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Date, ForeignKey, Integer, JSON, Numeric, String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.farm import Farm, Zone
    from app.models.harvest import Harvest
    from app.models.user import User


class CropProfile(BaseModel):
    __tablename__ = "crop_profiles"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    scientific_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    days_to_germination: Mapped[int] = mapped_column(Integer, nullable=False)
    days_to_harvest: Mapped[int] = mapped_column(Integer, nullable=False)

    # Ideal ranges
    ideal_ph_min: Mapped[Decimal] = mapped_column(Numeric(4, 2), nullable=False)
    ideal_ph_max: Mapped[Decimal] = mapped_column(Numeric(4, 2), nullable=False)
    ideal_ec_min: Mapped[Decimal] = mapped_column(Numeric(4, 2), nullable=False)
    ideal_ec_max: Mapped[Decimal] = mapped_column(Numeric(4, 2), nullable=False)
    ideal_temp_min: Mapped[Decimal] = mapped_column(Numeric(4, 1), nullable=False)
    ideal_temp_max: Mapped[Decimal] = mapped_column(Numeric(4, 1), nullable=False)
    ideal_humidity_min: Mapped[Decimal] = mapped_column(Numeric(4, 1), nullable=False)
    ideal_humidity_max: Mapped[Decimal] = mapped_column(Numeric(4, 1), nullable=False)
    ideal_co2_min: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    ideal_co2_max: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    ideal_light_hours: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 1), nullable=True)
    ideal_light_spectrum: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    nutrient_recipe: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    is_system_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    crop_cycles: Mapped[list["CropCycle"]] = relationship(back_populates="crop_profile")


class CropCycle(BaseModel):
    __tablename__ = "crop_cycles"

    farm_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("farms.id", ondelete="CASCADE"), nullable=False
    )
    zone_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("zones.id", ondelete="SET NULL"), nullable=True
    )
    tray_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("trays.id", ondelete="SET NULL"), nullable=True
    )
    crop_profile_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("crop_profiles.id", ondelete="CASCADE"), nullable=False
    )
    batch_code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    seed_source: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    seed_lot_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    quantity_planted: Mapped[int] = mapped_column(Integer, nullable=False)
    germination_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    germination_rate: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)

    seeded_at: Mapped[date] = mapped_column(Date, nullable=False)
    germinated_at: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    transplanted_at: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    expected_harvest_at: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    actual_harvest_at: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    status: Mapped[str] = mapped_column(String(50), default="seeded", nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    crop_profile: Mapped["CropProfile"] = relationship(back_populates="crop_cycles")
    farm: Mapped["Farm"] = relationship(foreign_keys=[farm_id])
    zone: Mapped[Optional["Zone"]] = relationship(foreign_keys=[zone_id])
    growth_logs: Mapped[list["GrowthLog"]] = relationship(
        back_populates="crop_cycle", cascade="all, delete-orphan"
    )
    harvests: Mapped[list["Harvest"]] = relationship(back_populates="crop_cycle")


class GrowthLog(BaseModel):
    __tablename__ = "growth_logs"

    crop_cycle_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("crop_cycles.id", ondelete="CASCADE"), nullable=False
    )
    logged_by: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    log_date: Mapped[date] = mapped_column(Date, nullable=False)
    height_cm: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 2), nullable=True)
    leaf_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    health_rating: Mapped[int] = mapped_column(Integer, nullable=False)
    photo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    crop_cycle: Mapped["CropCycle"] = relationship(back_populates="growth_logs")
    user: Mapped["User"] = relationship(foreign_keys=[logged_by])
