from datetime import datetime
from typing import Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    skip: int
    limit: int


class MessageResponse(BaseModel):
    message: str


class ErrorResponse(BaseModel):
    detail: str
    error_code: str | None = None


class HealthResponse(BaseModel):
    status: str
    service: str
