"""Add bounded verification attempts to authentication OTP records.

Revision ID: 0007
Revises: 0006
Create Date: 2026-11-07
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0007"
down_revision: str | None = "0006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "auth_action_tokens",
        sa.Column("attempts", sa.Integer(), server_default=sa.text("0"), nullable=False),
    )
    op.add_column(
        "auth_action_tokens",
        sa.Column("max_attempts", sa.Integer(), server_default=sa.text("5"), nullable=False),
    )
    op.create_check_constraint(
        op.f("ck_auth_action_tokens_attempts_nonnegative"),
        "auth_action_tokens",
        "attempts >= 0 AND max_attempts BETWEEN 1 AND 10 AND attempts <= max_attempts",
    )


def downgrade() -> None:
    op.drop_constraint(
        op.f("ck_auth_action_tokens_attempts_nonnegative"), "auth_action_tokens", type_="check"
    )
    op.drop_column("auth_action_tokens", "max_attempts")
    op.drop_column("auth_action_tokens", "attempts")
