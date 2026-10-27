"""Immutable audit trail.

Immutability is enforced by database triggers created in migration 0001:
UPDATE, DELETE and TRUNCATE on ``audit_logs`` raise an error. See the README
for the limits of that protection.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    ForeignKey,
    Identity,
    Index,
    String,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from agentops.db.base import Base
from agentops.db.models.enums import AuditOutcome, in_check


class AuditLog(Base):
    """One security-relevant action and its outcome."""

    __tablename__ = "audit_logs"
    __table_args__ = (
        CheckConstraint(in_check("outcome", AuditOutcome), name="outcome_valid"),
        CheckConstraint("length(btrim(action)) > 0", name="action_not_blank"),
        CheckConstraint("length(btrim(resource_type)) > 0", name="resource_type_not_blank"),
        Index("ix_audit_logs_actor_user_id_occurred_at", "actor_user_id", "occurred_at"),
        Index("ix_audit_logs_resource_type_resource_id", "resource_type", "resource_id"),
        Index("ix_audit_logs_occurred_at", "occurred_at"),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    occurred_at: Mapped[datetime] = mapped_column(server_default=text("now()"))
    # RESTRICT (not SET NULL): SET NULL would be an UPDATE the trigger must block.
    actor_user_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT", name="fk_audit_logs_actor_user_id_users")
    )
    action: Mapped[str] = mapped_column(String(100))
    resource_type: Mapped[str] = mapped_column(String(64))
    resource_id: Mapped[str | None] = mapped_column(String(128))
    outcome: Mapped[str] = mapped_column(String(16))
    request_id: Mapped[str | None] = mapped_column(String(64))
    ip_address: Mapped[str | None] = mapped_column(String(45))
    details: Mapped[dict[str, Any]] = mapped_column(default=dict)
