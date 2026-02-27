"""Tests for alert service."""
import pytest
from uuid import uuid4
from datetime import datetime

from app.core.constants import AlertStatus, AlertCondition, AlertSeverity, SensorType
from app.core.exceptions import NotFoundException, BadRequestException
from app.services.alert_service import AlertService
from app.schemas.alert import AlertRuleCreate
from app.models.alert import AlertRule, Alert


class TestAlertRuleService:
    """Test alert rule operations."""

    @pytest.mark.asyncio
    async def test_create_alert_rule(self, db_session, sample_farm):
        service = AlertService(db_session)
        data = AlertRuleCreate(
            name="High pH Alert",
            sensor_type=SensorType.PH,
            condition=AlertCondition.ABOVE,
            threshold_max=7.5,
            severity=AlertSeverity.WARNING,
            cooldown_minutes=15,
            notify_channels=["email", "push"],
        )
        rule = await service.create_rule(sample_farm.id, data)
        assert rule.name == "High pH Alert"
        assert rule.sensor_type == SensorType.PH
        assert rule.cooldown_minutes == 15

    @pytest.mark.asyncio
    async def test_get_rules(self, db_session, sample_farm):
        service = AlertService(db_session)
        # Create a rule first
        data = AlertRuleCreate(
            name="Low Temp Alert",
            sensor_type=SensorType.TEMPERATURE,
            condition=AlertCondition.BELOW,
            threshold_min=15.0,
            severity=AlertSeverity.CRITICAL,
            cooldown_minutes=5,
        )
        await service.create_rule(sample_farm.id, data)
        rules = await service.get_rules(sample_farm.id)
        assert len(rules) >= 1


class TestAlertEvaluation:
    """Test alert threshold evaluation logic."""

    @pytest.mark.asyncio
    async def test_threshold_above_triggers(self, db_session, sample_farm, sample_sensor):
        service = AlertService(db_session)
        # Create rule for pH above 7.0
        rule = AlertRule(
            id=uuid4(),
            farm_id=sample_farm.id,
            name="pH Too High",
            sensor_type=SensorType.PH,
            condition=AlertCondition.ABOVE,
            threshold_max=7.0,
            severity=AlertSeverity.WARNING,
            cooldown_minutes=0,
            is_active=True,
        )
        db_session.add(rule)
        await db_session.flush()

        # Evaluate a reading that's above threshold
        alerts = await service.evaluate_reading(
            sensor_id=sample_sensor.id,
            value=7.5,
            sensor_type=SensorType.PH,
            farm_id=sample_farm.id,
        )
        assert len(alerts) >= 1

    @pytest.mark.asyncio
    async def test_threshold_below_no_trigger(self, db_session, sample_farm, sample_sensor):
        service = AlertService(db_session)
        rule = AlertRule(
            id=uuid4(),
            farm_id=sample_farm.id,
            name="pH Too High",
            sensor_type=SensorType.PH,
            condition=AlertCondition.ABOVE,
            threshold_max=7.0,
            severity=AlertSeverity.WARNING,
            cooldown_minutes=0,
            is_active=True,
        )
        db_session.add(rule)
        await db_session.flush()

        # Value is below threshold - no alert
        alerts = await service.evaluate_reading(
            sensor_id=sample_sensor.id,
            value=6.5,
            sensor_type=SensorType.PH,
            farm_id=sample_farm.id,
        )
        assert len(alerts) == 0


class TestAlertWorkflow:
    """Test alert acknowledge/resolve workflow."""

    @pytest.mark.asyncio
    async def test_acknowledge_alert(self, db_session, sample_farm, sample_user):
        service = AlertService(db_session)
        # Create an alert directly
        alert = Alert(
            id=uuid4(),
            farm_id=sample_farm.id,
            alert_rule_id=None,
            sensor_id=None,
            triggered_value=8.0,
            status=AlertStatus.ACTIVE,
            message="Test alert",
        )
        db_session.add(alert)
        await db_session.flush()

        result = await service.acknowledge_alert(alert.id, sample_user.id, "Checking now")
        assert result.status == AlertStatus.ACKNOWLEDGED
        assert result.acknowledged_by_id == sample_user.id

    @pytest.mark.asyncio
    async def test_resolve_alert(self, db_session, sample_farm, sample_user):
        service = AlertService(db_session)
        alert = Alert(
            id=uuid4(),
            farm_id=sample_farm.id,
            alert_rule_id=None,
            sensor_id=None,
            triggered_value=8.0,
            status=AlertStatus.ACKNOWLEDGED,
            message="Test alert",
            acknowledged_by_id=sample_user.id,
            acknowledged_at=datetime.utcnow(),
        )
        db_session.add(alert)
        await db_session.flush()

        result = await service.resolve_alert(alert.id, sample_user.id)
        assert result.status == AlertStatus.RESOLVED

    @pytest.mark.asyncio
    async def test_resolve_active_alert_fails(self, db_session, sample_farm, sample_user):
        service = AlertService(db_session)
        alert = Alert(
            id=uuid4(),
            farm_id=sample_farm.id,
            alert_rule_id=None,
            sensor_id=None,
            triggered_value=8.0,
            status=AlertStatus.ACTIVE,
            message="Test alert",
        )
        db_session.add(alert)
        await db_session.flush()

        with pytest.raises(BadRequestException):
            await service.resolve_alert(alert.id, sample_user.id)
