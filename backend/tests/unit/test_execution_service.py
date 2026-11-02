"""Unit tests for the workflow execution service."""

from typing import Any, cast
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from agentops.db.models import TaskStatus, WorkflowStatus
from agentops.services.execution import ExecutionError, ExecutionService


@pytest.fixture
def session() -> MagicMock:
    """Provide a mocked SQLAlchemy session."""
    return MagicMock(spec=Session)


@pytest.fixture
def service(session: MagicMock) -> ExecutionService:
    """Provide an execution service using a mocked session."""
    return ExecutionService(cast(Session, session))


@pytest.fixture
def inline_task_runner(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep execution-service unit tests independent of subprocesses."""
    monkeypatch.setattr(
        "agentops.services.execution.run_task",
        lambda handler, input_data, timeout_seconds: handler(input_data),
    )


def test_register_handler(service: ExecutionService) -> None:
    """Register a task handler successfully."""

    def handler(data: dict[str, object]) -> dict[str, object]:
        return {"result": "ok"}

    service.register_handler("example", handler)

    assert service._handlers["example"] is handler


def test_register_handler_rejects_blank_name(
    service: ExecutionService,
) -> None:
    """Reject handler names containing only whitespace."""
    with pytest.raises(ValueError, match="cannot be blank"):
        service.register_handler("  ", lambda data: {})


def test_register_handler_rejects_duplicate_name(
    service: ExecutionService,
) -> None:
    """Reject duplicate handler registrations."""
    service.register_handler("example", lambda data: {})

    with pytest.raises(ValueError, match="already registered"):
        service.register_handler("example", lambda data: {})


def test_create_workflow_rejects_blank_goal(
    service: ExecutionService,
) -> None:
    """Reject a blank workflow goal."""
    user = MagicMock()
    user.id = uuid4()

    with pytest.raises(ValueError, match="Goal cannot be blank"):
        service.create_workflow(
            user,
            "  ",
            [{"key": "task1", "name": "Task"}],
        )


def test_create_workflow_requires_tasks(
    service: ExecutionService,
) -> None:
    """Reject workflows without tasks."""
    user = MagicMock()
    user.id = uuid4()

    with pytest.raises(ValueError, match="at least one task"):
        service.create_workflow(user, "Run a task", [])


def test_create_workflow_rejects_duplicate_task_keys(
    service: ExecutionService,
) -> None:
    """Reject duplicate task keys."""
    user = MagicMock()
    user.id = uuid4()
    tasks = [
        {"key": "task1", "name": "First task"},
        {"key": "task1", "name": "Duplicate task"},
    ]

    with pytest.raises(ValueError, match="Duplicate task key"):
        service.create_workflow(user, "Run tasks", tasks)


def test_execute_workflow_rejects_missing_workflow(
    service: ExecutionService,
) -> None:
    """Reject execution when the workflow does not exist."""
    cast(MagicMock, service.session).scalar.return_value = None

    with pytest.raises(ExecutionError, match="Workflow not found"):
        service.execute_workflow(uuid4())


def test_execute_workflow_rejects_non_pending_workflow(
    service: ExecutionService,
) -> None:
    """Reject execution when the workflow is not pending."""
    workflow = MagicMock()
    workflow.status = WorkflowStatus.SUCCEEDED.value
    cast(MagicMock, service.session).scalar.return_value = workflow

    with pytest.raises(ExecutionError, match="cannot start"):
        service.execute_workflow(uuid4())


def test_task_status_values() -> None:
    """Verify task status values used by the execution engine."""
    assert TaskStatus.PENDING.value == "pending"
    assert TaskStatus.RUNNING.value == "running"
    assert TaskStatus.SUCCEEDED.value == "succeeded"
    assert TaskStatus.FAILED.value == "failed"


def test_task_succeeds_after_retry(
    service: ExecutionService,
    inline_task_runner: None,
) -> None:
    """Verify that a task succeeds after its first attempt fails."""
    workflow = MagicMock()
    workflow.id = uuid4()

    task = MagicMock()
    task.id = uuid4()
    task.key = "task1"
    task.tool_name = "example"
    task.input_data = {"value": 1}
    task.max_attempts = 3
    task.timeout_seconds = 10
    task.attempt_count = 0

    attempts = 0

    def flaky_handler(data: dict[str, Any]) -> dict[str, Any]:
        nonlocal attempts
        attempts += 1

        if attempts == 1:
            raise RuntimeError("Temporary failure")

        return {"result": "success"}

    service.register_handler("example", flaky_handler)

    service._execute_task(workflow, task)

    assert attempts == 2
    assert task.attempt_count == 2
    assert task.status == TaskStatus.SUCCEEDED.value
    assert task.output_data == {"result": "success"}
    assert task.error is None
    assert task.finished_at is not None


def test_task_fails_after_maximum_attempts(
    service: ExecutionService,
    inline_task_runner: None,
) -> None:
    """Verify that a task fails after exhausting its retries."""
    workflow = MagicMock()
    workflow.id = uuid4()

    task = MagicMock()
    task.id = uuid4()
    task.key = "task1"
    task.tool_name = "example"
    task.input_data = {}
    task.max_attempts = 3
    task.timeout_seconds = 10
    task.attempt_count = 0

    attempts = 0

    def failing_handler(data: dict[str, Any]) -> dict[str, Any]:
        nonlocal attempts
        attempts += 1
        raise RuntimeError("Persistent failure")

    service.register_handler("example", failing_handler)

    with pytest.raises(ExecutionError, match="failed after 3 attempts"):
        service._execute_task(workflow, task)

    assert attempts == 3
    assert task.attempt_count == 3
    assert task.status == TaskStatus.FAILED.value
    assert task.finished_at is not None
    assert task.error["type"] == "RuntimeError"


def test_task_succeeds_without_retry(
    service: ExecutionService,
    inline_task_runner: None,
) -> None:
    """Verify that a successful first attempt does not trigger retries."""
    workflow = MagicMock()
    workflow.id = uuid4()

    task = MagicMock()
    task.id = uuid4()
    task.key = "task1"
    task.tool_name = "example"
    task.input_data = {}
    task.max_attempts = 3
    task.timeout_seconds = 10
    task.attempt_count = 0

    service.register_handler(
        "example",
        lambda data: {"result": "success"},
    )

    service._execute_task(workflow, task)

    assert task.attempt_count == 1
    assert task.status == TaskStatus.SUCCEEDED.value
    assert task.finished_at is not None
    assert task.error is None
