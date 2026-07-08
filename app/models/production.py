"""Domain 5 — Production.

Main line: ProductionOrder (<- production_orders), ProductionBatch (<- batches),
StationRecord (consolidates the 8 station logs; core columns + JSONB params).

Aux lines:
- PVS/PSP transformations — TransformationRun (header) + per-line structured
  records LogProcessing (PVS) / SplicingRecord (PSP); genealogy via lot_linkage.
- PUV is NOT a transform: Mode A = standard production (assembly BOM + rework
  batch), Mode B = a FinishingJob queued off a UV_TOPCOAT BOM line on a P01 batch.

See docs/production_logs.md.
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
    rework_pass: int = 0                         # >0 = rework batch (e.g. PUV C->A)
    split_reason: str = ""
    notes: str = ""


class StationRecord(TimestampMixin, table=True):
    """One record per batch per station pass. Core columns + JSONB `params`
    for the station-specific fields (pressure/temp/grit/grade split/2-pass g/m²/…)."""

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


# ── PVS / PSP transformations ──────────────────────────────────────────────

class HeatingVat(TimestampMixin, table=True):
    """PVS log-heating vat resource (3 vats)."""

    __tablename__ = "heating_vat"

    id: int | None = Field(default=None, primary_key=True)
    vat_number: int = Field(unique=True, index=True)
    label: str | None = None
    is_active: bool = True
    notes: str = ""


class TransformationRun(TimestampMixin, table=True):
    """Header for one PVS/PSP run. Per-log / per-input detail lives in
    LogProcessing / SplicingRecord; genealogy lives in lot_linkage."""

    __tablename__ = "transformation_run"

    id: int | None = Field(default=None, primary_key=True)
    run_number: str = Field(unique=True, index=True, max_length=64)
    line_code: str = Field(index=True)          # PVS/PSP
    production_order_id: int | None = Field(default=None, foreign_key="production_order.id")
    operator_1: str | None = None
    operator_2: str | None = None
    machine: str | None = None
    status: OrderStatus = Field(default=OrderStatus.IN_PROGRESS)
    run_at: datetime = Field(
        default_factory=utcnow, sa_type=DateTime(timezone=True), nullable=False
    )
    notes: str = ""


class LogProcessing(TimestampMixin, table=True):
    """PVS per-log yield record (structured metrics for the log→veneer report)."""

    __tablename__ = "log_processing"

    id: int | None = Field(default=None, primary_key=True)
    run_id: int = Field(foreign_key="transformation_run.id", index=True)
    log_id: int = Field(foreign_key="log.id", index=True)
    heating_vat_id: int | None = Field(default=None, foreign_key="heating_vat.id")
    flitch_length_m: float | None = None
    flitch_diameter_m: float | None = None
    sawing_loss: float | None = None
    veneer_thickness_mm: float | None = None
    sliced_veneer_m2: float | None = None
    trimmed_veneer_m2: float | None = None
    final_yield_pct: float | None = None
    output_lot_id: int | None = Field(default=None, foreign_key="raw_material_lot.id")
    params: dict = Field(default_factory=dict, sa_type=JSONB)
    notes: str = ""


class SplicingRecord(TimestampMixin, table=True):
    """PSP per-input record. `grade` is set later at the grading step."""

    __tablename__ = "splicing_record"

    id: int | None = Field(default=None, primary_key=True)
    run_id: int = Field(foreign_key="transformation_run.id", index=True)
    input_lot_id: int = Field(foreign_key="raw_material_lot.id", index=True)
    trim_loss: float | None = None
    sheet_count_4x8: int | None = None
    output_lot_id: int | None = Field(default=None, foreign_key="raw_material_lot.id")
    grade: str | None = None
    params: dict = Field(default_factory=dict, sa_type=JSONB)
    notes: str = ""


# ── PUV Mode-B finishing job (UV topcoat detour) ───────────────────────────

class FinishingJob(TimestampMixin, table=True):
    """A finishing detour (PUV UV-topcoat) queued off a UV_TOPCOAT BOM line when a
    P01 batch reaches grading; the batch returns to P01 grading when DONE."""

    __tablename__ = "finishing_job"

    id: int | None = Field(default=None, primary_key=True)
    batch_id: int = Field(foreign_key="production_batch.id", index=True)
    line_code: str = "PUV"
    job_type: str = "UV_TOPCOAT"
    sides: int | None = None                     # 1 or 2
    status: str = Field(default="QUEUED", index=True)   # QUEUED | IN_PROGRESS | DONE
    requested_at: datetime = Field(
        default_factory=utcnow, sa_type=DateTime(timezone=True), nullable=False
    )
    started_at: datetime | None = Field(default=None, sa_type=DateTime(timezone=True))
    completed_at: datetime | None = Field(default=None, sa_type=DateTime(timezone=True))
    notes: str = ""
