"""Persistent, owner-scoped episodic and semantic agent memories."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pgvector.sqlalchemy import VECTOR
from sqlalchemy import (
    CheckConstraint,
    Float,
    ForeignKey,
    Index,
    String,
    Text,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from agentops.db.base import Base, TimestampMixin

EMBEDDING_DIMENSIONS = 768


class AgentMemory(TimestampMixin, Base):
    """One persistent memory owned by a user and optionally scoped to an agent."""

    __tablename__ = "agent_memories"
    __table_args__ = (
        CheckConstraint(
            "memory_type IN ('episodic', 'semantic')",
            name="memory_type_valid",
        ),
        CheckConstraint(
            "memory_scope IN ('user', 'agent')",
            name="memory_scope_valid",
        ),
        CheckConstraint(
            "(memory_scope = 'user' AND agent_key IS NULL) OR "
            "(memory_scope = 'agent' AND agent_key IS NOT NULL "
            "AND agent_key ~ '^[a-z][a-z0-9_]{0,99}$')",
            name="scope_agent_key_consistent",
        ),
        CheckConstraint(
            "source_type IN ('user', 'agent', 'workflow')",
            name="source_type_valid",
        ),
        CheckConstraint(
            "(source_type = 'workflow' AND source_workflow_run_id IS NOT NULL) OR "
            "(source_type IN ('user', 'agent') AND source_workflow_run_id IS NULL)",
            name="source_workflow_consistent",
        ),
        CheckConstraint("length(btrim(content)) > 0", name="content_not_blank"),
        CheckConstraint("length(btrim(embedding_model)) > 0", name="embedding_model_not_blank"),
        CheckConstraint("confidence >= 0 AND confidence <= 1", name="confidence_in_range"),
        CheckConstraint("importance >= 0 AND importance <= 1", name="importance_in_range"),
        Index(
            "ix_agent_memories_owner_scope_type_created",
            "owner_user_id",
            "memory_scope",
            "memory_type",
            "created_at",
        ),
        Index("ix_agent_memories_expires_at", "expires_at"),
        Index(
            "ix_agent_memories_embedding_hnsw",
            "embedding",
            postgresql_using="hnsw",
            postgresql_with={"m": 16, "ef_construction": 64},
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    owner_user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    memory_type: Mapped[str] = mapped_column(String(16), nullable=False)
    memory_scope: Mapped[str] = mapped_column(String(16), nullable=False)
    agent_key: Mapped[str | None] = mapped_column(String(100), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[list[float]] = mapped_column(VECTOR(EMBEDDING_DIMENSIONS), nullable=False)
    embedding_model: Mapped[str] = mapped_column(String(100), nullable=False)
    confidence: Mapped[float] = mapped_column(
        Float, nullable=False, default=1.0, server_default=text("1.0")
    )
    importance: Mapped[float] = mapped_column(
        Float, nullable=False, default=0.5, server_default=text("0.5")
    )
    source_type: Mapped[str] = mapped_column(
        String(16), nullable=False, default="user", server_default=text("'user'")
    )
    source_workflow_run_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("workflow_runs.id", ondelete="RESTRICT"), nullable=True
    )
    metadata_json: Mapped[dict[str, Any]] = mapped_column(
        default=dict,
        server_default=text("'{}'::jsonb"),
        nullable=False,
    )
    last_accessed_at: Mapped[datetime] = mapped_column(
        server_default=text("now()"),
        nullable=False,
    )
    expires_at: Mapped[datetime | None] = mapped_column(nullable=True)
