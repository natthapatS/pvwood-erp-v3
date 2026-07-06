"""Domain 8 — Finished goods.

FGLot — distinct finished-goods lot identity (today FG == batch); completes the
RM -> batch -> FG traceability spine. DispatchLine — FG lots leaving on a shipment.
FG can originate from a main-line ProductionBatch or a PUV mode-A run.
"""
from datetime import datetime

from sqlalchemy import DateTime
from sqlmodel import Field

from app.models.core import TimestampMixin, utcnow


class FGLot(TimestampMixin, table=True):
    __tablename__ = "fg_lot"

    id: int | None = Field(default=None, primary_key=True)
    lot_code: str = Field(unique=True, index=True, max_length=64)
    product_id: int = Field(foreign_key="product.id", index=True)
    production_batch_id: int | None = Field(default=None, foreign_key="production_batch.id")
    grade: str | None = None
    quantity: float
    uom: str = ""
    location_id: int | None = Field(default=None, foreign_key="warehouse_location.id")
    status: str = "IN_STOCK"                 # IN_STOCK | HOLD | DISPATCHED
    produced_at: datetime = Field(
        default_factory=utcnow, sa_type=DateTime(timezone=True), nullable=False
    )
    notes: str = ""


class DispatchLine(TimestampMixin, table=True):
    __tablename__ = "dispatch_line"

    id: int | None = Field(default=None, primary_key=True)
    shipment_id: int = Field(foreign_key="shipment.id", index=True)
    fg_lot_id: int = Field(foreign_key="fg_lot.id", index=True)
    quantity: float
    uom: str = ""
    notes: str = ""
