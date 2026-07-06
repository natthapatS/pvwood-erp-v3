"""Domain 11 — Cost accounting.

BatchCostRecord — per-batch roll-up of actual RM lot cost + conversion (labor /
overhead / glue). `grade_allocation` holds the TAS 2 split across output grades,
populated in Stage 2d after the costing-method sign-off. Distinct grain from the
legacy dept/month dept_cost_ledger.
"""
from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field

from app.models.core import TimestampMixin, utcnow


class BatchCostRecord(TimestampMixin, table=True):
    __tablename__ = "batch_cost_record"

    id: int | None = Field(default=None, primary_key=True)
    batch_id: int = Field(foreign_key="production_batch.id", index=True)
    material_cost: float = 0.0
    conversion_cost: float = 0.0                # labor + overhead + glue
    total_cost: float = 0.0
    cost_per_unit: float | None = None
    grade_allocation: dict = Field(default_factory=dict, sa_type=JSONB)  # TAS 2 (Stage 2d)
    computed_at: datetime = Field(
        default_factory=utcnow, sa_type=DateTime(timezone=True), nullable=False
    )
    notes: str = ""
