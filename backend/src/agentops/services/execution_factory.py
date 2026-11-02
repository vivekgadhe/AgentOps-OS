"""Build workflow execution services with the application's trusted tool set."""

from collections.abc import Iterable

from sqlalchemy.orm import Session

from agentops.core.config import Settings
from agentops.services.execution import ExecutionService
from agentops.services.handlers import ToolRegistrar, build_application_tool_registry


def build_execution_service(
    session: Session,
    settings: Settings,
    *,
    tool_registrars: Iterable[ToolRegistrar] = (),
) -> ExecutionService:
    """Create an execution service with the same tool set used by planning/API.

    Register extension tools through ``create_app(tool_registrars=[...])``.
    Approval-protected actions must set ``requires_approval=True`` in their
    trusted ``ToolDefinition``.
    """
    registry = build_application_tool_registry(tool_registrars)
    return ExecutionService(
        session,
        approval_ttl_hours=settings.approval_ttl_hours,
        tool_registry=registry,
    )
