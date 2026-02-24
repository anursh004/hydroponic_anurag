from pydantic import BaseModel

from app.schemas.harvest import HarvestCalendarEntry
from app.schemas.sensor import SensorSummaryResponse


class DashboardResponse(BaseModel):
    sensor_summary: list[SensorSummaryResponse]
    active_alerts_count: int
    critical_alerts_count: int
    active_crop_cycles: int
    upcoming_harvests: list[HarvestCalendarEntry]
    pending_tasks: int
    recent_orders: int
    total_zones: int
    active_sensors: int
    monthly_yield_kg: float
