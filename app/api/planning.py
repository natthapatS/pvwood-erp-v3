"""Planning portal API — PRODUCTION_PLANNING (production orders, BOM, sales).

Add this portal's endpoints here. Frontend counterpart:
frontend/js/portals/portal_planning.js
"""
from fastapi import APIRouter

router = APIRouter(prefix="/api/planning", tags=["planning"])


@router.get("/ping")
def ping() -> dict:
    return {"portal": "planning", "ok": True}
