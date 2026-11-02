"""Persistent human approval requests for sensitive workflow tasks."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from agentops.db.base import Base


class ApprovalRequest(Base):
    """Approval decision bound to one task in one workflow."""

    __tablename__ = "approval_requests"
    __table_args__ = (
        ForeignKeyConstraint(
            ["task_run_id", "workflow_run_id"],
            ["task_runs.id", "task_runs.workflow_run_id"],
            name="fk_approval_requests_task_in_workflow",
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["requester_user_id"],
            ["users.id"],
            name="fk_approval_requests_requester_user_id_users",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["decided_by_user_id"],
            ["users.id"],
            name="fk_approval_requests_decided_by_user_id_users",
            ondelete="RESTRICT",
        ),
        UniqueConstraint("task_run_id", name="uq_approval_requests_task_run_id"),
        CheckConstraint(
            "status IN ('pending', 'approved', 'rejected', 'expired', 'cancelled', 'executed')",
            name="status_valid",
        ),
        CheckConstraint("length(btrim(tool_name)) > 0", name="tool_name_not_blank"),
        CheckConstraint("length(btrim(action_summary)) > 0", name="action_summary_not_blank"),
        CheckConstraint("expires_at > requested_at", name="expires_after_requested"),
        CheckConstraint(
            "status NOT IN ('approved', 'rejected', 'executed') OR decided_at IS NOT NULL",
            name="decision_timestamp_required",
        ),
        Index("ix_approval_requests_status_expires_at", "status", "expires_at"),
        Index("ix_approval_requests_requester_status", "requester_user_id", "status"),
        Index("ix_approval_requests_workflow_status", "workflow_run_id", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    workflow_run_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("workflow_runs.id", ondelete="CASCADE"), nullable=False
    )
    task_run_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    requester_user_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    decided_by_user_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True)
    tool_name: Mapped[str] = mapped_column(String(100), nullable=False)
    action_summary: Mapped[str] = mapped_column(String(500), nullable=False)
    input_snapshot: Mapped[dict[str, Any]] = mapped_column(default=dict, nullable=False)
    status: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default="pending",
        server_default=text("'pending'"),
    )
    decision_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    requested_at: Mapped[datetime] = mapped_column(server_default=text("now()"))
    expires_at: Mapped[datetime] = mapped_column(nullable=False)
    decided_at: Mapped[datetime | None] = mapped_column(nullable=True)
