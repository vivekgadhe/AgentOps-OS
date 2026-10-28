"""Schemas for LLM-generated workflow plans."""

from collections import deque
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class WorkflowPlanRequest(BaseModel):
    """Request to generate a workflow plan from a goal."""

    model_config = ConfigDict(extra="forbid")

    goal: str = Field(min_length=1, max_length=10_000)

    @field_validator("goal")
    @classmethod
    def normalize_goal(cls, value: str) -> str:
        """Reject blank goals and normalize surrounding whitespace."""
        normalized = value.strip()

        if not normalized:
            raise ValueError("Workflow goal cannot be blank.")

        return normalized


class PlannedTask(BaseModel):
    """A proposed task within an AI-generated workflow plan."""

    model_config = ConfigDict(extra="forbid")

    key: str = Field(min_length=1, max_length=64)
    name: str = Field(min_length=1, max_length=200)
    tool_name: str = Field(min_length=1, max_length=100)
    input_data: dict[str, Any] = Field(default_factory=dict)
    max_attempts: int = Field(default=3, ge=1, le=10)
    timeout_seconds: int = Field(default=300, ge=1, le=3600)
    depends_on: list[str] = Field(default_factory=list, max_length=100)

    @field_validator("key", "name")
    @classmethod
    def normalize_required_strings(cls, value: str) -> str:
        """Reject blank values and remove surrounding whitespace."""
        normalized = value.strip()

        if not normalized:
            raise ValueError("Value cannot be blank.")

        return normalized

    @field_validator("tool_name")
    @classmethod
    def normalize_tool_name(cls, value: str) -> str:
        """Reject blank tool names and normalize whitespace."""
        normalized = value.strip()

        if not normalized:
            raise ValueError("Tool name cannot be blank.")

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


class WorkflowPlan(BaseModel):
    """Validate the structure and dependency graph of a proposed plan."""

    model_config = ConfigDict(extra="forbid")

    tasks: list[PlannedTask] = Field(min_length=1, max_length=100)

    @model_validator(mode="after")
    def validate_task_graph(self) -> "WorkflowPlan":
        """Reject duplicate keys, invalid references, and dependency cycles."""
        task_keys = [task.key for task in self.tasks]
        known_keys = set(task_keys)

        if len(task_keys) != len(known_keys):
            raise ValueError("Workflow plan contains duplicate task keys.")

        in_degree: dict[str, int] = {key: 0 for key in task_keys}
        children: dict[str, list[str]] = {key: [] for key in task_keys}

        for task in self.tasks:
            for dependency in task.depends_on:
                if dependency == task.key:
                    raise ValueError(f"Task '{task.key}' cannot depend on itself.")

                if dependency not in known_keys:
                    raise ValueError(f"Task '{task.key}' depends on unknown task '{dependency}'.")

                in_degree[task.key] += 1
                children[dependency].append(task.key)

        ready = deque(key for key in task_keys if in_degree[key] == 0)
        processed = 0

        while ready:
            current = ready.popleft()
            processed += 1

            for child in children[current]:
                in_degree[child] -= 1

                if in_degree[child] == 0:
                    ready.append(child)

        if processed != len(task_keys):
            raise ValueError("Workflow plan contains a dependency cycle.")

        return self
