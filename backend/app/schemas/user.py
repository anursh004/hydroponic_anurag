from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class PermissionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    codename: str
    description: str | None = None


class RoleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str | None = None
    permissions: list[PermissionResponse] = []
    created_at: datetime
    updated_at: datetime


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str = Field(..., min_length=1, max_length=255)
    phone: str | None = None
    is_active: bool = True
    is_superuser: bool = False
    role_id: UUID | None = None


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    full_name: str | None = Field(None, min_length=1, max_length=255)
    phone: str | None = None
    is_active: bool | None = None
    is_superuser: bool | None = None
    role_id: UUID | None = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    full_name: str | None = None
    phone: str | None = None
    is_active: bool
    is_superuser: bool
    role_id: UUID | None = None
    role: RoleResponse | None = None
    created_at: datetime
    updated_at: datetime


class UserRoleUpdate(BaseModel):
    role_id: UUID
