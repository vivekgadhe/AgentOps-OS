"""Add privacy-conscious LLM and agent-attributed telemetry.

Revision ID: 0005
Revises: 0004
Create Date: 2026-11-04
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0005"
down_revision: str | None = "0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "telemetry_events",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("owner_user_id", sa.Uuid(), nullable=False),
        sa.Column("workflow_run_id", sa.Uuid(), nullable=True),
        sa.Column("request_id", sa.String(length=64), nullable=True),
        sa.Column(
            "event_type",
            sa.String(length=32),
            server_default=sa.text("'llm_attempt'"),
            nullable=False,
        ),
        sa.Column("component", sa.String(length=32), nullable=False),
        sa.Column("agent_name", sa.String(length=100), nullable=True),
        sa.Column("provider", sa.String(length=32), nullable=False),
        sa.Column("model", sa.String(length=120), nullable=False),
        sa.Column("outcome", sa.String(length=16), nullable=False),
        sa.Column("duration_ms", sa.Float(), nullable=False),
        sa.Column("input_tokens", sa.Integer(), nullable=True),
        sa.Column("output_tokens", sa.Integer(), nullable=True),
        sa.Column("error_type", sa.String(length=100), nullable=True),
        sa.Column(
            "attributes",
            postgresql.JSONB(none_as_null=True),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_telemetry_events")),
        sa.ForeignKeyConstraint(
            ["owner_user_id"],
            ["users.id"],
            name=op.f("fk_telemetry_events_owner_user_id_users"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["workflow_run_id"],
            ["workflow_runs.id"],
            name=op.f("fk_telemetry_events_workflow_run_id_workflow_runs"),
            ondelete="SET NULL",
        ),
        sa.CheckConstraint(
            "event_type = 'llm_attempt'",
            name=op.f("ck_telemetry_events_event_type_valid"),
        ),
        sa.CheckConstraint(
            "component IN ('llm', 'planner', 'agent', 'rag')",
            name=op.f("ck_telemetry_events_component_valid"),
        ),
        sa.CheckConstraint(
            "outcome IN ('success', 'failure', 'refused')",
            name=op.f("ck_telemetry_events_outcome_valid"),
        ),
        sa.CheckConstraint(
            "length(btrim(provider)) > 0",
            name=op.f("ck_telemetry_events_provider_not_blank"),
        ),
        sa.CheckConstraint(
            "length(btrim(model)) > 0",
            name=op.f("ck_telemetry_events_model_not_blank"),
        ),
        sa.CheckConstraint(
            "duration_ms >= 0",
            name=op.f("ck_telemetry_events_duration_non_negative"),
        ),
        sa.CheckConstraint(
            "jsonb_typeof(attributes) = 'object'",
            name=op.f("ck_telemetry_events_attributes_object"),
        ),
        sa.CheckConstraint(
            "input_tokens IS NULL OR input_tokens >= 0",
            name=op.f("ck_telemetry_events_input_tokens_non_negative"),
        ),
        sa.CheckConstraint(
            "output_tokens IS NULL OR output_tokens >= 0",
            name=op.f("ck_telemetry_events_output_tokens_non_negative"),
        ),
    )
    op.create_index(
        "ix_telemetry_events_owner_created",
        "telemetry_events",
        ["owner_user_id", "created_at"],
    )
    op.create_index(
        "ix_telemetry_events_owner_provider_created",
        "telemetry_events",
        ["owner_user_id", "provider", "created_at"],
    )
    op.create_index(
        "ix_telemetry_events_owner_agent_created",
        "telemetry_events",
        ["owner_user_id", "agent_name", "created_at"],
    )
    op.create_index(
        "ix_telemetry_events_workflow",
        "telemetry_events",
        ["workflow_run_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_telemetry_events_workflow", table_name="telemetry_events")
    op.drop_index(
        "ix_telemetry_events_owner_agent_created",
        table_name="telemetry_events",
    )
    op.drop_index(
        "ix_telemetry_events_owner_provider_created",
        table_name="telemetry_events",
    )
    op.drop_index(
        "ix_telemetry_events_owner_created",
        table_name="telemetry_events",
    )
    op.drop_table("telemetry_events")
