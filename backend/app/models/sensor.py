import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import BigInteger, Boolean, ForeignKey, Index, JSON, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, BaseModel, TimestampMixin

if TYPE_CHECKING:
    from app.models.farm import Farm, Zone


class Sensor(BaseModel):
    __tablename__ = "sensors"

    farm_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("farms.id", ondelete="CASCADE"), nullable=False
    )
    zone_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("zones.id", ondelete="SET NULL"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    sensor_type: Mapped[str] = mapped_column(String(50), nullable=False)
    unit: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    mqtt_topic: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    hardware_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    calibration_offset: Mapped[Decimal] = mapped_column(
        Numeric(10, 4), default=0, nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_reading_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    last_value: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4), nullable=True)
    sensor_metadata: Mapped[Optional[dict]] = mapped_column(
        "metadata", JSON, nullable=True
    )

    farm: Mapped["Farm"] = relationship(back_populates="sensors")
    zone: Mapped[Optional["Zone"]] = relationship(back_populates="sensors")
    readings: Mapped[list["SensorReading"]] = relationship(
        back_populates="sensor", cascade="all, delete-orphan"
    )


class SensorReading(Base):
    __tablename__ = "sensor_readings"
    __table_args__ = (
        Index("ix_sensor_readings_sensor_recorded", "sensor_id", "recorded_at"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    sensor_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("sensors.id", ondelete="CASCADE"), nullable=False
    )
    value: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    raw_value: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4), nullable=True)
    recorded_at: Mapped[datetime] = mapped_column(nullable=False)
    received_at: Mapped[datetime] = mapped_column(default=func.now(), nullable=False)

    sensor: Mapped["Sensor"] = relationship(back_populates="readings")
