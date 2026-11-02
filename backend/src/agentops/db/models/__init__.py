"""Importing this package registers every table on Base.metadata."""

from agentops.db.models.ai_provider import AIProviderConfig
from agentops.db.models.approval import ApprovalRequest
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
    "AIProviderConfig",
    "ApprovalRequest",
    "AuditLog",
    "AuditOutcome",
    "EventLevel",
    "ExecutionEvent",
    "KnowledgeChunk",
    "KnowledgeDocument",
    "TaskDependency",
    "TaskRun",
    "TaskStatus",
    "User",
    "UserRole",
    "WorkflowRun",
    "WorkflowStatus",
]
