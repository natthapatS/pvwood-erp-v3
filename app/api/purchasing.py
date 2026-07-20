"""Purchasing portal API — PURCHASING (suppliers, purchase orders, PO lines).

Add this portal's endpoints here. Frontend counterpart:
frontend/js/portals/portal_purchasing.js
"""
from fastapi import APIRouter

router = APIRouter(prefix="/api/purchasing", tags=["purchasing"])


@router.get("/ping")
def ping() -> dict:
    return {"portal": "purchasing", "ok": True}
