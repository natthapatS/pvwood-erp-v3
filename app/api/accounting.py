"""Accounting portal API — ACCOUNTING (TAS 2 costing, cost ledgers, financial reports).

Add this portal's endpoints here. Frontend counterpart:
frontend/js/portals/portal_accounting.js
"""
from fastapi import APIRouter

router = APIRouter(prefix="/api/accounting", tags=["accounting"])


@router.get("/ping")
def ping() -> dict:
    return {"portal": "accounting", "ok": True}
