"""Policy-bound, persistent approval requests and immutable audit decisions."""

from __future__ import annotations

import math
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from agentops.core.context import request_id_var
from agentops.db.models import AuditLog, ExecutionEvent, TaskRun, WorkflowRun
from agentops.db.models.approval import ApprovalRequest

SENSITIVE_KEY_PARTS = ("password", "secret", "token", "api_key", "authorization", "credential")


class ApprovalError(RuntimeError):
    """Base error for approval operations."""


class ApprovalNotFoundError(ApprovalError):
    """The approval request does not exist."""


class ApprovalPermissionError(ApprovalError):
    """The current actor cannot approve or inspect the request."""


class ApprovalTransitionError(ApprovalError):
    """The request is not in a state that permits the requested transition."""


class ApprovalExpiredError(ApprovalTransitionError):
    """The approval request has expired."""


def _safe_snapshot(value: Any, *, depth: int = 0) -> Any:
    """Redact likely secrets and bound nested approval input snapshots."""
    if depth > 6:
        return "[maximum nesting reached]"
    if isinstance(value, dict):
        result: dict[str, Any] = {}
        for key, item in list(value.items())[:100]:
            normalized = str(key).lower()
            if any(part in normalized for part in SENSITIVE_KEY_PARTS):
                result[str(key)] = "[REDACTED]"
            else:
                result[str(key)] = _safe_snapshot(item, depth=depth + 1)
        return result
    if isinstance(value, list):
        return [_safe_snapshot(item, depth=depth + 1) for item in value[:100]]
    if isinstance(value, str):
        return value[:2000]
    if isinstance(value, float):
        return value if math.isfinite(value) else "[non-finite number]"
    if value is None or isinstance(value, (bool, int)):
        return value
    return str(value)[:500]


def _audit(
    session: Session,
    *,
    actor_user_id: uuid.UUID | None,
    action: str,
    approval: ApprovalRequest,
    outcome: str = "success",
    details: dict[str, Any] | None = None,
) -> None:
    session.add(
        AuditLog(
            actor_user_id=actor_user_id,
            action=action,
            resource_type="approval_request",
            resource_id=str(approval.id),
            outcome=outcome,
            request_id=request_id_var.get(),
            details={
                "workflow_run_id": str(approval.workflow_run_id),
                "task_run_id": str(approval.task_run_id),
                "tool_name": approval.tool_name,
                **(details or {}),
            },
        )
    )


def _event(
    session: Session,
    approval: ApprovalRequest,
    event_type: str,
    message: str,
    data: dict[str, Any] | None = None,
) -> None:
    session.add(
        ExecutionEvent(
            workflow_run_id=approval.workflow_run_id,
            task_run_id=approval.task_run_id,
            event_type=event_type,
            message=message,
            level="info",
            data={"approval_request_id": str(approval.id), **(data or {})},
            request_id=request_id_var.get(),
        )
    )


