"""Registration checks for Phase 8 provider and approval APIs."""

from fastapi.testclient import TestClient


def test_ai_provider_and_approval_routes_are_registered(client: TestClient) -> None:
    paths = set(client.app.openapi().get("paths", {}))
    expected = {
        "/api/v1/ai-providers",
        "/api/v1/ai-providers/{provider_name}",
        "/api/v1/ai-providers/test",
        "/api/v1/approvals",
        "/api/v1/approvals/{approval_id}",
        "/api/v1/approvals/{approval_id}/approve",
        "/api/v1/approvals/{approval_id}/reject",
        "/api/v1/approvals/{approval_id}/cancel",
    }
    assert expected <= paths
