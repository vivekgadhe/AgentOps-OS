"""Shared schemas for multi-agent execution."""

from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

AgentStatus = Literal["succeeded", "failed"]
VALID_AGENT_ROLES = frozenset({"admin", "operator", "viewer"})


class AgentContext(BaseModel):
    """Validated context supplied to an agent."""

    model_config = ConfigDict(extra="forbid")

    goal: str = Field(min_length=1, max_length=10_000)
    actor_role: str
    workflow_id: UUID | None = None
    task_id: UUID | None = None

    # Results are keyed by the name or key of the completed agent/task.
    prior_results: dict[str, dict[str, Any]] = Field(default_factory=dict)

    # Additional non-secret execution metadata.
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("goal")
    @classmethod
    def normalize_goal(cls, value: str) -> str:
        """Reject blank goals and normalize surrounding whitespace."""
        normalized = value.strip()

        if not normalized:
            raise ValueError("Agent goal cannot be blank.")

        return normalized

    @field_validator("actor_role")
    @classmethod
    def validate_actor_role(cls, value: str) -> str:
        """Require a recognized application role."""
        if value not in VALID_AGENT_ROLES:
            raise ValueError("Invalid actor role.")

        return value


class AgentResult(BaseModel):
    """Standard result returned by a specialized agent."""

    model_config = ConfigDict(extra="forbid")

    agent_name: str = Field(pattern=r"^[a-z][a-z0-9_]{0,99}$")
    status: AgentStatus
    summary: str = Field(min_length=1, max_length=2_000)
    output: dict[str, Any] = Field(default_factory=dict)

    # Safe, structured failure information; never store stack traces here.
    error_type: str | None = None
    error_message: str | None = Field(default=None, max_length=1_000)

    @field_validator("summary")
    @classmethod
    def normalize_summary(cls, value: str) -> str:
        """Reject blank summaries."""
        normalized = value.strip()

        if not normalized:
            raise ValueError("Agent result summary cannot be blank.")

        return normalized

    @model_validator(mode="after")
    def validate_failure_information(self) -> "AgentResult":
        """Require error information for failed agents."""
        if self.status == "failed":
            if not self.error_type or not self.error_type.strip():
                raise ValueError("Failed agent results require an error type.")

            if not self.error_message or not self.error_message.strip():
                raise ValueError(
                    "Failed agent results require an error message."
                )
        elif self.error_type is not None or self.error_message is not None:
            raise ValueError(
                "Successful agent results cannot contain failure information."
            )

        return self