"""Tests for trusted application tool registration."""

from typing import Any

from pydantic import BaseModel

from agentops.services.handlers import build_application_tool_registry
from agentops.services.tool_registry import ToolDefinition, ToolRegistry


class _Input(BaseModel):
    value: str


class _Output(BaseModel):
    value: str


def _protected_handler(payload: dict[str, Any]) -> dict[str, Any]:
    return payload


def test_application_registrar_adds_trusted_approval_tool() -> None:
    def register_protected_tool(registry: ToolRegistry) -> None:
        registry.register(
            ToolDefinition(
                name="protected_operation",
                description="A sample protected application operation.",
                input_model=_Input,
                output_model=_Output,
                handler=_protected_handler,
                requires_approval=True,
            )
        )

    registry = build_application_tool_registry([register_protected_tool])
    tool = registry.get("protected_operation")

    assert tool.requires_approval is True
    assert "text_statistics" in {definition.name for definition in registry.list_tools()}
