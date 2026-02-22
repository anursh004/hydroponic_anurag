import uuid
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Date, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.crop import CropCycle
    from app.models.farm import Farm, Zone
    from app.models.user import User


class Cost(BaseModel):
    __tablename__ = "costs"

    farm_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("farms.id", ondelete="CASCADE"), nullable=False
    )
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    crop_cycle_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("crop_cycles.id", ondelete="SET NULL"), nullable=True
    )
    zone_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("zones.id", ondelete="SET NULL"), nullable=True
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    farm: Mapped["Farm"] = relationship(foreign_keys=[farm_id])
    creator: Mapped["User"] = relationship(foreign_keys=[created_by])
