"""API v1 router - aggregates all endpoint routers."""
from fastapi import APIRouter

from app.api.v1 import (
    auth,
    users,
    farms,
    sensors,
    crops,
    alerts,
    dosing,
    inventory,
    harvests,
    lighting,
    orders,
    tasks,
    finance,
    vision,
    dashboard,
)

api_v1_router = APIRouter()

api_v1_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_v1_router.include_router(users.router, prefix="/users", tags=["Users"])
api_v1_router.include_router(farms.router, prefix="/farms", tags=["Farms"])
api_v1_router.include_router(sensors.router, prefix="/farms/{farm_id}/sensors", tags=["Sensors"])
api_v1_router.include_router(crops.router, prefix="/crops", tags=["Crops"])
api_v1_router.include_router(alerts.router, prefix="/farms/{farm_id}/alerts", tags=["Alerts"])
api_v1_router.include_router(dosing.router, prefix="/farms/{farm_id}/dosing", tags=["Dosing"])
api_v1_router.include_router(inventory.router, prefix="/farms/{farm_id}/inventory", tags=["Inventory"])
api_v1_router.include_router(harvests.router, prefix="/farms/{farm_id}/harvests", tags=["Harvests"])
api_v1_router.include_router(lighting.router, prefix="/farms/{farm_id}/lighting", tags=["Lighting"])
api_v1_router.include_router(orders.router, prefix="/farms/{farm_id}/orders", tags=["Orders"])
api_v1_router.include_router(tasks.router, prefix="/farms/{farm_id}/tasks", tags=["Tasks"])
api_v1_router.include_router(finance.router, prefix="/farms/{farm_id}/finance", tags=["Finance"])
api_v1_router.include_router(vision.router, prefix="/farms/{farm_id}/vision", tags=["Vision"])
api_v1_router.include_router(dashboard.router, prefix="/farms/{farm_id}/dashboard", tags=["Dashboard"])
