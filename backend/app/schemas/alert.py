from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class AlertRuleCreate(BaseModel):
    sensor_type: str
    condition: str
    threshold_min: float | None = None
    threshold_max: float | None = None
    severity: str = "warning"
    zone_id: UUID | None = None
    cooldown_minutes: int = Field(15, ge=1)
    notify_channels: list[str] | None = None
    escalation_policy_id: UUID | None = None

    @model_validator(mode="after")
    def validate_thresholds(self):
        if self.condition == "above" and self.threshold_max is None:
            raise ValueError("threshold_max required when condition is 'above'")
        if self.condition == "below" and self.threshold_min is None:
            raise ValueError("threshold_min required when condition is 'below'")
        if self.condition == "outside_range":
            if self.threshold_min is None or self.threshold_max is None:
                raise ValueError("Both threshold_min and threshold_max required for 'outside_range'")
        return self


class AlertRuleUpdate(BaseModel):
    sensor_type: str | None = None
    condition: str | None = None
    threshold_min: float | None = None
    threshold_max: float | None = None
    severity: str | None = None
    zone_id: UUID | None = None
    cooldown_minutes: int | None = None
    is_active: bool | None = None
    notify_channels: list[str] | None = None
    escalation_policy_id: UUID | None = None


class AlertRuleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    farm_id: UUID
    zone_id: UUID | None = None
    sensor_type: str
    condition: str
    threshold_min: float | None = None
    threshold_max: float | None = None
    severity: str
    cooldown_minutes: int
    is_active: bool
    notify_channels: list | None = None
    escalation_policy_id: UUID | None = None
    created_at: datetime
    updated_at: datetime


class AlertResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    alert_rule_id: UUID
    sensor_id: UUID
    sensor_reading_id: int | None = None
    severity: str
    title: str
    message: str | None = None
    triggered_value: float
    status: str
    acknowledged_by: UUID | None = None
    acknowledged_at: datetime | None = None
    resolved_at: datetime | None = None
    created_at: datetime


class AlertAcknowledge(BaseModel):
    notes: str | None = None


class EscalationPolicyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    steps: list[dict]


class EscalationPolicyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    farm_id: UUID
    steps: list | dict
    created_at: datetime
    updated_at: datetime
