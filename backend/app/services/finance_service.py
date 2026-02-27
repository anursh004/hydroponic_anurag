"""Finance and cost-tracking service."""
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select, func, and_, extract
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import CostCategory, InvoiceStatus
from app.core.exceptions import NotFoundException
from app.models.finance import Cost
from app.models.order import Order, OrderItem, Invoice
from app.models.harvest import Harvest
from app.models.crop import CropCycle, CropProfile
from app.schemas.finance import CostCreate


class FinanceService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # --- Cost tracking ---
    async def create_cost(self, data: CostCreate) -> Cost:
        cost = Cost(**data.model_dump())
        self.db.add(cost)
        await self.db.flush()
        await self.db.refresh(cost)
        return cost

    async def get_cost(self, cost_id: UUID) -> Cost:
        result = await self.db.execute(select(Cost).where(Cost.id == cost_id))
        cost = result.scalar_one_or_none()
        if not cost:
            raise NotFoundException("Cost", cost_id)
        return cost

    async def list_costs(
        self,
        farm_id: UUID,
        skip: int = 0,
        limit: int = 20,
        category: CostCategory | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> tuple[list[Cost], int]:
        query = select(Cost).where(Cost.farm_id == farm_id)
        count_q = select(func.count()).select_from(Cost).where(Cost.farm_id == farm_id)

        if category:
            query = query.where(Cost.category == category)
            count_q = count_q.where(Cost.category == category)
        if start_date:
            query = query.where(Cost.date >= start_date)
            count_q = count_q.where(Cost.date >= start_date)
        if end_date:
            query = query.where(Cost.date <= end_date)
            count_q = count_q.where(Cost.date <= end_date)

        total = (await self.db.execute(count_q)).scalar()
        result = await self.db.execute(
            query.order_by(Cost.date.desc()).offset(skip).limit(limit)
        )
        return list(result.scalars().all()), total

    async def delete_cost(self, cost_id: UUID) -> None:
        cost = await self.get_cost(cost_id)
        await self.db.delete(cost)
        await self.db.flush()

    # --- Revenue dashboard ---
    async def get_revenue_summary(
        self, farm_id: UUID, start_date: date | None = None, end_date: date | None = None
    ) -> dict:
        """Get total revenue from paid invoices."""
        inv_query = (
            select(func.coalesce(func.sum(Invoice.total_amount), 0))
            .join(Order, Invoice.order_id == Order.id)
            .where(
                and_(
                    Order.farm_id == farm_id,
                    Invoice.status == InvoiceStatus.PAID,
                )
            )
        )
        cost_query = (
            select(func.coalesce(func.sum(Cost.amount), 0))
            .where(Cost.farm_id == farm_id)
        )

        if start_date:
            inv_query = inv_query.where(Invoice.paid_at >= datetime.combine(start_date, datetime.min.time()))
            cost_query = cost_query.where(Cost.date >= start_date)
        if end_date:
            inv_query = inv_query.where(Invoice.paid_at <= datetime.combine(end_date, datetime.max.time()))
            cost_query = cost_query.where(Cost.date <= end_date)

        total_revenue = (await self.db.execute(inv_query)).scalar()
        total_costs = (await self.db.execute(cost_query)).scalar()

        return {
            "total_revenue": float(total_revenue),
            "total_costs": float(total_costs),
            "net_profit": float(total_revenue - total_costs),
            "profit_margin": float(
                ((total_revenue - total_costs) / total_revenue * 100)
                if total_revenue > 0 else 0
            ),
        }

    async def get_costs_by_category(self, farm_id: UUID) -> list[dict]:
        """Group costs by category."""
        result = await self.db.execute(
            select(Cost.category, func.sum(Cost.amount).label("total"))
            .where(Cost.farm_id == farm_id)
            .group_by(Cost.category)
            .order_by(func.sum(Cost.amount).desc())
        )
        return [
            {"category": row.category, "total": float(row.total)}
            for row in result.all()
        ]

    async def get_monthly_revenue(self, farm_id: UUID, year: int) -> list[dict]:
        """Monthly revenue breakdown for a year."""
        result = await self.db.execute(
            select(
                extract("month", Invoice.paid_at).label("month"),
                func.sum(Invoice.total_amount).label("revenue"),
            )
            .join(Order, Invoice.order_id == Order.id)
            .where(
                and_(
                    Order.farm_id == farm_id,
                    Invoice.status == InvoiceStatus.PAID,
                    extract("year", Invoice.paid_at) == year,
                )
            )
            .group_by(extract("month", Invoice.paid_at))
            .order_by(extract("month", Invoice.paid_at))
        )
        months = {int(r.month): float(r.revenue) for r in result.all()}
        return [
            {"month": m, "revenue": months.get(m, 0.0)}
            for m in range(1, 13)
        ]

    async def get_profit_by_crop(self, farm_id: UUID) -> list[dict]:
        """Calculate profit per crop."""
        # Revenue per crop: sum of order items linked to harvests linked to crop cycles
        revenue_result = await self.db.execute(
            select(
                CropProfile.name,
                func.sum(OrderItem.quantity_kg * OrderItem.unit_price).label("revenue"),
            )
            .join(Harvest, OrderItem.harvest_id == Harvest.id)
            .join(CropCycle, Harvest.crop_cycle_id == CropCycle.id)
            .join(CropProfile, CropCycle.crop_profile_id == CropProfile.id)
            .where(CropCycle.farm_id == farm_id)
            .group_by(CropProfile.name)
        )
        revenue_by_crop = {r.name: float(r.revenue) for r in revenue_result.all()}

        # Costs per crop
        cost_result = await self.db.execute(
            select(
                CropProfile.name,
                func.sum(Cost.amount).label("costs"),
            )
            .join(CropCycle, Cost.crop_cycle_id == CropCycle.id)
            .join(CropProfile, CropCycle.crop_profile_id == CropProfile.id)
            .where(CropCycle.farm_id == farm_id)
            .group_by(CropProfile.name)
        )
        costs_by_crop = {r.name: float(r.costs) for r in cost_result.all()}

        all_crops = set(list(revenue_by_crop.keys()) + list(costs_by_crop.keys()))
        return [
            {
                "crop_name": crop,
                "revenue": revenue_by_crop.get(crop, 0.0),
                "costs": costs_by_crop.get(crop, 0.0),
                "profit": revenue_by_crop.get(crop, 0.0) - costs_by_crop.get(crop, 0.0),
            }
            for crop in sorted(all_crops)
        ]
