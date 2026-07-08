"""Domain 1c — Logs (PVS raw material).

LogArrival (a container arrival = the lot) → Log (each individual log, with
dual-unit dimensions; a service fills any missing unit) → LogDocument (photos /
certs uploaded to a stored path). Logs are consumed by PVS runs and their yield is
tracked per log (see LogProcessing in domain 5).
"""
from datetime import date, datetime

from sqlalchemy import DateTime
from sqlmodel import Field

from app.models.core import TimestampMixin, utcnow


class LogArrival(TimestampMixin, table=True):
    __tablename__ = "log_arrival"

    id: int | None = Field(default=None, primary_key=True)
    arrival_code: str = Field(unique=True, index=True, max_length=64)  # container lot no.
    arrival_date: date | None = None
    supplier_id: int | None = Field(default=None, foreign_key="supplier.id")
    container_ref: str = ""
    notes: str = ""


class Log(TimestampMixin, table=True):
    __tablename__ = "log"

    id: int | None = Field(default=None, primary_key=True)
    log_number: str = Field(unique=True, index=True, max_length=64)
    arrival_id: int = Field(foreign_key="log_arrival.id", index=True)
    log_code: str = Field(index=True, max_length=64)    # generic: species + grade
    species_id: int | None = Field(default=None, foreign_key="species.id")
    grade: str | None = None

    # dual-unit dimensions (a service fills any missing unit on entry)
    length_in: float | None = None
    length_m: float | None = None
    diameter_in: float | None = None
    diameter_m: float | None = None
    volume_ft3: float | None = None
    volume_m3: float | None = None

    status: str = "IN_YARD"                     # IN_YARD | HEATING | PROCESSING | CONSUMED
    notes: str = ""


class LogDocument(TimestampMixin, table=True):
    """Photo / certificate attached to a log (uploaded -> stored path)."""

    __tablename__ = "log_document"

    id: int | None = Field(default=None, primary_key=True)
    log_id: int = Field(foreign_key="log.id", index=True)
    doc_type: str = "PHOTO"                      # PHOTO | CERT | OTHER
    filename: str
    stored_path: str
    content_type: str = ""
    file_size: int = 0
    uploaded_by: str | None = None
    uploaded_at: datetime = Field(
        default_factory=utcnow, sa_type=DateTime(timezone=True), nullable=False
    )
    notes: str = ""
