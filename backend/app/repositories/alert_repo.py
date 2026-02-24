import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alert import Alert, AlertRule, EscalationPolicy
from app.repositories.base import BaseRepository


class AlertRuleRepository(BaseRepository[AlertRule]):
    def __init__(self, db: AsyncSession):
        super().__init__(AlertRule, db)

    async def get_active_rules_for_sensor_type(
        self, farm_id: uuid.UUID, sensor_type: str
    ) -> list[AlertRule]:
        result = await self.db.execute(
            select(AlertRule).where(
                AlertRule.farm_id == farm_id,
                AlertRule.sensor_type == sensor_type,
                AlertRule.is_active.is_(True),
            )
        )
        return list(result.scalars().all())


class AlertRepository(BaseRepository[Alert]):
    def __init__(self, db: AsyncSession):
        super().__init__(Alert, db)

    async def get_active_alerts(
        self, farm_id: uuid.UUID, severity: str | None = None
    ) -> list[Alert]:
        query = (
            select(Alert)
            .join(AlertRule, Alert.alert_rule_id == AlertRule.id)
            .where(AlertRule.farm_id == farm_id, Alert.status == "active")
        )
        if severity:
            query = query.where(Alert.severity == severity)
        result = await self.db.execute(query.order_by(desc(Alert.created_at)))
        return list(result.scalars().all())

    async def count_active(self, farm_id: uuid.UUID, severity: str | None = None) -> int:
        query = (
            select(func.count())
            .select_from(Alert)
            .join(AlertRule, Alert.alert_rule_id == AlertRule.id)
            .where(AlertRule.farm_id == farm_id, Alert.status == "active")
        )
        if severity:
            query = query.where(Alert.severity == severity)
        result = await self.db.execute(query)
        return result.scalar() or 0

    async def get_recent_alert_for_rule(
        self, rule_id: uuid.UUID, cooldown_minutes: int
    ) -> Alert | None:
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=cooldown_minutes)
        result = await self.db.execute(
            select(Alert)
            .where(
                Alert.alert_rule_id == rule_id,
                Alert.created_at >= cutoff,
            )
            .order_by(desc(Alert.created_at))
            .limit(1)
        )
        return result.scalar_one_or_none()


class EscalationPolicyRepository(BaseRepository[EscalationPolicy]):
    def __init__(self, db: AsyncSession):
        super().__init__(EscalationPolicy, db)
