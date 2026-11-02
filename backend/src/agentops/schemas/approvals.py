"""API schemas for human approval workflows."""

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

ApprovalStatus = Literal["pending", "approved", "rejected", "expired", "cancelled", "executed"]


class ApprovalDecisionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    reason: str | None = Field(default=None, max_length=2000)


class ApprovalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    workflow_run_id: UUID
    task_run_id: UUID
    requester_user_id: UUID
    decided_by_user_id: UUID | None
    tool_name: str
    action_summary: str
    input_snapshot: dict[str, Any]
    status: ApprovalStatus
    decision_reason: str | None
    requested_at: datetime
    expires_at: datetime
    decided_at: datetime | None


class ApprovalDecisionResponse(BaseModel):
    approval: ApprovalResponse
    workflow_status: str
