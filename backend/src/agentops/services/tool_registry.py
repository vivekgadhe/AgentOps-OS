"""Registry and contracts for approved task tools."""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, ValidationError

ToolHandler = Callable[[dict[str, Any]], dict[str, Any]]

VALID_TOOL_ROLES = frozenset({"admin", "operator", "viewer"})


class ToolRegistryError(ValueError):
    """Base error for tool registration and validation."""


class ToolNotFoundError(ToolRegistryError):
    """Raised when a requested tool is not registered."""


class ToolInputValidationError(ToolRegistryError):
    """Raised when tool input violates its declared schema."""


class ToolOutputValidationError(ToolRegistryError):
    """Raised when tool output violates its declared schema."""


class ToolAccessDeniedError(ToolRegistryError):
    """Raised when a user's role cannot execute a tool."""


@dataclass(frozen=True, slots=True)
class ToolDefinition:
    """Describe a tool, its contracts, and its implementation."""

    name: str
    description: str
    input_model: type[BaseModel]
    output_model: type[BaseModel]
    handler: ToolHandler
    allowed_roles: frozenset[str] = frozenset({"admin", "operator"})
    requires_approval: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not re.fullmatch(
            r"[a-z][a-z0-9_]{0,99}",
            self.name,
        ):
            raise ToolRegistryError(
                "Tool names must start with a lowercase letter "
                "and contain only lowercase letters, digits, and underscores."
            )

        if not isinstance(self.description, str) or not self.description.strip():
            raise ToolRegistryError("Tool description cannot be blank.")

        if not isinstance(self.input_model, type) or not issubclass(self.input_model, BaseModel):
            raise ToolRegistryError("Tool input_model must be a Pydantic model.")

        if not isinstance(self.output_model, type) or not issubclass(self.output_model, BaseModel):
            raise ToolRegistryError("Tool output_model must be a Pydantic model.")

        if not callable(self.handler):
            raise ToolRegistryError("Tool handler must be callable.")

        try:
            roles = frozenset(self.allowed_roles)
        except TypeError as exc:
            raise ToolRegistryError("Tool roles must be an iterable of role names.") from exc

        if not roles:
            raise ToolRegistryError("A tool must allow at least one role.")

        if not all(isinstance(role, str) for role in roles):
            raise ToolRegistryError("Every allowed role must be a string.")

        invalid_roles = roles - VALID_TOOL_ROLES

        if invalid_roles:
            raise ToolRegistryError(f"Invalid tool roles: {', '.join(sorted(invalid_roles))}")

        object.__setattr__(self, "allowed_roles", roles)
        if not isinstance(self.requires_approval, bool):
            raise ToolRegistryError("requires_approval must be a boolean.")


class ToolRegistry:
    """Store approved tool definitions and validate their contracts."""

    def __init__(self) -> None:
        self._tools: dict[str, ToolDefinition] = {}

    def register(self, definition: ToolDefinition) -> None:
        """Register a tool under a unique name."""
        if definition.name in self._tools:
            raise ToolRegistryError(f"Tool already registered: {definition.name}")

        self._tools[definition.name] = definition

    def get(self, name: str) -> ToolDefinition:
        """Return a registered tool or raise a clear error."""
        try:
            return self._tools[name]
        except KeyError as exc:
            raise ToolNotFoundError(f"Tool not registered: {name}") from exc

    def list_tools(self) -> list[ToolDefinition]:
        """Return registered tools in deterministic name order."""
        return [self._tools[name] for name in sorted(self._tools)]

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
            raise ToolInputValidationError(f"Invalid input for tool '{name}': {exc}") from exc

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
            raise ToolOutputValidationError(f"Invalid output from tool '{name}': {exc}") from exc

        return validated.model_dump()

    def authorize(self, name: str, role: str) -> ToolDefinition:
        """Return a tool only when the caller's role is permitted."""
        tool = self.get(name)

        if role not in tool.allowed_roles:
            raise ToolAccessDeniedError(f"Role '{role}' is not permitted to execute tool '{name}'.")

        return tool
