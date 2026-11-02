"""API endpoints for creating, planning, executing, and retrieving workflows."""

from collections.abc import Iterator
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from agentops.api.deps import get_current_user, get_db
from agentops.db.models import TaskDependency, User, WorkflowRun
from agentops.schemas.planning import WorkflowPlanRequest
from agentops.schemas.workflows import (
    TaskResponse,
    WorkflowCreate,
    WorkflowResponse,
)
from agentops.services.execution import ExecutionError
from agentops.services.execution_factory import build_execution_service
from agentops.services.handlers import build_application_tool_registry
from agentops.services.llm import LLMConfigurationError, LLMProviderError
from agentops.services.planner import (
    PlanningOutputError,
    PlanningValidationError,
    WorkflowPlanner,
)
from agentops.services.providers.base import ProviderError
from agentops.services.providers.provider_manager import build_provider_manager

router = APIRouter(prefix="/runs", tags=["workflows"])


def get_workflow_planner(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Iterator[WorkflowPlanner]:
    """Construct a user-configured planner and close provider clients after use."""
    try:
        manager = build_provider_manager(db, user.id, request.app.state.settings)
    except ProviderError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI provider configuration is unavailable.",
        ) from exc
    try:
        yield WorkflowPlanner(
            manager,
            build_application_tool_registry(request.app.state.tool_registrars),
        )
    finally:
        manager.close()


@router.post(
    "",
    response_model=WorkflowResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_workflow(
    payload: WorkflowCreate,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> WorkflowResponse:
    """Create a workflow and persist its tasks."""
    service = build_execution_service(
        db,
        request.app.state.settings,
        tool_registrars=request.app.state.tool_registrars,
    )

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

    return _to_response(result, db)


@router.post("/plan", response_model=WorkflowCreate)
def plan_workflow(
    payload: WorkflowPlanRequest,
    planner: WorkflowPlanner = Depends(get_workflow_planner),
    user: User = Depends(get_current_user),
) -> WorkflowCreate:
    """Generate a validated workflow plan without persisting or executing it."""
    try:
        return planner.plan(payload.goal, actor_role=user.role)
    except LLMConfigurationError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LLM service is not configured.",
        ) from exc
    except LLMProviderError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="The LLM provider request failed.",
        ) from exc
    except PlanningOutputError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="The LLM returned an invalid workflow plan.",
        ) from exc
    except PlanningValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="The generated workflow plan failed validation.",
        ) from exc


@router.post("/{run_id}/execute", response_model=WorkflowResponse)
def execute_workflow(
    run_id: UUID,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> WorkflowResponse:
    """Execute a workflow owned by the authenticated user."""
    workflow = _get_owned_workflow(db, run_id, user.id)
    service = build_execution_service(
        db,
        request.app.state.settings,
        tool_registrars=request.app.state.tool_registrars,
    )

    try:
        service.execute_workflow(
            workflow.id,
            actor_role=user.role,
        )
    except ExecutionError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    result = _get_owned_workflow(db, run_id, user.id)
    return _to_response(result, db)


@router.get("/{run_id}", response_model=WorkflowResponse)
def get_workflow(
    run_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> WorkflowResponse:
    """Retrieve a workflow and its tasks."""
    workflow = _get_owned_workflow(db, run_id, user.id)
    return _to_response(workflow, db)


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


def _to_response(
    workflow: WorkflowRun,
    db: Session,
) -> WorkflowResponse:
    """Convert a workflow and its dependencies to the response schema."""
    task_by_id = {task.id: task for task in workflow.tasks}

    dependencies_by_task_id: dict[UUID, list[str]] = {task.id: [] for task in workflow.tasks}

    edges = list(
        db.scalars(
            select(TaskDependency).where(TaskDependency.workflow_run_id == workflow.id)
        ).all()
    )

    for edge in edges:
        prerequisite = task_by_id.get(edge.depends_on_task_id)

        if prerequisite is not None:
            dependencies_by_task_id[edge.task_id].append(prerequisite.key)

    task_responses = [
        TaskResponse.model_validate(task).model_copy(
            update={"depends_on": sorted(dependencies_by_task_id[task.id])}
        )
        for task in workflow.tasks
    ]

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
        tasks=task_responses,
    )
