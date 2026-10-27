"""initial schema: users, workflow runs, tasks, dependencies, events, audit log

Revision ID: 0001
Revises:
Create Date: 2026-10-25

Written by hand and kept independent of the application's enums on purpose: a
migration is a frozen snapshot and must not change when application code does.
A test (test_no_drift_between_models_and_migrations) catches any mismatch
between this file and the ORM models.
"""

from collections.abc import Sequence
from typing import Any

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

USER_ROLES = ("admin", "operator", "viewer")
WORKFLOW_STATUSES = (
    "pending",
    "planning",
    "running",
    "awaiting_approval",
    "succeeded",
    "failed",
    "cancelled",
)
TASK_STATUSES = (
    "pending",
    "ready",
    "running",
    "awaiting_approval",
    "succeeded",
    "failed",
    "skipped",
    "cancelled",
)
EVENT_LEVELS = ("debug", "info", "warning", "error")
AUDIT_OUTCOMES = ("success", "denied", "failure")


def _in(column: str, values: tuple[str, ...]) -> str:
    return f"{column} IN ({', '.join(repr(v) for v in values)})"


def _created_at() -> sa.Column[Any]:
    return sa.Column(
        "created_at",
        sa.DateTime(timezone=True),
        server_default=sa.text("now()"),
        nullable=False,
    )


def _updated_at() -> sa.Column[Any]:
    return sa.Column(
        "updated_at",
        sa.DateTime(timezone=True),
        server_default=sa.text("now()"),
        nullable=False,
    )


def _nullable_json(name: str) -> sa.Column[Any]:
    return sa.Column(name, postgresql.JSONB(none_as_null=True), nullable=True)


_FINISHED_AFTER_STARTED = "finished_at IS NULL OR started_at IS NULL OR finished_at >= started_at"

_AUDIT_FUNCTION = """
CREATE FUNCTION audit_logs_reject_mutation() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
    RAISE EXCEPTION
        'audit_logs is append-only; UPDATE, DELETE and TRUNCATE are not permitted'
        USING ERRCODE = 'restrict_violation';
END;
$$
"""


