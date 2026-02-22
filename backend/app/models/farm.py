import uuid
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, ForeignKey, Integer, JSON, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.models.user import user_farms

if TYPE_CHECKING:
    from app.models.sensor import Sensor
    from app.models.user import User


class Farm(BaseModel):
    __tablename__ = "farms"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    location: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    latitude: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 8), nullable=True)
    longitude: Mapped[Optional[Decimal]] = mapped_column(Numeric(11, 8), nullable=True)
    timezone: Mapped[str] = mapped_column(String(50), default="UTC", nullable=False)
    owner_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    settings: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    owner: Mapped["User"] = relationship(foreign_keys=[owner_id])
    users: Mapped[list["User"]] = relationship(
        secondary=user_farms, back_populates="farms"
    )
    zones: Mapped[list["Zone"]] = relationship(back_populates="farm", cascade="all, delete-orphan")
    sensors: Mapped[list["Sensor"]] = relationship(back_populates="farm", cascade="all, delete-orphan")


class Zone(BaseModel):
    __tablename__ = "zones"

    farm_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("farms.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    zone_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    position_x: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    position_y: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    width: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    height: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    environment_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    farm: Mapped["Farm"] = relationship(back_populates="zones")
    racks: Mapped[list["Rack"]] = relationship(back_populates="zone", cascade="all, delete-orphan")
    sensors: Mapped[list["Sensor"]] = relationship(back_populates="zone")


class Rack(BaseModel):
    __tablename__ = "racks"

    zone_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("zones.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    levels: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    position_index: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    zone: Mapped["Zone"] = relationship(back_populates="racks")
    trays: Mapped[list["Tray"]] = relationship(back_populates="rack", cascade="all, delete-orphan")


class Tray(BaseModel):
    __tablename__ = "trays"

    rack_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("racks.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    level: Mapped[int] = mapped_column(Integer, nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    current_crop_cycle_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("crop_cycles.id", ondelete="SET NULL"), nullable=True
    )

    rack: Mapped["Rack"] = relationship(back_populates="trays")
