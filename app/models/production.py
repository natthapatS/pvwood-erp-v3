"""Domain 5 — Production (unified model for ALL lines).

Every line (main P01/P02/P37 + aux PVS/PSP/PUV) runs the same engine: a
ProductionBatch moves through the ordered departments of its line's `line_flow`
(the Kanban board), and each stage is logged in StationRecord (the Station Hub).
Movement is free-form (BatchMovement ledger); the line_flow just defines the
expected route + Kanban columns. `current_department` is a catalog department code
(string), so new stages (aux-line vat_heating/sawmill/… ) need no schema change.

The aux "transformation" is therefore just a batch on the PVS/PSP line; the
input→graded-output *yield* lives in the TransformationRecipe (domain 2b). See
docs/production_logs.md.
"""
from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field

from app.models.core import TimestampMixin, utcnow
from app.models.enums import BatchStatus, OrderStatus


class ProductionOrder(TimestampMixin, table=True):
    __tablename__ = "production_order"

    id: int | None = Field(default=None, primary_key=True)
    prod_order_number: str = Field(unique=True, index=True, max_length=64)
    sales_order_line_id: int | None = Field(default=None, foreign_key="sales_order_line.id")
    product_id: int = Field(foreign_key="product.id", index=True)
    line_code: str = Field(index=True)          # P01/P02/P37/PUV/PVS/PSP
    quantity: int
    status: OrderStatus = Field(default=OrderStatus.PLANNED)
    priority: int = 3
    planned_start: datetime | None = Field(default=None, sa_type=DateTime(timezone=True))
    planned_end: datetime | None = Field(default=None, sa_type=DateTime(timezone=True))
    actual_start: datetime | None = Field(default=None, sa_type=DateTime(timezone=True))
    actual_end: datetime | None = Field(default=None, sa_type=DateTime(timezone=True))
    notes: str = ""


class ProductionBatch(TimestampMixin, table=True):
    __tablename__ = "production_batch"

    id: int | None = Field(default=None, primary_key=True)
    batch_number: str = Field(unique=True, index=True, max_length=64)
    production_order_id: int = Field(foreign_key="production_order.id", index=True)
    parent_batch_id: int | None = Field(default=None, foreign_key="production_batch.id")
    quantity: int
    line_code: str = Field(index=True)
    current_department: str | None = Field(default=None, index=True)  # catalog dept code
    status: BatchStatus = Field(default=BatchStatus.ACTIVE, index=True)
    rework_pass: int = 0                          # >0 = rework batch (e.g. PUV C->A)
    split_reason: str = ""
    notes: str = ""


class BatchMovement(TimestampMixin, table=True):
    """Kanban movement ledger — one row per department-to-department move."""

    __tablename__ = "batch_movement"

    id: int | None = Field(default=None, primary_key=True)
    batch_id: int = Field(foreign_key="production_batch.id", index=True)
    from_department: str | None = None
    to_department: str
    quantity: int = 0
    time_in_dept_min: int = 0
    moved_by: str | None = None
    notes: str = ""
    moved_at: datetime = Field(
        default_factory=utcnow, sa_type=DateTime(timezone=True), nullable=False
    )


class StationRecord(TimestampMixin, table=True):
    """One record per batch per stage pass (the Station Hub log). Core columns +
    JSONB `params` for stage-specific fields (pressure/temp/grit/grade split /
    2-pass g/m² / sawing loss / veneer m² / sheet count / …)."""

    __tablename__ = "station_record"

    id: int | None = Field(default=None, primary_key=True)
    batch_id: int = Field(foreign_key="production_batch.id", index=True)
    department: str = Field(index=True)          # catalog dept code (the stage)
    pcs_in: int = 0
    pcs_out: int = 0
    operator_1: str | None = None
    operator_2: str | None = None
    machine: str | None = None
    time_min: int = 0
    params: dict = Field(default_factory=dict, sa_type=JSONB)
    notes: str = ""
    recorded_at: datetime = Field(
        default_factory=utcnow, sa_type=DateTime(timezone=True), nullable=False
    )


class HeatingVat(TimestampMixin, table=True):
    """PVS log-heating vat resource (3 vats); referenced from a vat_heating
    StationRecord's params."""

    __tablename__ = "heating_vat"

    id: int | None = Field(default=None, primary_key=True)
    vat_number: int = Field(unique=True, index=True)
    label: str | None = None
    is_active: bool = True
    notes: str = ""
