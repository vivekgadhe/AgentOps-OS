
"""API endpoints for creating, executing, and retrieving workflows."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from agentops.api.deps import get_current_user, get_db
from agentops.db.models import User, WorkflowRun
from agentops.schemas.workflows import WorkflowCreate, WorkflowResponse
from agentops.services.execution import ExecutionError, ExecutionService
from agentops.services.handlers import register_builtin_handlers

router = APIRouter(prefix="/runs", tags=["workflows"])


@router.post(
    "",
    response_model=WorkflowResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_workflow(
    payload: WorkflowCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> WorkflowResponse:
    """Create a workflow and persist its tasks."""
    service = ExecutionService(db)
    register_builtin_handlers(service)

    try:
        workflow = service.create_workflow(
            user=user,
            goal=payload.goal,
            tasks=[task.model_dump() for task in payload.tasks],
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    result = db.scalar(
        select(WorkflowRun)
        .options(selectinload(WorkflowRun.tasks))
        .where(WorkflowRun.id == workflow.id)
    )
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Workflow creation failed",
        )

    return _to_response(result)


@router.post("/{run_id}/execute", response_model=WorkflowResponse)
def execute_workflow(
    run_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> WorkflowResponse:
    """Execute a workflow owned by the authenticated user."""
    workflow = _get_owned_workflow(db, run_id, user.id)
    service = ExecutionService(db)
    register_builtin_handlers(service)
    try:
        service.execute_workflow(workflow.id)
    except ExecutionError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    result = _get_owned_workflow(db, run_id, user.id)
    return _to_response(result)


@router.get("/{run_id}", response_model=WorkflowResponse)
def get_workflow(
    run_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> WorkflowResponse:
    """Retrieve a workflow and its tasks."""
    return _to_response(_get_owned_workflow(db, run_id, user.id))


def _get_owned_workflow(
    db: Session,
    run_id: UUID,
    user_id: UUID,
) -> WorkflowRun:
    """Load a workflow only if it belongs to the requesting user."""
    workflow = db.scalar(
        select(WorkflowRun)
        .options(selectinload(WorkflowRun.tasks))
        .where(
            WorkflowRun.id == run_id,
            WorkflowRun.created_by == user_id,
        )
    )
    if workflow is None:
        # Do not disclose whether another user's workflow exists.
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found",
        )
    return workflow


def _to_response(workflow: WorkflowRun) -> WorkflowResponse:
    """Convert an ORM workflow and its tasks into the public response schema."""
    return WorkflowResponse(
        id=workflow.id,
        goal=workflow.goal,
        status=workflow.status,
        plan=workflow.plan,
        error=workflow.error,
        started_at=workflow.started_at,
        finished_at=workflow.finished_at,
        created_at=workflow.created_at,
        updated_at=workflow.updated_at,
        tasks=workflow.tasks,
    )