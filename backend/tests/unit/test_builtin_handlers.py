"""Tests for the built-in task handlers and their contracts."""

from unittest.mock import MagicMock

import pytest

from agentops.services.execution import ExecutionService
from agentops.services.handlers import (
    FindMatchingLinesInput,
    find_matching_lines,
    normalize_whitespace,
    register_builtin_handlers,
    summarize_input,
    text_statistics,
)
from agentops.services.tool_registry import (
    ToolAccessDeniedError,
    ToolInputValidationError,
)


def test_text_statistics_counts_words_characters_and_lines() -> None:
    """Count the words, characters, and lines in supplied text."""
    text = "Hello agents\nAI tools"

    result = text_statistics({"text": text})

    assert result == {
        "word_count": 4,
        "character_count": len(text),
        "line_count": 2,
    }


def test_text_statistics_rejects_non_string_input() -> None:
    """Reject values that are not strings."""
    with pytest.raises(ValueError, match="'text' must be a string"):
        text_statistics({"text": ["not", "text"]})


def test_normalize_whitespace_collapses_spacing() -> None:
    """Replace repeated whitespace with single spaces."""
    result = normalize_whitespace({"text": "  AgentOps \n\t tools   "})

    assert result == {"normalized_text": "AgentOps tools"}


def test_normalize_whitespace_rejects_non_string_input() -> None:
    """Reject non-string text."""
    with pytest.raises(ValueError, match="'text' must be a string"):
        normalize_whitespace({"text": None})


def test_find_matching_lines_is_case_insensitive() -> None:
    """Return matching lines without changing their original text."""
    text = "Alpha systems\nagent tools\nAI AGENT platform\nNo match"

    result = find_matching_lines({"text": text, "query": "agent"})

    assert result == {
        "matches": [
            "agent tools",
            "AI AGENT platform",
        ],
        "match_count": 2,
    }


def test_find_matching_lines_rejects_blank_query() -> None:
    """Reject search queries containing only whitespace."""
    with pytest.raises(ValueError, match="'query' must be a non-empty string"):
        find_matching_lines({"text": "Some content", "query": "   "})


def test_find_matching_lines_input_schema_rejects_blank_query() -> None:
    """Validate a search query before the tool executes."""
    with pytest.raises(ValueError, match="Search query cannot be blank"):
        FindMatchingLinesInput(
            text="Some content",
            query="   ",
        )


def test_builtin_tools_are_registered() -> None:
    """Register all four built-in tools with the execution service."""
    service = ExecutionService(MagicMock())

    register_builtin_handlers(service)

    tools = service._tool_registry.list_tools()
    names = {tool.name for tool in tools}

    assert names == {
        "summarize_input",
        "text_statistics",
        "normalize_whitespace",
        "find_matching_lines",
    }


def test_existing_summarize_tool_keeps_viewer_permission() -> None:
    """Preserve viewer access to the existing summarization tool."""
    service = ExecutionService(MagicMock())

    register_builtin_handlers(service)

    tool = service._tool_registry.authorize(
        "summarize_input",
        "viewer",
    )

    assert tool.name == "summarize_input"


def test_new_tools_restrict_viewer_access() -> None:
    """New built-in tools use the default admin/operator permissions."""
    service = ExecutionService(MagicMock())

    register_builtin_handlers(service)

    with pytest.raises(ToolAccessDeniedError, match="not permitted"):
        service._tool_registry.authorize(
            "text_statistics",
            "viewer",
        )


def test_text_statistics_rejects_unexpected_input_fields() -> None:
    """Reject undeclared fields through the tool registry."""
    service = ExecutionService(MagicMock())

    register_builtin_handlers(service)

    with pytest.raises(ToolInputValidationError, match="Invalid input"):
        service._tool_registry.validate_input(
            "text_statistics",
            {
                "text": "Hello",
                "unexpected": True,
            },
        )


def test_summarize_input_preserves_existing_behavior() -> None:
    """Keep the original summarization result unchanged."""
    result = summarize_input({"text": "  Hello AgentOps  "})

    assert result == {
        "summary": "Hello AgentOps",
        "character_count": 14,
    }
