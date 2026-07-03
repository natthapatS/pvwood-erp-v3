-- PVWood ERP v3 — one-time database bootstrap.
--
-- Run once as the PostgreSQL superuser (the `postgres` role), e.g. on the server:
--   & "C:\Program Files\PostgreSQL\12\bin\psql.exe" -U postgres -h 127.0.0.1 -f scripts\bootstrap_db.sql
--
-- Creates the least-privilege app role + the dev / staging / prod databases.
-- After running: set the same password in `.env` (PG_PASSWORD=...), then
--   alembic upgrade head

-- 1) App login role (owns the v3 databases). CHANGE THE PASSWORD.
DO $$
BEGIN
   IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'pvwood') THEN
      CREATE ROLE pvwood LOGIN PASSWORD 'CHANGE_ME';
   END IF;
END
$$;

-- 2) Databases (owned by the app role). CREATE DATABASE cannot run inside a
--    transaction/DO block; these run as individual autocommit statements in psql.
--    Re-running errors with "already exists" — safe to ignore.
CREATE DATABASE pvwood_v3_dev      OWNER pvwood;
CREATE DATABASE pvwood_v3_staging  OWNER pvwood;
CREATE DATABASE pvwood_v3          OWNER pvwood;
