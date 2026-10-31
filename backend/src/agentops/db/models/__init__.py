"""Importing this package registers every table on ``Base.metadata``."""

from agentops.db.models.audit import AuditLog
from agentops.db.models.enums import (
    AuditOutcome,
    EventLevel,
    TaskStatus,
    UserRole,
    WorkflowStatus,
)
from agentops.db.models.knowledge import KnowledgeChunk, KnowledgeDocument
from agentops.db.models.user import User
from agentops.db.models.workflow import (
    ExecutionEvent,
    TaskDependency,
    TaskRun,
    WorkflowRun,
)

__all__ = [
    "AuditLog",
    "AuditOutcome",
    "EventLevel",
    "ExecutionEvent",
    "TaskDependency",
    "TaskRun",
    "TaskStatus",
    "User",
    "UserRole",
    "WorkflowRun",
    "WorkflowStatus",
    "KnowledgeChunk",
    "KnowledgeDocument",
]
