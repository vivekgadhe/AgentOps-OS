"""Allow self-service registration verification OTPs.

Revision ID: 0008
Revises: 0007
Create Date: 2026-11-07
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0008"
down_revision: str | None = "0007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Allow registration-purpose OTPs without changing existing records."""

    op.drop_constraint(
        op.f("ck_auth_action_tokens_purpose_valid"),
        "auth_action_tokens",
        type_="check",
    )

    op.drop_constraint(
        op.f("ck_auth_action_tokens_purpose_role_consistent"),
        "auth_action_tokens",
        type_="check",
    )

    op.create_check_constraint(
        op.f("ck_auth_action_tokens_purpose_valid"),
        "auth_action_tokens",
        "purpose IN ('invitation', 'registration', 'password_reset')",
    )

    op.create_check_constraint(
        op.f("ck_auth_action_tokens_purpose_role_consistent"),
        "auth_action_tokens",
        "(purpose = 'invitation' AND role IN ('admin', 'operator', 'viewer')) OR "
        "(purpose IN ('registration', 'password_reset') AND role IS NULL)",
    )


def downgrade() -> None:
    """Remove registration tokens and restore the previous constraints."""

    op.execute(
        sa.text(
            "DELETE FROM auth_action_tokens "
            "WHERE purpose = 'registration'"
        )
    )

    op.drop_constraint(
        op.f("ck_auth_action_tokens_purpose_role_consistent"),
        "auth_action_tokens",
        type_="check",
    )

    op.drop_constraint(
        op.f("ck_auth_action_tokens_purpose_valid"),
        "auth_action_tokens",
        type_="check",
    )

    op.create_check_constraint(
        op.f("ck_auth_action_tokens_purpose_valid"),
        "auth_action_tokens",
        "purpose IN ('invitation', 'password_reset')",
    )

    op.create_check_constraint(
        op.f("ck_auth_action_tokens_purpose_role_consistent"),
        "auth_action_tokens",
        "(purpose = 'invitation' AND role IN ('admin', 'operator', 'viewer')) OR "
        "(purpose = 'password_reset' AND role IS NULL)",
    )