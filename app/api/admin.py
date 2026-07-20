"""Admin portal API — MANAGERIAL (master data, enums, users, Factory Assistant, config).

Add this portal's endpoints here. Frontend counterpart:
frontend/js/portals/portal_admin.js
"""
from fastapi import APIRouter

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/ping")
def ping() -> dict:
    return {"portal": "admin", "ok": True}
