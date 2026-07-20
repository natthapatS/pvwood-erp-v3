"""Warehouse portal API — WAREHOUSE (RM lots, FG, locations, goods receipt, mobile scan).

Add this portal's endpoints here. Frontend counterpart:
frontend/js/portals/portal_warehouse.js
"""
from fastapi import APIRouter

router = APIRouter(prefix="/api/warehouse", tags=["warehouse"])


@router.get("/ping")
def ping() -> dict:
    return {"portal": "warehouse", "ok": True}
