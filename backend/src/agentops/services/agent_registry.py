"""Registry and execution contracts for specialized AI agents."""

import re
from collections.abc import Callable
from dataclasses import dataclass
from typing import Protocol

from pydantic import BaseModel, ValidationError

from agentops.schemas.agents import (
    VALID_AGENT_ROLES,
    AgentContext,
    AgentResult,
)
from agentops.services.tool_registry import (
    ToolDefinition,
    ToolNotFoundError,
    ToolRegistry,
)

AgentHandler = Callable[[AgentContext], AgentResult]


class AgentRegistryError(ValueError):
    """Base error for agent registration and execution."""


class AgentNotFoundError(AgentRegistryError):
    """Raised when an agent is not registered."""


class AgentAccessDeniedError(AgentRegistryError):
    """Raised when a role cannot use an agent."""


class AgentOutputValidationError(AgentRegistryError):
    """Raised when an agent produces output outside its declared contract."""


@dataclass(frozen=True, slots=True)
class AgentDefinition:
    """Describe an agent's responsibility, output, permissions, and tools."""

    name: str
    description: str
    output_model: type[BaseModel]
    allowed_roles: frozenset[str] = frozenset({"admin", "operator"})
    allowed_tools: frozenset[str] = frozenset()

    def __post_init__(self) -> None:
        """Validate the agent's registration metadata."""
        if not isinstance(self.name, str) or not re.fullmatch(
            r"[a-z][a-z0-9_]{0,99}",
            self.name,
        ):
            raise AgentRegistryError(
                "Agent names must start with a lowercase letter "
                "and contain only lowercase letters, digits, and underscores."
            )

        if not isinstance(self.description, str) or not self.description.strip():
            raise AgentRegistryError("Agent description cannot be blank.")

        if not isinstance(self.output_model, type) or not issubclass(
            self.output_model,
            BaseModel,
        ):
            raise AgentRegistryError("Agent output_model must be a Pydantic model.")

        try:
            roles = frozenset(self.allowed_roles)
            tools = frozenset(self.allowed_tools)
        except TypeError as exc:
            raise AgentRegistryError("Agent roles and tools must be iterable.") from exc

        if not roles:
            raise AgentRegistryError("An agent must allow at least one role.")

        if not all(isinstance(role, str) for role in roles):
            raise AgentRegistryError("Every allowed role must be a string.")

        invalid_roles = roles - VALID_AGENT_ROLES

        if invalid_roles:
            raise AgentRegistryError(f"Invalid agent roles: {', '.join(sorted(invalid_roles))}")

        if not all(isinstance(tool, str) and tool.strip() for tool in tools):
            raise AgentRegistryError("Every allowed tool name must be a non-empty string.")

        object.__setattr__(self, "allowed_roles", roles)
        object.__setattr__(self, "allowed_tools", tools)


class AgentImplementation(Protocol):
    """Interface implemented by each specialized agent."""

    definition: AgentDefinition

    def run(self, context: AgentContext) -> AgentResult:
        """Execute the agent's assigned responsibility."""
        ...


class AgentRegistry:
    """Register agents and enforce their role and tool boundaries."""

    def __init__(self, tool_registry: ToolRegistry) -> None:
        self._tool_registry = tool_registry
        self._agents: dict[str, AgentImplementation] = {}

    def register(self, agent: AgentImplementation) -> None:
        """Register an agent with a unique name and known tools."""
        definition = agent.definition

        if not isinstance(definition, AgentDefinition):
            raise AgentRegistryError("Agent implementation must expose an AgentDefinition.")

        if not callable(agent.run):
            raise AgentRegistryError("Agent implementation must provide run().")

        if definition.name in self._agents:
            raise AgentRegistryError(f"Agent already registered: {definition.name}")

        # Reject misspelled or unregistered tools at registration time.
        for tool_name in definition.allowed_tools:
            try:
                self._tool_registry.get(tool_name)
            except ToolNotFoundError as exc:
                raise AgentRegistryError(
                    f"Agent '{definition.name}' references unknown tool '{tool_name}'."
                ) from exc

        self._agents[definition.name] = agent

    def get(self, name: str) -> AgentImplementation:
        """Return a registered agent."""
        try:
            return self._agents[name]
        except KeyError as exc:
            raise AgentNotFoundError(f"Agent not registered: {name}") from exc

    def list_agents(self) -> list[AgentDefinition]:
        """Return agent definitions in deterministic name order."""
        return [self._agents[name].definition for name in sorted(self._agents)]

    def authorize(self, name: str, role: str) -> AgentDefinition:
        """Return an agent only if the caller's role is permitted."""
        agent = self.get(name)
        definition = agent.definition

        if role not in VALID_AGENT_ROLES:
            raise AgentAccessDeniedError("Invalid actor role.")

        if role not in definition.allowed_roles:
            raise AgentAccessDeniedError(f"Role '{role}' is not permitted to use agent '{name}'.")

        return definition

    def list_available_tools(
        self,
        name: str,
        role: str,
    ) -> list[ToolDefinition]:
        """List tools permitted for both the agent and requesting role."""
        definition = self.authorize(name, role)

        return [
            tool
            for tool in self._tool_registry.list_tools()
            if (tool.name in definition.allowed_tools and role in tool.allowed_roles)
        ]

    def execute(
        self,
        name: str,
        context: AgentContext,
    ) -> AgentResult:
        """Execute an authorized agent and validate its successful output."""
        self.authorize(name, context.actor_role)
        agent = self.get(name)

        result = agent.run(context)

        if not isinstance(result, AgentResult):
            raise AgentRegistryError(f"Agent '{name}' returned an invalid result type.")

        if result.agent_name != name:
            raise AgentRegistryError(f"Agent '{name}' returned a result for '{result.agent_name}'.")

        if result.status == "succeeded":
            try:
                validated_output = agent.definition.output_model.model_validate(result.output)
            except ValidationError as exc:
                raise AgentOutputValidationError(
                    f"Agent '{name}' returned output outside its declared contract."
                ) from exc

            return result.model_copy(update={"output": validated_output.model_dump(mode="json")})

        return result
