"""Tests for inventory service."""
import pytest
from uuid import uuid4
from decimal import Decimal

from app.core.constants import InventoryCategory, TransactionType
from app.core.exceptions import NotFoundException, BadRequestException
from app.services.inventory_service import InventoryService
from app.schemas.inventory import InventoryItemCreate, StockTransactionCreate


class TestInventoryService:
    """Test inventory management operations."""

    @pytest.mark.asyncio
    async def test_create_item(self, db_session, sample_farm):
        service = InventoryService(db_session)
        data = InventoryItemCreate(
            name="pH Up Solution",
            category=InventoryCategory.NUTRIENT,
            unit="liters",
            current_stock=Decimal("50.0"),
            reorder_threshold=Decimal("10.0"),
            reorder_quantity=Decimal("25.0"),
        )
        item = await service.create_item(sample_farm.id, data)
        assert item.name == "pH Up Solution"
        assert float(item.current_stock) == 50.0

    @pytest.mark.asyncio
    async def test_get_item(self, db_session, sample_farm):
        service = InventoryService(db_session)
        data = InventoryItemCreate(
            name="Test Item",
            category=InventoryCategory.SUPPLY,
            unit="pcs",
            current_stock=Decimal("100.0"),
        )
        item = await service.create_item(sample_farm.id, data)
        fetched = await service.get_item(item.id)
        assert fetched.id == item.id

    @pytest.mark.asyncio
    async def test_create_transaction_add(self, db_session, sample_farm, sample_user):
        service = InventoryService(db_session)
        item_data = InventoryItemCreate(
            name="Rockwool Cubes",
            category=InventoryCategory.SUPPLY,
            unit="pcs",
            current_stock=Decimal("100.0"),
        )
        item = await service.create_item(sample_farm.id, item_data)

        tx_data = StockTransactionCreate(
            quantity=Decimal("50.0"),
            transaction_type=TransactionType.PURCHASE,
            notes="Restocking",
        )
        tx = await service.create_transaction(item.id, tx_data, sample_user.id)
        assert float(tx.quantity) == 50.0

        # Check stock updated
        updated_item = await service.get_item(item.id)
        assert float(updated_item.current_stock) == 150.0

    @pytest.mark.asyncio
    async def test_create_transaction_remove(self, db_session, sample_farm, sample_user):
        service = InventoryService(db_session)
        item_data = InventoryItemCreate(
            name="Nutrient A",
            category=InventoryCategory.NUTRIENT,
            unit="liters",
            current_stock=Decimal("100.0"),
        )
        item = await service.create_item(sample_farm.id, item_data)

        tx_data = StockTransactionCreate(
            quantity=Decimal("-20.0"),
            transaction_type=TransactionType.USAGE,
            notes="Used in dosing",
        )
        tx = await service.create_transaction(item.id, tx_data, sample_user.id)
        updated = await service.get_item(item.id)
        assert float(updated.current_stock) == 80.0

    @pytest.mark.asyncio
    async def test_get_low_stock(self, db_session, sample_farm):
        service = InventoryService(db_session)
        # Create item below threshold
        data = InventoryItemCreate(
            name="Low Stock Item",
            category=InventoryCategory.NUTRIENT,
            unit="liters",
            current_stock=Decimal("5.0"),
            reorder_threshold=Decimal("10.0"),
            reorder_quantity=Decimal("25.0"),
        )
        await service.create_item(sample_farm.id, data)

        low = await service.get_low_stock(sample_farm.id)
        assert any(i.name == "Low Stock Item" for i in low)

    @pytest.mark.asyncio
    async def test_delete_item(self, db_session, sample_farm):
        service = InventoryService(db_session)
        data = InventoryItemCreate(
            name="Temp Item",
            category=InventoryCategory.SUPPLY,
            unit="pcs",
            current_stock=Decimal("10.0"),
        )
        item = await service.create_item(sample_farm.id, data)
        await service.delete_item(item.id)
        with pytest.raises(NotFoundException):
            await service.get_item(item.id)