class ApprovalService:
    """Create, inspect, decide, and consume approval requests."""

    def __init__(self, session: Session, *, ttl_hours: int = 24) -> None:
        if not 1 <= ttl_hours <= 720:
            raise ValueError("Approval TTL must be between 1 and 720 hours.")
        self.session = session
        self.ttl_hours = ttl_hours

    def create_for_task(
        self,
        workflow: WorkflowRun,
        task: TaskRun,
        *,
        tool_name: str,
        action_summary: str,
    ) -> ApprovalRequest:
        """Idempotently create one approval request for a protected task."""
        existing = self.session.scalar(
            select(ApprovalRequest).where(ApprovalRequest.task_run_id == task.id).with_for_update()
        )
        if existing is not None:
            if existing.status == "pending":
                return existing
            if existing.status == "approved":
                return existing
            if existing.status == "expired":
                raise ApprovalExpiredError("The approval request for this task has expired.")
            raise ApprovalTransitionError(
                f"The task already has a final approval decision: {existing.status}."
            )

        now = datetime.now(UTC)
        approval = ApprovalRequest(
            workflow_run_id=workflow.id,
            task_run_id=task.id,
            requester_user_id=workflow.created_by,
            tool_name=tool_name,
            action_summary=action_summary.strip()[:500],
            input_snapshot=_safe_snapshot(task.input_data or {}),
            status="pending",
            requested_at=now,
            expires_at=now + timedelta(hours=self.ttl_hours),
        )
        self.session.add(approval)
        self.session.flush()
        _event(
            self.session,
            approval,
            "approval.requested",
            "Human approval is required before this task can execute.",
            {"tool_name": tool_name},
        )
        _audit(
            self.session,
            actor_user_id=workflow.created_by,
            action="approval.request",
            approval=approval,
            details={"status": "pending"},
        )
        self.session.flush()
        return approval

    def get(self, approval_id: uuid.UUID) -> ApprovalRequest:
        approval = self.session.get(ApprovalRequest, approval_id)
        if approval is None:
            raise ApprovalNotFoundError("Approval request not found.")
        return approval

    def expire_pending(
        self,
        approval: ApprovalRequest,
        *,
        actor_user_id: uuid.UUID | None = None,
    ) -> None:
        """Expire a pending approval and cancel its paused task/workflow."""
        if approval.status != "pending":
            raise ApprovalTransitionError(
                f"Only pending approvals can expire, not '{approval.status}'."
            )
        now = datetime.now(UTC)
        approval.status = "expired"
        approval.decided_by_user_id = actor_user_id
        approval.decided_at = now
        task = self.session.get(TaskRun, approval.task_run_id)
        workflow = self.session.get(WorkflowRun, approval.workflow_run_id)
        if task is not None:
            task.status = "cancelled"
            task.finished_at = now
        if workflow is not None:
            workflow.status = "cancelled"
            workflow.finished_at = now
        _event(self.session, approval, "approval.expired", "Approval request expired.")
        _audit(
            self.session,
            actor_user_id=actor_user_id,
            action="approval.expire",
            approval=approval,
            outcome="failure",
        )
        self.session.flush()

    def decide(
        self,
        approval_id: uuid.UUID,
        *,
        approver_user_id: uuid.UUID,
        approver_role: str,
        approve: bool,
        reason: str | None = None,
    ) -> ApprovalRequest:
        """Approve or reject; only another admin may make the decision."""
        if approver_role != "admin":
            raise ApprovalPermissionError("Only an admin can decide approval requests.")

        approval = self.session.scalar(
            select(ApprovalRequest).where(ApprovalRequest.id == approval_id).with_for_update()
        )
        if approval is None:
            raise ApprovalNotFoundError("Approval request not found.")
        if approval.requester_user_id == approver_user_id:
            raise ApprovalPermissionError("The requester cannot approve their own action.")
        if approval.status != "pending":
            raise ApprovalTransitionError(
                f"Approval request cannot be decided from status '{approval.status}'."
            )

        now = datetime.now(UTC)
        if approval.expires_at <= now:
            self.expire_pending(approval, actor_user_id=approver_user_id)
            self.session.commit()
            raise ApprovalExpiredError("Approval request has expired.")

        approval.status = "approved" if approve else "rejected"
        approval.decided_by_user_id = approver_user_id
        approval.decided_at = now
        approval.decision_reason = reason.strip()[:2000] if reason and reason.strip() else None

        if not approve:
            task = self.session.get(TaskRun, approval.task_run_id)
            workflow = self.session.get(WorkflowRun, approval.workflow_run_id)
            if task is not None:
                task.status = "cancelled"
                task.finished_at = now
            if workflow is not None:
                workflow.status = "cancelled"
                workflow.finished_at = now
            _event(
                self.session,
                approval,
                "approval.rejected",
                "The requested action was rejected by an administrator.",
                {"reason": approval.decision_reason},
            )
        else:
            _event(
                self.session,
                approval,
                "approval.approved",
                "The requested action was approved by an administrator.",
                {"reason": approval.decision_reason},
            )

        _audit(
            self.session,
            actor_user_id=approver_user_id,
            action="approval.approve" if approve else "approval.reject",
            approval=approval,
            details={"reason": approval.decision_reason},
        )
        self.session.commit()
        self.session.refresh(approval)
        return approval

    def cancel(
        self,
        approval_id: uuid.UUID,
        *,
        actor_user_id: uuid.UUID,
        actor_role: str,
    ) -> ApprovalRequest:
        """Allow the requester or an admin to cancel a still-pending request."""
        approval = self.session.scalar(
            select(ApprovalRequest).where(ApprovalRequest.id == approval_id).with_for_update()
        )
        if approval is None:
            raise ApprovalNotFoundError("Approval request not found.")
        if actor_role != "admin" and approval.requester_user_id != actor_user_id:
            raise ApprovalNotFoundError("Approval request not found.")
        if approval.status != "pending":
            raise ApprovalTransitionError(
                f"Approval request cannot be cancelled from status '{approval.status}'."
            )

        now = datetime.now(UTC)
        approval.status = "cancelled"
        approval.decided_by_user_id = actor_user_id
        approval.decided_at = now
        approval.decision_reason = "Cancelled by requester or administrator."
        task = self.session.get(TaskRun, approval.task_run_id)
        workflow = self.session.get(WorkflowRun, approval.workflow_run_id)
        if task is not None:
            task.status = "cancelled"
            task.finished_at = now
        if workflow is not None:
            workflow.status = "cancelled"
            workflow.finished_at = now
        _event(self.session, approval, "approval.cancelled", "Approval request was cancelled.")
        _audit(
            self.session,
            actor_user_id=actor_user_id,
            action="approval.cancel",
            approval=approval,
        )
        self.session.commit()
        self.session.refresh(approval)
        return approval

    def mark_executed(self, task_run_id: uuid.UUID) -> None:
        """Record that a previously approved task completed execution."""
        approval = self.session.scalar(
            select(ApprovalRequest).where(
                ApprovalRequest.task_run_id == task_run_id,
                ApprovalRequest.status == "approved",
            )
        )
        if approval is None:
            return
        approval.status = "executed"
        _event(
            self.session,
            approval,
            "approval.executed",
            "The approved task completed execution.",
        )
        _audit(
            self.session,
            actor_user_id=approval.decided_by_user_id,
            action="approval.execution_complete",
            approval=approval,
        )

    def list_for_actor(self, *, user_id: uuid.UUID, role: str) -> list[ApprovalRequest]:
        statement = select(ApprovalRequest)
        if role != "admin":
            statement = statement.where(ApprovalRequest.requester_user_id == user_id)
        return list(
            self.session.scalars(statement.order_by(ApprovalRequest.requested_at.desc())).all()
        )

    def ensure_can_view(self, approval: ApprovalRequest, *, user_id: uuid.UUID, role: str) -> None:
        if role != "admin" and approval.requester_user_id != user_id:
            raise ApprovalNotFoundError("Approval request not found.")
