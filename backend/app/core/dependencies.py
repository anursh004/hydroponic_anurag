from dataclasses import dataclass

from fastapi import Depends, Query

from app.core.database import get_db
from app.core.security import get_current_active_user, get_current_user


@dataclass
class PaginationParams:
    skip: int = Query(0, ge=0, description="Number of records to skip")
    limit: int = Query(100, ge=1, le=1000, description="Max records to return")


__all__ = [
    "get_db",
    "get_current_user",
    "get_current_active_user",
    "PaginationParams",
]
