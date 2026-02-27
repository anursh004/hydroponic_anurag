"""Tests for task service."""
import pytest
from uuid import uuid4
from datetime import datetime, timedelta

from app.core.constants import TaskStatus, TaskPriority, TaskType
from app.core.exceptions import NotFoundException, BadRequestException
from app.services.task_service import TaskService
from app.schemas.task import TaskCreate, TaskUpdate, TaskStatusUpdate


class TestTaskService:
    """Test task management operations."""

    async def _create_task(self, service, farm_id, user_id, **kwargs):
        defaults = {
            "title": "Test Task",
            "task_type": TaskType.MAINTENANCE if hasattr(TaskType, "MAINTENANCE") else "maintenance",
            "priority": TaskPriority.MEDIUM,
            "farm_id": farm_id,
        }
        defaults.update(kwargs)
        data = TaskCreate(**defaults)
        return await service.create_task(data, user_id)

    @pytest.mark.asyncio
    async def test_create_task(self, db_session, sample_farm, sample_user):
        service = TaskService(db_session)
        task = await self._create_task(service, sample_farm.id, sample_user.id)
        assert task.title == "Test Task"
        assert task.status == TaskStatus.PENDING

    @pytest.mark.asyncio
    async def test_get_task(self, db_session, sample_farm, sample_user):
        service = TaskService(db_session)
        task = await self._create_task(service, sample_farm.id, sample_user.id)
        fetched = await service.get_task(task.id)
        assert fetched.id == task.id

    @pytest.mark.asyncio
    async def test_get_task_not_found(self, db_session):
        service = TaskService(db_session)
        with pytest.raises(NotFoundException):
            await service.get_task(uuid4())

    @pytest.mark.asyncio
    async def test_list_tasks(self, db_session, sample_farm, sample_user):
        service = TaskService(db_session)
        for i in range(3):
            await self._create_task(
                service, sample_farm.id, sample_user.id, title=f"Task {i}"
            )
        tasks, total = await service.list_tasks(sample_farm.id)
        assert total >= 3

    @pytest.mark.asyncio
    async def test_list_tasks_filter_by_status(self, db_session, sample_farm, sample_user):
        service = TaskService(db_session)
        await self._create_task(service, sample_farm.id, sample_user.id)
        tasks, total = await service.list_tasks(
            sample_farm.id, status=TaskStatus.PENDING
        )
        assert all(t.status == TaskStatus.PENDING for t, in [(t,) for t in tasks])

    @pytest.mark.asyncio
    async def test_update_task(self, db_session, sample_farm, sample_user):
        service = TaskService(db_session)
        task = await self._create_task(service, sample_farm.id, sample_user.id)
        data = TaskUpdate(title="Updated Task Title")
        updated = await service.update_task(task.id, data)
        assert updated.title == "Updated Task Title"

    @pytest.mark.asyncio
    async def test_status_transition_pending_to_in_progress(self, db_session, sample_farm, sample_user):
        service = TaskService(db_session)
        task = await self._create_task(service, sample_farm.id, sample_user.id)
        data = TaskStatusUpdate(status=TaskStatus.IN_PROGRESS)
        updated = await service.update_status(task.id, data, sample_user.id)
        assert updated.status == TaskStatus.IN_PROGRESS

    @pytest.mark.asyncio
    async def test_status_transition_in_progress_to_completed(self, db_session, sample_farm, sample_user):
        service = TaskService(db_session)
        task = await self._create_task(service, sample_farm.id, sample_user.id)
        # Move to in_progress first
        await service.update_status(
            task.id, TaskStatusUpdate(status=TaskStatus.IN_PROGRESS), sample_user.id
        )
        # Then complete
        data = TaskStatusUpdate(status=TaskStatus.COMPLETED)
        updated = await service.update_status(task.id, data, sample_user.id)
        assert updated.status == TaskStatus.COMPLETED
        assert updated.completed_at is not None

    @pytest.mark.asyncio
    async def test_invalid_status_transition(self, db_session, sample_farm, sample_user):
        service = TaskService(db_session)
        task = await self._create_task(service, sample_farm.id, sample_user.id)
        # Cannot go directly from PENDING to COMPLETED
        data = TaskStatusUpdate(status=TaskStatus.COMPLETED)
        with pytest.raises(BadRequestException):
            await service.update_status(task.id, data, sample_user.id)

    @pytest.mark.asyncio
    async def test_delete_task(self, db_session, sample_farm, sample_user):
        service = TaskService(db_session)
        task = await self._create_task(service, sample_farm.id, sample_user.id)
        await service.delete_task(task.id)
        with pytest.raises(NotFoundException):
            await service.get_task(task.id)

    @pytest.mark.asyncio
    async def test_delete_in_progress_task_fails(self, db_session, sample_farm, sample_user):
        service = TaskService(db_session)
        task = await self._create_task(service, sample_farm.id, sample_user.id)
        await service.update_status(
            task.id, TaskStatusUpdate(status=TaskStatus.IN_PROGRESS), sample_user.id
        )
        with pytest.raises(BadRequestException):
            await service.delete_task(task.id)

    @pytest.mark.asyncio
    async def test_count_pending_tasks(self, db_session, sample_farm, sample_user):
        service = TaskService(db_session)
        for _ in range(2):
            await self._create_task(service, sample_farm.id, sample_user.id)
        count = await service.count_pending_tasks(sample_farm.id)
        assert count >= 2
