"""Add one-time invitation and password-reset tokens.

Revision ID: 0006
Revises: 0005
Create Date: 2026-11-07
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0006"
down_revision: str | None = "0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "auth_action_tokens",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("purpose", sa.String(length=20), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("role", sa.String(length=16), nullable=True),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("created_by_user_id", sa.Uuid(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("consumed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_auth_action_tokens")),
        sa.UniqueConstraint("token_hash", name=op.f("uq_auth_action_tokens_token_hash")),
        sa.ForeignKeyConstraint(
            ["created_by_user_id"],
            ["users.id"],
            name=op.f("fk_auth_action_tokens_created_by_user_id_users"),
            ondelete="RESTRICT",
        ),
        sa.CheckConstraint(
            "purpose IN ('invitation', 'password_reset')",
            name=op.f("ck_auth_action_tokens_purpose_valid"),
        ),
        sa.CheckConstraint(
            "(purpose = 'invitation' AND role IN ('admin', 'operator', 'viewer')) OR "
            "(purpose = 'password_reset' AND role IS NULL)",
            name=op.f("ck_auth_action_tokens_purpose_role_consistent"),
        ),
        sa.CheckConstraint(
            "email = lower(email)",
            name=op.f("ck_auth_action_tokens_email_lowercase"),
        ),
        sa.CheckConstraint(
            "length(btrim(email)) > 0",
            name=op.f("ck_auth_action_tokens_email_not_blank"),
        ),
        sa.CheckConstraint(
            "length(token_hash) = 64",
            name=op.f("ck_auth_action_tokens_token_hash_length"),
        ),
        sa.CheckConstraint(
            "expires_at > created_at",
            name=op.f("ck_auth_action_tokens_expires_after_created"),
        ),
    )
    op.create_index(
        "ix_auth_action_tokens_email_purpose_expires",
        "auth_action_tokens",
        ["email", "purpose", "expires_at"],
    )
    op.create_index(
        "ix_auth_action_tokens_created_by",
        "auth_action_tokens",
        ["created_by_user_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_auth_action_tokens_created_by", table_name="auth_action_tokens")
    op.drop_index("ix_auth_action_tokens_email_purpose_expires", table_name="auth_action_tokens")
    op.drop_table("auth_action_tokens")
