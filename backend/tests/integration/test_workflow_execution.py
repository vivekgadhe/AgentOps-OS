"""Integration tests for authenticated workflow and tool execution."""

from collections.abc import Iterator
from datetime import timedelta
from typing import Any
from unittest.mock import Mock
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from agentops.api.v1.runs import get_workflow_planner
from agentops.core.security import create_access_token, hash_password
from agentops.db.models.user import User
from agentops.db.models.workflow import ExecutionEvent
from agentops.db.session import create_db_engine
from agentops.main import create_app
from agentops.schemas.workflows import TaskCreate, WorkflowCreate

pytestmark = pytest.mark.integration

TEST_PASSWORD = "Integration-Test-Password-123!"


@pytest.fixture
def workflow_client(integration_settings) -> Iterator[TestClient]:
    """Create a client connected to the isolated integration database."""
    with TestClient(create_app(integration_settings)) as client:
        yield client


@pytest.fixture
def workflow_users(integration_settings) -> list[tuple[UUID, str]]:
    """Create deterministic viewer and operator accounts."""
    engine = create_db_engine(integration_settings)
    users: list[tuple[UUID, str]] = []

    accounts = (
        ("workflow-owner@example.test", "viewer"),
        ("workflow-other@example.test", "viewer"),
        ("workflow-operator@example.test", "operator"),
    )

    try:
        with Session(engine) as session:
            for email, role in accounts:
                user = session.scalar(select(User).where(User.email == email))

                if user is None:
                    user = User(
                        email=email,
                        password_hash=hash_password(TEST_PASSWORD),
                        role=role,
                        is_active=True,
                    )
                    session.add(user)
                    session.flush()
                else:
                    # Keep these dedicated test accounts consistent across
                    # repeated integration-test runs.
                    user.role = role
                    user.is_active = True

                users.append((user.id, user.email))

            session.commit()
    finally:
        engine.dispose()

    return users


def auth_headers(
    integration_settings,
    user_id: UUID,
    role: str = "viewer",
) -> dict[str, str]:
    """Create an access token for an existing test user."""
    token = create_access_token(
        subject=str(user_id),
        secret=integration_settings.jwt_secret.get_secret_value(),
        expires_in=timedelta(minutes=15),
        role=role,
    )
    return {"Authorization": f"Bearer {token}"}


def create_workflow(
    client: TestClient,
    headers: dict[str, str],
):
    """Create a workflow containing one summarization task."""
    return client.post(
        "/api/v1/runs",
        headers=headers,
        json={
            "goal": "Summarize a greeting",
            "tasks": [
                {
                    "key": "summarize",
                    "name": "Summarize greeting",
                    "tool_name": "summarize_input",
                    "input_data": {"text": "  Hello AgentOps  "},
                }
            ],
        },
    )


def test_workflow_requires_authentication(
    workflow_client: TestClient,
) -> None:
    """Reject workflow creation without an access token."""
    response = workflow_client.post(
        "/api/v1/runs",
        json={
            "goal": "Summarize text",
            "tasks": [
                {
                    "key": "summarize",
                    "name": "Summarize text",
                    "tool_name": "summarize_input",
                    "input_data": {"text": "Hello AgentOps"},
                }
            ],
        },
    )

    assert response.status_code == 401


def test_create_and_retrieve_workflow(
    workflow_client: TestClient,
    integration_settings,
    workflow_users: list[tuple[UUID, str]],
) -> None:
    """Allow the owner to create and retrieve a workflow."""
    owner_id, _ = workflow_users[0]
    headers = auth_headers(integration_settings, owner_id)

    response = create_workflow(workflow_client, headers)

    assert response.status_code == 201, response.text
    created = response.json()

    assert created["goal"] == "Summarize a greeting"
    assert created["status"] == "pending"
    assert len(created["tasks"]) == 1
    assert created["tasks"][0]["key"] == "summarize"
    assert created["tasks"][0]["depends_on"] == []

    retrieve_response = workflow_client.get(
        f"/api/v1/runs/{created['id']}",
        headers=headers,
    )

    assert retrieve_response.status_code == 200
    assert retrieve_response.json()["id"] == created["id"]


def test_user_cannot_access_another_users_workflow(
    workflow_client: TestClient,
    integration_settings,
    workflow_users: list[tuple[UUID, str]],
) -> None:
    """Hide a workflow from users other than its owner."""
    owner_id, _ = workflow_users[0]
    other_id, _ = workflow_users[1]

    create_response = create_workflow(
        workflow_client,
        auth_headers(integration_settings, owner_id),
    )

    assert create_response.status_code == 201, create_response.text
    run_id = create_response.json()["id"]

    response = workflow_client.get(
        f"/api/v1/runs/{run_id}",
        headers=auth_headers(integration_settings, other_id),
    )

    assert response.status_code == 404


