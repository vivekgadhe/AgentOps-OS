"""Registry and contracts for approved task tools."""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, ValidationError

ToolHandler = Callable[[dict[str, Any]], dict[str, Any]]


class ToolRegistryError(ValueError):
    """Base error for tool registration and validation."""


class ToolNotFoundError(ToolRegistryError):
    """Raised when a requested tool is not registered."""


class ToolInputValidationError(ToolRegistryError):
    """Raised when tool input violates its declared schema."""


class ToolOutputValidationError(ToolRegistryError):
    """Raised when tool output violates its declared schema."""


@dataclass(frozen=True, slots=True)
class ToolDefinition:
    """Describe a tool, its contracts, and its implementation."""

    name: str
    description: str
    input_model: type[BaseModel]
    output_model: type[BaseModel]
    handler: ToolHandler

    def __post_init__(self) -> None:
        if not re.fullmatch(r"[a-z][a-z0-9_]{0,99}", self.name):
            raise ToolRegistryError(
                "Tool names must start with a lowercase letter "
                "and contain only lowercase letters, digits, and underscores."
            )

        if not self.description.strip():
            raise ToolRegistryError("Tool description cannot be blank.")

        if not isinstance(self.input_model, type) or not issubclass(
            self.input_model, BaseModel
        ):
            raise ToolRegistryError(
                "Tool input_model must be a Pydantic model."
            )

        if not isinstance(self.output_model, type) or not issubclass(
            self.output_model, BaseModel
        ):
            raise ToolRegistryError(
                "Tool output_model must be a Pydantic model."
            )


class ToolRegistry:
    """Store approved tool definitions and validate their contracts."""

    def __init__(self) -> None:
        self._tools: dict[str, ToolDefinition] = {}

    def register(self, definition: ToolDefinition) -> None:
        """Register a tool under a unique name."""
        if definition.name in self._tools:
            raise ToolRegistryError(
                f"Tool already registered: {definition.name}"
            )

        self._tools[definition.name] = definition

    def get(self, name: str) -> ToolDefinition:
        """Return a registered tool or raise a clear error."""
        try:
            return self._tools[name]
        except KeyError as exc:
            raise ToolNotFoundError(
                f"Tool not registered: {name}"
            ) from exc

    def list_tools(self) -> list[ToolDefinition]:
        """Return registered tools in deterministic name order."""
        return [
            self._tools[name]
            for name in sorted(self._tools)
        ]

    def validate_input(
        self,
        name: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        """Validate and normalize a tool's input."""
        tool = self.get(name)

        try:
            validated = tool.input_model.model_validate(payload)
        except ValidationError as exc:
            raise ToolInputValidationError(
                f"Invalid input for tool '{name}': {exc}"
            ) from exc

        return validated.model_dump()

    def validate_output(
        self,
        name: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        """Validate and normalize a tool's output."""
        tool = self.get(name)

        try:
            validated = tool.output_model.model_validate(payload)
        except ValidationError as exc:
            raise ToolOutputValidationError(
                f"Invalid output from tool '{name}': {exc}"
            ) from exc

        return validated.model_dump()