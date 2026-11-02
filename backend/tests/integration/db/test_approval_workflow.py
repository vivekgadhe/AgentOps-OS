"""PostgreSQL integration tests for task approval, pause, and resume."""

from typing import Any

from pydantic import BaseModel, ConfigDict
from sqlalchemy import select

from agentops.db.models.approval import ApprovalRequest
from agentops.db.models.enums import TaskStatus, WorkflowStatus
from agentops.services.approval_service import ApprovalService
from agentops.services.execution import ExecutionService
from agentops.services.tool_registry import ToolDefinition


class _ActionInput(BaseModel):
    value: str


class _ActionOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    result: str


def _protected_action(data: dict[str, Any]) -> dict[str, Any]:
    """Top-level handler so Windows spawn can import it in the child process."""
    return {"result": str(data["value"]).upper()}


def test_protected_tool_pauses_until_admin_approval_then_resumes(orm_session, factory) -> None:
    requester = factory.user(role="operator")
    approver = factory.user(role="admin")
    service = ExecutionService(orm_session, approval_ttl_hours=24)
    service.register_tool(
        ToolDefinition(
            name="protected_action",
            description="Perform a protected operation.",
            input_model=_ActionInput,
            output_model=_ActionOutput,
            handler=_protected_action,
            requires_approval=True,
        )
    )
    workflow = service.create_workflow(
        requester,
        "Run a protected action",
        [
            {
                "key": "protected",
                "name": "Protected action",
                "tool_name": "protected_action",
                "input_data": {"value": "approved"},
            }
        ],
    )

    paused = service.execute_workflow(workflow.id, actor_role="operator")
    assert paused.status == WorkflowStatus.AWAITING_APPROVAL.value

    approval = orm_session.scalar(
        select(ApprovalRequest).where(ApprovalRequest.workflow_run_id == workflow.id)
    )
    assert approval is not None
    assert approval.status == "pending"
    assert approval.input_snapshot == {"value": "approved"}

    decision = ApprovalService(orm_session).decide(
        approval.id,
        approver_user_id=approver.id,
        approver_role=approver.role,
        approve=True,
        reason="Reviewed and approved.",
    )
    assert decision.status == "approved"

    completed = service.execute_workflow(workflow.id, actor_role="operator")
    assert completed.status == WorkflowStatus.SUCCEEDED.value
    assert completed.tasks[0].status == TaskStatus.SUCCEEDED.value

    orm_session.refresh(approval)
    assert approval.status == "executed"


def test_requester_cannot_approve_their_own_action(orm_session, factory) -> None:
    from datetime import UTC, datetime, timedelta

    from agentops.db.models.approval import ApprovalRequest
    from agentops.services.approval_service import ApprovalPermissionError

    requester = factory.user(role="admin")
    workflow = factory.workflow(created_by=requester, status=WorkflowStatus.AWAITING_APPROVAL.value)
    task = factory.task(workflow, status=TaskStatus.AWAITING_APPROVAL.value)
    approval = ApprovalRequest(
        workflow_run_id=workflow.id,
        task_run_id=task.id,
        requester_user_id=requester.id,
        tool_name="protected_action",
        action_summary="Protected action",
        input_snapshot={},
        status="pending",
        expires_at=datetime.now(UTC) + timedelta(hours=1),
    )
    orm_session.add(approval)
    orm_session.flush()

    try:
        ApprovalService(orm_session).decide(
            approval.id,
            approver_user_id=requester.id,
            approver_role="admin",
            approve=True,
        )
    except ApprovalPermissionError:
        pass
    else:
        raise AssertionError("The requester must not approve their own action.")


def test_rejection_cancels_task_and_workflow(orm_session, factory) -> None:
    from datetime import UTC, datetime, timedelta

    requester = factory.user(role="operator")
    approver = factory.user(role="admin")
    workflow = factory.workflow(created_by=requester, status=WorkflowStatus.AWAITING_APPROVAL.value)
    task = factory.task(workflow, status=TaskStatus.AWAITING_APPROVAL.value)
    approval = ApprovalRequest(
        workflow_run_id=workflow.id,
        task_run_id=task.id,
        requester_user_id=requester.id,
        tool_name="protected_action",
        action_summary="Protected action",
        input_snapshot={},
        status="pending",
        expires_at=datetime.now(UTC) + timedelta(hours=1),
    )
    orm_session.add(approval)
    orm_session.flush()

    ApprovalService(orm_session).decide(
        approval.id,
        approver_user_id=approver.id,
        approver_role="admin",
        approve=False,
        reason="Not permitted.",
    )
    assert approval.status == "rejected"
    assert workflow.status == WorkflowStatus.CANCELLED.value
    assert task.status == TaskStatus.CANCELLED.value
