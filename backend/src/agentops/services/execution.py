"""Core workflow execution service."""

from __future__ import annotations

import logging
import uuid
from collections import deque
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.orm import Session

from agentops.db.models import (
    EventLevel,
    ExecutionEvent,
    TaskDependency,
    TaskRun,
    TaskStatus,
    User,
    WorkflowRun,
    WorkflowStatus,
)
from agentops.services.task_runner import run_task
from agentops.services.tool_registry import (
    ToolAccessDeniedError,
    ToolDefinition,
    ToolNotFoundError,
    ToolRegistry,
)

logger = logging.getLogger(__name__)

TaskHandler = Callable[[dict[str, Any]], dict[str, Any]]


class _FlexibleToolPayload(BaseModel):
    """Compatibility schema for handlers without explicit contracts."""

    model_config = ConfigDict(extra="allow")


def _topological_order(
    task_keys: list[str],
    dependencies_by_key: dict[str, list[str]],
) -> list[str]:
    """Return tasks in deterministic prerequisite-first order."""
    key_set = set(task_keys)

    if len(key_set) != len(task_keys):
        raise ValueError("Workflow contains duplicate task keys")

    children: dict[str, list[str]] = {key: [] for key in task_keys}
    in_degree: dict[str, int] = {}

    for key in task_keys:
        prerequisites = dependencies_by_key.get(key, [])

        unknown = [dependency for dependency in prerequisites if dependency not in key_set]

        if unknown:
            raise ValueError(f"Task '{key}' depends on unknown task '{unknown[0]}'")

        in_degree[key] = len(prerequisites)

        for prerequisite in prerequisites:
            children[prerequisite].append(key)

    ready = deque(key for key in task_keys if in_degree[key] == 0)
    ordered: list[str] = []

    while ready:
        current = ready.popleft()
        ordered.append(current)

        for child in children[current]:
            in_degree[child] -= 1

            if in_degree[child] == 0:
                ready.append(child)

    if len(ordered) != len(task_keys):
        cyclic = [key for key in task_keys if in_degree[key] > 0]
        raise ValueError("Workflow contains a dependency cycle involving: " + ", ".join(cyclic))

    return ordered


class ExecutionError(Exception):
    """Raised when a workflow cannot be executed."""


