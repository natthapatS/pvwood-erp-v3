"""Domain 7 — Feed Center.

FCGradingRecord — grade split of a veneer lot or batch at FC (<- grading_records /
grading_log). `grade_split` is a grade -> qty map; `cost_allocation` holds the
TAS 2 allocation across output grades (populated in Stage 2d after sign-off).
"""
from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field

from app.models.core import TimestampMixin, utcnow


class FCGradingRecord(TimestampMixin, table=True):
    __tablename__ = "fc_grading_record"

    id: int | None = Field(default=None, primary_key=True)
    lot_id: int | None = Field(default=None, foreign_key="raw_material_lot.id", index=True)
    batch_id: int | None = Field(default=None, foreign_key="production_batch.id", index=True)
    grader: str | None = None
    input_qty: float = 0.0
    uom: str = ""
    grade_split: dict = Field(default_factory=dict, sa_type=JSONB)   # grade -> qty
    ncg_qty: float = 0.0
    reject_qty: float = 0.0
    cost_allocation: dict = Field(default_factory=dict, sa_type=JSONB)  # TAS 2 (Stage 2d)
    notes: str = ""
    recorded_at: datetime = Field(
        default_factory=utcnow, sa_type=DateTime(timezone=True), nullable=False
    )
