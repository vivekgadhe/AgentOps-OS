"""Importable handlers for task runner subprocess tests."""

import time
from typing import Any


def successful_handler(data: dict[str, Any]) -> dict[str, Any]:
    """Return a successful result."""
    return {"result": data.get("value", "ok")}


def slow_handler(data: dict[str, Any]) -> dict[str, Any]:
    """Simulate a task that exceeds its timeout."""
    time.sleep(3)
    return {"result": "finished"}


def invalid_handler(data: dict[str, Any]) -> Any:
    """Return an invalid result to exercise validation."""
    return "invalid"


def protected_action_handler(data: dict[str, Any]) -> dict[str, Any]:
    """Execute the protected-action handler in a spawn-importable module."""
    return {"result": str(data["value"]).upper()}
