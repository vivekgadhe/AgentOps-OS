"""Add persistent, owner-scoped agent memories.

Revision ID: 0004
Revises: 0003
Create Date: 2026-11-03
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import VECTOR
from sqlalchemy.dialects import postgresql

revision: str = "0004"
down_revision: str | None = "0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

EMBEDDING_DIMENSIONS = 768


def upgrade() -> None:
    op.create_table(
        "agent_memories",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("owner_user_id", sa.Uuid(), nullable=False),
        sa.Column("memory_type", sa.String(length=16), nullable=False),
        sa.Column("memory_scope", sa.String(length=16), nullable=False),
        sa.Column("agent_key", sa.String(length=100), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("embedding", VECTOR(EMBEDDING_DIMENSIONS), nullable=False),
        sa.Column("embedding_model", sa.String(length=100), nullable=False),
        sa.Column("confidence", sa.Float(), server_default=sa.text("1.0"), nullable=False),
        sa.Column("importance", sa.Float(), server_default=sa.text("0.5"), nullable=False),
        sa.Column(
            "source_type",
            sa.String(length=16),
            server_default=sa.text("'user'"),
            nullable=False,
        ),
        sa.Column("source_workflow_run_id", sa.Uuid(), nullable=True),
        sa.Column(
            "metadata_json",
            postgresql.JSONB(none_as_null=True),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "last_accessed_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_agent_memories")),
        sa.ForeignKeyConstraint(
            ["owner_user_id"], ["users.id"],
            name=op.f("fk_agent_memories_owner_user_id_users"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["source_workflow_run_id"], ["workflow_runs.id"],
            name=op.f("fk_agent_memories_source_workflow_run_id_workflow_runs"),
            ondelete="RESTRICT",
        ),
        sa.CheckConstraint(
            "memory_type IN ('episodic', 'semantic')",
            name=op.f("ck_agent_memories_memory_type_valid"),
        ),
        sa.CheckConstraint(
            "memory_scope IN ('user', 'agent')",
            name=op.f("ck_agent_memories_memory_scope_valid"),
        ),
        sa.CheckConstraint(
            "(memory_scope = 'user' AND agent_key IS NULL) OR "
            "(memory_scope = 'agent' AND agent_key IS NOT NULL "
            "AND agent_key ~ '^[a-z][a-z0-9_]{0,99}$')",
            name=op.f("ck_agent_memories_scope_agent_key_consistent"),
        ),
        sa.CheckConstraint(
            "source_type IN ('user', 'agent', 'workflow')",
            name=op.f("ck_agent_memories_source_type_valid"),
        ),
        sa.CheckConstraint(
            "(source_type = 'workflow' AND source_workflow_run_id IS NOT NULL) OR "
            "(source_type IN ('user', 'agent') AND source_workflow_run_id IS NULL)",
            name=op.f("ck_agent_memories_source_workflow_consistent"),
        ),
        sa.CheckConstraint(
            "length(btrim(content)) > 0",
            name=op.f("ck_agent_memories_content_not_blank"),
        ),
        sa.CheckConstraint(
            "length(btrim(embedding_model)) > 0",
            name=op.f("ck_agent_memories_embedding_model_not_blank"),
        ),
        sa.CheckConstraint(
            "confidence >= 0 AND confidence <= 1",
            name=op.f("ck_agent_memories_confidence_in_range"),
        ),
        sa.CheckConstraint(
            "importance >= 0 AND importance <= 1",
            name=op.f("ck_agent_memories_importance_in_range"),
        ),
    )
    op.create_index(
        op.f("ix_agent_memories_owner_scope_type_created"),
        "agent_memories",
        ["owner_user_id", "memory_scope", "memory_type", "created_at"],
    )
    op.create_index(
        op.f("ix_agent_memories_expires_at"),
        "agent_memories",
        ["expires_at"],
    )
    op.create_index(
        "ix_agent_memories_embedding_hnsw",
        "agent_memories",
        ["embedding"],
        postgresql_using="hnsw",
        postgresql_with={"m": 16, "ef_construction": 64},
        postgresql_ops={"embedding": "vector_cosine_ops"},
    )


def downgrade() -> None:
    op.drop_index("ix_agent_memories_embedding_hnsw", table_name="agent_memories")
    op.drop_index(op.f("ix_agent_memories_expires_at"), table_name="agent_memories")
    op.drop_index(
        op.f("ix_agent_memories_owner_scope_type_created"),
        table_name="agent_memories",
    )
    op.drop_table("agent_memories")
