"""Authenticated, owner-scoped observability and analytics endpoints."""

from datetime import UTC, datetime, timedelta
from typing import Any, cast
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import case, delete, func, select
from sqlalchemy.engine import CursorResult
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.sql.elements import ColumnElement

from agentops.api.deps import get_current_user, get_db
from agentops.core.config import Settings
from agentops.db.models.telemetry import TelemetryEvent
from agentops.db.models.user import User
from agentops.db.models.workflow import TaskRun, WorkflowRun
from agentops.schemas.observability import (
    AgentUsageItem,
    AgentUsageResponse,
    ObservabilityOverviewResponse,
    ProviderUsageItem,
    ProviderUsageResponse,
    TelemetryEventResponse,
    TelemetryEventsResponse,
    TelemetryOutcome,
    TelemetryPurgeResponse,
    WorkflowAnalyticsItem,
    WorkflowAnalyticsResponse,
)

router = APIRouter(prefix="/observability", tags=["observability"])


def _settings(request: Request) -> Settings:
    return cast(Settings, request.app.state.settings)


def _window(
    start_at: datetime | None,
    end_at: datetime | None,
) -> tuple[datetime, datetime]:
    """Resolve a bounded reporting window and reject ambiguous naive datetimes."""
    resolved_end = end_at or datetime.now(UTC)
    resolved_start = start_at or resolved_end - timedelta(days=30)
    if resolved_start.tzinfo is None or resolved_end.tzinfo is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="start_at and end_at must include a timezone.",
        )
    if resolved_start >= resolved_end:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="start_at must be earlier than end_at.",
        )
    return resolved_start, resolved_end


def _telemetry_filters(
    owner_user_id: UUID,
    start_at: datetime,
    end_at: datetime,
) -> tuple[ColumnElement[bool], ...]:
    return (
        TelemetryEvent.owner_user_id == owner_user_id,
        TelemetryEvent.created_at >= start_at,
        TelemetryEvent.created_at < end_at,
    )


def _rate(successes: int, total: int) -> float:
    return round(successes / total, 4) if total else 0.0


def _duration(value: float | None) -> float | None:
    return round(float(value), 2) if value is not None else None


def _safe_event_attributes(value: object) -> dict[str, Any]:
    """Return only the recorder's allow-listed, non-content attributes."""
    if not isinstance(value, dict):
        return {}
    result: dict[str, Any] = {}
    attempt_number = value.get("attempt_number")
    if isinstance(attempt_number, int) and not isinstance(attempt_number, bool):
        result["attempt_number"] = max(1, attempt_number)
    used_fallback = value.get("used_fallback")
    if isinstance(used_fallback, bool):
        result["used_fallback"] = used_fallback
    output_schema = value.get("output_schema")
    if isinstance(output_schema, str):
        result["output_schema"] = output_schema[:120]
    return result


