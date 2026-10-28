"""Built-in task handlers and their declared contracts."""

from typing import Any

from pydantic import BaseModel, ConfigDict, field_validator

from agentops.services.execution import ExecutionService
from agentops.services.tool_registry import ToolDefinition, ToolRegistry


class SummarizeInput(BaseModel):
    """Input contract for the text summarization tool."""

    model_config = ConfigDict(extra="forbid")

    text: str = ""


class SummarizeOutput(BaseModel):
    """Output contract for the text summarization tool."""

    model_config = ConfigDict(extra="forbid")

    summary: str
    character_count: int


class TextStatisticsInput(BaseModel):
    """Input contract for text statistics."""

    model_config = ConfigDict(extra="forbid")

    text: str


class TextStatisticsOutput(BaseModel):
    """Output contract for text statistics."""

    model_config = ConfigDict(extra="forbid")

    word_count: int
    character_count: int
    line_count: int


class NormalizeWhitespaceInput(BaseModel):
    """Input contract for whitespace normalization."""

    model_config = ConfigDict(extra="forbid")

    text: str


class NormalizeWhitespaceOutput(BaseModel):
    """Output contract for whitespace normalization."""

    model_config = ConfigDict(extra="forbid")

    normalized_text: str


class FindMatchingLinesInput(BaseModel):
    """Input contract for searching text lines."""

    model_config = ConfigDict(extra="forbid")

    text: str
    query: str

    @field_validator("query")
    @classmethod
    def validate_query(cls, value: str) -> str:
        """Reject queries containing only whitespace."""
        normalized = value.strip()

        if not normalized:
            raise ValueError("Search query cannot be blank.")

        return normalized


class FindMatchingLinesOutput(BaseModel):
    """Output contract for matching lines."""

    model_config = ConfigDict(extra="forbid")

    matches: list[str]
    match_count: int


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


def text_statistics(data: dict[str, Any]) -> dict[str, Any]:
    """Return word, character, and line counts for supplied text."""
    text = data.get("text")

    if not isinstance(text, str):
        raise ValueError("'text' must be a string")

    return {
        "word_count": len(text.split()),
        "character_count": len(text),
        "line_count": len(text.splitlines()),
    }


def normalize_whitespace(data: dict[str, Any]) -> dict[str, Any]:
    """Collapse consecutive whitespace into single spaces."""
    text = data.get("text")

    if not isinstance(text, str):
        raise ValueError("'text' must be a string")

    return {"normalized_text": " ".join(text.split())}


def find_matching_lines(data: dict[str, Any]) -> dict[str, Any]:
    """Find lines containing a case-insensitive search query."""
    text = data.get("text")
    query = data.get("query")

    if not isinstance(text, str):
        raise ValueError("'text' must be a string")

    if not isinstance(query, str) or not query.strip():
        raise ValueError("'query' must be a non-empty string")

    normalized_query = query.strip().casefold()

    matches = [line for line in text.splitlines() if normalized_query in line.casefold()]

    return {
        "matches": matches,
        "match_count": len(matches),
    }


def _builtin_tool_definitions() -> tuple[ToolDefinition, ...]:
    """Return the canonical definitions for all built-in tools."""
    return (
        ToolDefinition(
            name="summarize_input",
            description="Normalize supplied text and count its characters.",
            input_model=SummarizeInput,
            output_model=SummarizeOutput,
            handler=summarize_input,
            allowed_roles=frozenset({"admin", "operator", "viewer"}),
        ),
        ToolDefinition(
            name="text_statistics",
            description="Calculate word, character, and line counts for text.",
            input_model=TextStatisticsInput,
            output_model=TextStatisticsOutput,
            handler=text_statistics,
        ),
        ToolDefinition(
            name="normalize_whitespace",
            description="Collapse consecutive whitespace into single spaces.",
            input_model=NormalizeWhitespaceInput,
            output_model=NormalizeWhitespaceOutput,
            handler=normalize_whitespace,
        ),
        ToolDefinition(
            name="find_matching_lines",
            description="Find text lines containing a case-insensitive query.",
            input_model=FindMatchingLinesInput,
            output_model=FindMatchingLinesOutput,
            handler=find_matching_lines,
        ),
    )


def build_builtin_tool_registry() -> ToolRegistry:
    """Build an independent registry containing all built-in tools."""
    registry = ToolRegistry()

    for definition in _builtin_tool_definitions():
        registry.register(definition)

    return registry


def register_builtin_handlers(service: ExecutionService) -> None:
    """Register the canonical built-in tools with the execution service."""
    for definition in _builtin_tool_definitions():
        service.register_tool(definition)
