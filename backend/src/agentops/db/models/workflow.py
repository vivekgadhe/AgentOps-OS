"""Workflow runs, their tasks, the dependency graph, and execution events."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    ForeignKey,
    ForeignKeyConstraint,
    Identity,
    Index,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from agentops.db.base import Base, TimestampMixin
from agentops.db.models.enums import EventLevel, TaskStatus, WorkflowStatus, in_check


class WorkflowRun(TimestampMixin, Base):
    """One execution of a natural-language goal."""

    __tablename__ = "workflow_runs"
    __table_args__ = (
        CheckConstraint(in_check("status", WorkflowStatus), name="status_valid"),
        CheckConstraint("length(btrim(goal)) > 0", name="goal_not_blank"),
        CheckConstraint(
            "finished_at IS NULL OR started_at IS NULL OR finished_at >= started_at",
            name="finished_after_started",
        ),
        Index("ix_workflow_runs_created_by_created_at", "created_by", "created_at"),
        Index("ix_workflow_runs_status", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    created_by: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT", name="fk_workflow_runs_created_by_users")
    )
    goal: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(32), default=WorkflowStatus.PENDING.value)
    plan: Mapped[dict[str, Any] | None] = mapped_column()
    error: Mapped[dict[str, Any] | None] = mapped_column()
    started_at: Mapped[datetime | None] = mapped_column()
    finished_at: Mapped[datetime | None] = mapped_column()
    tasks: Mapped[list[TaskRun]] = relationship(
        back_populates="workflow",
        cascade="all, delete-orphan",
        order_by="TaskRun.created_at",
    )

class TaskRun(TimestampMixin, Base):
    """One node of a workflow's task graph."""

    __tablename__ = "task_runs"
    __table_args__ = (
        UniqueConstraint("workflow_run_id", "key", name="uq_task_runs_workflow_run_id_key"),
        # Lets other tables reference (id, workflow_run_id) as a pair, which is how
        # the database proves two tasks belong to the same workflow.
        UniqueConstraint("id", "workflow_run_id", name="uq_task_runs_id_workflow_run_id"),
        CheckConstraint(in_check("status", TaskStatus), name="status_valid"),
        CheckConstraint("length(btrim(key)) > 0", name="key_not_blank"),
        CheckConstraint("length(btrim(name)) > 0", name="name_not_blank"),
        CheckConstraint("attempt_count >= 0", name="attempts_non_negative"),
        CheckConstraint("max_attempts >= 1", name="max_attempts_positive"),
        CheckConstraint("attempt_count <= max_attempts", name="attempts_within_max"),
        CheckConstraint("timeout_seconds > 0", name="timeout_positive"),
        CheckConstraint(
            "finished_at IS NULL OR started_at IS NULL OR finished_at >= started_at",
            name="finished_after_started",
        ),
        Index("ix_task_runs_workflow_run_id_status", "workflow_run_id", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    workflow_run_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(
            "workflow_runs.id",
            ondelete="CASCADE",
            name="fk_task_runs_workflow_run_id_workflow_runs",
        )
    )
    key: Mapped[str] = mapped_column(String(64))
    name: Mapped[str] = mapped_column(String(200))
    # Plain text on purpose: the tool registry does not exist yet (Phase 4).
    tool_name: Mapped[str | None] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(32), default=TaskStatus.PENDING.value)
    input_data: Mapped[dict[str, Any] | None] = mapped_column()
    output_data: Mapped[dict[str, Any] | None] = mapped_column()
    error: Mapped[dict[str, Any] | None] = mapped_column()
    attempt_count: Mapped[int] = mapped_column(server_default=text("0"))
    max_attempts: Mapped[int] = mapped_column(server_default=text("3"))
    timeout_seconds: Mapped[int] = mapped_column(server_default=text("300"))
    started_at: Mapped[datetime | None] = mapped_column()
    finished_at: Mapped[datetime | None] = mapped_column()
    workflow: Mapped[WorkflowRun] = relationship(
        back_populates="tasks",
    )


class TaskDependency(Base):
    """Edge of the task graph: ``task_id`` waits for ``depends_on_task_id``.

    Both composite foreign keys include ``workflow_run_id``, so the database
    itself rejects an edge between tasks of different workflows. Cycles cannot
    be expressed as a SQL constraint; the planner checks them in Phase 3.
    """

    __tablename__ = "task_dependencies"
    __table_args__ = (
        ForeignKeyConstraint(
            ["task_id", "workflow_run_id"],
            ["task_runs.id", "task_runs.workflow_run_id"],
            name="fk_task_deps_task_in_workflow",
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["depends_on_task_id", "workflow_run_id"],
            ["task_runs.id", "task_runs.workflow_run_id"],
            name="fk_task_deps_dependency_in_workflow",
            ondelete="CASCADE",
        ),
        CheckConstraint("task_id <> depends_on_task_id", name="no_self_dependency"),
        Index("ix_task_deps_workflow_run_id", "workflow_run_id"),
        Index("ix_task_deps_depends_on_task_id", "depends_on_task_id"),
    )

    task_id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    depends_on_task_id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    workflow_run_id: Mapped[uuid.UUID] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(server_default=text("now()"))


class ExecutionEvent(Base):
    """Append-only operational log entry shown on the observability dashboard."""

    __tablename__ = "execution_events"
    __table_args__ = (
        # task_run_id may be NULL (workflow-level event). When it is set, the
        # composite key proves the task belongs to the same workflow.
        ForeignKeyConstraint(
            ["task_run_id", "workflow_run_id"],
            ["task_runs.id", "task_runs.workflow_run_id"],
            name="fk_execution_events_task_in_workflow",
            ondelete="CASCADE",
        ),
        CheckConstraint(in_check("level", EventLevel), name="level_valid"),
        CheckConstraint("length(btrim(event_type)) > 0", name="event_type_not_blank"),
        Index("ix_execution_events_workflow_run_id_id", "workflow_run_id", "id"),
        Index("ix_execution_events_task_run_id", "task_run_id"),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    workflow_run_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(
            "workflow_runs.id",
            ondelete="CASCADE",
            name="fk_execution_events_workflow_run_id_workflow_runs",
        )
    )
    task_run_id: Mapped[uuid.UUID | None] = mapped_column()
    event_type: Mapped[str] = mapped_column(String(64))
    level: Mapped[str] = mapped_column(String(16), default=EventLevel.INFO.value)
    message: Mapped[str] = mapped_column(Text)
    data: Mapped[dict[str, Any]] = mapped_column(default=dict)
    request_id: Mapped[str | None] = mapped_column(String(64))
    occurred_at: Mapped[datetime] = mapped_column(server_default=text("now()"))
