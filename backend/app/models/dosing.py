import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, ForeignKey, JSON, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.crop import CropProfile
    from app.models.farm import Farm, Zone
    from app.models.user import User


class DosingPump(BaseModel):
    __tablename__ = "dosing_pumps"

    farm_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("farms.id", ondelete="CASCADE"), nullable=False
    )
    zone_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("zones.id", ondelete="SET NULL"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    pump_type: Mapped[str] = mapped_column(String(50), nullable=False)
    mqtt_topic_command: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    mqtt_topic_status: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    ml_per_second: Mapped[Decimal] = mapped_column(Numeric(6, 2), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_dose_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    farm: Mapped["Farm"] = relationship(foreign_keys=[farm_id])
    zone: Mapped[Optional["Zone"]] = relationship(foreign_keys=[zone_id])
    dosing_events: Mapped[list["DosingEvent"]] = relationship(back_populates="pump")


class DosingRecipe(BaseModel):
    __tablename__ = "dosing_recipes"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    crop_profile_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("crop_profiles.id", ondelete="SET NULL"), nullable=True
    )
    growth_stage: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    target_ph_min: Mapped[Decimal] = mapped_column(Numeric(4, 2), nullable=False)
    target_ph_max: Mapped[Decimal] = mapped_column(Numeric(4, 2), nullable=False)
    target_ec: Mapped[Decimal] = mapped_column(Numeric(4, 2), nullable=False)
    nutrient_ratios: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    crop_profile: Mapped[Optional["CropProfile"]] = relationship(foreign_keys=[crop_profile_id])
    dosing_events: Mapped[list["DosingEvent"]] = relationship(back_populates="recipe")


class DosingEvent(BaseModel):
    __tablename__ = "dosing_events"

    pump_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("dosing_pumps.id", ondelete="CASCADE"), nullable=False
    )
    recipe_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("dosing_recipes.id", ondelete="SET NULL"), nullable=True
    )
    trigger: Mapped[str] = mapped_column(String(50), nullable=False)
    volume_ml: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False)
    duration_seconds: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False)
    sensor_reading_before: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    sensor_reading_after: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)
    initiated_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    pump: Mapped["DosingPump"] = relationship(back_populates="dosing_events")
    recipe: Mapped[Optional["DosingRecipe"]] = relationship(back_populates="dosing_events")
    initiator: Mapped[Optional["User"]] = relationship(foreign_keys=[initiated_by])
