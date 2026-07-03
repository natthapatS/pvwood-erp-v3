"""Domain 3 — Procurement.

Supplier is modeled now because Item (domain 1) references it. PurchaseOrder /
POLine / GoodsReceipt land with the procurement behavior (Stage 2e): Purchasing
raises the PO; Warehouse performs Goods Receipt, which creates the RawMaterialLot
+ barcode label.
"""
from sqlmodel import Field

from app.models.core import TimestampMixin


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

# PurchaseOrder / POLine / GoodsReceipt — added in the procurement phase (Stage 2e).
