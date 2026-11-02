"""Add per-user AI provider settings and persistent approval requests.

Revision ID: 0003
Revises: 0002
Create Date: 2026-10-31
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "ai_provider_configs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("owner_user_id", sa.Uuid(), nullable=False),
        sa.Column("provider", sa.String(length=20), nullable=False),
        sa.Column("model_name", sa.String(length=120), nullable=False),
        sa.Column("api_key_ciphertext", sa.Text(), nullable=True),
        sa.Column("base_url", sa.String(length=500), nullable=True),
        sa.Column("priority", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("enabled", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column(
            "metadata_json",
            postgresql.JSONB(none_as_null=True),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_ai_provider_configs")),
        sa.ForeignKeyConstraint(
            ["owner_user_id"], ["users.id"],
            name=op.f("fk_ai_provider_configs_owner_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint(
            "owner_user_id", "provider",
            name=op.f("uq_ai_provider_configs_owner_provider"),
        ),
        sa.CheckConstraint(
            "provider IN ('openai', 'groq', 'ollama')",
            name=op.f("ck_ai_provider_configs_provider_valid"),
        ),
        sa.CheckConstraint(
            "length(btrim(model_name)) > 0",
            name=op.f("ck_ai_provider_configs_model_name_not_blank"),
        ),
        sa.CheckConstraint(
            "priority >= 0",
            name=op.f("ck_ai_provider_configs_priority_non_negative"),
        ),
        sa.CheckConstraint(
            "provider = 'ollama' OR api_key_ciphertext IS NOT NULL",
            name=op.f("ck_ai_provider_configs_hosted_provider_requires_encrypted_key"),
        ),
    )
    op.create_index(
        op.f("ix_ai_provider_configs_owner_enabled_priority"),
        "ai_provider_configs",
        ["owner_user_id", "enabled", "priority"],
    )

    op.create_table(
        "approval_requests",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("workflow_run_id", sa.Uuid(), nullable=False),
        sa.Column("task_run_id", sa.Uuid(), nullable=False),
        sa.Column("requester_user_id", sa.Uuid(), nullable=False),
        sa.Column("decided_by_user_id", sa.Uuid(), nullable=True),
        sa.Column("tool_name", sa.String(length=100), nullable=False),
        sa.Column("action_summary", sa.String(length=500), nullable=False),
        sa.Column("input_snapshot", postgresql.JSONB(none_as_null=True), nullable=False),
        sa.Column("status", sa.String(length=16), server_default=sa.text("'pending'"), nullable=False),
        sa.Column("decision_reason", sa.Text(), nullable=True),
        sa.Column("requested_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_approval_requests")),
        sa.ForeignKeyConstraint(
            ["workflow_run_id"], ["workflow_runs.id"],
            name=op.f("fk_approval_requests_workflow_run_id_workflow_runs"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["task_run_id", "workflow_run_id"],
            ["task_runs.id", "task_runs.workflow_run_id"],
            name=op.f("fk_approval_requests_task_in_workflow"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["requester_user_id"], ["users.id"],
            name=op.f("fk_approval_requests_requester_user_id_users"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["decided_by_user_id"], ["users.id"],
            name=op.f("fk_approval_requests_decided_by_user_id_users"),
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint("task_run_id", name=op.f("uq_approval_requests_task_run_id")),
        sa.CheckConstraint(
            "status IN ('pending', 'approved', 'rejected', 'expired', 'cancelled', 'executed')",
            name=op.f("ck_approval_requests_status_valid"),
        ),
        sa.CheckConstraint(
            "length(btrim(tool_name)) > 0",
            name=op.f("ck_approval_requests_tool_name_not_blank"),
        ),
        sa.CheckConstraint(
            "length(btrim(action_summary)) > 0",
            name=op.f("ck_approval_requests_action_summary_not_blank"),
        ),
        sa.CheckConstraint(
            "expires_at > requested_at",
            name=op.f("ck_approval_requests_expires_after_requested"),
        ),
        sa.CheckConstraint(
            "status NOT IN ('approved', 'rejected', 'executed') OR decided_at IS NOT NULL",
            name=op.f("ck_approval_requests_decision_timestamp_required"),
        ),
    )
    op.create_index(
        op.f("ix_approval_requests_status_expires_at"),
        "approval_requests",
        ["status", "expires_at"],
    )
    op.create_index(
        op.f("ix_approval_requests_requester_status"),
        "approval_requests",
        ["requester_user_id", "status"],
    )
    op.create_index(
        op.f("ix_approval_requests_workflow_status"),
        "approval_requests",
        ["workflow_run_id", "status"],
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_approval_requests_workflow_status"), table_name="approval_requests")
    op.drop_index(op.f("ix_approval_requests_requester_status"), table_name="approval_requests")
    op.drop_index(op.f("ix_approval_requests_status_expires_at"), table_name="approval_requests")
    op.drop_table("approval_requests")
    op.drop_index(op.f("ix_ai_provider_configs_owner_enabled_priority"), table_name="ai_provider_configs")
    op.drop_table("ai_provider_configs")
