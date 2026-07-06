"""Domain 5 — Production.

Main line: ProductionOrder (<- production_orders), ProductionBatch (<- batches),
StationRecord (consolidates the 8 station logs; core columns + JSONB params).

Aux lines (PUV/PVS/PSP): TransformationRun + TransformationStep (per-step loss) +
TransformationInput (raw lot OR WIP batch) + TransformationOutput (new raw lot /
graded pcs; FG link added with domain 8). See docs/production_logs.md.
"""
from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field

from app.models.core import TimestampMixin, utcnow
from app.models.enums import BatchStatus, OrderStatus, StationCode


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
    current_station: StationCode | None = Field(default=None, index=True)
    status: BatchStatus = Field(default=BatchStatus.ACTIVE, index=True)
    split_reason: str = ""
    notes: str = ""


class StationRecord(TimestampMixin, table=True):
    """One record per batch per station pass. Core columns + JSONB `params`
    for the station-specific fields (pressure/temp/grit/grade split/…)."""

    __tablename__ = "station_record"

    id: int | None = Field(default=None, primary_key=True)
    batch_id: int = Field(foreign_key="production_batch.id", index=True)
    station: StationCode = Field(index=True)
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


# ── Aux-line transformations (PUV / PVS / PSP) ─────────────────────────────

class TransformationRun(TimestampMixin, table=True):
    __tablename__ = "transformation_run"

    id: int | None = Field(default=None, primary_key=True)
    run_number: str = Field(unique=True, index=True, max_length=64)
    line_code: str = Field(index=True)          # PVS/PSP/PUV
    mode: str | None = None                     # PUV: DOOR_SKIN | TOPCOAT (flexible)
    operator_1: str | None = None
    operator_2: str | None = None
    machine: str | None = None
    status: OrderStatus = Field(default=OrderStatus.IN_PROGRESS)
    run_at: datetime = Field(
        default_factory=utcnow, sa_type=DateTime(timezone=True), nullable=False
    )
    notes: str = ""


class TransformationStep(TimestampMixin, table=True):
    """Ordered step within a run, each with its own loss (e.g. PVS sawmill loss)."""

    __tablename__ = "transformation_step"

    id: int | None = Field(default=None, primary_key=True)
    run_id: int = Field(foreign_key="transformation_run.id", index=True)
    seq: int = 0
    name: str                                   # condition / sawmill / slice / splice / …
    input_qty: float | None = None
    input_uom: str | None = None
    output_qty: float | None = None
    output_uom: str | None = None
    loss_qty: float | None = None
    params: dict = Field(default_factory=dict, sa_type=JSONB)
    notes: str = ""


class TransformationInput(TimestampMixin, table=True):
    """A consumed input — a raw lot (PVS logs, PSP veneer) or a WIP batch (PUV mode B)."""

    __tablename__ = "transformation_input"

    id: int | None = Field(default=None, primary_key=True)
    run_id: int = Field(foreign_key="transformation_run.id", index=True)
    lot_id: int | None = Field(default=None, foreign_key="raw_material_lot.id")
    batch_id: int | None = Field(default=None, foreign_key="production_batch.id")
    qty: float
    uom: str = ""
    notes: str = ""


class TransformationOutput(TimestampMixin, table=True):
    """A produced output lot (new raw lot / graded pcs). FG output link (fg_lot_id)
    is added with domain 8; genealogy to inputs lives in domain 6 (LotLinkage)."""

    __tablename__ = "transformation_output"

    id: int | None = Field(default=None, primary_key=True)
    run_id: int = Field(foreign_key="transformation_run.id", index=True)
    item_id: int = Field(foreign_key="item.id")
    grade: str | None = None
    output_lot_id: int | None = Field(default=None, foreign_key="raw_material_lot.id")
    qty: float
    uom: str = ""
    yield_pct: float | None = None
    notes: str = ""
