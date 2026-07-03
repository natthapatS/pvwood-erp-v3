"""Env-driven configuration — the single source of truth for settings.

Values come from the process environment or a local `.env` file (gitignored).
Either set a full ``DATABASE_URL`` or the discrete ``PG_*`` parts; the URL is
assembled with an ``sslmode`` query so the same code reaches a local instance
now and a network/offsite instance later without changes.
"""
from functools import lru_cache
from urllib.parse import quote_plus

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    app_env: str = "dev"                 # dev | staging | prod
    app_name: str = "PVWood ERP v3"

    # Full URL wins if provided; otherwise assembled from the PG_* parts below.
    database_url: str | None = None
    pg_host: str = "127.0.0.1"
    pg_port: int = 5432
    pg_db: str = "pvwood_v3_dev"
    pg_user: str = "pvwood"
    pg_password: str = ""
    pg_sslmode: str = "prefer"           # prefer | require | disable

    sql_echo: bool = False

    @computed_field  # type: ignore[prop-decorator]
    @property
    def sqlalchemy_url(self) -> str:
        """SQLAlchemy URL for the psycopg (v3) driver."""
        if self.database_url:
            return self.database_url
        user = quote_plus(self.pg_user)
        pwd = quote_plus(self.pg_password)
        return (
            f"postgresql+psycopg://{user}:{pwd}"
            f"@{self.pg_host}:{self.pg_port}/{self.pg_db}"
            f"?sslmode={self.pg_sslmode}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
