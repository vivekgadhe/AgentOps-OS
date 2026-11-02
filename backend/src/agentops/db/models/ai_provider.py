"""Per-user AI provider configuration with encrypted credentials."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from agentops.db.base import Base, TimestampMixin


class AIProviderConfig(TimestampMixin, Base):
    """A user's configured generation provider and its fallback priority."""

    __tablename__ = "ai_provider_configs"
    __table_args__ = (
        UniqueConstraint("owner_user_id", "provider", name="uq_ai_provider_configs_owner_provider"),
        CheckConstraint(
            "provider IN ('openai', 'groq', 'ollama')",
            name="provider_valid",
        ),
        CheckConstraint("length(btrim(model_name)) > 0", name="model_name_not_blank"),
        CheckConstraint("priority >= 0", name="priority_non_negative"),
        CheckConstraint(
            "provider = 'ollama' OR api_key_ciphertext IS NOT NULL",
            name="hosted_provider_requires_encrypted_key",
        ),
        Index(
            "ix_ai_provider_configs_owner_enabled_priority",
            "owner_user_id",
            "enabled",
            "priority",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    owner_user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    provider: Mapped[str] = mapped_column(String(20), nullable=False)
    model_name: Mapped[str] = mapped_column(String(120), nullable=False)
    api_key_ciphertext: Mapped[str | None] = mapped_column(Text, nullable=True)
    base_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    priority: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default=text("0"),
    )
    enabled: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=text("true"),
    )
    metadata_json: Mapped[dict[str, Any]] = mapped_column(
        default=dict, server_default=text("'{}'::jsonb"), nullable=False
    )
