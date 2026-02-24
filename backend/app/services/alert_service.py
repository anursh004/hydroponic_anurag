import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.alert import Alert, AlertRule
from app.models.sensor import Sensor, SensorReading
from app.models.user import User
from app.repositories.alert_repo import AlertRepository, AlertRuleRepository


class AlertService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.rule_repo = AlertRuleRepository(db)
        self.alert_repo = AlertRepository(db)

    # Rules
    async def create_rule(self, farm_id: uuid.UUID, data: dict) -> AlertRule:
        data["farm_id"] = farm_id
        return await self.rule_repo.create(data)

    async def update_rule(self, rule_id: uuid.UUID, data: dict) -> AlertRule:
        rule = await self.rule_repo.update(rule_id, data)
        if not rule:
            raise NotFoundException(detail="Alert rule not found")
        return rule

    async def delete_rule(self, rule_id: uuid.UUID) -> None:
        if not await self.rule_repo.delete(rule_id):
            raise NotFoundException(detail="Alert rule not found")

    async def list_rules(self, farm_id: uuid.UUID) -> list[AlertRule]:
        return await self.rule_repo.get_multi(limit=1000, farm_id=farm_id)

    # Alert evaluation
    async def evaluate_reading(
        self, sensor: Sensor, reading: SensorReading
    ) -> list[Alert]:
        rules = await self.rule_repo.get_active_rules_for_sensor_type(
            sensor.farm_id, sensor.sensor_type
        )
        triggered = []
        for rule in rules:
            if self._is_threshold_violated(reading.value, rule):
                recent = await self.alert_repo.get_recent_alert_for_rule(
                    rule.id, rule.cooldown_minutes
                )
                if recent is None:
                    alert = await self.alert_repo.create(
                        {
                            "alert_rule_id": rule.id,
                            "sensor_id": sensor.id,
                            "sensor_reading_id": reading.id,
                            "severity": rule.severity,
                            "title": f"{sensor.sensor_type.upper()} alert on {sensor.name}",
                            "message": f"Value {reading.value} violated threshold (rule: {rule.condition})",
                            "triggered_value": reading.value,
                            "status": "active",
                        }
                    )
                    triggered.append(alert)
        return triggered

    def _is_threshold_violated(self, value: Decimal, rule: AlertRule) -> bool:
        val = float(value)
        if rule.condition == "above" and rule.threshold_max is not None:
            return val > float(rule.threshold_max)
        if rule.condition == "below" and rule.threshold_min is not None:
            return val < float(rule.threshold_min)
        if rule.condition == "outside_range":
            if rule.threshold_min is not None and rule.threshold_max is not None:
                return val < float(rule.threshold_min) or val > float(rule.threshold_max)
        return False

    # Alert management
    async def list_alerts(
        self, farm_id: uuid.UUID, status: str | None = None, severity: str | None = None
    ) -> list[Alert]:
        if status == "active":
            return await self.alert_repo.get_active_alerts(farm_id, severity)
        return await self.alert_repo.get_multi(limit=100)

    async def get_alert(self, alert_id: uuid.UUID) -> Alert:
        alert = await self.alert_repo.get_by_id(alert_id)
        if not alert:
            raise NotFoundException(detail="Alert not found")
        return alert

    async def acknowledge_alert(self, alert_id: uuid.UUID, user: User) -> Alert:
        alert = await self.get_alert(alert_id)
        alert.status = "acknowledged"
        alert.acknowledged_by = user.id
        alert.acknowledged_at = datetime.now(timezone.utc)
        await self.db.flush()
        await self.db.refresh(alert)
        return alert

    async def resolve_alert(self, alert_id: uuid.UUID) -> Alert:
        alert = await self.get_alert(alert_id)
        alert.status = "resolved"
        alert.resolved_at = datetime.now(timezone.utc)
        await self.db.flush()
        await self.db.refresh(alert)
        return alert

    async def count_active(self, farm_id: uuid.UUID) -> int:
        return await self.alert_repo.count_active(farm_id)

    async def count_critical(self, farm_id: uuid.UUID) -> int:
        return await self.alert_repo.count_active(farm_id, severity="critical")
