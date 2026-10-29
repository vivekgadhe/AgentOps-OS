"""Unit tests for persistent multi-agent state."""

from types import SimpleNamespace
from unittest.mock import MagicMock, Mock
from uuid import uuid4

import pytest

from agentops.db.models.workflow import ExecutionEvent, WorkflowRun
from agentops.schemas.orchestration import OrchestrationTaskResult
from agentops.services.agent_state import (
    AgentStateStore,
    AgentStateStoreError,
)


def make_result(
    status: str = "succeeded",
    *,
    key: str = "analysis",
) -> OrchestrationTaskResult:
    """Create a sample orchestration task result."""
    if status == "succeeded":
        return OrchestrationTaskResult(
            key=key,
            agent_name="analysis_agent",
            status="succeeded",
            result={
                "agent_name": "analysis_agent",
                "status": "succeeded",
                "summary": "Analysis finished.",
                "output": {"finding": "delivery delay"},
            },
        )

    return OrchestrationTaskResult(
        key=key,
        agent_name="analysis_agent",
        status="failed",
        error_type="TestError",
        error_message="Analysis failed.",
    )


def make_session_factory(session: Mock) -> Mock:
    """Return a mock factory supporting SQLAlchemy's session context manager."""
    factory = Mock()
    context = MagicMock()
    context.__enter__.return_value = session
    context.__exit__.return_value = False
    factory.return_value = context
    return factory


def test_save_result_persists_execution_event() -> None:
    workflow_id = uuid4()
    session = Mock()
    session.get.return_value = object()

    store = AgentStateStore(
        make_session_factory(session),
        workflow_id,
    )

    result = make_result()
    store.save_task_result(result)

    session.get.assert_called_once_with(WorkflowRun, workflow_id)
    session.add.assert_called_once()

    event = session.add.call_args.args[0]

    assert isinstance(event, ExecutionEvent)
    assert event.workflow_run_id == workflow_id
    assert event.event_type == "agent.task.succeeded"
    assert event.data["task_key"] == "analysis"
    assert event.data["task_result"]["status"] == "succeeded"
    session.commit.assert_called_once()


def test_save_result_rejects_unknown_workflow() -> None:
    workflow_id = uuid4()
    session = Mock()
    session.get.return_value = None

    store = AgentStateStore(
        make_session_factory(session),
        workflow_id,
    )

    with pytest.raises(AgentStateStoreError, match="unknown workflow"):
        store.save_task_result(make_result())

    session.add.assert_not_called()
    session.commit.assert_not_called()


def test_load_results_restores_latest_result_for_each_task() -> None:
    workflow_id = uuid4()
    session = Mock()
    session.get.return_value = object()

    earlier = make_result("failed")
    later = make_result("succeeded")

    events = [
        SimpleNamespace(data={"task_result": earlier.model_dump(mode="json")}),
        SimpleNamespace(data={"task_result": later.model_dump(mode="json")}),
    ]
    session.scalars.return_value.all.return_value = events

    store = AgentStateStore(
        make_session_factory(session),
        workflow_id,
    )

    results = store.load_task_results()

    assert list(results) == ["analysis"]
    assert results["analysis"].status == "succeeded"


def test_load_results_rejects_invalid_stored_state() -> None:
    session = Mock()
    session.get.return_value = object()
    session.scalars.return_value.all.return_value = [
        SimpleNamespace(data={"task_result": {"invalid": "stored result"}})
    ]

    store = AgentStateStore(
        make_session_factory(session),
        uuid4(),
    )

    with pytest.raises(AgentStateStoreError, match="does not match"):
        store.load_task_results()


def test_load_results_rejects_unknown_workflow() -> None:
    session = Mock()
    session.get.return_value = None

    store = AgentStateStore(
        make_session_factory(session),
        uuid4(),
    )

    with pytest.raises(AgentStateStoreError, match="unknown workflow"):
        store.load_task_results()
