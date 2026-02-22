import uuid
from datetime import datetime, timedelta, timezone
from typing import Callable

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.database import get_db
from app.core.exceptions import ForbiddenException, UnauthorizedException

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_PREFIX}/auth/login")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        raise UnauthorizedException(detail="Invalid or expired token")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    from app.models.user import User

    payload = verify_token(token)
    if payload.get("type") != "access":
        raise UnauthorizedException(detail="Invalid token type")

    user_id = payload.get("sub")
    if user_id is None:
        raise UnauthorizedException(detail="Invalid token payload")

    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise UnauthorizedException(detail="Invalid user ID in token")

    result = await db.execute(
        select(User).options(selectinload(User.role)).where(User.id == user_uuid)
    )
    user = result.scalar_one_or_none()

    if user is None:
        raise UnauthorizedException(detail="User not found")

    return user


async def get_current_active_user(
    current_user=Depends(get_current_user),
):
    if not current_user.is_active:
        raise ForbiddenException(detail="Inactive user account")
    return current_user


def require_role(allowed_roles: list[str]) -> Callable:
    async def role_checker(current_user=Depends(get_current_active_user)):
        if current_user.is_superuser:
            return current_user
        if current_user.role is None or current_user.role.name not in allowed_roles:
            raise ForbiddenException(
                detail=f"Role '{current_user.role.name if current_user.role else 'none'}' not authorized"
            )
        return current_user

    return role_checker


def require_permission(permission: str) -> Callable:
    async def permission_checker(current_user=Depends(get_current_active_user)):
        if current_user.is_superuser:
            return current_user

        if current_user.role is None:
            raise ForbiddenException(detail="No role assigned")

        # Check permissions through role
        from app.models.user import Permission, RolePermission

        # Permissions are loaded through role relationship
        user_permissions = []
        if hasattr(current_user.role, "permissions"):
            user_permissions = [p.codename for p in current_user.role.permissions]

        if permission not in user_permissions:
            raise ForbiddenException(detail=f"Permission '{permission}' required")

        return current_user

    return permission_checker
