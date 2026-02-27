"""AI Vision endpoints."""
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_active_user, require_role
from app.models.user import User
from app.schemas.common import PaginatedResponse
from app.schemas.vision import (
    PlantScanCreate, PlantScanResponse,
    AnomalyDetectionResponse, AIAdvisoryResponse,
)
from app.services.vision_service import VisionService

router = APIRouter()


@router.post("/scans", response_model=PlantScanResponse, status_code=201)
async def create_scan(
    farm_id: UUID,
    data: PlantScanCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = VisionService(db)
    return await service.create_scan(data, current_user.id)


@router.get("/scans", response_model=PaginatedResponse[PlantScanResponse])
async def list_scans(
    farm_id: UUID,
    crop_cycle_id: UUID | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    service = VisionService(db)
    scans, total = await service.list_scans(
        farm_id, skip=skip, limit=limit, crop_cycle_id=crop_cycle_id
    )
    return PaginatedResponse(items=scans, total=total, skip=skip, limit=limit)


@router.get("/scans/{scan_id}", response_model=PlantScanResponse)
async def get_scan(
    farm_id: UUID,
    scan_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    service = VisionService(db)
    return await service.get_scan(scan_id)


@router.get("/anomaly-stats")
async def get_anomaly_stats(
    farm_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    service = VisionService(db)
    return await service.get_anomaly_stats(farm_id)


@router.get("/advisory", response_model=AIAdvisoryResponse)
async def get_ai_advisory(
    farm_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    service = VisionService(db)
    result = await service.get_ai_advisory(farm_id)
    return AIAdvisoryResponse(**result)
