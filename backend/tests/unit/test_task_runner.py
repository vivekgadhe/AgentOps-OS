"""Unit tests for the isolated task runner."""

import pytest

from agentops.services._task_runner_test_support import (
    invalid_handler,
    slow_handler,
    successful_handler,
)
from agentops.services.task_runner import TaskTimeoutError, run_task


def test_run_task_returns_handler_result() -> None:
    """Return the handler's dictionary result."""
    result = run_task(
        successful_handler,
        {"value": "success"},
        timeout_seconds=10,
    )
    assert result == {"result": "success"}


def test_run_task_raises_timeout() -> None:
    """Terminate a handler that exceeds its time limit."""
    with pytest.raises(TaskTimeoutError, match="exceeded"):
        run_task(slow_handler, {}, timeout_seconds=2)


def test_run_task_rejects_non_dictionary_result() -> None:
    """Reject handler results that are not dictionaries."""
    with pytest.raises(RuntimeError, match="Handler failed"):
        run_task(invalid_handler, {}, timeout_seconds=10)


def test_run_task_rejects_invalid_timeout() -> None:
    """Reject timeouts below one second."""
    with pytest.raises(ValueError, match="at least 1"):
        run_task(successful_handler, {}, timeout_seconds=0)