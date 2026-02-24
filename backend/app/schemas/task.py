from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    task_type: str
    priority: str = "medium"
    assigned_to: UUID | None = None
    zone_id: UUID | None = None
    crop_cycle_id: UUID | None = None
    due_date: date | None = None
    photo_proof_required: bool = False


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    priority: str | None = None
    assigned_to: UUID | None = None
    status: str | None = None
    due_date: date | None = None


class TaskStatusUpdate(BaseModel):
    status: str
    notes: str | None = None


class TaskPhotoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    task_id: UUID
    photo_url: str
    caption: str | None = None
    uploaded_by: UUID
    uploaded_at: datetime


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    farm_id: UUID
    title: str
    description: str | None = None
    task_type: str
    priority: str
    status: str
    assigned_to: UUID | None = None
    zone_id: UUID | None = None
    crop_cycle_id: UUID | None = None
    due_date: date | None = None
    completed_at: datetime | None = None
    photo_proof_required: bool
    created_by: UUID
    photos: list[TaskPhotoResponse] = []
    created_at: datetime
    updated_at: datetime
