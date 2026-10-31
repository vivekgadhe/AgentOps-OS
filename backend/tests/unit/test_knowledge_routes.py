"""Verify that knowledge API endpoints are registered."""

from fastapi.testclient import TestClient


def test_knowledge_routes_are_registered(client: TestClient) -> None:
    """Ensure all knowledge endpoints appear in the generated OpenAPI schema."""

    schema = client.app.openapi()
    registered_paths = set(schema.get("paths", {}))

    expected_paths = {
        "/api/v1/knowledge/documents",
        "/api/v1/knowledge/documents/{document_id}",
        "/api/v1/knowledge/search",
        "/api/v1/knowledge/query",
        "/api/v1/knowledge/report",
    }

    missing_paths = expected_paths - registered_paths

    assert not missing_paths, (
        f"Knowledge routes are missing: {sorted(missing_paths)}"
    )