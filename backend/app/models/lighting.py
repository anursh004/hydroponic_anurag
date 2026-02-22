import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.crop import CropProfile
    from app.models.farm import Zone


class LightZone(BaseModel):
    __tablename__ = "light_zones"

    zone_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("zones.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    mqtt_topic_command: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    fixture_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    max_intensity_percent: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    current_state: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    zone: Mapped["Zone"] = relationship(foreign_keys=[zone_id])
    schedules: Mapped[list["LightSchedule"]] = relationship(
        back_populates="light_zone", cascade="all, delete-orphan"
    )


class LightSchedule(BaseModel):
    __tablename__ = "light_schedules"

    light_zone_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("light_zones.id", ondelete="CASCADE"), nullable=False
    )
    crop_profile_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("crop_profiles.id", ondelete="SET NULL"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    schedule: Mapped[dict] = mapped_column(JSON, nullable=False)
    spectrum_config: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    light_zone: Mapped["LightZone"] = relationship(back_populates="schedules")
    crop_profile: Mapped[Optional["CropProfile"]] = relationship(foreign_keys=[crop_profile_id])