def test_execute_workflow_persists_task_output(
    workflow_client: TestClient,
    integration_settings,
    workflow_users: list[tuple[UUID, str]],
) -> None:
    """Execute a registered task and verify its persisted result."""
    owner_id, _ = workflow_users[0]
    headers = auth_headers(integration_settings, owner_id)

    create_response = create_workflow(workflow_client, headers)

    assert create_response.status_code == 201, create_response.text
    run_id = create_response.json()["id"]

    execute_response = workflow_client.post(
        f"/api/v1/runs/{run_id}/execute",
        headers=headers,
    )

    assert execute_response.status_code == 200, execute_response.text

    result = execute_response.json()
    assert result["status"] == "succeeded"
    assert result["tasks"][0]["status"] == "succeeded"
    assert result["tasks"][0]["output_data"] == {
        "summary": "Hello AgentOps",
        "character_count": 14,
    }

    retrieve_response = workflow_client.get(
        f"/api/v1/runs/{run_id}",
        headers=headers,
    )

    assert retrieve_response.status_code == 200

    saved = retrieve_response.json()
    assert saved["status"] == "succeeded"
    assert saved["tasks"][0]["output_data"] == {
        "summary": "Hello AgentOps",
        "character_count": 14,
    }


def test_workflow_dependencies_are_persisted_and_retrieved(
    workflow_client: TestClient,
    integration_settings,
    workflow_users: list[tuple[UUID, str]],
) -> None:
    """Persist task dependencies and return them through the API."""
    owner_id, _ = workflow_users[0]
    headers = auth_headers(integration_settings, owner_id)

    # Deliberately provide tasks in reverse dependency order.
    response = workflow_client.post(
        "/api/v1/runs",
        headers=headers,
        json={
            "goal": "Research, write, and publish a report",
            "tasks": [
                {
                    "key": "publish",
                    "name": "Publish report",
                    "depends_on": ["write"],
                },
                {
                    "key": "write",
                    "name": "Write report",
                    "depends_on": ["research"],
                },
                {
                    "key": "research",
                    "name": "Research topic",
                    "depends_on": [],
                },
            ],
        },
    )

    assert response.status_code == 201, response.text

    created = response.json()
    run_id = created["id"]

    tasks_by_key = {task["key"]: task for task in created["tasks"]}

    assert tasks_by_key["publish"]["depends_on"] == ["write"]
    assert tasks_by_key["write"]["depends_on"] == ["research"]
    assert tasks_by_key["research"]["depends_on"] == []

    retrieve_response = workflow_client.get(
        f"/api/v1/runs/{run_id}",
        headers=headers,
    )

    assert retrieve_response.status_code == 200

    retrieved_tasks = {task["key"]: task for task in retrieve_response.json()["tasks"]}

    assert retrieved_tasks["publish"]["depends_on"] == ["write"]
    assert retrieved_tasks["write"]["depends_on"] == ["research"]
    assert retrieved_tasks["research"]["depends_on"] == []


@pytest.mark.parametrize(
    ("tool_name", "input_data", "expected_output"),
    [
        (
            "text_statistics",
            {"text": "AgentOps tools\nAI agents"},
            {
                "word_count": 4,
                "character_count": 24,
                "line_count": 2,
            },
        ),
        (
            "normalize_whitespace",
            {"text": "  AgentOps \n\t tools   "},
            {"normalized_text": "AgentOps tools"},
        ),
        (
            "find_matching_lines",
            {
                "text": "Alpha systems\nagent tools\nAI AGENT platform\nNo match",
                "query": "agent",
            },
            {
                "matches": [
                    "agent tools",
                    "AI AGENT platform",
                ],
                "match_count": 2,
            },
        ),
    ],
    ids=[
        "text-statistics",
        "normalize-whitespace",
        "find-matching-lines",
    ],
)
def test_builtin_tool_executes_through_api(
    workflow_client: TestClient,
    integration_settings,
    workflow_users: list[tuple[UUID, str]],
    tool_name: str,
    input_data: dict[str, Any],
    expected_output: dict[str, Any],
) -> None:
    """Execute each additional built-in tool through the workflow API."""
    operator_id, _ = workflow_users[2]
    headers = auth_headers(
        integration_settings,
        operator_id,
        role="operator",
    )

    create_response = workflow_client.post(
        "/api/v1/runs",
        headers=headers,
        json={
            "goal": f"Run the {tool_name} tool",
            "tasks": [
                {
                    "key": "task",
                    "name": f"Run {tool_name}",
                    "tool_name": tool_name,
                    "input_data": input_data,
                }
            ],
        },
    )

    assert create_response.status_code == 201, create_response.text
    run_id = create_response.json()["id"]

    execute_response = workflow_client.post(
        f"/api/v1/runs/{run_id}/execute",
        headers=headers,
    )

    assert execute_response.status_code == 200, execute_response.text

    result = execute_response.json()

    assert result["status"] == "succeeded", result
    assert result["tasks"][0]["status"] == "succeeded"
    assert result["tasks"][0]["output_data"] == expected_output


