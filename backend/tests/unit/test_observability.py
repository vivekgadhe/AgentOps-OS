"""Unit tests for observability reporting window validation."""

from datetime import UTC, datetime, timedelta

import pytest
from fastapi import FastAPI, HTTPException

from agentops.api.v1.observability import _rate, _safe_event_attributes, _window
from agentops.api.v1.router import api_router


def test_window_defaults_to_last_thirty_days() -> None:
    start, end = _window(None, None)
    assert end.tzinfo is not None
    assert start.tzinfo is not None
    assert timedelta(days=30) - timedelta(seconds=1) < end - start
    assert end - start < timedelta(days=30) + timedelta(seconds=1)


def test_window_rejects_naive_datetime() -> None:
    with pytest.raises(HTTPException, match="timezone"):
        _window(datetime(2026, 1, 1), datetime(2026, 1, 2))


def test_window_rejects_reversed_range() -> None:
    with pytest.raises(HTTPException, match="earlier"):
        _window(
            datetime(2026, 1, 2, tzinfo=UTC),
            datetime(2026, 1, 1, tzinfo=UTC),
        )


def test_rate_is_safe_for_empty_groups() -> None:
    assert _rate(0, 0) == 0.0
    assert _rate(1, 4) == 0.25


def test_observability_endpoints_are_registered() -> None:
    app = FastAPI()
    app.include_router(api_router)
    paths = set(app.openapi()["paths"])
    assert "/observability/overview" in paths
    assert "/observability/providers" in paths
    assert "/observability/agents" in paths
    assert "/observability/workflows" in paths
    assert "/observability/events" in paths
    assert "/observability/telemetry/purge" in paths


def test_event_attributes_allow_only_safe_metadata() -> None:
    assert _safe_event_attributes(
        {
            "attempt_number": 2,
            "used_fallback": True,
            "output_schema": "AgentOutput",
            "prompt": "must-not-be-exposed",
        }
    ) == {
        "attempt_number": 2,
        "used_fallback": True,
        "output_schema": "AgentOutput",
    }
