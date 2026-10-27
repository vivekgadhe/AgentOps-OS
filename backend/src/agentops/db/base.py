"""Declarative base, naming convention, and shared column types.

Why a naming convention? Without one PostgreSQL invents constraint names, and
Alembic cannot reliably drop or alter them later. Every constraint and index in
this project therefore has a predictable, explicit name.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, MetaData, func, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

NAMING_CONVENTION = {
    "ix": "ix_%(table_name)s_%(column_0_N_name)s",
    "uq": "uq_%(table_name)s_%(column_0_N_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_N_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """Base class for all ORM models."""

    metadata = MetaData(naming_convention=NAMING_CONVENTION)
    type_annotation_map = {
        # Every datetime is timezone-aware (timestamptz) in PostgreSQL.
        datetime: DateTime(timezone=True),
        # Python None is stored as SQL NULL, not as the JSON value "null".
        dict[str, Any]: JSONB(none_as_null=True),
    }


class TimestampMixin:
    """``created_at`` / ``updated_at`` columns for mutable tables.

    ``created_at`` is set by the database. ``updated_at`` is set by the database
    on insert and by the ORM (``onupdate``) on ORM updates. Raw SQL updates do
    NOT refresh it. Inside one transaction ``now()`` is the transaction start.
    """

    created_at: Mapped[datetime] = mapped_column(server_default=text("now()"))
    updated_at: Mapped[datetime] = mapped_column(server_default=text("now()"), onupdate=func.now())
