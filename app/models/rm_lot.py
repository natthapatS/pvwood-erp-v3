"""Domain 4 — RM lot tracking.

RawMaterialLot (<- legacy material_lots, generalized so it also holds
internally-transformed stock) + LotMovement, the unified ledger for
RECEIVE / TRANSFER / ADJUST / CONSUME and the internal transforms
GRADE / SPLICE / CUT_RESIZE.

Genealogy (parent lot -> child lot) is completed in domain 6 (LotLinkage) once
batches / FG lots exist. LotMovement.ref_type/ref_id is a lightweight polymorphic
link to the driving document (batch, goods receipt, transform run) until those
domains land with their own FKs.
"""
from datetime import date, datetime

from sqlalchemy import DateTime
from sqlmodel import Field

from app.models.core import TimestampMixin, utcnow
from app.models.enums import LotOrigin, MovementType


class RawMaterialLot(TimestampMixin, table=True):
    __tablename__ = "raw_material_lot"

    id: int | None = Field(default=None, primary_key=True)
    lot_code: str = Field(unique=True, index=True, max_length=64)
    item_id: int = Field(foreign_key="item.id", index=True)
    origin: LotOrigin = Field(default=LotOrigin.RECEIVED)

    # lot-specific grade (e.g. graded veneer differs from the item's default)
    grade: str | None = None

    supplier_id: int | None = Field(default=None, foreign_key="supplier.id")
    supplier_lot_ref: str = ""

    received_qty: float
    remaining_qty: float
    uom: str = ""
    unit_cost: float = 0.0

    location_id: int | None = Field(default=None, foreign_key="warehouse_location.id")
    received_at: datetime = Field(
        default_factory=utcnow, sa_type=DateTime(timezone=True), nullable=False
    )
    expiry_date: date | None = None
    is_active: bool = True
    notes: str = ""


class LotMovement(TimestampMixin, table=True):
    """Unified stock/lot ledger. One row per movement event."""

    __tablename__ = "lot_movement"

    id: int | None = Field(default=None, primary_key=True)
    lot_id: int = Field(foreign_key="raw_material_lot.id", index=True)
    movement_type: MovementType = Field(index=True)
    qty: float                                   # positive; direction implied by type
    uom: str = ""

    from_location_id: int | None = Field(default=None, foreign_key="warehouse_location.id")
    to_location_id: int | None = Field(default=None, foreign_key="warehouse_location.id")

    # polymorphic link to the driving document (batch / goods_receipt / transform / adjust)
    ref_type: str | None = None
    ref_id: int | None = None

    moved_at: datetime = Field(
        default_factory=utcnow, sa_type=DateTime(timezone=True), nullable=False
    )
    moved_by: str | None = None
    notes: str = ""
