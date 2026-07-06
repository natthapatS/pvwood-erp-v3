"""Domain 3 — Procurement.

Supplier, PurchaseOrder, POLine, GoodsReceipt. Purchasing raises the PO; Warehouse
performs Goods Receipt, which creates the RawMaterialLot (+ barcode label, Stage 2c).
Full receiving behavior is Stage 2e; the tables land now.
"""
from datetime import date, datetime

from sqlalchemy import DateTime
from sqlmodel import Field

from app.models.core import TimestampMixin, utcnow
from app.models.enums import OrderStatus


class Supplier(TimestampMixin, table=True):
    __tablename__ = "supplier"

    id: int | None = Field(default=None, primary_key=True)
    code: str = Field(unique=True, index=True, max_length=32)
    name: str
    contact_person: str = ""
    phone: str = ""
    email: str = ""
    address: str = ""
    notes: str = ""
    is_active: bool = True


class PurchaseOrder(TimestampMixin, table=True):
    __tablename__ = "purchase_order"

    id: int | None = Field(default=None, primary_key=True)
    po_number: str = Field(unique=True, index=True, max_length=64)
    supplier_id: int = Field(foreign_key="supplier.id", index=True)
    order_date: date
    expected_date: date | None = None
    status: OrderStatus = Field(default=OrderStatus.OPEN)
    notes: str = ""


class POLine(TimestampMixin, table=True):
    __tablename__ = "po_line"

    id: int | None = Field(default=None, primary_key=True)
    purchase_order_id: int = Field(foreign_key="purchase_order.id", index=True)
    item_id: int = Field(foreign_key="item.id")
    qty_ordered: float
    qty_received: float = 0.0
    uom: str = ""
    unit_price: float = 0.0
    notes: str = ""


class GoodsReceipt(TimestampMixin, table=True):
    """A receiving event (Warehouse). Creates the RawMaterialLot referenced here."""

    __tablename__ = "goods_receipt"

    id: int | None = Field(default=None, primary_key=True)
    receipt_number: str = Field(unique=True, index=True, max_length=64)
    purchase_order_id: int | None = Field(default=None, foreign_key="purchase_order.id")
    po_line_id: int | None = Field(default=None, foreign_key="po_line.id")
    item_id: int = Field(foreign_key="item.id")
    supplier_id: int | None = Field(default=None, foreign_key="supplier.id")
    qty_received: float
    uom: str = ""
    unit_cost: float = 0.0
    lot_id: int | None = Field(default=None, foreign_key="raw_material_lot.id")  # lot created on receipt
    location_id: int | None = Field(default=None, foreign_key="warehouse_location.id")
    received_at: datetime = Field(
        default_factory=utcnow, sa_type=DateTime(timezone=True), nullable=False
    )
    received_by: str | None = None
    notes: str = ""
