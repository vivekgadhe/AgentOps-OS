"""Privacy-conscious telemetry for provider and agent execution attempts."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    CheckConstraint,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from agentops.db.base import Base


class TelemetryEvent(Base):
    """One observable generation attempt; prompts and model outputs are never stored."""

    __tablename__ = "telemetry_events"
    __table_args__ = (
        CheckConstraint("event_type = 'llm_attempt'", name="event_type_valid"),
        CheckConstraint(
            "component IN ('llm', 'planner', 'agent', 'rag')",
            name="component_valid",
        ),
        CheckConstraint("outcome IN ('success', 'failure', 'refused')", name="outcome_valid"),
        CheckConstraint("length(btrim(provider)) > 0", name="provider_not_blank"),
        CheckConstraint("length(btrim(model)) > 0", name="model_not_blank"),
        CheckConstraint("duration_ms >= 0", name="duration_non_negative"),
        CheckConstraint("jsonb_typeof(attributes) = 'object'", name="attributes_object"),
        CheckConstraint(
            "input_tokens IS NULL OR input_tokens >= 0",
            name="input_tokens_non_negative",
        ),
        CheckConstraint(
            "output_tokens IS NULL OR output_tokens >= 0",
            name="output_tokens_non_negative",
        ),
        Index("ix_telemetry_events_owner_created", "owner_user_id", "created_at"),
        Index(
            "ix_telemetry_events_owner_provider_created",
            "owner_user_id",
            "provider",
            "created_at",
        ),
        Index(
            "ix_telemetry_events_owner_agent_created",
            "owner_user_id",
            "agent_name",
            "created_at",
        ),
        Index("ix_telemetry_events_workflow", "workflow_run_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    owner_user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    workflow_run_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("workflow_runs.id", ondelete="SET NULL"), nullable=True
    )
    request_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    event_type: Mapped[str] = mapped_column(
        String(32), nullable=False, default="llm_attempt", server_default=text("'llm_attempt'")
    )
    component: Mapped[str] = mapped_column(String(32), nullable=False, default="llm")
    agent_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    provider: Mapped[str] = mapped_column(String(32), nullable=False)
    model: Mapped[str] = mapped_column(String(120), nullable=False)
    outcome: Mapped[str] = mapped_column(String(16), nullable=False)
    duration_ms: Mapped[float] = mapped_column(Float, nullable=False)
    input_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    output_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    attributes: Mapped[dict[str, Any]] = mapped_column(
        default=dict, server_default=text("'{}'::jsonb"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(server_default=text("now()"))
