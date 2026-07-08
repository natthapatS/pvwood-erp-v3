"""Domain 2b — Transformation recipes (PVS / PSP planned inputs/outputs/steps).

The *planned* recipe for an aux-line transformation: what it consumes, produces,
and the ordered steps with expected yield/loss. Actual runs (with per-log / per-input
measured metrics) live in domain 5 (LogProcessing / SplicingRecord). PUV is a
production line, not a transform, so it has no recipe here — it uses assembly BOMs.
"""
from sqlmodel import Field

from app.models.core import TimestampMixin


class TransformationRecipe(TimestampMixin, table=True):
    __tablename__ = "transformation_recipe"

    id: int | None = Field(default=None, primary_key=True)
    line_code: str = Field(index=True)          # PVS | PSP
    code: str = Field(unique=True, index=True, max_length=64)
    name: str
    mode: str | None = None
    is_active: bool = True
    notes: str = ""


class TransformationRecipeLine(TimestampMixin, table=True):
    __tablename__ = "transformation_recipe_line"

    id: int | None = Field(default=None, primary_key=True)
    recipe_id: int = Field(foreign_key="transformation_recipe.id", index=True)
    kind: str = Field(index=True)               # INPUT | OUTPUT | STEP
    seq: int = 0
    item_id: int | None = Field(default=None, foreign_key="item.id")
    role: str | None = None
    qty: float | None = None
    uom: str | None = None
    grade: str | None = None
    expected_yield_pct: float | None = None
    expected_loss_pct: float | None = None
    notes: str = ""
