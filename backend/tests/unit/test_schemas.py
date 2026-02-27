"""Tests for Pydantic schema validations."""
import pytest
from decimal import Decimal
from pydantic import ValidationError

from app.schemas.auth import RegisterRequest, LoginRequest
from app.schemas.farm import FarmCreate
from app.schemas.sensor import SensorCreate, SensorReadingCreate
from app.schemas.crop import CropProfileCreate, GrowthLogCreate
from app.schemas.harvest import HarvestCreate
from app.schemas.dosing import DosingPumpCreate, ManualDoseRequest
from app.schemas.finance import CostCreate
from app.schemas.order import OrderCreate, OrderItemCreate
from app.core.constants import SensorType, PumpType, CostCategory, InventoryCategory


class TestAuthSchemas:
    """Test auth request validations."""

    def test_register_valid(self):
        req = RegisterRequest(
            email="valid@example.com",
            password="SecurePass1!",
            full_name="John Doe",
        )
        assert req.email == "valid@example.com"

    def test_register_invalid_email(self):
        with pytest.raises(ValidationError):
            RegisterRequest(
                email="not-an-email",
                password="SecurePass1!",
                full_name="John",
            )

    def test_register_short_password(self):
        with pytest.raises(ValidationError):
            RegisterRequest(
                email="test@test.com",
                password="Short1",
                full_name="John",
            )

    def test_login_valid(self):
        req = LoginRequest(email="test@test.com", password="password123")
        assert req.email == "test@test.com"


class TestFarmSchemas:
    """Test farm schema validations."""

    def test_farm_create_minimal(self):
        farm = FarmCreate(name="My Farm", location="Test", timezone="UTC")
        assert farm.name == "My Farm"

    def test_farm_create_with_coordinates(self):
        farm = FarmCreate(
            name="My Farm",
            location="NYC",
            latitude=40.7128,
            longitude=-74.0060,
            timezone="America/New_York",
        )
        assert farm.latitude == 40.7128


class TestSensorSchemas:
    """Test sensor schema validations."""

    def test_sensor_create(self):
        sensor = SensorCreate(
            name="pH Sensor",
            sensor_type=SensorType.PH,
            mqtt_topic="test/ph",
        )
        assert sensor.sensor_type == SensorType.PH

    def test_sensor_reading_create(self):
        reading = SensorReadingCreate(value=Decimal("6.5"))
        assert reading.value == Decimal("6.5")


class TestCropSchemas:
    """Test crop schema validations."""

    def test_growth_log_valid_rating(self):
        log = GrowthLogCreate(health_rating=5, height_cm=10.0)
        assert log.health_rating == 5

    def test_growth_log_invalid_rating_too_high(self):
        with pytest.raises(ValidationError):
            GrowthLogCreate(health_rating=6)

    def test_growth_log_invalid_rating_too_low(self):
        with pytest.raises(ValidationError):
            GrowthLogCreate(health_rating=0)


class TestHarvestSchemas:
    """Test harvest schema validations."""

    def test_harvest_valid(self):
        harvest = HarvestCreate(
            crop_cycle_id="00000000-0000-0000-0000-000000000001",
            weight_kg=Decimal("25.5"),
            grade="A",
        )
        assert harvest.weight_kg == Decimal("25.5")

    def test_harvest_negative_weight(self):
        with pytest.raises(ValidationError):
            HarvestCreate(
                crop_cycle_id="00000000-0000-0000-0000-000000000001",
                weight_kg=Decimal("-1.0"),
                grade="A",
            )


class TestDosingSchemas:
    """Test dosing schema validations."""

    def test_manual_dose_valid(self):
        dose = ManualDoseRequest(volume_ml=Decimal("50.0"))
        assert dose.volume_ml == Decimal("50.0")

    def test_manual_dose_negative(self):
        with pytest.raises(ValidationError):
            ManualDoseRequest(volume_ml=Decimal("-10.0"))

    def test_pump_create_valid(self):
        pump = DosingPumpCreate(
            name="pH Up Pump",
            pump_type=PumpType.PH_UP if hasattr(PumpType, "PH_UP") else "ph_up",
            ml_per_second=Decimal("2.5"),
            mqtt_command_topic="dosing/ph_up/cmd",
            mqtt_status_topic="dosing/ph_up/status",
        )
        assert pump.ml_per_second == Decimal("2.5")


class TestFinanceSchemas:
    """Test finance schema validations."""

    def test_cost_create_valid(self):
        cost = CostCreate(
            farm_id="00000000-0000-0000-0000-000000000001",
            category=CostCategory.NUTRIENT if hasattr(CostCategory, "NUTRIENT") else "nutrient",
            description="Nutrient A purchase",
            amount=Decimal("125.50"),
            date="2025-01-15",
        )
        assert cost.amount == Decimal("125.50")

    def test_cost_negative_amount(self):
        with pytest.raises(ValidationError):
            CostCreate(
                farm_id="00000000-0000-0000-0000-000000000001",
                category="nutrient",
                description="Test",
                amount=Decimal("-10.00"),
                date="2025-01-15",
            )


class TestOrderSchemas:
    """Test order schema validations."""

    def test_order_item_valid(self):
        item = OrderItemCreate(
            crop_name="Lettuce",
            quantity_kg=Decimal("5.0"),
            unit_price=Decimal("4.50"),
        )
        assert item.quantity_kg == Decimal("5.0")

    def test_order_create_calculates_items(self):
        order = OrderCreate(
            customer_id="00000000-0000-0000-0000-000000000001",
            items=[
                OrderItemCreate(
                    crop_name="Basil",
                    quantity_kg=Decimal("2.0"),
                    unit_price=Decimal("8.00"),
                ),
            ],
        )
        assert len(order.items) == 1
