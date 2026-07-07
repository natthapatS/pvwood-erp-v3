"""Catalog API — lines / departments / line-flow / stations (DB-driven config).

Mirrors the legacy /api/catalog/* contract the frontend consumes.
"""
from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.db import get_session
from app.models.catalog import Department, LineFlow, ManufacturingLine, Station

router = APIRouter(prefix="/api/catalog", tags=["catalog"])


@router.get("/lines")
def list_lines(active_only: bool = True, session: Session = Depends(get_session)):
    stmt = select(ManufacturingLine).order_by(ManufacturingLine.sort_order)
    if active_only:
        stmt = stmt.where(ManufacturingLine.is_active.is_(True))
    return session.exec(stmt).all()


@router.get("/departments")
def list_departments(active_only: bool = True, session: Session = Depends(get_session)):
    stmt = select(Department).order_by(Department.sort_order)
    if active_only:
        stmt = stmt.where(Department.is_active.is_(True))
    return session.exec(stmt).all()


@router.get("/line-flow/{line_code}")
def get_line_flow(line_code: str, session: Session = Depends(get_session)):
    """Ordered department sequence for a line. Aux lines return []."""
    stmt = select(LineFlow).where(LineFlow.line_code == line_code).order_by(LineFlow.seq)
    return session.exec(stmt).all()


@router.get("/stations")
def list_stations(
    line_code: str | None = None,
    active_only: bool = True,
    session: Session = Depends(get_session),
):
    stmt = select(Station)
    if line_code:
        stmt = stmt.where(Station.line_code == line_code)
    if active_only:
        stmt = stmt.where(Station.is_active.is_(True))
    return session.exec(stmt).all()
