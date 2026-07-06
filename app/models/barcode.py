"""Domain 10 — Barcode.

BarcodeLabel (a printed QR/DataMatrix label pointing at a lot/batch/FG/location)
and ScanEvent (the scan ledger). Mobile camera-scan behavior is Stage 2c; the
tables land now. target_type/target_id and ref_type/ref_id are lightweight
polymorphic links across domains.
"""
from datetime import datetime

from sqlalchemy import DateTime
from sqlmodel import Field

from app.models.core import TimestampMixin, utcnow


class BarcodeLabel(TimestampMixin, table=True):
    __tablename__ = "barcode_label"

    id: int | None = Field(default=None, primary_key=True)
    code: str = Field(unique=True, index=True, max_length=128)   # QR/DataMatrix payload
    symbology: str = "QR"                       # QR | DATAMATRIX | CODE128
    target_type: str = Field(index=True)        # raw_lot | batch | fg_lot | location | item
    target_id: int
    printed_at: datetime | None = Field(default=None, sa_type=DateTime(timezone=True))
    printed_by: str | None = None
    is_active: bool = True
    notes: str = ""


class ScanEvent(TimestampMixin, table=True):
    __tablename__ = "scan_event"

    id: int | None = Field(default=None, primary_key=True)
    label_id: int | None = Field(default=None, foreign_key="barcode_label.id", index=True)
    scanned_code: str | None = None             # raw value if no label resolved
    action: str                                 # RECEIVE | MOVE | CONSUME | DISPATCH | LOOKUP
    location_id: int | None = Field(default=None, foreign_key="warehouse_location.id")
    ref_type: str | None = None
    ref_id: int | None = None
    scanned_at: datetime = Field(
        default_factory=utcnow, sa_type=DateTime(timezone=True), nullable=False
    )
    scanned_by: str | None = None
    notes: str = ""
