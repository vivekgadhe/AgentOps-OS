"""Human approval inbox and decision endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from agentops.api.deps import get_current_user, get_db
from agentops.core.config import Settings
from agentops.db.models.approval import ApprovalRequest
from agentops.db.models.user import User
from agentops.db.models.workflow import WorkflowRun
from agentops.schemas.approvals import (
    ApprovalDecisionRequest,
    ApprovalDecisionResponse,
    ApprovalResponse,
)
from agentops.services.approval_service import (
    ApprovalError,
    ApprovalNotFoundError,
    ApprovalPermissionError,
    ApprovalService,
)
from agentops.services.execution_factory import build_execution_service

router = APIRouter(prefix="/approvals", tags=["human approvals"])


def _response(
    approval: ApprovalRequest,
    workflow_status: str | None = None,
) -> ApprovalDecisionResponse:
    return ApprovalDecisionResponse(
        approval=ApprovalResponse.model_validate(approval),
        workflow_status=workflow_status or "awaiting_approval",
    )


def _workflow_status(db: Session, workflow_id: UUID) -> str:
    workflow = db.get(WorkflowRun, workflow_id)
    return workflow.status if workflow is not None else "not_found"


@router.get("", response_model=list[ApprovalResponse])
def list_approvals(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[ApprovalResponse]:
    """Admins see the inbox; other roles see only requests they created."""
    service = ApprovalService(db)
    return [
        ApprovalResponse.model_validate(item)
        for item in service.list_for_actor(user_id=user.id, role=user.role)
    ]


@router.get("/{approval_id}", response_model=ApprovalResponse)
def get_approval(
    approval_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ApprovalResponse:
    service = ApprovalService(db)
    try:
        approval = service.get(approval_id)
        service.ensure_can_view(approval, user_id=user.id, role=user.role)
    except ApprovalNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Approval request not found.") from exc
    return ApprovalResponse.model_validate(approval)


@router.post("/{approval_id}/approve", response_model=ApprovalDecisionResponse)
def approve_request(
    approval_id: UUID,
    payload: ApprovalDecisionRequest,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ApprovalDecisionResponse:
    """Approve as a distinct admin, then resume the paused workflow."""
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Only an admin can approve actions.")
    try:
        approval = ApprovalService(db).decide(
            approval_id,
            approver_user_id=user.id,
            approver_role=user.role,
            approve=True,
            reason=payload.reason,
        )
    except ApprovalNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Approval request not found.") from exc
    except ApprovalPermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ApprovalError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    settings: Settings = request.app.state.settings
    execution = build_execution_service(
        db,
        settings,
        tool_registrars=request.app.state.tool_registrars,
    )
    execution.execute_workflow(approval.workflow_run_id)
    db.refresh(approval)
    return _response(approval, _workflow_status(db, approval.workflow_run_id))


@router.post("/{approval_id}/reject", response_model=ApprovalDecisionResponse)
def reject_request(
    approval_id: UUID,
    payload: ApprovalDecisionRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ApprovalDecisionResponse:
    """Reject as a distinct admin and cancel the associated workflow."""
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Only an admin can reject actions.")
    try:
        approval = ApprovalService(db).decide(
            approval_id,
            approver_user_id=user.id,
            approver_role=user.role,
            approve=False,
            reason=payload.reason,
        )
    except ApprovalNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Approval request not found.") from exc
    except ApprovalPermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ApprovalError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return _response(approval, _workflow_status(db, approval.workflow_run_id))


@router.post("/{approval_id}/cancel", response_model=ApprovalDecisionResponse)
def cancel_request(
    approval_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ApprovalDecisionResponse:
    """Allow the requester or an administrator to cancel a pending action."""
    try:
        approval = ApprovalService(db).cancel(
            approval_id,
            actor_user_id=user.id,
            actor_role=user.role,
        )
    except ApprovalNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Approval request not found.") from exc
    except ApprovalError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return _response(approval, _workflow_status(db, approval.workflow_run_id))
