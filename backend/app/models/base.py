import uuid
from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        default=func.now(), onupdate=func.now(), nullable=False
    )


class BaseModel(TimestampMixin, Base):
    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
