import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, Date, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.crop import CropCycle
    from app.models.farm import Farm, Zone
    from app.models.user import User


class Task(BaseModel):
    __tablename__ = "tasks"

    farm_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("farms.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    task_type: Mapped[str] = mapped_column(String(50), nullable=False)
    priority: Mapped[str] = mapped_column(String(20), default="medium", nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)
    assigned_to: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    zone_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("zones.id", ondelete="SET NULL"), nullable=True
    )
    crop_cycle_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("crop_cycles.id", ondelete="SET NULL"), nullable=True
    )
    due_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    photo_proof_required: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_by: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    farm: Mapped["Farm"] = relationship(foreign_keys=[farm_id])
    assignee: Mapped[Optional["User"]] = relationship(foreign_keys=[assigned_to])
    creator: Mapped["User"] = relationship(foreign_keys=[created_by])
    zone: Mapped[Optional["Zone"]] = relationship(foreign_keys=[zone_id])
    photos: Mapped[list["TaskPhoto"]] = relationship(
        back_populates="task", cascade="all, delete-orphan"
    )


class TaskPhoto(BaseModel):
    __tablename__ = "task_photos"

    task_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False
    )
    photo_url: Mapped[str] = mapped_column(String(500), nullable=False)
    caption: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    uploaded_by: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    uploaded_at: Mapped[datetime] = mapped_column(nullable=False)

    task: Mapped["Task"] = relationship(back_populates="photos")
    uploader: Mapped["User"] = relationship(foreign_keys=[uploaded_by])
