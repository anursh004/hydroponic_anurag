"""Celery tasks for inventory management."""
import asyncio
import logging

from app.core.celery_app import celery_app
from app.core.database import async_session_factory
from app.services.notification_service import NotificationService

logger = logging.getLogger(__name__)


def run_async(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(name="tasks.check_low_stock", queue="default")
def check_low_stock():
    """Check all farms for low stock items and send notifications."""

    async def _check():
        from sqlalchemy import select, and_
        from app.models.inventory import InventoryItem
        from app.models.farm import Farm

        async with async_session_factory() as session:
            # Get all items below reorder threshold
            result = await session.execute(
                select(InventoryItem).where(
                    and_(
                        InventoryItem.current_stock <= InventoryItem.reorder_threshold,
                        InventoryItem.reorder_threshold > 0,
                    )
                )
            )
            low_stock_items = result.scalars().all()

            for item in low_stock_items:
                await NotificationService.publish_alert(
                    item.farm_id,
                    {
                        "type": "low_stock",
                        "item_id": str(item.id),
                        "item_name": item.name,
                        "current_stock": float(item.current_stock),
                        "reorder_threshold": float(item.reorder_threshold),
                        "reorder_quantity": float(item.reorder_quantity) if item.reorder_quantity else None,
                    },
                )

            logger.info(f"Low stock check: {len(low_stock_items)} items below threshold")
            return len(low_stock_items)

    return run_async(_check())


@celery_app.task(name="tasks.generate_inventory_report", queue="default")
def generate_inventory_report(farm_id: str):
    """Generate inventory summary report for a farm."""

    async def _generate():
        from uuid import UUID
        from sqlalchemy import select, func
        from app.models.inventory import InventoryItem

        async with async_session_factory() as session:
            result = await session.execute(
                select(
                    InventoryItem.category,
                    func.count().label("item_count"),
                    func.sum(InventoryItem.current_stock).label("total_stock"),
                )
                .where(InventoryItem.farm_id == UUID(farm_id))
                .group_by(InventoryItem.category)
            )
            report = [
                {
                    "category": row.category,
                    "item_count": row.item_count,
                    "total_stock": float(row.total_stock) if row.total_stock else 0,
                }
                for row in result.all()
            ]
            logger.info(f"Generated inventory report for farm {farm_id}: {len(report)} categories")
            return report

    return run_async(_generate())
