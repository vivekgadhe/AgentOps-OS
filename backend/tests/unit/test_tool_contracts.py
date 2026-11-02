"""Tests for tool input and output contract enforcement."""

from typing import Any
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from agentops.db.models.enums import TaskStatus
from agentops.services.execution import ExecutionError, ExecutionService
from agentops.services.handlers import register_builtin_handlers


def _make_task(
    input_data: dict[str, Any],
) -> tuple[ExecutionService, MagicMock, MagicMock]:
    """Create a service and task for isolated contract tests."""
    service = ExecutionService(MagicMock())
    register_builtin_handlers(service)

    workflow = MagicMock()
    workflow.id = uuid4()

    task = MagicMock()
    task.id = uuid4()
    task.key = "summarize"
    task.tool_name = "summarize_input"
    task.input_data = input_data
    task.max_attempts = 1
    task.attempt_count = 0
    task.timeout_seconds = 5
    task.status = TaskStatus.PENDING.value

    return service, workflow, task


def test_invalid_tool_input_fails_without_running_handler(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Reject non-string text before invoking the task runner."""
    service, workflow, task = _make_task({"text": ["not", "text"]})

    def unexpected_runner(
        handler: Any,
        input_data: dict[str, Any],
        timeout_seconds: int,
    ) -> dict[str, Any]:
        pytest.fail("The runner must not execute when input is invalid.")

    monkeypatch.setattr(
        "agentops.services.execution.run_task",
        unexpected_runner,
    )

    with pytest.raises(ExecutionError, match="failed after 1 attempts"):
        service._execute_task(workflow, task)

    assert task.status == TaskStatus.FAILED.value
    assert task.error["type"] == "ToolInputValidationError"
    assert task.attempt_count == 1


def test_invalid_tool_output_fails_the_task(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Reject output that does not satisfy the tool's output schema."""
    service, workflow, task = _make_task({"text": "Hello AgentOps"})

    def malformed_runner_result(
        handler: Any,
        input_data: dict[str, Any],
        timeout_seconds: int,
    ) -> dict[str, Any]:
        return {"summary": "Hello AgentOps"}

    monkeypatch.setattr(
        "agentops.services.execution.run_task",
        malformed_runner_result,
    )

    with pytest.raises(ExecutionError, match="failed after 1 attempts"):
        service._execute_task(workflow, task)

    assert task.status == TaskStatus.FAILED.value
    assert task.error["type"] == "ToolOutputValidationError"
    assert task.attempt_count == 1
