"""Domain 1 — Master data.

Species, ProductCategory, WarehouseLocation, Item (polymorphic RM/consumable
catalog <- legacy `materials`), and Product (finished-goods catalog <- legacy
`skus`).

Design note: on-hand QUANTITY is deliberately not stored on Item (the legacy
current_stock / fc_stock / wlwh_stock columns). It is derived from the
RawMaterialLot / LotMovement ledger per location — the point of lot tracking.
Only the catalog definition, costing, and reorder policy live here.
"""
from datetime import date

from sqlmodel import Field

from app.models.core import TimestampMixin
from app.models.enums import ItemKind


class ProductCategory(TimestampMixin, table=True):
    __tablename__ = "product_category"

    id: int | None = Field(default=None, primary_key=True)
    code: str = Field(unique=True, index=True, max_length=32)
    name: str
    description: str = ""
    is_active: bool = True


class Species(TimestampMixin, table=True):
    """Veneer species master (<- legacy free-text materials.species)."""

    __tablename__ = "species"

    id: int | None = Field(default=None, primary_key=True)
    code: str = Field(unique=True, index=True, max_length=32)
    common_name: str
    botanical_name: str = ""
    notes: str = ""
    is_active: bool = True


class WarehouseLocation(TimestampMixin, table=True):
    """Formalizes the legacy free-text from_location / to_location strings."""

    __tablename__ = "warehouse_location"

    id: int | None = Field(default=None, primary_key=True)
    code: str = Field(unique=True, index=True, max_length=32)
    name: str
    kind: str = ""          # WAREHOUSE | FC | WIP | FG | STAGING (free-form for now)
    notes: str = ""
    is_active: bool = True


class Item(TimestampMixin, table=True):
    """Raw-material / consumable catalog (<- legacy polymorphic `materials`)."""

    __tablename__ = "item"

    id: int | None = Field(default=None, primary_key=True)
    code: str = Field(unique=True, index=True, max_length=64)
    kind: ItemKind = Field(index=True)
    name: str
    name_th: str = ""
    name_zh: str = ""
    unit: str                                    # unit of measure

    # veneer / board / glue attributes (nullable per kind)
    species_id: int | None = Field(default=None, foreign_key="species.id")
    grade: str | None = None
    cut_type: str | None = None
    matching: str | None = None
    face_back: str | None = None
    fsc: str | None = None
    board_type: str | None = None
    glue_type: str | None = None
    auto_glue_code: str | None = None
    thickness_mm: float | None = None
    width_mm: float | None = None
    length_mm: float | None = None

    # costing
    unit_cost: float = 0.0
    fc_unit_cost: float | None = None
    price: float = 0.0
    acc_code: str | None = None                  # accounting / GL code (TAS 2 mapping)

    # policy / relations
    reorder_point: float = 0.0
    supplier_id: int | None = Field(default=None, foreign_key="supplier.id")
    is_active: bool = True
    notes: str = ""


class Product(TimestampMixin, table=True):
    """Finished-goods catalog (<- legacy `skus`)."""

    __tablename__ = "product"

    id: int | None = Field(default=None, primary_key=True)
    code: str = Field(unique=True, index=True, max_length=64)
    name: str
    category_id: int | None = Field(default=None, foreign_key="product_category.id")
    thickness_mm: float | None = None
    width_mm: float | None = None
    length_mm: float | None = None
    pallet_qty: int = 1
    approved_date: date | None = None
    revision: int = 0
    is_active: bool = True
    notes: str = ""
