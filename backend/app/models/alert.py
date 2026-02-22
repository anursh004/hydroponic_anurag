import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import BigInteger, Boolean, ForeignKey, Integer, JSON, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.farm import Farm
    from app.models.sensor import Sensor
    from app.models.user import User


class EscalationPolicy(BaseModel):
    __tablename__ = "escalation_policies"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    farm_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("farms.id", ondelete="CASCADE"), nullable=False
    )
    steps: Mapped[dict] = mapped_column(JSON, nullable=False)

    farm: Mapped["Farm"] = relationship(foreign_keys=[farm_id])
    alert_rules: Mapped[list["AlertRule"]] = relationship(back_populates="escalation_policy")


class AlertRule(BaseModel):
    __tablename__ = "alert_rules"

    farm_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("farms.id", ondelete="CASCADE"), nullable=False
    )
    zone_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("zones.id", ondelete="SET NULL"), nullable=True
    )
    sensor_type: Mapped[str] = mapped_column(String(50), nullable=False)
    condition: Mapped[str] = mapped_column(String(20), nullable=False)
    threshold_min: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4), nullable=True)
    threshold_max: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4), nullable=True)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    cooldown_minutes: Mapped[int] = mapped_column(Integer, default=15, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notify_channels: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    escalation_policy_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("escalation_policies.id", ondelete="SET NULL"), nullable=True
    )

    farm: Mapped["Farm"] = relationship(foreign_keys=[farm_id])
    escalation_policy: Mapped[Optional["EscalationPolicy"]] = relationship(
        back_populates="alert_rules"
    )
    alerts: Mapped[list["Alert"]] = relationship(back_populates="alert_rule")


class Alert(BaseModel):
    __tablename__ = "alerts"

    alert_rule_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("alert_rules.id", ondelete="CASCADE"), nullable=False
    )
    sensor_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("sensors.id", ondelete="CASCADE"), nullable=False
    )
    sensor_reading_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    triggered_value: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)
    acknowledged_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    acknowledged_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    alert_rule: Mapped["AlertRule"] = relationship(back_populates="alerts")
    sensor: Mapped["Sensor"] = relationship(foreign_keys=[sensor_id])
    acknowledger: Mapped[Optional["User"]] = relationship(foreign_keys=[acknowledged_by])
