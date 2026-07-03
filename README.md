# PVWood ERP v3

Greenfield rebuild of the PVWood veneer / wood-panel ERP on **FastAPI + SQLModel +
PostgreSQL** (Alembic migrations). Replaces the legacy embedded-SQLite app while it keeps
running untouched.

See the migration plan and domain design in the build notes. High level:

- **12-domain model** (SQLModel) — master data, BOM, procurement, RM lot tracking,
  production, traceability, feed-center grading, finished goods, sales, barcode, cost.
- **Universal lot traceability** — lot codes identify purchased RM *and* internally
  transformed materials (grade / splice / cut) with parent→child genealogy + cost flow.
- **Mobile QR/DataMatrix scanning** inside the Warehouse + Production portals.
- **Per-batch TAS 2 cost accounting**.

## Stack

- Python 3.14, FastAPI, SQLModel (SQLAlchemy 2.0 + Pydantic v2), `psycopg` v3.
- PostgreSQL (dev against the existing local instance; a supported PG 16/17 before
  production cutover).
- Alembic for versioned migrations (no more ad-hoc `init_db()`).

## Layout

```
app/
  config.py        env-driven settings (DATABASE_URL / discrete PG_* + sslmode)
  db.py            SQLAlchemy engine + pooled Session dependency
  main.py          FastAPI app + /api/health
  models/          one module per domain (SQLModel tables) -> SQLModel.metadata
alembic/           migration environment + versions
scripts/           ETL + ops scripts
tests/             pytest suite
```

## Dev quickstart

1. `python -m venv .venv && .venv\Scripts\activate`
2. `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and fill in a working `DATABASE_URL` (or `PG_*`).
4. `alembic upgrade head`
5. `uvicorn app.main:app --reload` → http://127.0.0.1:8001/api/health

## Ports

Dev runs on **8001** to stay clear of the legacy app on 8000.
