"""Domain 2 — BOM.

Main-line (P01/P02/P37) product assembly BOMs, carried over from the legacy
structure: BOMHeader (per product) -> BOMItem (board + face/back veneer) +
BOMConsumable (face/back glue via GlueRecipe, plus packing). BOMGroup carries the
per-sheet / per-pallet calc basis.

BOMHeader.bom_type leaves room for the aux-line (PUV/PVS/PSP) TRANSFORMATION BOMs
(input lot -> output lot), designed + built in the aux-line pass.
"""
from sqlalchemy import CheckConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field

from app.models.core import TimestampMixin
from app.models.enums import BOMLineRole, BOMType, CalcMethod


class GlueRecipe(TimestampMixin, table=True):
    """Glue mix recipe (<- legacy glue_recipes): component ratios + links to items."""

    __tablename__ = "glue_recipe"

    id: int | None = Field(default=None, primary_key=True)
    recipe_code: str = Field(unique=True, index=True, max_length=32)
    name: str
    resin_ratio: float = 100.0
    hardener_ratio: float = 20.0
    extender_ratio: float = 0.0
    filler_ratio: float = 0.0
    water_ratio: float = 0.0
    mix_time_min: int = 20
    # component role -> item_id map (<- legacy material_links JSON)
    material_links: dict = Field(default_factory=dict, sa_type=JSONB)
    notes: str = ""
    is_active: bool = True


class BOMGroup(TimestampMixin, table=True):
    """Named grouping with a quantity basis (<- legacy bom_groups)."""

    __tablename__ = "bom_group"

    id: int | None = Field(default=None, primary_key=True)
    name: str
    calc_method: CalcMethod
    sort_order: int = 0
    notes: str = ""


class BOMHeader(TimestampMixin, table=True):
    """A product's bill of materials (one active header per product + revision)."""

    __tablename__ = "bom_header"
    __table_args__ = (UniqueConstraint("product_id", "revision", name="uq_bom_product_rev"),)

    id: int | None = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="product.id", index=True)
    bom_type: BOMType = Field(default=BOMType.ASSEMBLY)
    revision: int = 0
    is_active: bool = True
    notes: str = ""


class BOMItem(TimestampMixin, table=True):
    """Structural material line — board + face/back veneer (<- legacy bom_lines)."""

    __tablename__ = "bom_item"
    __table_args__ = (UniqueConstraint("bom_header_id", "seq", name="uq_bomitem_header_seq"),)

    id: int | None = Field(default=None, primary_key=True)
    bom_header_id: int = Field(foreign_key="bom_header.id", index=True)
    item_id: int = Field(foreign_key="item.id")
    group_id: int | None = Field(default=None, foreign_key="bom_group.id")
    seq: int = 0
    role: BOMLineRole
    qty_override: float | None = None
    qty_unit: str | None = None
    waste_factor: float | None = None
    notes: str = ""


class BOMConsumable(TimestampMixin, table=True):
    """Glue + packing line (<- legacy bom_lines glue rows + packing_lines).

    Either a glue_recipe_id (face/back glue) or an item_id (packing/consumable).
    """

    __tablename__ = "bom_consumable"
    __table_args__ = (
        CheckConstraint(
            "glue_recipe_id IS NOT NULL OR item_id IS NOT NULL",
            name="ck_bomconsumable_target",
        ),
    )

    id: int | None = Field(default=None, primary_key=True)
    bom_header_id: int = Field(foreign_key="bom_header.id", index=True)
    glue_recipe_id: int | None = Field(default=None, foreign_key="glue_recipe.id")
    item_id: int | None = Field(default=None, foreign_key="item.id")
    seq: int = 0
    role: BOMLineRole
    usage_g_per_face: float | None = None
    qty: float | None = None
    qty_unit: str | None = None
    notes: str = ""
