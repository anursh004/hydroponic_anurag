"""Task management endpoints."""
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_active_user, require_role
from app.core.constants import TaskStatus, TaskPriority
from app.models.user import User
from app.schemas.common import PaginatedResponse
from app.schemas.task import (
    TaskCreate, TaskUpdate, TaskResponse, TaskStatusUpdate,
)
from app.services.task_service import TaskService

router = APIRouter()


@router.post("/", response_model=TaskResponse, status_code=201)
async def create_task(
    farm_id: UUID,
    data: TaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "farm_manager")),
):
    service = TaskService(db)
    return await service.create_task(data, current_user.id)


@router.get("/", response_model=PaginatedResponse[TaskResponse])
async def list_tasks(
    farm_id: UUID,
    status: TaskStatus | None = None,
    priority: TaskPriority | None = None,
    assigned_to: UUID | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    service = TaskService(db)
    tasks, total = await service.list_tasks(
        farm_id, skip=skip, limit=limit, status=status,
        priority=priority, assigned_to=assigned_to,
    )
    return PaginatedResponse(items=tasks, total=total, skip=skip, limit=limit)


@router.get("/overdue", response_model=list[TaskResponse])
async def get_overdue_tasks(
    farm_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    service = TaskService(db)
    return await service.get_overdue_tasks(farm_id)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    farm_id: UUID,
    task_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    service = TaskService(db)
    return await service.get_task(task_id)


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    farm_id: UUID,
    task_id: UUID,
    data: TaskUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("admin", "farm_manager")),
):
    service = TaskService(db)
    return await service.update_task(task_id, data)


@router.post("/{task_id}/status", response_model=TaskResponse)
async def update_task_status(
    farm_id: UUID,
    task_id: UUID,
    data: TaskStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = TaskService(db)
    return await service.update_status(task_id, data, current_user.id)


@router.post("/{task_id}/photos", status_code=201)
async def add_task_photo(
    farm_id: UUID,
    task_id: UUID,
    photo_url: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = TaskService(db)
    photo = await service.add_photo(task_id, photo_url, current_user.id)
    return {"id": str(photo.id), "photo_url": photo.photo_url}


@router.delete("/{task_id}", status_code=204)
async def delete_task(
    farm_id: UUID,
    task_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("admin", "farm_manager")),
):
    service = TaskService(db)
    await service.delete_task(task_id)