def upgrade() -> None:
    # ---- users --------------------------------------------------------------
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=16), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        _created_at(),
        _updated_at(),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
        sa.UniqueConstraint("email", name=op.f("uq_users_email")),
        sa.CheckConstraint(_in("role", USER_ROLES), name=op.f("ck_users_role_valid")),
        sa.CheckConstraint("email = lower(email)", name=op.f("ck_users_email_lowercase")),
        sa.CheckConstraint("length(email) > 0", name=op.f("ck_users_email_not_empty")),
        sa.CheckConstraint(
            "length(password_hash) > 0", name=op.f("ck_users_password_hash_not_empty")
        ),
    )

    # ---- workflow_runs ------------------------------------------------------
    op.create_table(
        "workflow_runs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_by", sa.Uuid(), nullable=False),
        sa.Column("goal", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        _nullable_json("plan"),
        _nullable_json("error"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        _created_at(),
        _updated_at(),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_workflow_runs")),
        sa.ForeignKeyConstraint(
            ["created_by"],
            ["users.id"],
            name=op.f("fk_workflow_runs_created_by_users"),
            ondelete="RESTRICT",
        ),
        sa.CheckConstraint(
            _in("status", WORKFLOW_STATUSES),
            name=op.f("ck_workflow_runs_status_valid"),
        ),
        sa.CheckConstraint("length(btrim(goal)) > 0", name=op.f("ck_workflow_runs_goal_not_blank")),
        sa.CheckConstraint(
            _FINISHED_AFTER_STARTED,
            name=op.f("ck_workflow_runs_finished_after_started"),
        ),
    )
    op.create_index(
        op.f("ix_workflow_runs_created_by_created_at"),
        "workflow_runs",
        ["created_by", "created_at"],
    )
    op.create_index(op.f("ix_workflow_runs_status"), "workflow_runs", ["status"])

    # ---- task_runs ----------------------------------------------------------
    op.create_table(
        "task_runs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("workflow_run_id", sa.Uuid(), nullable=False),
        sa.Column("key", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("tool_name", sa.String(length=100), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        _nullable_json("input_data"),
        _nullable_json("output_data"),
        _nullable_json("error"),
        sa.Column("attempt_count", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("max_attempts", sa.Integer(), server_default=sa.text("3"), nullable=False),
        sa.Column(
            "timeout_seconds",
            sa.Integer(),
            server_default=sa.text("300"),
            nullable=False,
        ),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        _created_at(),
        _updated_at(),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_task_runs")),
        sa.ForeignKeyConstraint(
            ["workflow_run_id"],
            ["workflow_runs.id"],
            name=op.f("fk_task_runs_workflow_run_id_workflow_runs"),
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint(
            "workflow_run_id", "key", name=op.f("uq_task_runs_workflow_run_id_key")
        ),
        sa.UniqueConstraint("id", "workflow_run_id", name=op.f("uq_task_runs_id_workflow_run_id")),
        sa.CheckConstraint(_in("status", TASK_STATUSES), name=op.f("ck_task_runs_status_valid")),
        sa.CheckConstraint("length(btrim(key)) > 0", name=op.f("ck_task_runs_key_not_blank")),
        sa.CheckConstraint("length(btrim(name)) > 0", name=op.f("ck_task_runs_name_not_blank")),
        sa.CheckConstraint("attempt_count >= 0", name=op.f("ck_task_runs_attempts_non_negative")),
        sa.CheckConstraint("max_attempts >= 1", name=op.f("ck_task_runs_max_attempts_positive")),
        sa.CheckConstraint(
            "attempt_count <= max_attempts",
            name=op.f("ck_task_runs_attempts_within_max"),
        ),
        sa.CheckConstraint("timeout_seconds > 0", name=op.f("ck_task_runs_timeout_positive")),
        sa.CheckConstraint(
            _FINISHED_AFTER_STARTED, name=op.f("ck_task_runs_finished_after_started")
        ),
    )
    op.create_index(
        op.f("ix_task_runs_workflow_run_id_status"),
        "task_runs",
        ["workflow_run_id", "status"],
    )

    # ---- task_dependencies --------------------------------------------------
    op.create_table(
        "task_dependencies",
        sa.Column("task_id", sa.Uuid(), nullable=False),
        sa.Column("depends_on_task_id", sa.Uuid(), nullable=False),
        sa.Column("workflow_run_id", sa.Uuid(), nullable=False),
        _created_at(),
        sa.PrimaryKeyConstraint("task_id", "depends_on_task_id", name=op.f("pk_task_dependencies")),
        sa.ForeignKeyConstraint(
            ["task_id", "workflow_run_id"],
            ["task_runs.id", "task_runs.workflow_run_id"],
            name=op.f("fk_task_deps_task_in_workflow"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["depends_on_task_id", "workflow_run_id"],
            ["task_runs.id", "task_runs.workflow_run_id"],
            name=op.f("fk_task_deps_dependency_in_workflow"),
            ondelete="CASCADE",
        ),
        sa.CheckConstraint(
            "task_id <> depends_on_task_id",
            name=op.f("ck_task_dependencies_no_self_dependency"),
        ),
    )
    op.create_index(op.f("ix_task_deps_workflow_run_id"), "task_dependencies", ["workflow_run_id"])
    op.create_index(
        op.f("ix_task_deps_depends_on_task_id"),
        "task_dependencies",
        ["depends_on_task_id"],
    )

    # ---- execution_events ---------------------------------------------------
    op.create_table(
        "execution_events",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), nullable=False),
        sa.Column("workflow_run_id", sa.Uuid(), nullable=False),
        sa.Column("task_run_id", sa.Uuid(), nullable=True),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("level", sa.String(length=16), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("data", postgresql.JSONB(none_as_null=True), nullable=False),
        sa.Column("request_id", sa.String(length=64), nullable=True),
        sa.Column(
            "occurred_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_execution_events")),
        sa.ForeignKeyConstraint(
            ["workflow_run_id"],
            ["workflow_runs.id"],
            name=op.f("fk_execution_events_workflow_run_id_workflow_runs"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["task_run_id", "workflow_run_id"],
            ["task_runs.id", "task_runs.workflow_run_id"],
            name=op.f("fk_execution_events_task_in_workflow"),
            ondelete="CASCADE",
        ),
        sa.CheckConstraint(
            _in("level", EVENT_LEVELS), name=op.f("ck_execution_events_level_valid")
        ),
        sa.CheckConstraint(
            "length(btrim(event_type)) > 0",
            name=op.f("ck_execution_events_event_type_not_blank"),
        ),
    )
    op.create_index(
        op.f("ix_execution_events_workflow_run_id_id"),
        "execution_events",
        ["workflow_run_id", "id"],
    )
    op.create_index(op.f("ix_execution_events_task_run_id"), "execution_events", ["task_run_id"])

    # ---- audit_logs ---------------------------------------------------------
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), nullable=False),
        sa.Column(
            "occurred_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("actor_user_id", sa.Uuid(), nullable=True),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("resource_type", sa.String(length=64), nullable=False),
        sa.Column("resource_id", sa.String(length=128), nullable=True),
        sa.Column("outcome", sa.String(length=16), nullable=False),
        sa.Column("request_id", sa.String(length=64), nullable=True),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("details", postgresql.JSONB(none_as_null=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_audit_logs")),
        sa.ForeignKeyConstraint(
            ["actor_user_id"],
            ["users.id"],
            name=op.f("fk_audit_logs_actor_user_id_users"),
            ondelete="RESTRICT",
        ),
        sa.CheckConstraint(
            _in("outcome", AUDIT_OUTCOMES), name=op.f("ck_audit_logs_outcome_valid")
        ),
        sa.CheckConstraint(
            "length(btrim(action)) > 0", name=op.f("ck_audit_logs_action_not_blank")
        ),
        sa.CheckConstraint(
            "length(btrim(resource_type)) > 0",
            name=op.f("ck_audit_logs_resource_type_not_blank"),
        ),
    )
    op.create_index(
        op.f("ix_audit_logs_actor_user_id_occurred_at"),
        "audit_logs",
        ["actor_user_id", "occurred_at"],
    )
    op.create_index(
        op.f("ix_audit_logs_resource_type_resource_id"),
        "audit_logs",
        ["resource_type", "resource_id"],
    )
    op.create_index(op.f("ix_audit_logs_occurred_at"), "audit_logs", ["occurred_at"])

    # Immutability: reject UPDATE / DELETE per row and TRUNCATE per statement.
    op.execute(_AUDIT_FUNCTION)
    op.execute(
        "CREATE TRIGGER audit_logs_no_update_delete "
        "BEFORE UPDATE OR DELETE ON audit_logs "
        "FOR EACH ROW EXECUTE FUNCTION audit_logs_reject_mutation()"
    )
    op.execute(
        "CREATE TRIGGER audit_logs_no_truncate "
        "BEFORE TRUNCATE ON audit_logs "
        "FOR EACH STATEMENT EXECUTE FUNCTION audit_logs_reject_mutation()"
    )


def downgrade() -> None:
    # DESTRUCTIVE: removes every table (and all data) created by this revision.
    # Dropping audit_logs removes its triggers; the function is dropped after.
    op.drop_table("audit_logs")
    op.execute("DROP FUNCTION audit_logs_reject_mutation()")
    op.drop_table("execution_events")
    op.drop_table("task_dependencies")
    op.drop_table("task_runs")
    op.drop_table("workflow_runs")
    op.drop_table("users")
