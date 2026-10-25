import pytest
from fastapi.testclient import TestClient

from agentops.core.config import Settings
from agentops.main import create_app

LIVE = "/api/v1/health/live"
READY = "/api/v1/health/ready"


def test_live_returns_ok(client: TestClient) -> None:
    response = client.get(LIVE)
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_response_carries_a_generated_request_id(client: TestClient) -> None:
    response = client.get(LIVE)
    assert len(response.headers["x-request-id"]) == 32


def test_safe_incoming_request_id_is_echoed(client: TestClient) -> None:
    response = client.get(LIVE, headers={"X-Request-ID": "abc-12345678"})
    assert response.headers["x-request-id"] == "abc-12345678"


def test_unsafe_incoming_request_id_is_replaced(client: TestClient) -> None:
    response = client.get(LIVE, headers={"X-Request-ID": "not valid!! spaces"})
    assert response.headers["x-request-id"] != "not valid!! spaces"
    assert len(response.headers["x-request-id"]) == 32


def test_ready_returns_503_when_database_is_unreachable(jwt_secret_for_tests: str) -> None:
    # Port 1 refuses connections immediately: a real failure, no mocking involved.
    unreachable = Settings(
        _env_file=None,
        app_env="test",
        jwt_secret=jwt_secret_for_tests,
        database_url="postgresql+psycopg://nobody:nobody@127.0.0.1:1/none",
        db_connect_timeout_s=1,
    )
    with TestClient(create_app(unreachable)) as test_client:
        response = test_client.get(READY)
    assert response.status_code == 503
    assert response.json() == {"status": "unavailable", "db": "down"}


def test_ready_returns_ok_when_database_check_passes(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("agentops.api.v1.health.check_database", lambda engine: True)
    response = client.get(READY)
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "db": "up"}