class ExecutionService:
    """Create workflows and execute tasks through registered handlers."""

    def __init__(self, session: Session) -> None:
        self.session = session
        self._handlers: dict[str, TaskHandler] = {}
        self._tool_registry = ToolRegistry()

    def register_tool(self, definition: ToolDefinition) -> None:
        """Register a tool with explicit input and output contracts."""
        self._tool_registry.register(definition)
        self._handlers[definition.name] = definition.handler

    def register_handler(
        self,
        name: str,
        handler: TaskHandler,
    ) -> None:
        """Register a handler using a permissive compatibility schema."""
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Handler name cannot be blank")

        if not callable(handler):
            raise ValueError("Handler must be callable")

        normalized_name = name.strip()

        self.register_tool(
            ToolDefinition(
                name=normalized_name,
                description=f"Task handler for {normalized_name}",
                input_model=_FlexibleToolPayload,
                output_model=_FlexibleToolPayload,
                handler=handler,
            )
        )

    def create_workflow(
        self,
        user: User,
        goal: str,
        tasks: list[dict[str, Any]],
    ) -> WorkflowRun:
        """Validate and persist a workflow and its dependency graph."""
        if not goal.strip():
            raise ValueError("Goal cannot be blank")

        if not tasks:
            raise ValueError("A workflow must contain at least one task")

        normalized_tasks: list[dict[str, Any]] = []
        seen_keys: set[str] = set()

        # Validate and normalize task definitions first.
        for task in tasks:
            key = task.get("key")
            name = task.get("name")
            tool_name = task.get("tool_name")

            if not isinstance(key, str) or not key.strip():
                raise ValueError("Every task must have a non-empty key")

            key = key.strip()

            if key in seen_keys:
                raise ValueError(f"Duplicate task key: {key}")

            if not isinstance(name, str) or not name.strip():
                raise ValueError(f"Task {key} must have a non-empty name")

            if tool_name is not None and (not isinstance(tool_name, str) or not tool_name.strip()):
                raise ValueError(f"Task {key} has an invalid tool name")

            normalized_task = dict(task)
            normalized_task["key"] = key
            normalized_task["name"] = name.strip()

            if tool_name is not None:
                normalized_task["tool_name"] = tool_name.strip()

            normalized_tasks.append(normalized_task)
            seen_keys.add(key)

        # Validate dependency references before writing anything.
        task_keys = [task["key"] for task in normalized_tasks]
        dependencies_by_key: dict[str, list[str]] = {}

        for task in normalized_tasks:
            key = task["key"]
            raw_dependencies = task.get("depends_on", [])

            if not isinstance(raw_dependencies, list):
                raise ValueError(f"Task '{key}' dependencies must be a list")

            dependencies: list[str] = []
            seen_dependencies: set[str] = set()

            for raw_dependency in raw_dependencies:
                if not isinstance(raw_dependency, str) or not raw_dependency.strip():
                    raise ValueError(f"Task '{key}' has an invalid dependency key")

                dependency = raw_dependency.strip()

                if dependency == key:
                    raise ValueError(f"Task '{key}' cannot depend on itself")

                if dependency not in seen_keys:
                    raise ValueError(f"Task '{key}' depends on unknown task '{dependency}'")

                if dependency in seen_dependencies:
                    raise ValueError(f"Task '{key}' lists dependency '{dependency}' more than once")

                dependencies.append(dependency)
                seen_dependencies.add(dependency)

            task["depends_on"] = dependencies
            dependencies_by_key[key] = dependencies

        # Reject circular dependencies before creating database records.
        _topological_order(task_keys, dependencies_by_key)

        workflow = WorkflowRun(
            created_by=user.id,
            goal=goal.strip(),
            status=WorkflowStatus.PENDING.value,
        )
        self.session.add(workflow)
        self.session.flush()

        # Create tasks and retain their IDs for dependency persistence.
        task_runs_by_key: dict[str, TaskRun] = {}

        for task_data in normalized_tasks:
            task_run = TaskRun(
                workflow_run_id=workflow.id,
                key=task_data["key"],
                name=task_data["name"],
                tool_name=task_data.get("tool_name"),
                input_data=task_data.get("input_data", {}),
                status=TaskStatus.PENDING.value,
                max_attempts=task_data.get("max_attempts", 3),
                timeout_seconds=task_data.get("timeout_seconds", 300),
            )

            self.session.add(task_run)
            task_runs_by_key[task_data["key"]] = task_run

        # Flush so task IDs are available for the dependency edges.
        self.session.flush()

        for task_key, prerequisites in dependencies_by_key.items():
            task_run = task_runs_by_key[task_key]

            for prerequisite_key in prerequisites:
                prerequisite = task_runs_by_key[prerequisite_key]

                self.session.add(
                    TaskDependency(
                        task_id=task_run.id,
                        depends_on_task_id=prerequisite.id,
                        workflow_run_id=workflow.id,
                    )
                )

        self.session.flush()

        self._record_event(
            workflow.id,
            event_type="workflow.created",
            message="Workflow created",
            data={"task_count": len(normalized_tasks)},
        )

        self.session.commit()
        self.session.refresh(workflow)

        return workflow

    def execute_workflow(
        self,
        workflow_id: uuid.UUID,
        *,
        actor_role: str | None = None,
    ) -> WorkflowRun:
        """Execute tasks in dependency order and skip blocked tasks."""
        workflow = self.session.scalar(
            select(WorkflowRun).where(WorkflowRun.id == workflow_id).with_for_update()
        )
        if workflow is None:
            raise ExecutionError("Workflow not found")

        # Resolve the creator's role for internal callers that do not pass
        # the authenticated actor's role explicitly.
        if actor_role is None:
            creator = self.session.get(User, workflow.created_by)
            if creator is None or not creator.is_active:
                raise ExecutionError("Workflow creator is unavailable.")
            actor_role = creator.role

        if workflow.status != WorkflowStatus.PENDING.value:
            raise ExecutionError(f"Workflow cannot start from status '{workflow.status}'")

        tasks = list(
            self.session.scalars(
                select(TaskRun)
                .where(TaskRun.workflow_run_id == workflow.id)
                .order_by(TaskRun.created_at, TaskRun.key)
                .with_for_update()
            ).all()
        )
        if not tasks:
            raise ExecutionError("Workflow has no tasks")

        tasks_by_id = {task.id: task for task in tasks}
        tasks_by_key = {task.key: task for task in tasks}
        dependencies_by_key: dict[str, list[str]] = {task.key: [] for task in tasks}

        dependency_edges = list(
            self.session.scalars(
                select(TaskDependency).where(TaskDependency.workflow_run_id == workflow.id)
            ).all()
        )

        for edge in dependency_edges:
            task = tasks_by_id.get(edge.task_id)
            prerequisite = tasks_by_id.get(edge.depends_on_task_id)
            if task is None or prerequisite is None:
                raise ExecutionError("Workflow contains an invalid dependency reference")
            dependencies_by_key[task.key].append(prerequisite.key)

        try:
            ordered_keys = _topological_order(
                [task.key for task in tasks],
                dependencies_by_key,
            )
        except ValueError as exc:
            raise ExecutionError(str(exc)) from exc

        tasks = [tasks_by_key[key] for key in ordered_keys]

        workflow.status = WorkflowStatus.RUNNING.value
        workflow.started_at = datetime.now(UTC)
        self._record_event(
            workflow.id,
            event_type="workflow.started",
            message="Workflow execution started",
        )
        self.session.commit()

        first_task_error: ExecutionError | None = None
        try:
            for task in tasks:
                # A task can run only if every prerequisite succeeded.
                blocked_by = [
                    dependency_key
                    for dependency_key in dependencies_by_key[task.key]
                    if tasks_by_key[dependency_key].status != TaskStatus.SUCCEEDED.value
                ]

                if blocked_by:
                    task.status = TaskStatus.SKIPPED.value
                    task.error = {
                        "type": "DependencyFailed",
                        "message": (
                            "Task skipped because dependencies did not "
                            f"succeed: {', '.join(blocked_by)}"
                        ),
                        "dependencies": blocked_by,
                    }
                    task.finished_at = datetime.now(UTC)
                    self._record_event(
                        workflow.id,
                        task_run_id=task.id,
                        event_type="task.skipped",
                        level=EventLevel.WARNING.value,
                        message="Task skipped because dependencies failed",
                        data={
                            "task_key": task.key,
                            "blocked_by": blocked_by,
                        },
                    )
                    self.session.flush()
                    continue

                try:
                    self._execute_task(
                        workflow,
                        task,
                        actor_role=actor_role,
                    )
                except ExecutionError as exc:
                    # Continue independent tasks; descendants of failed tasks
                    # will be skipped when their prerequisites are checked.
                    if first_task_error is None:
                        first_task_error = exc

            if first_task_error is not None:
                raise first_task_error

            if any(task.status != TaskStatus.SUCCEEDED.value for task in tasks):
                raise ExecutionError("Workflow contains tasks that did not succeed")

            workflow.status = WorkflowStatus.SUCCEEDED.value
            workflow.finished_at = datetime.now(UTC)
            self._record_event(
                workflow.id,
                event_type="workflow.succeeded",
                message="Workflow completed successfully",
            )

        except Exception as exc:
            logger.exception(
                "workflow_execution_failed",
                extra={"workflow_id": str(workflow.id)},
            )
            workflow.status = WorkflowStatus.FAILED.value
            workflow.error = {
                "type": type(exc).__name__,
                "message": str(exc),
            }
            workflow.finished_at = datetime.now(UTC)
            self._record_event(
                workflow.id,
                event_type="workflow.failed",
                level=EventLevel.ERROR.value,
                message="Workflow execution failed",
                data={"error_type": type(exc).__name__},
            )

        self.session.commit()
        self.session.refresh(workflow)
        return workflow

    def _execute_task(
        self,
        workflow: WorkflowRun,
        task: TaskRun,
        *,
        actor_role: str | None = None,
    ) -> None:
        """Run a task with bounded retries and persist its outcome."""
        tool_name = task.tool_name
        tool_definition: ToolDefinition | None = None

        # Resolve the tool before attempting authorization. This preserves the
        # more useful HandlerNotFound failure for tasks without a registered tool.
        if tool_name:
            try:
                tool_definition = self._tool_registry.get(tool_name)
            except ToolNotFoundError:
                tool_definition = None

        if tool_definition is None:
            task.status = TaskStatus.FAILED.value
            task.error = {
                "type": "HandlerNotFound",
                "message": f"No registered handler for task '{task.key}'",
            }
            task.finished_at = datetime.now(UTC)
            self._record_event(
                workflow.id,
                task_run_id=task.id,
                event_type="task.failed",
                level=EventLevel.ERROR.value,
                message="No registered handler for task",
                data={
                    "task_key": task.key,
                    "tool_name": tool_name,
                },
            )
            self.session.flush()
            raise ExecutionError(f"No handler registered for task '{task.key}'")

        # Actor roles are optional only for internal/unit-test calls directly
        # invoking this method. Workflow execution always resolves a real role.
        # When no role is supplied here, skip authorization rather than passing
        # None to the registry.
        if actor_role is not None:
            try:
                self._tool_registry.authorize(tool_definition.name, actor_role)
            except ToolAccessDeniedError as exc:
                task.status = TaskStatus.FAILED.value
                task.error = {
                    "type": "ToolAccessDeniedError",
                    "message": str(exc),
                }
                task.finished_at = datetime.now(UTC)
                self._record_event(
                    workflow.id,
                    task_run_id=task.id,
                    event_type="tool.access_denied",
                    level=EventLevel.WARNING.value,
                    message="Tool execution denied by role policy",
                    data={
                        "task_key": task.key,
                        "tool_name": tool_definition.name,
                        "actor_role": actor_role,
                    },
                )
                self.session.flush()
                raise ExecutionError(str(exc)) from exc

        task.started_at = datetime.now(UTC)
        task.finished_at = None
        last_error: Exception | None = None

        for attempt in range(1, task.max_attempts + 1):
            task.attempt_count += 1
            task.status = TaskStatus.RUNNING.value
            self._record_event(
                workflow.id,
                task_run_id=task.id,
                event_type="task.started" if attempt == 1 else "task.retrying",
                message=("Task execution started" if attempt == 1 else "Retrying failed task"),
                data={
                    "task_key": task.key,
                    "tool_name": tool_definition.name,
                    "attempt": attempt,
                    "max_attempts": task.max_attempts,
                },
            )
            self.session.flush()

            try:
                validated_input = self._tool_registry.validate_input(
                    tool_definition.name,
                    task.input_data or {},
                )
                result = run_task(
                    tool_definition.handler,
                    validated_input,
                    timeout_seconds=task.timeout_seconds,
                )
                result = self._tool_registry.validate_output(
                    tool_definition.name,
                    result,
                )

                if not isinstance(result, dict):
                    raise TypeError("Task handler must return a dictionary")

                task.output_data = result
                task.error = None
                task.status = TaskStatus.SUCCEEDED.value
                task.finished_at = datetime.now(UTC)
                self._record_event(
                    workflow.id,
                    task_run_id=task.id,
                    event_type="task.succeeded",
                    message="Task completed successfully",
                    data={
                        "task_key": task.key,
                        "attempt": attempt,
                        "attempt_count": task.attempt_count,
                    },
                )
                self.session.flush()
                return

            except Exception as exc:
                last_error = exc
                task.error = {
                    "type": type(exc).__name__,
                    "message": str(exc),
                    "attempt": attempt,
                }
                self._record_event(
                    workflow.id,
                    task_run_id=task.id,
                    event_type="task.attempt_failed",
                    level=EventLevel.WARNING.value,
                    message="Task attempt failed",
                    data={
                        "task_key": task.key,
                        "attempt": attempt,
                        "max_attempts": task.max_attempts,
                        "error_type": type(exc).__name__,
                    },
                )
                self.session.flush()

        task.status = TaskStatus.FAILED.value
        task.finished_at = datetime.now(UTC)
        self._record_event(
            workflow.id,
            task_run_id=task.id,
            event_type="task.failed",
            level=EventLevel.ERROR.value,
            message="Task failed after exhausting retries",
            data={
                "task_key": task.key,
                "attempt_count": task.attempt_count,
                "max_attempts": task.max_attempts,
            },
        )
        self.session.flush()

        raise ExecutionError(
            f"Task '{task.key}' failed after {task.max_attempts} attempts"
        ) from last_error

    def _record_event(
        self,
        workflow_id: uuid.UUID,
        *,
        event_type: str,
        message: str,
        task_run_id: uuid.UUID | None = None,
        level: str = EventLevel.INFO.value,
        data: dict[str, Any] | None = None,
    ) -> None:
        """Add an execution event to the current transaction."""
        self.session.add(
            ExecutionEvent(
                workflow_run_id=workflow_id,
                task_run_id=task_run_id,
                event_type=event_type,
                level=level,
                message=message,
                data=data or {},
            )
        )
