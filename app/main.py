"""FastAPI application entrypoint — API routers + static SPA."""
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app import __version__, models  # noqa: F401  (import registers SQLModel.metadata)
from app.api import (
    accounting,
    admin,
    catalog,
    planning,
    production,
    purchasing,
    qaqc,
    warehouse,
)
from app.config import settings
from app.db import check_db

app = FastAPI(title=settings.app_name, version=__version__)


@app.get("/api/health")
def health() -> dict:
    return {
        "status": "ok",
        "app": settings.app_name,
        "env": settings.app_env,
        "version": __version__,
        "db": "ok" if check_db() else "unreachable",
    }


# One router per portal (+ shared catalog). Each portal owns its file.
for _router_module in (
    catalog, admin, planning, warehouse, production, qaqc, accounting, purchasing,
):
    app.include_router(_router_module.router)

# Serve the vanilla-JS SPA. Must be mounted LAST — it's a catch-all for non-/api paths.
_FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
if _FRONTEND_DIR.is_dir():
    app.mount("/", StaticFiles(directory=str(_FRONTEND_DIR), html=True), name="frontend")
