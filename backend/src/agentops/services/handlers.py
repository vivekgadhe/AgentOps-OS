"""Built-in task handlers and their declared contracts."""

from typing import Any

from pydantic import BaseModel, ConfigDict

from agentops.services.execution import ExecutionService
from agentops.services.tool_registry import ToolDefinition


class SummarizeInput(BaseModel):
    """Input contract for the text summarization tool."""

    model_config = ConfigDict(extra="forbid")

    text: str = ""


class SummarizeOutput(BaseModel):
    """Output contract for the text summarization tool."""

    model_config = ConfigDict(extra="forbid")

    summary: str
    character_count: int


def summarize_input(data: dict[str, Any]) -> dict[str, Any]:
    """Return normalized text and its character count."""
    text = data.get("text", "")

    if not isinstance(text, str):
        raise ValueError("'text' must be a string")

    normalized_text = text.strip()

    return {
        "summary": normalized_text,
        "character_count": len(normalized_text),
    }


def register_builtin_handlers(service: ExecutionService) -> None:
    """Register built-in tools with explicit input and output contracts."""
    service.register_tool(
        ToolDefinition(
            name="summarize_input",
            description="Normalize supplied text and count its characters.",
            input_model=SummarizeInput,
            output_model=SummarizeOutput,
            handler=summarize_input,
        )
    )