import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, Column, ForeignKey, String, Table, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, BaseModel

if TYPE_CHECKING:
    from app.models.farm import Farm

# Association table: role <-> permission
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("permission_id", ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True),
)

# Association table: user <-> farm
user_farms = Table(
    "user_farms",
    Base.metadata,
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("farm_id", ForeignKey("farms.id", ondelete="CASCADE"), primary_key=True),
)


class Permission(BaseModel):
    __tablename__ = "permissions"

    codename: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    roles: Mapped[list["Role"]] = relationship(
        secondary=role_permissions, back_populates="permissions"
    )


class Role(BaseModel):
    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    users: Mapped[list["User"]] = relationship(back_populates="role")
    permissions: Mapped[list["Permission"]] = relationship(
        secondary=role_permissions, back_populates="roles", lazy="selectin"
    )


class User(BaseModel):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    role_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("roles.id", ondelete="SET NULL"), nullable=True
    )

    role: Mapped[Optional["Role"]] = relationship(back_populates="users", lazy="selectin")
    farms: Mapped[list["Farm"]] = relationship(
        secondary=user_farms, back_populates="users"
    )
