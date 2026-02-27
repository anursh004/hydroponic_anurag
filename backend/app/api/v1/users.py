"""User management endpoints."""
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_active_user, require_role
from app.models.user import User
from app.repositories.user_repo import UserRepository
from app.schemas.common import PaginatedResponse
from app.schemas.user import UserResponse, UserUpdate, UserRoleUpdate
from app.core.exceptions import NotFoundException

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[UserResponse])
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("admin")),
):
    repo = UserRepository(db)
    users, total = await repo.get_multi(skip=skip, limit=limit)
    return PaginatedResponse(
        items=users, total=total, skip=skip, limit=limit
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("admin")),
):
    repo = UserRepository(db)
    user = await repo.get_with_role(user_id)
    if not user:
        raise NotFoundException("User", user_id)
    return user


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("admin")),
):
    repo = UserRepository(db)
    user = await repo.update(user_id, data.model_dump(exclude_unset=True))
    if not user:
        raise NotFoundException("User", user_id)
    return user


@router.patch("/{user_id}/role", response_model=UserResponse)
async def update_user_role(
    user_id: UUID,
    data: UserRoleUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("admin")),
):
    repo = UserRepository(db)
    user = await repo.update(user_id, {"role_id": data.role_id})
    if not user:
        raise NotFoundException("User", user_id)
    return user


@router.delete("/{user_id}", status_code=204)
async def deactivate_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("admin")),
):
    repo = UserRepository(db)
    await repo.update(user_id, {"is_active": False})
