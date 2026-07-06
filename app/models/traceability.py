"""Domain 6 — Traceability spine.

LotLinkage is the genealogy edge connecting a parent entity to a child entity
across RM lots, production batches, and FG lots. It captures RM lot -> batch
(consumption), batch -> FG lot (production), and RM lot -> RM lot (aux-line
transforms: slice / splice / grade / cut). Supports forward (RM -> all FG) and
backward (FG -> all RM) trace.
"""
from sqlmodel import Field

from app.models.core import TimestampMixin


class LotLinkage(TimestampMixin, table=True):
    __tablename__ = "lot_linkage"

    id: int | None = Field(default=None, primary_key=True)

    # parent (source) — exactly one of these is set
    parent_lot_id: int | None = Field(default=None, foreign_key="raw_material_lot.id", index=True)
    parent_batch_id: int | None = Field(default=None, foreign_key="production_batch.id")
    parent_fg_lot_id: int | None = Field(default=None, foreign_key="fg_lot.id")

    # child (result) — exactly one of these is set
    child_lot_id: int | None = Field(default=None, foreign_key="raw_material_lot.id", index=True)
    child_batch_id: int | None = Field(default=None, foreign_key="production_batch.id")
    child_fg_lot_id: int | None = Field(default=None, foreign_key="fg_lot.id")

    relation: str                      # CONSUMED_INTO | TRANSFORMED_TO | PRODUCED | GRADED_TO
    qty: float | None = None
    uom: str = ""
    # link back to the driving record (transformation_run / lot_movement / station_record)
    ref_type: str | None = None
    ref_id: int | None = None
    notes: str = ""
