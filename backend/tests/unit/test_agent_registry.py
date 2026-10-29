"""Unit tests for the agent registry and execution contracts."""

from typing import Any

import pytest
from pydantic import BaseModel, ConfigDict

from agentops.schemas.agents import AgentContext, AgentResult
from agentops.services.agent_registry import (
    AgentAccessDeniedError,
    AgentDefinition,
    AgentNotFoundError,
    AgentOutputValidationError,
    AgentRegistry,
    AgentRegistryError,
)
from agentops.services.handlers import build_builtin_tool_registry


class TextOutput(BaseModel):
    """Expected output contract for the test agent."""

    model_config = ConfigDict(extra="forbid")

    text: str


class FakeAgent:
    """Minimal agent implementation for registry tests."""

    def __init__(
        self,
        definition: AgentDefinition,
        result: AgentResult | None = None,
    ) -> None:
        self.definition = definition
        self.result = result or AgentResult(
            agent_name=definition.name,
            status="succeeded",
            summary="Processing completed.",
            output={"text": "hello"},
        )
        self.received_context: AgentContext | None = None

    def run(self, context: AgentContext) -> AgentResult:
        """Return the configured result and record the supplied context."""
        self.received_context = context
        return self.result


def make_agent(
    name: str = "analysis_agent",
    *,
    allowed_roles: frozenset[str] = frozenset({"admin", "operator"}),
    allowed_tools: frozenset[str] = frozenset({"summarize_input"}),
    result: AgentResult | None = None,
) -> FakeAgent:
    """Build a test agent with a declared output contract."""
    definition = AgentDefinition(
        name=name,
        description="Analyze supplied information.",
        output_model=TextOutput,
        allowed_roles=allowed_roles,
        allowed_tools=allowed_tools,
    )

    return FakeAgent(definition, result)


def make_context(
    role: str = "operator",
    *,
    prior_results: dict[str, dict[str, Any]] | None = None,
) -> AgentContext:
    """Build a validated agent context."""
    return AgentContext(
        goal="Analyze the supplied text",
        actor_role=role,
        prior_results={} if prior_results is None else prior_results,
    )


def make_registry() -> AgentRegistry:
    """Build an empty agent registry with the built-in tool definitions."""
    return AgentRegistry(build_builtin_tool_registry())


def test_registry_registers_and_lists_agents_deterministically() -> None:
    registry = make_registry()

    registry.register(make_agent("report_agent"))
    registry.register(make_agent("analysis_agent"))

    assert [
        agent.name for agent in registry.list_agents()
    ] == ["analysis_agent", "report_agent"]


def test_registry_rejects_duplicate_agent_names() -> None:
    registry = make_registry()

    registry.register(make_agent())

    with pytest.raises(AgentRegistryError, match="already registered"):
        registry.register(make_agent())


def test_registry_rejects_unknown_allowed_tools() -> None:
    registry = make_registry()

    agent = make_agent(
        allowed_tools=frozenset({"tool_does_not_exist"})
    )

    with pytest.raises(AgentRegistryError, match="unknown tool"):
        registry.register(agent)


def test_registry_raises_for_unknown_agent() -> None:
    registry = make_registry()

    with pytest.raises(AgentNotFoundError, match="not registered"):
        registry.get("missing_agent")


def test_registry_authorizes_permitted_roles() -> None:
    registry = make_registry()
    registry.register(make_agent())

    definition = registry.authorize("analysis_agent", "operator")

    assert definition.name == "analysis_agent"


def test_registry_rejects_unauthorized_roles() -> None:
    registry = make_registry()
    registry.register(make_agent())

    with pytest.raises(AgentAccessDeniedError, match="not permitted"):
        registry.authorize("analysis_agent", "viewer")


def test_registry_filters_tools_by_agent_and_user_permissions() -> None:
    registry = make_registry()

    registry.register(
        make_agent(
            allowed_roles=frozenset({"admin", "operator", "viewer"}),
            allowed_tools=frozenset(
                {"summarize_input", "text_statistics"}
            ),
        )
    )

    viewer_tools = registry.list_available_tools(
        "analysis_agent",
        "viewer",
    )

    # summarize_input permits viewers; text_statistics does not.
    assert [tool.name for tool in viewer_tools] == ["summarize_input"]


def test_registry_executes_agent_and_validates_output() -> None:
    registry = make_registry()
    agent = make_agent()
    registry.register(agent)

    context = make_context()
    result = registry.execute("analysis_agent", context)

    assert result.status == "succeeded"
    assert result.output == {"text": "hello"}
    assert agent.received_context == context


def test_registry_rejects_invalid_successful_output() -> None:
    registry = make_registry()

    agent = make_agent(
        result=AgentResult(
            agent_name="analysis_agent",
            status="succeeded",
            summary="Finished.",
            output={"unexpected": "value"},
        )
    )
    registry.register(agent)

    with pytest.raises(
        AgentOutputValidationError,
        match="outside its declared contract",
    ):
        registry.execute("analysis_agent", make_context())


def test_registry_rejects_a_result_with_the_wrong_agent_name() -> None:
    registry = make_registry()

    agent = make_agent(
        result=AgentResult(
            agent_name="report_agent",
            status="succeeded",
            summary="Finished.",
            output={"text": "hello"},
        )
    )
    registry.register(agent)

    with pytest.raises(AgentRegistryError, match="returned a result for"):
        registry.execute("analysis_agent", make_context())


def test_registry_preserves_structured_agent_failure() -> None:
    registry = make_registry()

    agent = make_agent(
        result=AgentResult(
            agent_name="analysis_agent",
            status="failed",
            summary="Analysis failed.",
            output={},
            error_type="InputProcessingError",
            error_message="The supplied input could not be processed.",
        )
    )
    registry.register(agent)

    result = registry.execute("analysis_agent", make_context())

    assert result.status == "failed"
    assert result.error_type == "InputProcessingError"


def test_agent_context_normalizes_goal_and_preserves_prior_results() -> None:
    context = make_context(
        prior_results={"research_agent": {"finding": "Example finding"}}
    )

    assert context.goal == "Analyze the supplied text"
    assert context.prior_results == {
        "research_agent": {"finding": "Example finding"}
    }


def test_agent_context_rejects_invalid_roles() -> None:
    with pytest.raises(ValueError, match="Invalid actor role"):
        make_context("unknown_role")