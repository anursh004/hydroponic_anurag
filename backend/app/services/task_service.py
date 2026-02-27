"""Task management service."""
from datetime import datetime
from uuid import UUID

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.constants import TaskStatus, TaskPriority
from app.core.exceptions import NotFoundException, BadRequestException
from app.models.task import Task, TaskPhoto
from app.schemas.task import TaskCreate, TaskUpdate, TaskStatusUpdate


class TaskService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_task(self, data: TaskCreate, created_by: UUID) -> Task:
        task = Task(
            **data.model_dump(exclude={"assigned_to_id"}),
            assigned_to_id=data.assigned_to_id,
            created_by_id=created_by,
            status=TaskStatus.PENDING,
        )
        self.db.add(task)
        await self.db.flush()
        await self.db.refresh(task)
        return task

    async def get_task(self, task_id: UUID) -> Task:
        result = await self.db.execute(
            select(Task)
            .options(selectinload(Task.photos))
            .where(Task.id == task_id)
        )
        task = result.scalar_one_or_none()
        if not task:
            raise NotFoundException("Task", task_id)
        return task

    async def list_tasks(
        self,
        farm_id: UUID,
        skip: int = 0,
        limit: int = 20,
        status: TaskStatus | None = None,
        priority: TaskPriority | None = None,
        assigned_to: UUID | None = None,
    ) -> tuple[list[Task], int]:
        query = select(Task).where(Task.farm_id == farm_id)
        count_query = select(func.count()).select_from(Task).where(Task.farm_id == farm_id)

        if status:
            query = query.where(Task.status == status)
            count_query = count_query.where(Task.status == status)
        if priority:
            query = query.where(Task.priority == priority)
            count_query = count_query.where(Task.priority == priority)
        if assigned_to:
            query = query.where(Task.assigned_to_id == assigned_to)
            count_query = count_query.where(Task.assigned_to_id == assigned_to)

        total = (await self.db.execute(count_query)).scalar()
        result = await self.db.execute(
            query.options(selectinload(Task.photos))
            .order_by(Task.due_date.asc().nullslast(), Task.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all()), total

    async def update_task(self, task_id: UUID, data: TaskUpdate) -> Task:
        task = await self.get_task(task_id)
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(task, key, value)
        await self.db.flush()
        await self.db.refresh(task)
        return task

    async def update_status(self, task_id: UUID, data: TaskStatusUpdate, user_id: UUID) -> Task:
        task = await self.get_task(task_id)

        valid_transitions = {
            TaskStatus.PENDING: [TaskStatus.IN_PROGRESS, TaskStatus.CANCELLED],
            TaskStatus.IN_PROGRESS: [TaskStatus.COMPLETED, TaskStatus.BLOCKED, TaskStatus.CANCELLED],
            TaskStatus.BLOCKED: [TaskStatus.IN_PROGRESS, TaskStatus.CANCELLED],
            TaskStatus.COMPLETED: [],
            TaskStatus.CANCELLED: [],
        }

        if data.status not in valid_transitions.get(task.status, []):
            raise BadRequestException(
                f"Cannot transition from {task.status} to {data.status}"
            )

        if data.status == TaskStatus.COMPLETED and task.photo_proof_required:
            photo_count = await self.db.execute(
                select(func.count()).select_from(TaskPhoto).where(TaskPhoto.task_id == task_id)
            )
            if photo_count.scalar() == 0:
                raise BadRequestException("Photo proof is required to complete this task")

        task.status = data.status
        if data.status == TaskStatus.COMPLETED:
            task.completed_at = datetime.utcnow()
            task.completed_by_id = user_id
        if data.notes:
            task.notes = data.notes

        await self.db.flush()
        await self.db.refresh(task)
        return task

    async def add_photo(self, task_id: UUID, photo_url: str, uploaded_by: UUID) -> TaskPhoto:
        await self.get_task(task_id)
        photo = TaskPhoto(
            task_id=task_id,
            photo_url=photo_url,
            uploaded_by_id=uploaded_by,
        )
        self.db.add(photo)
        await self.db.flush()
        await self.db.refresh(photo)
        return photo

    async def delete_task(self, task_id: UUID) -> None:
        task = await self.get_task(task_id)
        if task.status == TaskStatus.IN_PROGRESS:
            raise BadRequestException("Cannot delete an in-progress task")
        await self.db.delete(task)
        await self.db.flush()

    async def count_pending_tasks(self, farm_id: UUID) -> int:
        result = await self.db.execute(
            select(func.count())
            .select_from(Task)
            .where(and_(Task.farm_id == farm_id, Task.status == TaskStatus.PENDING))
        )
        return result.scalar()

    async def get_overdue_tasks(self, farm_id: UUID) -> list[Task]:
        result = await self.db.execute(
            select(Task)
            .where(
                and_(
                    Task.farm_id == farm_id,
                    Task.due_date < datetime.utcnow(),
                    Task.status.in_([TaskStatus.PENDING, TaskStatus.IN_PROGRESS]),
                )
            )
            .order_by(Task.due_date.asc())
        )
        return list(result.scalars().all())
