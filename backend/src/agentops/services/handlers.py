
"""Built-in, explicitly registered task handlers."""

from typing import Any

from agentops.services.execution import ExecutionService


def summarize_input(data: dict[str, Any]) -> dict[str, Any]:
    """Return a deterministic summary of supplied text."""
    text = data.get("text", "")

    if not isinstance(text, str):
        raise ValueError("'text' must be a string")

    return {
        "summary": text.strip(),
        "character_count": len(text.strip()),
    }


def register_builtin_handlers(service: ExecutionService) -> None:
    """Register the supported built-in handlers."""
    service.register_handler("summarize_input", summarize_input)