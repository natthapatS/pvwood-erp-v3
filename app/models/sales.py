"""Domain 9 — Sales.

Customer (<- customers), SalesOrder (<- legacy purchase_orders, which is actually
the customer sales order), SalesOrderLine (<- po_lines), Shipment (<- pr_shipments).
"""
from datetime import date, datetime

from sqlalchemy import DateTime
from sqlmodel import Field

from app.models.core import TimestampMixin, utcnow
from app.models.enums import OrderStatus


class Customer(TimestampMixin, table=True):
    __tablename__ = "customer"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    contact_person: str = ""
    phone: str = ""
    email: str = ""
    address: str = ""
    notes: str = ""
    is_active: bool = True


class SalesOrder(TimestampMixin, table=True):
    __tablename__ = "sales_order"

    id: int | None = Field(default=None, primary_key=True)
    order_number: str = Field(unique=True, index=True, max_length=64)
    customer_id: int = Field(foreign_key="customer.id", index=True)
    order_date: date
    delivery_date: date | None = None
    status: OrderStatus = Field(default=OrderStatus.OPEN)
    notes: str = ""


class SalesOrderLine(TimestampMixin, table=True):
    __tablename__ = "sales_order_line"

    id: int | None = Field(default=None, primary_key=True)
    sales_order_id: int = Field(foreign_key="sales_order.id", index=True)
    product_id: int = Field(foreign_key="product.id")
    quantity: int
    unit_price: float = 0.0
    production_line: str | None = None      # requested line (P01/P02/P37/…)
    notes: str = ""


class Shipment(TimestampMixin, table=True):
    __tablename__ = "shipment"

    id: int | None = Field(default=None, primary_key=True)
    shipment_number: str = Field(unique=True, index=True, max_length=64)
    sales_order_id: int = Field(foreign_key="sales_order.id", index=True)
    shipped_at: datetime | None = Field(default=None, sa_type=DateTime(timezone=True))
    status: OrderStatus = Field(default=OrderStatus.OPEN)
    notes: str = ""
