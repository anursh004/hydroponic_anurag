import uuid
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.farm import Farm
    from app.models.user import User


class InventoryItem(BaseModel):
    __tablename__ = "inventory_items"

    farm_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("farms.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    sku: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    unit: Mapped[str] = mapped_column(String(20), nullable=False)
    current_stock: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    reorder_threshold: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    reorder_quantity: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    unit_cost: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    supplier: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    farm: Mapped["Farm"] = relationship(foreign_keys=[farm_id])
    transactions: Mapped[list["StockTransaction"]] = relationship(
        back_populates="inventory_item", cascade="all, delete-orphan"
    )


class StockTransaction(BaseModel):
    __tablename__ = "stock_transactions"

    inventory_item_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("inventory_items.id", ondelete="CASCADE"), nullable=False
    )
    transaction_type: Mapped[str] = mapped_column(String(20), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    reference: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    performed_by: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    inventory_item: Mapped["InventoryItem"] = relationship(back_populates="transactions")
    performer: Mapped["User"] = relationship(foreign_keys=[performed_by])
