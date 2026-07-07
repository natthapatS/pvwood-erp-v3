"""SQLModel table registry.

Importing this package imports every domain module, which registers all tables
on ``SQLModel.metadata`` — the single source of truth Alembic autogenerates
migrations from. Never import a domain module in isolation for migrations; always
go through this package so metadata is complete.
"""
from sqlmodel import SQLModel  # re-export

from app.models import core  # noqa: F401
from app.models import (  # noqa: F401
    enums,
    catalog,
    master,
    bom,
    procurement,
    rm_lot,
    production,
    traceability,
    fc,
    fg,
    sales,
    barcode,
    cost,
)

__all__ = ["SQLModel"]
