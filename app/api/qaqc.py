"""QA/QC portal API — QA_QC (FC grading, NCG items/dispositions, inspection, COA review).

Add this portal's endpoints here. Frontend counterpart:
frontend/js/portals/portal_qaqc.js
"""
from fastapi import APIRouter

router = APIRouter(prefix="/api/qaqc", tags=["qaqc"])


@router.get("/ping")
def ping() -> dict:
    return {"portal": "qaqc", "ok": True}
