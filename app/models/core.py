"""Cross-cutting utility tables (not part of a business domain)."""
from datetime import datetime, timezone

from sqlalchemy import DateTime
from sqlmodel import Field, SQLModel


def utcnow() -> datetime:
    """Timezone-aware UTC now (datetime.utcnow is deprecated on 3.12+)."""
    return datetime.now(timezone.utc)


class TimestampMixin(SQLModel):
    """Adds created_at / updated_at to a table model. Non-table mixin.

    Bump ``updated_at`` in the service layer on write (a future DB trigger can
    enforce it). Both are timezone-aware UTC.
    """

    created_at: datetime = Field(
        default_factory=utcnow, sa_type=DateTime(timezone=True), nullable=False
    )
    updated_at: datetime = Field(
        default_factory=utcnow, sa_type=DateTime(timezone=True), nullable=False
    )


class AppMeta(SQLModel, table=True):
    """Small key/value store for app-level metadata (schema tag, seed flags…).

    Also serves as the first real table so the Alembic baseline is non-empty and
    the migration pipeline is exercised end-to-end from Phase 0.
    """

    __tablename__ = "app_meta"

    key: str = Field(primary_key=True, max_length=64)
    value: str = ""
    updated_at: datetime = Field(
        default_factory=utcnow, sa_type=DateTime(timezone=True), nullable=False
    )
