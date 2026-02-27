"""Dashboard aggregation endpoint."""
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.services.dashboard_service import DashboardService

router = APIRouter()


@router.get("/")
async def get_dashboard(
    farm_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    service = DashboardService(db)
    return await service.get_dashboard(farm_id)
