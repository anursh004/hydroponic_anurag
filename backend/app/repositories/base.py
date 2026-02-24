import uuid
from typing import Any, Generic, Type, TypeVar

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import BaseModel

ModelType = TypeVar("ModelType", bound=BaseModel)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db

    async def get_by_id(self, id: uuid.UUID) -> ModelType | None:
        result = await self.db.execute(select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()

    async def get_multi(
        self, skip: int = 0, limit: int = 100, **filters: Any
    ) -> list[ModelType]:
        query = select(self.model)
        for key, value in filters.items():
            if value is not None and hasattr(self.model, key):
                query = query.where(getattr(self.model, key) == value)
        query = query.offset(skip).limit(limit).order_by(self.model.created_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count(self, **filters: Any) -> int:
        query = select(func.count()).select_from(self.model)
        for key, value in filters.items():
            if value is not None and hasattr(self.model, key):
                query = query.where(getattr(self.model, key) == value)
        result = await self.db.execute(query)
        return result.scalar() or 0

    async def create(self, obj_data: dict) -> ModelType:
        db_obj = self.model(**obj_data)
        self.db.add(db_obj)
        await self.db.flush()
        await self.db.refresh(db_obj)
        return db_obj

    async def update(self, id: uuid.UUID, obj_data: dict) -> ModelType | None:
        db_obj = await self.get_by_id(id)
        if db_obj is None:
            return None
        for key, value in obj_data.items():
            if value is not None and hasattr(db_obj, key):
                setattr(db_obj, key, value)
        await self.db.flush()
        await self.db.refresh(db_obj)
        return db_obj

    async def delete(self, id: uuid.UUID) -> bool:
        db_obj = await self.get_by_id(id)
        if db_obj is None:
            return False
        await self.db.delete(db_obj)
        await self.db.flush()
        return True
