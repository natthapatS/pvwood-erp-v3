"""FastAPI application entrypoint.

Phase 0 exposes only a health probe. Domain routers are added per phase as the
data-access layer and portals are built out.
"""
from fastapi import FastAPI

from app import __version__, models  # noqa: F401  (import registers SQLModel.metadata)
from app.api import catalog as catalog_api
from app.config import settings
from app.db import check_db

app = FastAPI(title=settings.app_name, version=__version__)

app.include_router(catalog_api.router)


@app.get("/api/health")
def health() -> dict:
    return {
        "status": "ok",
        "app": settings.app_name,
        "env": settings.app_env,
        "version": __version__,
        "db": "ok" if check_db() else "unreachable",
    }
