"""Application users (identity and role only; login is a later milestone)."""

from __future__ import annotations

import uuid

from sqlalchemy import CheckConstraint, String, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, validates

from agentops.db.base import Base, TimestampMixin
from agentops.db.models.enums import UserRole, in_check


class User(TimestampMixin, Base):
    """A person who can use the platform.

    Users are deactivated (``is_active = false``), never deleted: workflow runs
    and audit records reference them with ON DELETE RESTRICT.
    """

    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("email", name="uq_users_email"),
        CheckConstraint(in_check("role", UserRole), name="role_valid"),
        # Case-insensitive uniqueness without a functional index: emails are
        # stored lowercase, and the database rejects anything else.
        CheckConstraint("email = lower(email)", name="email_lowercase"),
        CheckConstraint("length(email) > 0", name="email_not_empty"),
        CheckConstraint("length(password_hash) > 0", name="password_hash_not_empty"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(320))
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(16), default=UserRole.VIEWER.value)
    is_active: Mapped[bool] = mapped_column(default=True, server_default=text("true"))

    @validates("email")
    def _normalise_email(self, _key: str, value: str) -> str:
        return value.strip().lower()