@router.get("/overview", response_model=ObservabilityOverviewResponse)
def get_observability_overview(
    start_at: datetime | None = None,
    end_at: datetime | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ObservabilityOverviewResponse:
    """Return workflow, task and LLM metrics for the authenticated user."""
    start, end = _window(start_at, end_at)
    workflow_filters = (
        WorkflowRun.created_by == user.id,
        WorkflowRun.created_at >= start,
        WorkflowRun.created_at < end,
    )
    workflow_status_rows = db.execute(
        select(WorkflowRun.status, func.count(WorkflowRun.id))
        .where(*workflow_filters)
        .group_by(WorkflowRun.status)
    ).all()
    workflow_statuses = {str(key): int(count) for key, count in workflow_status_rows}
    workflow_count = sum(workflow_statuses.values())
    workflow_duration = func.avg(
        func.extract("epoch", WorkflowRun.finished_at - WorkflowRun.started_at) * 1000
    )
    average_workflow_duration = db.scalar(
        select(workflow_duration).where(
            *workflow_filters,
            WorkflowRun.started_at.is_not(None),
            WorkflowRun.finished_at.is_not(None),
        )
    )

    task_status_rows = db.execute(
        select(TaskRun.status, func.count(TaskRun.id))
        .join(WorkflowRun, WorkflowRun.id == TaskRun.workflow_run_id)
        .where(*workflow_filters)
        .group_by(TaskRun.status)
    ).all()
    task_statuses = {str(key): int(count) for key, count in task_status_rows}
    task_count = sum(task_statuses.values())
    task_duration = func.avg(func.extract("epoch", TaskRun.finished_at - TaskRun.started_at) * 1000)
    average_task_duration = db.scalar(
        select(task_duration)
        .join(WorkflowRun, WorkflowRun.id == TaskRun.workflow_run_id)
        .where(
            *workflow_filters,
            TaskRun.started_at.is_not(None),
            TaskRun.finished_at.is_not(None),
        )
    )

    llm_result = db.execute(
        select(
            func.count(TelemetryEvent.id),
            func.sum(case((TelemetryEvent.outcome == "success", 1), else_=0)),
            func.sum(case((TelemetryEvent.outcome == "failure", 1), else_=0)),
            func.sum(case((TelemetryEvent.outcome == "refused", 1), else_=0)),
            func.avg(TelemetryEvent.duration_ms),
        ).where(
            *_telemetry_filters(user.id, start, end),
            TelemetryEvent.event_type == "llm_attempt",
        )
    ).one()
    llm_count = int(llm_result[0] or 0)
    llm_success = int(llm_result[1] or 0)
    llm_failure = int(llm_result[2] or 0)
    llm_refusal = int(llm_result[3] or 0)

    return ObservabilityOverviewResponse(
        start_at=start,
        end_at=end,
        workflow_count=workflow_count,
        workflow_status_counts=workflow_statuses,
        workflow_success_rate=_rate(workflow_statuses.get("succeeded", 0), workflow_count),
        average_workflow_duration_ms=_duration(average_workflow_duration),
        task_count=task_count,
        task_status_counts=task_statuses,
        task_success_rate=_rate(task_statuses.get("succeeded", 0), task_count),
        average_task_duration_ms=_duration(average_task_duration),
        llm_attempt_count=llm_count,
        llm_success_count=llm_success,
        llm_failure_count=llm_failure,
        llm_refusal_count=llm_refusal,
        llm_success_rate=_rate(llm_success, llm_count),
        average_llm_duration_ms=_duration(llm_result[4]),
    )


@router.get("/providers", response_model=ProviderUsageResponse)
def get_provider_usage(
    start_at: datetime | None = None,
    end_at: datetime | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ProviderUsageResponse:
    """Aggregate provider/model attempts, success rates and latency."""
    start, end = _window(start_at, end_at)
    rows = db.execute(
        select(
            TelemetryEvent.provider,
            TelemetryEvent.model,
            func.count(TelemetryEvent.id),
            func.sum(case((TelemetryEvent.outcome == "success", 1), else_=0)),
            func.sum(case((TelemetryEvent.outcome == "failure", 1), else_=0)),
            func.sum(case((TelemetryEvent.outcome == "refused", 1), else_=0)),
            func.avg(TelemetryEvent.duration_ms),
        )
        .where(*_telemetry_filters(user.id, start, end))
        .group_by(TelemetryEvent.provider, TelemetryEvent.model)
        .order_by(TelemetryEvent.provider, TelemetryEvent.model)
    ).all()
    items: list[ProviderUsageItem] = []
    for row in rows:
        total = int(row[2] or 0)
        successes = int(row[3] or 0)
        items.append(
            ProviderUsageItem(
                provider=str(row[0]),
                model=str(row[1]),
                attempt_count=total,
                success_count=successes,
                failure_count=int(row[4] or 0),
                refusal_count=int(row[5] or 0),
                success_rate=_rate(successes, total),
                average_duration_ms=_duration(row[6]),
            )
        )
    return ProviderUsageResponse(start_at=start, end_at=end, items=items)


@router.get("/agents", response_model=AgentUsageResponse)
def get_agent_usage(
    start_at: datetime | None = None,
    end_at: datetime | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> AgentUsageResponse:
    """Aggregate LLM attempts attributed to agents and RAG agent calls."""
    start, end = _window(start_at, end_at)
    rows = db.execute(
        select(
            TelemetryEvent.agent_name,
            func.count(TelemetryEvent.id),
            func.sum(case((TelemetryEvent.outcome == "success", 1), else_=0)),
            func.sum(case((TelemetryEvent.outcome == "failure", 1), else_=0)),
            func.sum(case((TelemetryEvent.outcome == "refused", 1), else_=0)),
            func.avg(TelemetryEvent.duration_ms),
        )
        .where(
            *_telemetry_filters(user.id, start, end),
            TelemetryEvent.agent_name.is_not(None),
            TelemetryEvent.component.in_(("agent", "planner", "rag")),
        )
        .group_by(TelemetryEvent.agent_name)
        .order_by(TelemetryEvent.agent_name)
    ).all()
    items: list[AgentUsageItem] = []
    for row in rows:
        total = int(row[1] or 0)
        successes = int(row[2] or 0)
        items.append(
            AgentUsageItem(
                agent_name=str(row[0]),
                generation_attempts=total,
                success_count=successes,
                failure_count=int(row[3] or 0),
                refusal_count=int(row[4] or 0),
                success_rate=_rate(successes, total),
                average_duration_ms=_duration(row[5]),
            )
        )
    return AgentUsageResponse(start_at=start, end_at=end, items=items)


@router.get("/workflows", response_model=WorkflowAnalyticsResponse)
def get_workflow_analytics(
    start_at: datetime | None = None,
    end_at: datetime | None = None,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0, le=100_000),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> WorkflowAnalyticsResponse:
    """List the authenticated user's workflows with task outcome summaries."""
    start, end = _window(start_at, end_at)
    filters = (
        WorkflowRun.created_by == user.id,
        WorkflowRun.created_at >= start,
        WorkflowRun.created_at < end,
    )
    total = int(db.scalar(select(func.count(WorkflowRun.id)).where(*filters)) or 0)
    workflows = list(
        db.scalars(
            select(WorkflowRun)
            .options(selectinload(WorkflowRun.tasks))
            .where(*filters)
            .order_by(WorkflowRun.created_at.desc(), WorkflowRun.id)
            .limit(limit)
            .offset(offset)
        ).all()
    )
    items: list[WorkflowAnalyticsItem] = []
    for workflow in workflows:
        duration_ms = None
        if workflow.started_at is not None and workflow.finished_at is not None:
            duration_ms = (workflow.finished_at - workflow.started_at).total_seconds() * 1000
        items.append(
            WorkflowAnalyticsItem(
                id=workflow.id,
                goal=workflow.goal,
                status=workflow.status,
                created_at=workflow.created_at,
                started_at=workflow.started_at,
                finished_at=workflow.finished_at,
                duration_ms=_duration(duration_ms),
                task_count=len(workflow.tasks),
                succeeded_task_count=sum(task.status == "succeeded" for task in workflow.tasks),
                failed_task_count=sum(task.status == "failed" for task in workflow.tasks),
            )
        )
    return WorkflowAnalyticsResponse(
        start_at=start,
        end_at=end,
        total=total,
        limit=limit,
        offset=offset,
        items=items,
    )


@router.get("/events", response_model=TelemetryEventsResponse)
def get_telemetry_events(
    start_at: datetime | None = None,
    end_at: datetime | None = None,
    event_type: str | None = Query(default=None, max_length=32),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0, le=100_000),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> TelemetryEventsResponse:
    """Return safe, owner-scoped telemetry metadata without model content."""
    start, end = _window(start_at, end_at)
    filters = list(_telemetry_filters(user.id, start, end))
    if event_type is not None:
        normalized = event_type.strip()
        if not normalized:
            raise HTTPException(status_code=422, detail="event_type cannot be blank.")
        filters.append(TelemetryEvent.event_type == normalized)
    total = int(db.scalar(select(func.count(TelemetryEvent.id)).where(*filters)) or 0)
    rows = list(
        db.scalars(
            select(TelemetryEvent)
            .where(*filters)
            .order_by(TelemetryEvent.created_at.desc(), TelemetryEvent.id)
            .limit(limit)
            .offset(offset)
        ).all()
    )
    return TelemetryEventsResponse(
        start_at=start,
        end_at=end,
        total=total,
        limit=limit,
        offset=offset,
        items=[
            TelemetryEventResponse(
                id=row.id,
                workflow_run_id=row.workflow_run_id,
                request_id=row.request_id,
                event_type=row.event_type,
                component=row.component,
                agent_name=row.agent_name,
                provider=row.provider,
                model=row.model,
                outcome=cast(TelemetryOutcome, row.outcome),
                duration_ms=row.duration_ms,
                input_tokens=row.input_tokens,
                output_tokens=row.output_tokens,
                error_type=row.error_type,
                attributes=_safe_event_attributes(row.attributes),
                created_at=row.created_at,
            )
            for row in rows
        ],
    )


@router.post("/telemetry/purge", response_model=TelemetryPurgeResponse)
def purge_expired_telemetry(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> TelemetryPurgeResponse:
    """Delete only the current user's telemetry older than configured retention."""
    if user.role not in {"admin", "operator"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="An admin or operator role is required to purge telemetry.",
        )
    settings = _settings(request)
    cutoff = datetime.now(UTC) - timedelta(days=settings.telemetry_retention_days)
    result = cast(
        CursorResult[Any],
        db.execute(
            delete(TelemetryEvent).where(
                TelemetryEvent.owner_user_id == user.id,
                TelemetryEvent.created_at < cutoff,
            )
        ),
    )
    db.commit()
    return TelemetryPurgeResponse(
        deleted_count=max(0, int(result.rowcount or 0)),
        retention_days=settings.telemetry_retention_days,
        cutoff_at=cutoff,
    )
