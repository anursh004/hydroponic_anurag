"""Tests for constants/enums."""
import pytest

from app.core.constants import (
    SensorType, AlertSeverity, AlertStatus, AlertCondition,
    CropCycleStatus, OrderStatus, TaskStatus, TaskPriority,
    UserRole, DosingTrigger, InventoryCategory, TransactionType,
    InvoiceStatus, CustomerType, HarvestGrade,
)


class TestEnumValues:
    """Verify enum definitions and values."""

    def test_sensor_types(self):
        assert SensorType.PH is not None
        assert SensorType.EC is not None
        assert SensorType.TEMPERATURE is not None
        assert SensorType.HUMIDITY is not None
        assert SensorType.CO2 is not None
        assert SensorType.LIGHT is not None
        assert SensorType.WATER_LEVEL is not None

    def test_alert_severity(self):
        assert AlertSeverity.INFO is not None
        assert AlertSeverity.WARNING is not None
        assert AlertSeverity.CRITICAL is not None

    def test_alert_status_workflow(self):
        statuses = [AlertStatus.ACTIVE, AlertStatus.ACKNOWLEDGED, AlertStatus.RESOLVED]
        assert len(set(s.value for s in statuses)) == 3

    def test_alert_conditions(self):
        assert AlertCondition.ABOVE is not None
        assert AlertCondition.BELOW is not None
        assert AlertCondition.OUTSIDE_RANGE is not None

    def test_crop_cycle_status_progression(self):
        statuses = [
            CropCycleStatus.SEEDED,
            CropCycleStatus.GERMINATING,
            CropCycleStatus.VEGETATIVE,
            CropCycleStatus.FLOWERING,
            CropCycleStatus.HARVESTED,
            CropCycleStatus.FAILED,
        ]
        assert len(set(s.value for s in statuses)) == 6

    def test_order_status(self):
        assert OrderStatus.PENDING is not None
        assert OrderStatus.CONFIRMED is not None
        assert OrderStatus.SHIPPED is not None
        assert OrderStatus.DELIVERED is not None
        assert OrderStatus.CANCELLED is not None

    def test_task_status(self):
        assert TaskStatus.PENDING is not None
        assert TaskStatus.IN_PROGRESS is not None
        assert TaskStatus.COMPLETED is not None
        assert TaskStatus.CANCELLED is not None

    def test_task_priority(self):
        assert TaskPriority.LOW is not None
        assert TaskPriority.MEDIUM is not None
        assert TaskPriority.HIGH is not None
        assert TaskPriority.URGENT is not None

    def test_user_roles(self):
        roles = [UserRole.ADMIN, UserRole.FARM_MANAGER, UserRole.OPERATOR, UserRole.VIEWER]
        assert len(set(r.value for r in roles)) == 4

    def test_inventory_category(self):
        assert InventoryCategory.NUTRIENT is not None
        assert InventoryCategory.SUPPLY is not None

    def test_transaction_type(self):
        assert TransactionType.PURCHASE is not None
        assert TransactionType.USAGE is not None

    def test_invoice_status(self):
        assert InvoiceStatus.DRAFT is not None
        assert InvoiceStatus.SENT is not None
        assert InvoiceStatus.PAID is not None

    def test_customer_type(self):
        assert CustomerType.RETAIL is not None
        assert CustomerType.WHOLESALE is not None

    def test_harvest_grade(self):
        grades = [HarvestGrade.A, HarvestGrade.B, HarvestGrade.C, HarvestGrade.REJECT]
        assert len(set(g.value for g in grades)) == 4
