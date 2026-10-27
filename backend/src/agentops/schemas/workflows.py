
"""Request and response schemas for workflow execution."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TaskCreate(BaseModel):
    """Definition of a task to include in a new workflow."""

    key: str = Field(min_length=1, max_length=64)
    name: str = Field(min_length=1, max_length=200)
    tool_name: str | None = Field(default=None, max_length=100)
    input_data: dict[str, Any] = Field(default_factory=dict)
    max_attempts: int = Field(default=3, ge=1, le=10)
    timeout_seconds: int = Field(default=300, ge=1, le=3600)

    @field_validator("key", "name")
    @classmethod
    def reject_blank_strings(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Value cannot be blank")
        return value.strip()

    @field_validator("tool_name")
    @classmethod
    def reject_blank_tool_name(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            raise ValueError("Tool name cannot be blank")
        return value.strip() if value is not None else None


class WorkflowCreate(BaseModel):
    """Request body for creating a workflow."""

    goal: str = Field(min_length=1, max_length=10_000)
    tasks: list[TaskCreate] = Field(min_length=1, max_length=100)

    @field_validator("goal")
    @classmethod
    def reject_blank_goal(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Goal cannot be blank")
        return value.strip()


class TaskResponse(BaseModel):
    """Public task representation."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    key: str
    name: str
    tool_name: str | None
    status: str
    input_data: dict[str, Any] | None
    output_data: dict[str, Any] | None
    error: dict[str, Any] | None
    attempt_count: int
    max_attempts: int
    started_at: datetime | None
    finished_at: datetime | None


class WorkflowResponse(BaseModel):
    """Public workflow representation."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    goal: str
    status: str
    plan: dict[str, Any] | None
    error: dict[str, Any] | None
    started_at: datetime | None
    finished_at: datetime | None
    created_at: datetime
    updated_at: datetime
    tasks: list[TaskResponse] = Field(default_factory=list)