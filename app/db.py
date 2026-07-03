"""Database engine + pooled session.

One SQLAlchemy engine with a real connection pool (replaces the legacy
one-sqlite3-connection-per-request model). Handlers get a context-managed
``Session`` via the ``get_session`` FastAPI dependency, so connections are
always returned to the pool — no manual ``conn.close()`` discipline.
"""
from collections.abc import Iterator

from sqlalchemy import text
from sqlmodel import Session, create_engine

from app.config import settings

engine = create_engine(
    settings.sqlalchemy_url,
    echo=settings.sql_echo,
    pool_pre_ping=True,      # drop dead connections before handing them out
    pool_size=10,
    max_overflow=20,
    pool_recycle=1800,       # recycle connections every 30 min
)


def get_session() -> Iterator[Session]:
    """FastAPI dependency yielding a pooled session (auto-closed)."""
    with Session(engine) as session:
        yield session


def check_db() -> bool:
    """Lightweight connectivity probe for the health endpoint."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
