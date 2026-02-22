import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, Date, ForeignKey, Integer, JSON, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.crop import CropProfile, CropCycle
    from app.models.farm import Farm
    from app.models.harvest import Harvest


class Customer(BaseModel):
    __tablename__ = "customers"

    farm_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("farms.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    company: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    customer_type: Mapped[str] = mapped_column(String(50), nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    farm: Mapped["Farm"] = relationship(foreign_keys=[farm_id])
    orders: Mapped[list["Order"]] = relationship(back_populates="customer")
    subscriptions: Mapped[list["Subscription"]] = relationship(back_populates="customer")


class Order(BaseModel):
    __tablename__ = "orders"

    farm_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("farms.id", ondelete="CASCADE"), nullable=False
    )
    customer_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("customers.id", ondelete="CASCADE"), nullable=False
    )
    order_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)
    order_date: Mapped[date] = mapped_column(Date, nullable=False)
    delivery_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    subscription_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("subscriptions.id", ondelete="SET NULL"), nullable=True
    )

    customer: Mapped["Customer"] = relationship(back_populates="orders")
    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )
    invoice: Mapped[Optional["Invoice"]] = relationship(back_populates="order", uselist=False)
    farm: Mapped["Farm"] = relationship(foreign_keys=[farm_id])


class OrderItem(BaseModel):
    __tablename__ = "order_items"

    order_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"), nullable=False
    )
    crop_profile_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("crop_profiles.id", ondelete="CASCADE"), nullable=False
    )
    quantity_kg: Mapped[Decimal] = mapped_column(Numeric(8, 3), nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False)
    total_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    harvest_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("harvests.id", ondelete="SET NULL"), nullable=True
    )
    crop_cycle_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("crop_cycles.id", ondelete="SET NULL"), nullable=True
    )

    order: Mapped["Order"] = relationship(back_populates="items")
    crop_profile: Mapped["CropProfile"] = relationship(foreign_keys=[crop_profile_id])


class Subscription(BaseModel):
    __tablename__ = "subscriptions"

    customer_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("customers.id", ondelete="CASCADE"), nullable=False
    )
    frequency: Mapped[str] = mapped_column(String(20), nullable=False)
    day_of_week: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    items: Mapped[dict] = mapped_column(JSON, nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    next_delivery_date: Mapped[date] = mapped_column(Date, nullable=False)

    customer: Mapped["Customer"] = relationship(back_populates="subscriptions")


class Invoice(BaseModel):
    __tablename__ = "invoices"

    order_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"), nullable=False
    )
    invoice_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    tax_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="draft", nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    paid_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    order: Mapped["Order"] = relationship(back_populates="invoice")
