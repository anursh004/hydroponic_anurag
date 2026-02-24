import uuid
from datetime import date, timedelta

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import NotFoundException
from app.models.crop import CropCycle
from app.models.harvest import Harvest
from app.models.order import Customer, Invoice, Order, OrderItem, Subscription
from app.repositories.base import BaseRepository


class OrderService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.customer_repo = BaseRepository(Customer, db)
        self.order_repo = BaseRepository(Order, db)
        self.item_repo = BaseRepository(OrderItem, db)
        self.sub_repo = BaseRepository(Subscription, db)
        self.invoice_repo = BaseRepository(Invoice, db)

    # Customers
    async def create_customer(self, farm_id: uuid.UUID, data: dict) -> Customer:
        data["farm_id"] = farm_id
        return await self.customer_repo.create(data)

    async def update_customer(self, cid: uuid.UUID, data: dict) -> Customer:
        c = await self.customer_repo.update(cid, data)
        if not c:
            raise NotFoundException(detail="Customer not found")
        return c

    async def get_customer(self, cid: uuid.UUID) -> Customer:
        c = await self.customer_repo.get_by_id(cid)
        if not c:
            raise NotFoundException(detail="Customer not found")
        return c

    async def list_customers(self, farm_id: uuid.UUID) -> list[Customer]:
        return await self.customer_repo.get_multi(limit=1000, farm_id=farm_id)

    # Orders
    async def create_order(self, farm_id: uuid.UUID, data: dict) -> Order:
        items_data = data.pop("items", [])

        count = await self.db.execute(select(func.count()).select_from(Order))
        seq = (count.scalar() or 0) + 1
        order_number = f"ORD-{date.today().year}-{seq:05d}"

        total = sum(i["quantity_kg"] * i["unit_price"] for i in items_data)

        data["farm_id"] = farm_id
        data["order_number"] = order_number
        data["total_amount"] = round(total, 2)
        data["status"] = "pending"

        order = await self.order_repo.create(data)

        for item_data in items_data:
            item_data["order_id"] = order.id
            item_data["total_price"] = round(
                item_data["quantity_kg"] * item_data["unit_price"], 2
            )
            await self.item_repo.create(item_data)

        await self.db.refresh(order)
        return order

    async def get_order(self, order_id: uuid.UUID) -> Order:
        result = await self.db.execute(
            select(Order)
            .options(selectinload(Order.items))
            .where(Order.id == order_id)
        )
        order = result.scalar_one_or_none()
        if not order:
            raise NotFoundException(detail="Order not found")
        return order

    async def update_order(self, order_id: uuid.UUID, data: dict) -> Order:
        order = await self.order_repo.update(order_id, data)
        if not order:
            raise NotFoundException(detail="Order not found")
        return order

    async def list_orders(self, farm_id: uuid.UUID) -> list[Order]:
        result = await self.db.execute(
            select(Order)
            .options(selectinload(Order.items))
            .where(Order.farm_id == farm_id)
            .order_by(Order.created_at.desc())
            .limit(100)
        )
        return list(result.scalars().all())

    async def get_traceability(self, order_id: uuid.UUID) -> dict:
        order = await self.get_order(order_id)
        trace_items = []
        for item in order.items:
            trace = {"crop_profile_id": str(item.crop_profile_id), "quantity_kg": float(item.quantity_kg)}
            if item.crop_cycle_id:
                result = await self.db.execute(
                    select(CropCycle).where(CropCycle.id == item.crop_cycle_id)
                )
                cycle = result.scalar_one_or_none()
                if cycle:
                    trace["batch_code"] = cycle.batch_code
                    trace["seed_source"] = cycle.seed_source
                    trace["seed_lot_number"] = cycle.seed_lot_number
                    trace["seeded_at"] = str(cycle.seeded_at)
            trace_items.append(trace)
        return {
            "order_id": str(order.id),
            "order_number": order.order_number,
            "items": trace_items,
        }

    # Subscriptions
    async def create_subscription(self, farm_id: uuid.UUID, data: dict) -> Subscription:
        return await self.sub_repo.create(data)

    async def update_subscription(self, sub_id: uuid.UUID, data: dict) -> Subscription:
        sub = await self.sub_repo.update(sub_id, data)
        if not sub:
            raise NotFoundException(detail="Subscription not found")
        return sub

    async def list_subscriptions(self, farm_id: uuid.UUID) -> list[Subscription]:
        return await self.sub_repo.get_multi(limit=100)

    # Invoices
    async def create_invoice(self, order_id: uuid.UUID) -> Invoice:
        order = await self.get_order(order_id)
        count = await self.db.execute(select(func.count()).select_from(Invoice))
        seq = (count.scalar() or 0) + 1
        invoice_number = f"INV-{date.today().year}-{seq:05d}"
        return await self.invoice_repo.create(
            {
                "order_id": order.id,
                "invoice_number": invoice_number,
                "amount": float(order.total_amount),
                "tax_amount": 0,
                "status": "draft",
                "due_date": date.today() + timedelta(days=30),
            }
        )

    async def get_invoice(self, invoice_id: uuid.UUID) -> Invoice:
        inv = await self.invoice_repo.get_by_id(invoice_id)
        if not inv:
            raise NotFoundException(detail="Invoice not found")
        return inv

    async def update_invoice_status(self, invoice_id: uuid.UUID, status: str) -> Invoice:
        inv = await self.invoice_repo.update(invoice_id, {"status": status})
        if not inv:
            raise NotFoundException(detail="Invoice not found")
        return inv

    async def count_recent_orders(self, farm_id: uuid.UUID) -> int:
        result = await self.db.execute(
            select(func.count()).select_from(Order).where(Order.farm_id == farm_id)
        )
        return result.scalar() or 0
