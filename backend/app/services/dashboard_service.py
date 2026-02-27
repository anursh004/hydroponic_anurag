"""Dashboard aggregation service."""
from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import (
    AlertStatus, CropCycleStatus, TaskStatus, SensorType
)
from app.models.sensor import Sensor, SensorReading
from app.models.alert import Alert
from app.models.crop import CropCycle, CropProfile
from app.models.harvest import Harvest
from app.models.task import Task
from app.models.order import Order
from app.models.dosing import DosingEvent


class DashboardService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_dashboard(self, farm_id: UUID) -> dict:
        """Aggregate dashboard data for a farm."""
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_ago = now - timedelta(days=7)

        (
            sensor_summary,
            active_alerts,
            active_crops,
            pending_tasks,
            overdue_tasks,
            recent_harvests,
            today_orders,
            dosing_events_24h,
            environment_snapshot,
        ) = await self._gather_all(farm_id, now, today_start, week_ago)

        return {
            "sensor_summary": sensor_summary,
            "alerts": {
                "active_count": active_alerts,
            },
            "crops": {
                "active_count": active_crops,
            },
            "tasks": {
                "pending_count": pending_tasks,
                "overdue_count": overdue_tasks,
            },
            "harvests": {
                "recent": recent_harvests,
            },
            "orders": {
                "today_count": today_orders,
            },
            "dosing": {
                "events_24h": dosing_events_24h,
            },
            "environment": environment_snapshot,
            "generated_at": now.isoformat(),
        }

    async def _gather_all(self, farm_id, now, today_start, week_ago):
        """Gather all dashboard metrics."""
        sensor_summary = await self._get_sensor_summary(farm_id)
        active_alerts = await self._count_active_alerts(farm_id)
        active_crops = await self._count_active_crops(farm_id)
        pending_tasks = await self._count_tasks(farm_id, TaskStatus.PENDING)
        overdue_tasks = await self._count_overdue_tasks(farm_id, now)
        recent_harvests = await self._get_recent_harvests(farm_id, week_ago)
        today_orders = await self._count_today_orders(farm_id, today_start)
        dosing_24h = await self._count_dosing_events(farm_id, now - timedelta(hours=24))
        env_snapshot = await self._get_environment_snapshot(farm_id)

        return (
            sensor_summary,
            active_alerts,
            active_crops,
            pending_tasks,
            overdue_tasks,
            recent_harvests,
            today_orders,
            dosing_24h,
            env_snapshot,
        )

    async def _get_sensor_summary(self, farm_id: UUID) -> list[dict]:
        result = await self.db.execute(
            select(
                Sensor.sensor_type,
                func.count().label("count"),
                func.avg(Sensor.last_value).label("avg_value"),
                func.min(Sensor.last_value).label("min_value"),
                func.max(Sensor.last_value).label("max_value"),
            )
            .where(and_(Sensor.farm_id == farm_id, Sensor.is_active.is_(True)))
            .group_by(Sensor.sensor_type)
        )
        return [
            {
                "sensor_type": row.sensor_type,
                "count": row.count,
                "avg_value": round(float(row.avg_value), 2) if row.avg_value else None,
                "min_value": round(float(row.min_value), 2) if row.min_value else None,
                "max_value": round(float(row.max_value), 2) if row.max_value else None,
            }
            for row in result.all()
        ]

    async def _count_active_alerts(self, farm_id: UUID) -> int:
        result = await self.db.execute(
            select(func.count())
            .select_from(Alert)
            .where(and_(Alert.farm_id == farm_id, Alert.status == AlertStatus.ACTIVE))
        )
        return result.scalar()

    async def _count_active_crops(self, farm_id: UUID) -> int:
        result = await self.db.execute(
            select(func.count())
            .select_from(CropCycle)
            .where(
                and_(
                    CropCycle.farm_id == farm_id,
                    CropCycle.status.in_([
                        CropCycleStatus.SEEDED,
                        CropCycleStatus.GERMINATING,
                        CropCycleStatus.VEGETATIVE,
                        CropCycleStatus.FLOWERING,
                    ]),
                )
            )
        )
        return result.scalar()

    async def _count_tasks(self, farm_id: UUID, status: TaskStatus) -> int:
        result = await self.db.execute(
            select(func.count())
            .select_from(Task)
            .where(and_(Task.farm_id == farm_id, Task.status == status))
        )
        return result.scalar()

    async def _count_overdue_tasks(self, farm_id: UUID, now: datetime) -> int:
        result = await self.db.execute(
            select(func.count())
            .select_from(Task)
            .where(
                and_(
                    Task.farm_id == farm_id,
                    Task.due_date < now,
                    Task.status.in_([TaskStatus.PENDING, TaskStatus.IN_PROGRESS]),
                )
            )
        )
        return result.scalar()

    async def _get_recent_harvests(self, farm_id: UUID, since: datetime) -> list[dict]:
        result = await self.db.execute(
            select(Harvest)
            .join(CropCycle, Harvest.crop_cycle_id == CropCycle.id)
            .where(and_(CropCycle.farm_id == farm_id, Harvest.harvested_at >= since))
            .order_by(Harvest.harvested_at.desc())
            .limit(5)
        )
        harvests = result.scalars().all()
        return [
            {
                "id": str(h.id),
                "weight_kg": float(h.weight_kg),
                "grade": h.grade,
                "harvested_at": h.harvested_at.isoformat(),
            }
            for h in harvests
        ]

    async def _count_today_orders(self, farm_id: UUID, today_start: datetime) -> int:
        result = await self.db.execute(
            select(func.count())
            .select_from(Order)
            .where(and_(Order.farm_id == farm_id, Order.created_at >= today_start))
        )
        return result.scalar()

    async def _count_dosing_events(self, farm_id: UUID, since: datetime) -> int:
        result = await self.db.execute(
            select(func.count())
            .select_from(DosingEvent)
            .where(and_(DosingEvent.farm_id == farm_id, DosingEvent.created_at >= since))
        )
        return result.scalar()

    async def _get_environment_snapshot(self, farm_id: UUID) -> dict:
        """Latest reading for key sensor types."""
        key_types = [
            SensorType.TEMPERATURE,
            SensorType.HUMIDITY,
            SensorType.PH,
            SensorType.EC,
            SensorType.CO2,
        ]
        snapshot = {}
        for sensor_type in key_types:
            result = await self.db.execute(
                select(Sensor.last_value)
                .where(
                    and_(
                        Sensor.farm_id == farm_id,
                        Sensor.sensor_type == sensor_type,
                        Sensor.is_active.is_(True),
                    )
                )
                .order_by(Sensor.last_reading_at.desc().nullslast())
                .limit(1)
            )
            value = result.scalar_one_or_none()
            snapshot[sensor_type.value] = round(float(value), 2) if value else None

        return snapshot
