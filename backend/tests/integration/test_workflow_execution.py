"""Integration tests for authenticated workflow execution."""

from collections.abc import Iterator
from datetime import timedelta
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from agentops.core.security import create_access_token, hash_password
from agentops.db.models.user import User
from agentops.db.session import create_db_engine
from agentops.main import create_app

pytestmark = pytest.mark.integration

TEST_PASSWORD = "Integration-Test-Password-123!"

@pytest.fixture
def workflow_client(integration_settings) -> Iterator[TestClient]:
    """Create a client connected to the isolated integration database."""
    with TestClient(create_app(integration_settings)) as client:
        yield client

@pytest.fixture
def workflow_users(integration_settings) -> list[tuple[UUID, str]]:
    """Create two active users for workflow ownership tests."""
    engine = create_db_engine(integration_settings)
    users: list[tuple[UUID, str]] = []


    try:
        with Session(engine) as session:
            for email in (
                "workflow-owner@example.test",
                "workflow-other@example.test",
            ):
                user = session.scalar(
                    select(User).where(User.email == email)
                )

                if user is None:
                    user = User(
                        email=email,
                        password_hash=hash_password(TEST_PASSWORD),
                        role="viewer",
                        is_active=True,
                    )
                    session.add(user)
                    session.flush()

                users.append((user.id, user.email))

            session.commit()
    finally:
        engine.dispose()

    return users


def auth_headers(integration_settings, user_id: UUID) -> dict[str, str]:
    """Create an access token for an existing user."""
    token = create_access_token(
        subject=str(user_id),
        secret=integration_settings.jwt_secret.get_secret_value(),
        expires_in=timedelta(minutes=15),
        role="viewer",
    )
    return {"Authorization": f"Bearer {token}"}

def create_workflow(client: TestClient, headers: dict[str, str]):
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

