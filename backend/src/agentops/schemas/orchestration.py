"""Schemas for multi-agent orchestration plans and results."""

from collections import deque
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from agentops.schemas.agents import AgentResult


class OrchestrationTask(BaseModel):
    """An agent assigned to one task in an orchestration plan."""

    model_config = ConfigDict(extra="forbid")

    key: str = Field(pattern=r"^[a-z][a-z0-9_]{0,63}$")
    agent_name: str = Field(pattern=r"^[a-z][a-z0-9_]{0,99}$")
    goal: str | None = Field(default=None, min_length=1, max_length=10_000)
    depends_on: list[str] = Field(default_factory=list, max_length=100)

    @field_validator("goal")
    @classmethod
    def normalize_goal(cls, value: str | None) -> str | None:
        """Reject blank task-specific goals."""
        if value is None:
            return None

        normalized = value.strip()

        if not normalized:
            raise ValueError("Task goal cannot be blank.")

        return normalized

    @field_validator("depends_on")
    @classmethod
    def normalize_dependencies(cls, values: list[str]) -> list[str]:
        """Normalize dependency keys and reject duplicates."""
        normalized: list[str] = []
        seen: set[str] = set()

        for value in values:
            dependency = value.strip()

            if not dependency:
                raise ValueError("Dependency keys cannot be blank.")

            if dependency in seen:
                raise ValueError(f"Duplicate dependency key: {dependency}")

            normalized.append(dependency)
            seen.add(dependency)

        return normalized


class OrchestrationPlan(BaseModel):
    """A validated workflow describing how agents collaborate."""

    model_config = ConfigDict(extra="forbid")

    goal: str = Field(min_length=1, max_length=10_000)
    tasks: list[OrchestrationTask] = Field(min_length=1, max_length=100)

    @field_validator("goal")
    @classmethod
    def normalize_goal(cls, value: str) -> str:
        """Reject blank workflow goals."""
        normalized = value.strip()

        if not normalized:
            raise ValueError("Orchestration goal cannot be blank.")

        return normalized

    @model_validator(mode="after")
    def validate_dependency_graph(self) -> "OrchestrationPlan":
        """Reject duplicate keys, unknown dependencies, and dependency cycles."""
        keys = [task.key for task in self.tasks]
        known_keys = set(keys)

        if len(keys) != len(known_keys):
            raise ValueError("Orchestration plan contains duplicate task keys.")

        in_degree = {key: 0 for key in keys}
        children: dict[str, list[str]] = {key: [] for key in keys}

        for task in self.tasks:
            for dependency in task.depends_on:
                if dependency == task.key:
                    raise ValueError(f"Task '{task.key}' cannot depend on itself.")

                if dependency not in known_keys:
                    raise ValueError(f"Task '{task.key}' depends on unknown task '{dependency}'.")

                in_degree[task.key] += 1
                children[dependency].append(task.key)

        ready = deque(key for key in keys if in_degree[key] == 0)
        processed = 0

        while ready:
            current = ready.popleft()
            processed += 1

            for child in children[current]:
                in_degree[child] -= 1

                if in_degree[child] == 0:
                    ready.append(child)

        if processed != len(keys):
            raise ValueError("Orchestration plan contains a dependency cycle.")

        return self


class OrchestrationTaskResult(BaseModel):
    """Execution outcome for one agent task."""

    model_config = ConfigDict(extra="forbid")

    key: str
    agent_name: str
    status: Literal["succeeded", "failed", "skipped"]
    result: AgentResult | None = None
    error_type: str | None = None
    error_message: str | None = Field(default=None, max_length=1000)


class OrchestrationResult(BaseModel):
    """Final outcome of a multi-agent orchestration run."""

    model_config = ConfigDict(extra="forbid")

    goal: str
    status: Literal["succeeded", "failed"]
    tasks: list[OrchestrationTaskResult]
