"""Response contracts for the Phase 10 observability and analytics API."""

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

TelemetryOutcome = Literal["success", "failure", "refused"]


class ObservabilityOverviewResponse(BaseModel):
    """Owner-scoped workflow, task and model-generation indicators."""

    start_at: datetime
    end_at: datetime
    workflow_count: int
    workflow_status_counts: dict[str, int]
    workflow_success_rate: float
    average_workflow_duration_ms: float | None
    task_count: int
    task_status_counts: dict[str, int]
    task_success_rate: float
    average_task_duration_ms: float | None
    llm_attempt_count: int
    llm_success_count: int
    llm_failure_count: int
    llm_refusal_count: int
    llm_success_rate: float
    average_llm_duration_ms: float | None


class ProviderUsageItem(BaseModel):
    provider: str
    model: str
    attempt_count: int
    success_count: int
    failure_count: int
    refusal_count: int
    success_rate: float
    average_duration_ms: float | None


class ProviderUsageResponse(BaseModel):
    start_at: datetime
    end_at: datetime
    items: list[ProviderUsageItem]


class AgentUsageItem(BaseModel):
    agent_name: str
    generation_attempts: int
    success_count: int
    failure_count: int
    refusal_count: int
    success_rate: float
    average_duration_ms: float | None


class AgentUsageResponse(BaseModel):
    start_at: datetime
    end_at: datetime
    items: list[AgentUsageItem]


class WorkflowAnalyticsItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    goal: str
    status: str
    created_at: datetime
    started_at: datetime | None
    finished_at: datetime | None
    duration_ms: float | None
    task_count: int = Field(ge=0)
    succeeded_task_count: int = Field(ge=0)
    failed_task_count: int = Field(ge=0)


class WorkflowAnalyticsResponse(BaseModel):
    start_at: datetime
    end_at: datetime
    total: int
    limit: int
    offset: int
    items: list[WorkflowAnalyticsItem]


class TelemetryEventResponse(BaseModel):
    id: UUID
    workflow_run_id: UUID | None
    request_id: str | None
    event_type: str
    component: str
    agent_name: str | None
    provider: str
    model: str
    outcome: TelemetryOutcome
    duration_ms: float
    input_tokens: int | None
    output_tokens: int | None
    error_type: str | None
    attributes: dict[str, Any]
    created_at: datetime


class TelemetryEventsResponse(BaseModel):
    start_at: datetime
    end_at: datetime
    total: int
    limit: int
    offset: int
    items: list[TelemetryEventResponse]


class TelemetryPurgeResponse(BaseModel):
    deleted_count: int
    retention_days: int
    cutoff_at: datetime
