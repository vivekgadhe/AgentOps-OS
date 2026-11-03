"""Verify persistent-memory routes are included in the API router."""

from agentops.api.v1.memories import router as memory_router


def test_memory_routes_are_registered() -> None:
    paths = {route.path for route in memory_router.routes}
    expected = {
        "/memories",
        "/memories/search",
        "/memories/expired",
        "/memories/{memory_id}",
    }
    assert expected <= paths
