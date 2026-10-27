
"""Core workflow execution service."""

from __future__ import annotations

import logging
import uuid
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from agentops.db.models import (
    EventLevel,
    ExecutionEvent,
    TaskRun,
    TaskStatus,
    User,
    WorkflowRun,
    WorkflowStatus,
)
from agentops.services.task_runner import run_task

logger = logging.getLogger(__name__)

TaskHandler = Callable[[dict[str, Any]], dict[str, Any]]


class ExecutionError(Exception):
    """Raised when a workflow cannot be executed."""


class ExecutionService:
    """Create workflows and execute tasks through registered handlers."""

    def __init__(self, session: Session) -> None:
        self.session = session
        self._handlers: dict[str, TaskHandler] = {}

    def register_handler(self, name: str, handler: TaskHandler) -> None:
        """Register a trusted handler under a unique name."""
        if not name.strip():
            raise ValueError("Handler name cannot be blank")
        if name in self._handlers:
            raise ValueError(f"Handler already registered: {name}")
        self._handlers[name] = handler

    def create_workflow(
        self,
        user: User,
        goal: str,
        tasks: list[dict[str, Any]],
    ) -> WorkflowRun:
        """Persist a workflow and its initial tasks."""
        if not goal.strip():
            raise ValueError("Goal cannot be blank")
        if not tasks:
            raise ValueError("A workflow must contain at least one task")

        seen_keys: set[str] = set()
        for task in tasks:
            key = task.get("key")
            name = task.get("name")
            tool_name = task.get("tool_name")

            if not isinstance(key, str) or not key.strip():
                raise ValueError("Every task must have a non-empty key")
            if key in seen_keys:
                raise ValueError(f"Duplicate task key: {key}")
            if not isinstance(name, str) or not name.strip():
                raise ValueError(f"Task {key} must have a non-empty name")
            if tool_name is not None and (
                not isinstance(tool_name, str) or not tool_name.strip()
            ):
                raise ValueError(f"Task {key} has an invalid tool name")

            seen_keys.add(key)

        workflow = WorkflowRun(
            created_by=user.id,
            goal=goal.strip(),
            status=WorkflowStatus.PENDING.value,
        )
        self.session.add(workflow)
        self.session.flush()

        for task_data in tasks:
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

        self._record_event(
            workflow.id,
            event_type="workflow.created",
            message="Workflow created",
            data={"task_count": len(tasks)},
        )
        self.session.commit()
        self.session.refresh(workflow)
        return workflow

    def execute_workflow(self, workflow_id: uuid.UUID) -> WorkflowRun:
        """Execute pending tasks in a workflow in deterministic order."""
        workflow = self.session.scalar(
            select(WorkflowRun)
            .where(WorkflowRun.id == workflow_id)
            .with_for_update()
        )
        if workflow is None:
            raise ExecutionError("Workflow not found")

        if workflow.status != WorkflowStatus.PENDING.value:
            raise ExecutionError(
                f"Workflow cannot start from status '{workflow.status}'"
            )

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

        workflow.status = WorkflowStatus.RUNNING.value
        workflow.started_at = datetime.now(UTC)
        self._record_event(
            workflow.id,
            event_type="workflow.started",
            message="Workflow execution started",
        )
        self.session.commit()

        try:
            for task in tasks:
                self._execute_task(workflow, task)

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
            workflow.error = {"type": type(exc).__name__, "message": str(exc)}
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


    def _execute_task(self, workflow: WorkflowRun, task: TaskRun) -> None:
        """Run a task with bounded retries and persist its outcome."""
        tool_name = task.tool_name
        handler = self._handlers.get(tool_name) if tool_name else None

        if handler is None:
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

            raise ExecutionError(
                f"No handler registered for task '{task.key}'"
            )

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
                message=(
                    "Task execution started"
                    if attempt == 1
                    else "Retrying failed task"
                ),
                data={
                    "task_key": task.key,
                    "tool_name": tool_name,
                    "attempt": attempt,
                    "max_attempts": task.max_attempts,
                },
            )
            self.session.flush()

            try:
                result = run_task(
                    handler,
                    task.input_data or {},
                    timeout_seconds=task.timeout_seconds,
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