def test_viewer_cannot_execute_restricted_tool(
    workflow_client: TestClient,
    integration_settings,
    workflow_users: list[tuple[UUID, str]],
) -> None:
    """Reject viewer access to tools restricted to operators and admins."""
    viewer_id, _ = workflow_users[0]
    headers = auth_headers(integration_settings, viewer_id)

    create_response = workflow_client.post(
        "/api/v1/runs",
        headers=headers,
        json={
            "goal": "Attempt restricted tool execution",
            "tasks": [
                {
                    "key": "statistics",
                    "name": "Calculate statistics",
                    "tool_name": "text_statistics",
                    "input_data": {"text": "Sensitive operation"},
                }
            ],
        },
    )

    assert create_response.status_code == 201, create_response.text
    run_id = create_response.json()["id"]

    execute_response = workflow_client.post(
        f"/api/v1/runs/{run_id}/execute",
        headers=headers,
    )

    assert execute_response.status_code == 200, execute_response.text

    result = execute_response.json()
    assert result["status"] == "failed"

    task = result["tasks"][0]
    assert task["status"] == "failed"
    assert task["error"]["type"] == "ToolAccessDeniedError"

    engine = create_db_engine(integration_settings)

    try:
        with Session(engine) as session:
            event = session.scalar(
                select(ExecutionEvent).where(
                    ExecutionEvent.workflow_run_id == UUID(run_id),
                    ExecutionEvent.event_type == "tool.access_denied",
                )
            )

            assert event is not None
            assert event.level == "warning"
            assert event.data["actor_role"] == "viewer"
            assert event.data["tool_name"] == "text_statistics"
    finally:
        engine.dispose()


def test_planned_workflow_can_be_saved_without_execution(
    workflow_client: TestClient,
    integration_settings,
    workflow_users: list[tuple[UUID, str]],
) -> None:
    """Allow a reviewed AI plan to be saved while remaining pending."""
    owner_id, _ = workflow_users[0]
    headers = auth_headers(integration_settings, owner_id)

    proposed_plan = WorkflowCreate(
        goal="Summarize a greeting",
        tasks=[
            TaskCreate(
                key="summarize",
                name="Summarize greeting",
                tool_name="summarize_input",
                input_data={"text": "Hello from a proposed plan"},
                max_attempts=3,
                timeout_seconds=30,
                depends_on=[],
            )
        ],
    )

    planner = Mock()
    planner.plan.return_value = proposed_plan

    app = workflow_client.app
    app.dependency_overrides[get_workflow_planner] = lambda: planner

    try:
        plan_response = workflow_client.post(
            "/api/v1/runs/plan",
            headers=headers,
            json={"goal": "Summarize a greeting"},
        )
    finally:
        app.dependency_overrides.pop(get_workflow_planner, None)

    assert plan_response.status_code == 200, plan_response.text

    plan_data = plan_response.json()

    # A proposed plan is not yet a persisted workflow.
    assert plan_data["goal"] == "Summarize a greeting"
    assert "id" not in plan_data
    assert "status" not in plan_data

    planner.plan.assert_called_once_with(
        "Summarize a greeting",
        actor_role="viewer",
    )

    # Submitting the reviewed plan to the existing create endpoint is the
    # explicit approval and persistence step.
    create_response = workflow_client.post(
        "/api/v1/runs",
        headers=headers,
        json=plan_data,
    )

    assert create_response.status_code == 201, create_response.text

    saved = create_response.json()
    run_id = saved["id"]

    assert saved["goal"] == "Summarize a greeting"
    assert saved["status"] == "pending"
    assert saved["tasks"][0]["status"] == "pending"
    assert saved["tasks"][0]["output_data"] is None
    assert saved["tasks"][0]["attempt_count"] == 0
    assert saved["tasks"][0]["finished_at"] is None

    # Confirm the saved workflow remains pending when retrieved.
    retrieve_response = workflow_client.get(
        f"/api/v1/runs/{run_id}",
        headers=headers,
    )

    assert retrieve_response.status_code == 200

    retrieved = retrieve_response.json()
    assert retrieved["id"] == run_id
    assert retrieved["status"] == "pending"
    assert retrieved["tasks"][0]["status"] == "pending"
    assert retrieved["tasks"][0]["output_data"] is None
    assert retrieved["tasks"][0]["attempt_count"] == 0
