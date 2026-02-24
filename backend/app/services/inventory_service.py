import uuid
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.inventory import InventoryItem, StockTransaction
from app.repositories.base import BaseRepository


class InventoryService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.item_repo = BaseRepository(InventoryItem, db)
        self.txn_repo = BaseRepository(StockTransaction, db)

    async def create_item(self, farm_id: uuid.UUID, data: dict) -> InventoryItem:
        data["farm_id"] = farm_id
        return await self.item_repo.create(data)

    async def update_item(self, item_id: uuid.UUID, data: dict) -> InventoryItem:
        item = await self.item_repo.update(item_id, data)
        if not item:
            raise NotFoundException(detail="Inventory item not found")
        return item

    async def delete_item(self, item_id: uuid.UUID) -> None:
        if not await self.item_repo.delete(item_id):
            raise NotFoundException(detail="Inventory item not found")

    async def list_items(self, farm_id: uuid.UUID) -> list[InventoryItem]:
        return await self.item_repo.get_multi(limit=1000, farm_id=farm_id)

    async def create_transaction(
        self, item_id: uuid.UUID, data: dict, user_id: uuid.UUID
    ) -> StockTransaction:
        item = await self.item_repo.get_by_id(item_id)
        if not item:
            raise NotFoundException(detail="Inventory item not found")

        data["inventory_item_id"] = item_id
        data["performed_by"] = user_id
        txn = await self.txn_repo.create(data)

        item.current_stock = Decimal(str(float(item.current_stock) + data["quantity"]))
        await self.db.flush()
        return txn

    async def get_transactions(self, item_id: uuid.UUID) -> list[StockTransaction]:
        return await self.txn_repo.get_multi(limit=100, inventory_item_id=item_id)

    async def get_low_stock(self, farm_id: uuid.UUID) -> list[InventoryItem]:
        result = await self.db.execute(
            select(InventoryItem).where(
                InventoryItem.farm_id == farm_id,
                InventoryItem.reorder_threshold.isnot(None),
                InventoryItem.current_stock <= InventoryItem.reorder_threshold,
            )
        )
        return list(result.scalars().all())
