"""Single-use registration, invitation and password-reset OTP records."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, ForeignKey, Index, Integer, String, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column

from agentops.db.base import Base


class AuthActionToken(Base):
    """Store only a keyed HMAC digest of a one-time authentication OTP.

    Registration and password-reset tokens have no assigned role. Optional
    invitation tokens may carry a role chosen by an administrator. Raw OTPs
    are sent by the backend mailer and are never stored in the database.
    """

    __tablename__ = "auth_action_tokens"
    __table_args__ = (
        UniqueConstraint("token_hash", name="uq_auth_action_tokens_token_hash"),
        CheckConstraint(
            "purpose IN ('invitation', 'registration', 'password_reset')",
            name="purpose_valid",
        ),
        CheckConstraint(
            "(purpose = 'invitation' AND role IN ('admin', 'operator', 'viewer')) OR "
            "(purpose IN ('registration', 'password_reset') AND role IS NULL)",
            name="purpose_role_consistent",
        ),
        CheckConstraint("email = lower(email)", name="email_lowercase"),
        CheckConstraint("length(btrim(email)) > 0", name="email_not_blank"),
        CheckConstraint("length(token_hash) = 64", name="token_hash_length"),
        CheckConstraint("expires_at > created_at", name="expires_after_created"),
        CheckConstraint(
            "attempts >= 0 AND max_attempts BETWEEN 1 AND 10 AND attempts <= max_attempts",
            name="attempts_nonnegative",
        ),
        Index("ix_auth_action_tokens_email_purpose_expires", "email", "purpose", "expires_at"),
        Index("ix_auth_action_tokens_created_by", "created_by_user_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    purpose: Mapped[str] = mapped_column(String(20))
    email: Mapped[str] = mapped_column(String(320))
    role: Mapped[str | None] = mapped_column(String(16), nullable=True)
    token_hash: Mapped[str] = mapped_column(String(64))
    created_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(server_default=text("now()"))
    expires_at: Mapped[datetime]
    attempts: Mapped[int] = mapped_column(Integer, default=0, server_default=text("0"))
    max_attempts: Mapped[int] = mapped_column(Integer, default=5, server_default=text("5"))
    consumed_at: Mapped[datetime | None] = mapped_column(nullable=True)
    revoked_at: Mapped[datetime | None] = mapped_column(nullable=True)
