"""Celery tasks for report generation."""
import asyncio
import logging
from datetime import date

from app.core.celery_app import celery_app
from app.core.database import async_session_factory

logger = logging.getLogger(__name__)


def run_async(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(name="tasks.generate_daily_report", queue="default")
def generate_daily_report(farm_id: str):
    """Generate daily farm summary report."""

    async def _generate():
        from uuid import UUID
        from app.services.dashboard_service import DashboardService

        async with async_session_factory() as session:
            service = DashboardService(session)
            dashboard = await service.get_dashboard(UUID(farm_id))
            logger.info(f"Daily report generated for farm {farm_id}")
            return dashboard

    return run_async(_generate())


@celery_app.task(name="tasks.generate_weekly_harvest_report", queue="default")
def generate_weekly_harvest_report(farm_id: str):
    """Generate weekly harvest summary."""

    async def _generate():
        from uuid import UUID
        from app.services.harvest_service import HarvestService

        async with async_session_factory() as session:
            service = HarvestService(session)
            report = await service.get_yield_report(UUID(farm_id))
            monthly = await service.get_monthly_yield(UUID(farm_id), date.today().year)
            logger.info(f"Weekly harvest report generated for farm {farm_id}")
            return {
                "yield_report": [
                    {"crop_name": r.crop_name, "total_kg": r.total_weight_kg}
                    for r in report
                ] if report else [],
                "monthly_yield": monthly,
            }

    return run_async(_generate())


@celery_app.task(name="tasks.generate_financial_report", queue="default")
def generate_financial_report(farm_id: str, year: int = None):
    """Generate financial summary report."""

    async def _generate():
        from uuid import UUID
        from app.services.finance_service import FinanceService

        if year is None:
            report_year = date.today().year
        else:
            report_year = year

        async with async_session_factory() as session:
            service = FinanceService(session)
            revenue = await service.get_revenue_summary(UUID(farm_id))
            by_category = await service.get_costs_by_category(UUID(farm_id))
            monthly = await service.get_monthly_revenue(UUID(farm_id), report_year)
            profit_by_crop = await service.get_profit_by_crop(UUID(farm_id))

            logger.info(f"Financial report generated for farm {farm_id}, year {report_year}")
            return {
                "revenue_summary": revenue,
                "costs_by_category": by_category,
                "monthly_revenue": monthly,
                "profit_by_crop": profit_by_crop,
            }

    return run_async(_generate())


@celery_app.task(name="tasks.subscription_order_generation", queue="default")
def generate_subscription_orders():
    """Generate orders for active subscriptions that are due."""

    async def _generate():
        from datetime import datetime
        from sqlalchemy import select, and_
        from app.models.order import Subscription

        async with async_session_factory() as session:
            today = date.today()
            result = await session.execute(
                select(Subscription).where(
                    and_(
                        Subscription.is_active.is_(True),
                        Subscription.next_delivery_date <= today,
                    )
                )
            )
            due_subscriptions = result.scalars().all()
            logger.info(f"Found {len(due_subscriptions)} subscriptions due for order generation")
            # In production, auto-create orders from subscription templates
            return len(due_subscriptions)

    return run_async(_generate())
