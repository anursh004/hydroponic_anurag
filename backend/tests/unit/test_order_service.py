"""Tests for order service."""
import pytest
from uuid import uuid4
from decimal import Decimal

from app.core.constants import OrderStatus, CustomerType
from app.core.exceptions import NotFoundException
from app.services.order_service import OrderService
from app.schemas.order import CustomerCreate, OrderCreate, OrderItemCreate


class TestCustomerService:
    """Test customer operations."""

    @pytest.mark.asyncio
    async def test_create_customer(self, db_session, sample_farm):
        service = OrderService(db_session)
        data = CustomerCreate(
            name="Fresh Market Co",
            email="orders@freshmarket.com",
            phone="+1234567890",
            customer_type=CustomerType.WHOLESALE,
            company="Fresh Market Corp",
            address="123 Market St",
        )
        customer = await service.create_customer(sample_farm.id, data)
        assert customer.name == "Fresh Market Co"
        assert customer.customer_type == CustomerType.WHOLESALE

    @pytest.mark.asyncio
    async def test_get_customer(self, db_session, sample_farm):
        service = OrderService(db_session)
        data = CustomerCreate(
            name="Test Customer",
            email="test@customer.com",
            customer_type=CustomerType.RETAIL,
        )
        customer = await service.create_customer(sample_farm.id, data)
        fetched = await service.get_customer(customer.id)
        assert fetched.id == customer.id

    @pytest.mark.asyncio
    async def test_get_customer_not_found(self, db_session):
        service = OrderService(db_session)
        with pytest.raises(NotFoundException):
            await service.get_customer(uuid4())


class TestOrderService:
    """Test order operations."""

    @pytest.mark.asyncio
    async def test_create_order(self, db_session, sample_farm, sample_user):
        service = OrderService(db_session)
        # Create customer first
        cust = CustomerCreate(
            name="Order Customer",
            email="c@test.com",
            customer_type=CustomerType.RETAIL,
        )
        customer = await service.create_customer(sample_farm.id, cust)

        data = OrderCreate(
            customer_id=customer.id,
            items=[
                OrderItemCreate(
                    crop_name="Lettuce",
                    quantity_kg=Decimal("5.0"),
                    unit_price=Decimal("4.50"),
                ),
                OrderItemCreate(
                    crop_name="Basil",
                    quantity_kg=Decimal("2.0"),
                    unit_price=Decimal("8.00"),
                ),
            ],
            delivery_date="2025-02-01",
            notes="Handle with care",
        )
        order = await service.create_order(sample_farm.id, data, sample_user.id)
        assert order.order_number.startswith("ORD-")
        expected_total = 5.0 * 4.50 + 2.0 * 8.00  # 38.50
        assert float(order.total_amount) == expected_total
        assert order.status == OrderStatus.PENDING

    @pytest.mark.asyncio
    async def test_order_auto_generates_number(self, db_session, sample_farm, sample_user):
        service = OrderService(db_session)
        cust = CustomerCreate(
            name="C2", email="c2@test.com", customer_type=CustomerType.RETAIL,
        )
        customer = await service.create_customer(sample_farm.id, cust)

        data = OrderCreate(
            customer_id=customer.id,
            items=[
                OrderItemCreate(
                    crop_name="Spinach",
                    quantity_kg=Decimal("3.0"),
                    unit_price=Decimal("5.00"),
                ),
            ],
        )
        order = await service.create_order(sample_farm.id, data, sample_user.id)
        assert order.order_number is not None
        assert len(order.order_number) > 0

    @pytest.mark.asyncio
    async def test_list_orders(self, db_session, sample_farm, sample_user):
        service = OrderService(db_session)
        cust = CustomerCreate(
            name="C3", email="c3@test.com", customer_type=CustomerType.RETAIL,
        )
        customer = await service.create_customer(sample_farm.id, cust)

        for i in range(3):
            data = OrderCreate(
                customer_id=customer.id,
                items=[
                    OrderItemCreate(
                        crop_name=f"Crop {i}",
                        quantity_kg=Decimal("1.0"),
                        unit_price=Decimal("2.00"),
                    ),
                ],
            )
            await service.create_order(sample_farm.id, data, sample_user.id)

        orders, total = await service.get_orders(sample_farm.id)
        assert total >= 3
