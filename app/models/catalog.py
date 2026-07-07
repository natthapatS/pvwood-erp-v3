"""Domain 1b — Line / department / station catalog (DB-driven configuration).

Mirrors the legacy manufacturing_line / departments / line_flow / stations. These
are configuration, not hardcoded: seeded from canonical defaults
(scripts/seed_catalog.py) and editable in the DB. Per-line departments run once
per main line; centralised departments (packing, fg_receiving, fg_warehouse) are
line-less. Aux lines (PUV/PVS/PSP) have no line_flow (request/transform hubs).
"""
from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel

from app.models.core import TimestampMixin


class ManufacturingLine(TimestampMixin, table=True):
    __tablename__ = "manufacturing_line"

    line_id: str = Field(primary_key=True, max_length=16)   # FC/P01/P02/P37/PUV/PVS/PSP
    label: str
    line_type: str = "main"                                 # main | aux | prep
    sort_order: int = 0
    is_active: bool = True


class Department(TimestampMixin, table=True):
    __tablename__ = "department"

    code: str = Field(primary_key=True, max_length=32)
    label: str
    icon: str | None = None
    is_centralised: bool = False
    sort_order: int = 0
    is_active: bool = True


class LineFlow(SQLModel, table=True):
    """Ordered department sequence for a line (composite PK)."""

    __tablename__ = "line_flow"

    line_code: str = Field(
        foreign_key="manufacturing_line.line_id", primary_key=True, max_length=16
    )
    seq: int = Field(primary_key=True)
    department_code: str = Field(foreign_key="department.code", max_length=32)


class Station(TimestampMixin, table=True):
    """A concrete (line, department) pair. Centralised depts get one row with
    line_code NULL."""

    __tablename__ = "station"
    __table_args__ = (
        UniqueConstraint("line_code", "department_code", name="uq_station_line_dept"),
    )

    id: int | None = Field(default=None, primary_key=True)
    line_code: str | None = Field(
        default=None, foreign_key="manufacturing_line.line_id", max_length=16
    )
    department_code: str = Field(foreign_key="department.code", max_length=32)
    label: str | None = None
    capacity_per_shift: int | None = None
    is_active: bool = True
