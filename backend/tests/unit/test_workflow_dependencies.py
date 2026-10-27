"""Tests for workflow dependency validation and execution."""

from types import SimpleNamespace
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from agentops.db.models import TaskStatus, WorkflowStatus
from agentops.services.execution import (
    ExecutionError,
    ExecutionService,
    _topological_order,
)


class FakeRows:
    """Provide a minimal scalar-result interface for unit tests."""

    def __init__(self, values: list[object]) -> None:
        self.values = values

    def all(self) -> list[object]:
        return self.values


def test_topological_order_respects_dependencies() -> None:
    """Prerequisites must come before their dependent tasks."""
    ordered = _topological_order(
        ["publish", "write", "research"],
        {
            "publish": ["write"],
            "write": ["research"],
            "research": [],
        },
    )

    assert ordered == ["research", "write", "publish"]


def test_topological_order_rejects_cycles() -> None:
    """Circular dependencies must not produce an execution order."""
    with pytest.raises(ValueError, match="dependency cycle"):
        _topological_order(
            ["research", "write"],
            {
                "research": ["write"],
                "write": ["research"],
            },
        )


def test_create_workflow_rejects_unknown_dependencies() -> None:
    """Unknown dependency keys are rejected before database writes."""
    service = ExecutionService(MagicMock())
    user = SimpleNamespace(id=uuid4())

    with pytest.raises(ValueError, match="unknown task"):
        service.create_workflow(
            user,  # type: ignore[arg-type]
            "Test workflow",
            [
                {
                    "key": "write",
                    "name": "Write report",
                    "depends_on": ["missing"],
                }
            ],
        )


def test_create_workflow_rejects_self_dependency() -> None:
    """A task cannot depend on itself."""
    service = ExecutionService(MagicMock())
    user = SimpleNamespace(id=uuid4())

    with pytest.raises(ValueError, match="cannot depend on itself"):
        service.create_workflow(
            user,  # type: ignore[arg-type]
            "Test workflow",
            [
                {
                    "key": "write",
                    "name": "Write report",
                    "depends_on": ["write"],
                }
            ],
        )


def test_create_workflow_rejects_dependency_cycles() -> None:
    """Circular dependency graphs are rejected during creation."""
    service = ExecutionService(MagicMock())
    user = SimpleNamespace(id=uuid4())

    with pytest.raises(ValueError, match="dependency cycle"):
        service.create_workflow(
            user,  # type: ignore[arg-type]
            "Test workflow",
            [
                {
                    "key": "research",
                    "name": "Research",
                    "depends_on": ["write"],
                },
                {
                    "key": "write",
                    "name": "Write",
                    "depends_on": ["research"],
                },
            ],
        )


def _make_execution_fixture() -> tuple[
    ExecutionService,
    SimpleNamespace,
    list[SimpleNamespace],
]:
    """Build a small in-memory workflow with reverse-ordered tasks."""
    session = MagicMock()

    workflow_id = uuid4()
    workflow = SimpleNamespace(
        id=workflow_id,
        status=WorkflowStatus.PENDING.value,
        started_at=None,
        finished_at=None,
        error=None,
    )

    research = SimpleNamespace(
        id=uuid4(),
        key="research",
        status=TaskStatus.PENDING.value,
        error=None,
        started_at=None,
        finished_at=None,
    )
    write = SimpleNamespace(
        id=uuid4(),
        key="write",
        status=TaskStatus.PENDING.value,
        error=None,
        started_at=None,
        finished_at=None,
    )
    publish = SimpleNamespace(
        id=uuid4(),
        key="publish",
        status=TaskStatus.PENDING.value,
        error=None,
        started_at=None,
        finished_at=None,
    )

    tasks = [publish, write, research]

    edges = [
        SimpleNamespace(
            workflow_run_id=workflow_id,
            task_id=write.id,
            depends_on_task_id=research.id,
        ),
        SimpleNamespace(
            workflow_run_id=workflow_id,
            task_id=publish.id,
            depends_on_task_id=write.id,
        ),
    ]

    session.scalar.return_value = workflow
    session.scalars.side_effect = [
        FakeRows(tasks),
        FakeRows(edges),
    ]

    return ExecutionService(session), workflow, tasks


def test_execution_uses_dependency_order(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Tasks execute prerequisite-first even when created in reverse order."""
    service, workflow, tasks = _make_execution_fixture()
    execution_order: list[str] = []

    def mark_succeeded(
        _workflow: object,
        task: SimpleNamespace,
    ) -> None:
        execution_order.append(task.key)
        task.status = TaskStatus.SUCCEEDED.value

    monkeypatch.setattr(service, "_execute_task", mark_succeeded)

    service.execute_workflow(workflow.id)

    assert execution_order == ["research", "write", "publish"]
    assert workflow.status == WorkflowStatus.SUCCEEDED.value
    assert all(
        task.status == TaskStatus.SUCCEEDED.value for task in tasks
    )


def test_execution_skips_dependents_after_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Dependent tasks are skipped after a prerequisite fails."""
    service, workflow, tasks = _make_execution_fixture()
    execution_order: list[str] = []

    def fail_write(
        _workflow: object,
        task: SimpleNamespace,
    ) -> None:
        execution_order.append(task.key)

        if task.key == "write":
            task.status = TaskStatus.FAILED.value
            raise ExecutionError("Write task failed")

        task.status = TaskStatus.SUCCEEDED.value

    monkeypatch.setattr(service, "_execute_task", fail_write)

    service.execute_workflow(workflow.id)

    tasks_by_key = {task.key: task for task in tasks}

    assert execution_order == ["research", "write"]
    assert tasks_by_key["research"].status == TaskStatus.SUCCEEDED.value
    assert tasks_by_key["write"].status == TaskStatus.FAILED.value
    assert tasks_by_key["publish"].status == TaskStatus.SKIPPED.value
    assert workflow.status == WorkflowStatus.FAILED.value
    assert tasks_by_key["publish"].error["type"] == "DependencyFailed"