"""Tests for the tool registry and tool contracts."""

from typing import Any

import pytest
from pydantic import BaseModel, ConfigDict

from agentops.services.tool_registry import (
    ToolDefinition,
    ToolInputValidationError,
    ToolNotFoundError,
    ToolOutputValidationError,
    ToolRegistry,
    ToolRegistryError,
)


class GreetingInput(BaseModel):
    """Input contract for a greeting tool."""

    model_config = ConfigDict(extra="forbid")

    name: str


class GreetingOutput(BaseModel):
    """Output contract for a greeting tool."""

    model_config = ConfigDict(extra="forbid")

    greeting: str


def greet(data: dict[str, Any]) -> dict[str, Any]:
    """Create a greeting."""
    return {"greeting": f"Hello, {data['name']}!"}


@pytest.fixture
def registry() -> ToolRegistry:
    """Provide a registry containing one tool."""
    result = ToolRegistry()
    result.register(
        ToolDefinition(
            name="greet",
            description="Generate a greeting.",
            input_model=GreetingInput,
            output_model=GreetingOutput,
            handler=greet,
        )
    )
    return result


def test_register_and_retrieve_tool(registry: ToolRegistry) -> None:
    """Retrieve a registered tool by name."""
    assert registry.get("greet").name == "greet"


def test_duplicate_registration_is_rejected(
    registry: ToolRegistry,
) -> None:
    """Prevent accidental tool-name collisions."""
    with pytest.raises(ToolRegistryError, match="already registered"):
        registry.register(
            ToolDefinition(
                name="greet",
                description="Another greeting implementation.",
                input_model=GreetingInput,
                output_model=GreetingOutput,
                handler=greet,
            )
        )


def test_unknown_tool_is_rejected(registry: ToolRegistry) -> None:
    """Fail clearly when a tool is unavailable."""
    with pytest.raises(ToolNotFoundError, match="not registered"):
        registry.get("missing_tool")


def test_input_contract_is_validated(
    registry: ToolRegistry,
) -> None:
    """Reject missing required input fields."""
    with pytest.raises(ToolInputValidationError, match="Invalid input"):
        registry.validate_input("greet", {})


def test_unknown_input_fields_are_rejected(
    registry: ToolRegistry,
) -> None:
    """Reject arguments not declared by the tool schema."""
    with pytest.raises(ToolInputValidationError, match="Invalid input"):
        registry.validate_input(
            "greet",
            {"name": "Ada", "unexpected": True},
        )


def test_valid_input_is_normalized(
    registry: ToolRegistry,
) -> None:
    """Return validated input as a dictionary."""
    assert registry.validate_input(
        "greet",
        {"name": "Ada"},
    ) == {"name": "Ada"}


def test_output_contract_is_validated(
    registry: ToolRegistry,
) -> None:
    """Reject tool results that violate the output schema."""
    with pytest.raises(ToolOutputValidationError, match="Invalid output"):
        registry.validate_output("greet", {})


def test_valid_output_is_normalized(
    registry: ToolRegistry,
) -> None:
    """Return a valid output dictionary."""
    assert registry.validate_output(
        "greet",
        {"greeting": "Hello, Ada!"},
    ) == {"greeting": "Hello, Ada!"}


def test_tool_listing_is_sorted(
    registry: ToolRegistry,
) -> None:
    """Return tools in deterministic order."""
    registry.register(
        ToolDefinition(
            name="add_numbers",
            description="Add two numbers.",
            input_model=GreetingInput,
            output_model=GreetingOutput,
            handler=greet,
        )
    )

    assert [tool.name for tool in registry.list_tools()] == [
        "add_numbers",
        "greet",
    ]


def test_authorize_allows_permitted_role(
    registry: ToolRegistry,
) -> None:
    """Allow an operator to execute a default tool."""
    assert registry.authorize("greet", "operator").name == "greet"


def test_authorize_rejects_viewer_for_restricted_tool(
    registry: ToolRegistry,
) -> None:
    """Reject a role that is not in the tool's permission set."""
    from agentops.services.tool_registry import ToolAccessDeniedError

    with pytest.raises(ToolAccessDeniedError, match="not permitted"):
        registry.authorize("greet", "viewer")
