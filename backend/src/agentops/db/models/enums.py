"""Allowed values for status-like columns.

The database stores these as plain strings protected by CHECK constraints (not
native PostgreSQL enums, which are painful to change in migrations). The same
values are written out literally in the migration, and an integration test
inserts every member to prove the two stay in sync.
"""

from __future__ import annotations

from enum import StrEnum


class UserRole(StrEnum):
    ADMIN = "admin"
    OPERATOR = "operator"
    VIEWER = "viewer"


class WorkflowStatus(StrEnum):
    PENDING = "pending"
    PLANNING = "planning"
    RUNNING = "running"
    AWAITING_APPROVAL = "awaiting_approval"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskStatus(StrEnum):
    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    AWAITING_APPROVAL = "awaiting_approval"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"


class EventLevel(StrEnum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class AuditOutcome(StrEnum):
    SUCCESS = "success"
    DENIED = "denied"
    FAILURE = "failure"


def in_check(column: str, enum_class: type[StrEnum]) -> str:
    """Build ``column IN ('a', 'b', ...)`` from a trusted enum (never user input)."""
    values = ", ".join(f"'{member.value}'" for member in enum_class)
    return f"{column} IN ({values})"
