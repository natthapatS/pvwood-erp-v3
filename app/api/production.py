"""Production portal API — DEPARTMENT_LEADER (station records, Kanban, batch flow).

Add this portal's endpoints here. Frontend counterpart:
frontend/js/portals/portal_production.js
"""
from fastapi import APIRouter

router = APIRouter(prefix="/api/production", tags=["production"])


@router.get("/ping")
def ping() -> dict:
    return {"portal": "production", "ok": True}
