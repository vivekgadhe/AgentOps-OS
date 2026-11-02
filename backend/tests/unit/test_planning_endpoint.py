"""Unit tests for the workflow planning API endpoint."""

from collections.abc import Iterator
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from agentops.api.deps import get_current_user
from agentops.api.v1.runs import get_workflow_planner
from agentops.core.config import Settings
from agentops.main import create_app
from agentops.schemas.workflows import TaskCreate, WorkflowCreate
from agentops.services.llm import LLMConfigurationError, LLMProviderError
from agentops.services.planner import PlanningOutputError, PlanningValidationError

STRONG_SECRET = "unit-test-jwt-secret-" + ("x" * 32)


class StubPlanner:
    """Return a prepared plan or raise a prepared error."""

    def __init__(
        self,
        result: WorkflowCreate | None = None,
        error: Exception | None = None,
    ) -> None:
        self.result = result
        self.error = error
        self.calls: list[tuple[str, str]] = []

    def plan(self, goal: str, *, actor_role: str) -> WorkflowCreate:
        """Record the call and return the configured result."""
        self.calls.append((goal, actor_role))

        if self.error is not None:
            raise self.error

        if self.result is None:
            raise AssertionError("StubPlanner requires a result or an error.")

        return self.result


@pytest.fixture
def planning_app() -> FastAPI:
    """Create an app with authentication overridden and no database access."""
    settings = Settings(
        _env_file=None,
        app_env="test",
        jwt_secret=STRONG_SECRET,
    )
    app = create_app(settings)

    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(
        id=uuid4(),
        role="operator",
    )

    return app


@pytest.fixture
def planning_client(planning_app: FastAPI) -> Iterator[TestClient]:
    """Create a test client for the isolated planning API."""
    with TestClient(planning_app) as client:
        yield client


def make_result() -> WorkflowCreate:
    """Build a valid proposed workflow."""
    return WorkflowCreate(
        goal="Process text",
        tasks=[
            TaskCreate(
                key="process",
                name="Process text",
                tool_name="summarize_input",
                input_data={"text": "Hello AgentOps"},
            )
        ],
    )


def test_plan_endpoint_returns_validated_plan(
    planning_app: FastAPI,
    planning_client: TestClient,
) -> None:
    """Return a plan without persisting or executing it."""
    planner = StubPlanner(result=make_result())
    planning_app.dependency_overrides[get_workflow_planner] = lambda: planner

    response = planning_client.post(
        "/api/v1/runs/plan",
        json={"goal": "  Process text  "},
    )

    assert response.status_code == 200
    assert response.json()["goal"] == "Process text"
    assert response.json()["tasks"][0]["tool_name"] == "summarize_input"
    assert response.json()["tasks"][0]["input_data"] == {"text": "Hello AgentOps"}
    assert planner.calls == [("Process text", "operator")]


def test_plan_endpoint_rejects_blank_goal(
    planning_app: FastAPI,
    planning_client: TestClient,
) -> None:
    """Reject a blank goal at request validation."""
    planning_app.dependency_overrides[get_workflow_planner] = lambda: StubPlanner(
        error=AssertionError("Planner must not run for invalid input.")
    )

    response = planning_client.post(
        "/api/v1/runs/plan",
        json={"goal": "   "},
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    ("error_type", "expected_status", "expected_detail"),
    [
        (
            LLMConfigurationError,
            503,
            "LLM service is not configured.",
        ),
        (
            LLMProviderError,
            502,
            "The LLM provider request failed.",
        ),
        (
            PlanningOutputError,
            502,
            "The LLM returned an invalid workflow plan.",
        ),
        (
            PlanningValidationError,
            502,
            "The generated workflow plan failed validation.",
        ),
    ],
)
def test_plan_endpoint_maps_planning_errors(
    planning_app: FastAPI,
    planning_client: TestClient,
    error_type: type[Exception],
    expected_status: int,
    expected_detail: str,
) -> None:
    """Translate planner and provider errors into safe HTTP responses."""
    planner = StubPlanner(error=error_type("internal test detail"))
    planning_app.dependency_overrides[get_workflow_planner] = lambda: planner

    response = planning_client.post(
        "/api/v1/runs/plan",
        json={"goal": "Process text"},
    )

    assert response.status_code == expected_status
    assert response.json()["detail"] == expected_detail
    assert "internal test detail" not in response.text
