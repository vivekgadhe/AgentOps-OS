"""Static checks on the ORM metadata (no database needed)."""

from __future__ import annotations

from enum import StrEnum

import pytest
from sqlalchemy import (
    CheckConstraint,
    ForeignKeyConstraint,
    PrimaryKeyConstraint,
    UniqueConstraint,
)

from agentops.db.base import Base
from agentops.db.models import (
    AuditOutcome,
    EventLevel,
    TaskStatus,
    UserRole,
    WorkflowStatus,
)

EXPECTED_TABLES = {
    "users",
    "workflow_runs",
    "task_runs",
    "task_dependencies",
    "execution_events",
    "audit_logs",
}
POSTGRES_MAX_IDENTIFIER = 63


def test_all_expected_tables_are_registered() -> None:
    assert set(Base.metadata.tables) == EXPECTED_TABLES


def test_every_constraint_and_index_is_named_and_fits_postgres() -> None:
    problems: list[str] = []
    for table in Base.metadata.tables.values():
        names = [c.name for c in table.constraints] + [i.name for i in table.indexes]
        for name in names:
            if not name:
                problems.append(f"{table.name}: unnamed constraint or index")
            elif len(str(name)) > POSTGRES_MAX_IDENTIFIER:
                problems.append(f"{table.name}: {name!r} longer than 63 characters")
    assert problems == []


@pytest.mark.parametrize(
    ("constraint_type", "prefix"),
    [
        (PrimaryKeyConstraint, "pk_"),
        (ForeignKeyConstraint, "fk_"),
        (UniqueConstraint, "uq_"),
        (CheckConstraint, "ck_"),
    ],
)
def test_constraint_names_follow_the_prefix_convention(constraint_type: type, prefix: str) -> None:
    wrong = [
        f"{table.name}.{constraint.name}"
        for table in Base.metadata.tables.values()
        for constraint in table.constraints
        if isinstance(constraint, constraint_type) and not str(constraint.name).startswith(prefix)
    ]
    assert wrong == []


def test_every_foreign_key_declares_its_delete_behaviour() -> None:
    missing = [
        f"{table.name}.{fk.name}"
        for table in Base.metadata.tables.values()
        for fk in table.foreign_key_constraints
        if fk.ondelete not in {"CASCADE", "RESTRICT"}
    ]
    assert missing == []


def test_every_datetime_column_is_timezone_aware() -> None:
    naive = [
        f"{table.name}.{column.name}"
        for table in Base.metadata.tables.values()
        for column in table.columns
        if column.type.__class__.__name__ == "DateTime"
        and not getattr(column.type, "timezone", False)
    ]
    assert naive == []


@pytest.mark.parametrize(
    "enum_class", [UserRole, WorkflowStatus, TaskStatus, EventLevel, AuditOutcome]
)
def test_enum_values_are_lowercase_and_unique(enum_class: type[StrEnum]) -> None:
    values = [member.value for member in enum_class]
    assert values == [v.lower() for v in values]
    assert len(values) == len(set(values))
