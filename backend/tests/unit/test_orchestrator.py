"""Unit tests for multi-agent orchestration."""

from typing import Any

import pytest
from pydantic import BaseModel, ConfigDict

from agentops.schemas.agents import AgentContext, AgentResult
from agentops.schemas.orchestration import (
    OrchestrationPlan,
    OrchestrationResult,
)
from agentops.services.agent_registry import (
    AgentDefinition,
    AgentRegistry,
)
from agentops.services.handlers import build_builtin_tool_registry
from agentops.services.orchestrator import (
    AgentOrchestrationError,
    AgentOrchestrator,
    RetryableAgentExecutionError,
)


class AgentOutput(BaseModel):
    """Expected output contract for test agents."""

    model_config = ConfigDict(extra="forbid")

    value: str


class FakeAgent:
    """Simple agent with configurable results and recorded contexts."""

    def __init__(
        self,
        name: str,
        *,
        allowed_roles: frozenset[str] = frozenset({"admin", "operator"}),
        output: dict[str, Any] | None = None,
        fail: bool = False,
    ) -> None:
        self.definition = AgentDefinition(
            name=name,
            description=f"Test agent {name}",
            output_model=AgentOutput,
            allowed_roles=allowed_roles,
        )
        self.output = {"value": name} if output is None else output
        self.fail = fail
        self.calls: list[AgentContext] = []

    def run(self, context: AgentContext) -> AgentResult:
        self.calls.append(context)

        if self.fail:
            return AgentResult(
                agent_name=self.definition.name,
                status="failed",
                summary="Agent failed.",
                output={},
                error_type="TestFailure",
                error_message="Configured test failure.",
            )

        return AgentResult(
            agent_name=self.definition.name,
            status="succeeded",
            summary=f"{self.definition.name} completed.",
            output=self.output,
        )

class RetryableFakeAgent(FakeAgent):
    """Fake agent that raises explicitly retryable failures."""

    def __init__(
        self,
        name: str,
        *,
        failures_before_success: int,
    ) -> None:
        super().__init__(name)
        self.failures_remaining = failures_before_success

    def run(self, context: AgentContext) -> AgentResult:
        self.calls.append(context)

        if self.failures_remaining > 0:
            self.failures_remaining -= 1
            raise RetryableAgentExecutionError(
                "Temporary test failure."
            )

        return AgentResult(
            agent_name=self.definition.name,
            status="succeeded",
            summary=f"{self.definition.name} completed.",
            output=self.output,
        )
        
        
def make_registry(*agents: FakeAgent) -> AgentRegistry:
    """Create a registry and register the given fake agents."""
    registry = AgentRegistry(build_builtin_tool_registry())

    for agent in agents:
        registry.register(agent)

    return registry


def make_plan(tasks: list[dict[str, Any]]) -> OrchestrationPlan:
    """Build a validated orchestration plan."""
    return OrchestrationPlan(
        goal="Analyze customer feedback",
        tasks=tasks,
    )


def task(
    key: str,
    agent_name: str,
    depends_on: list[str] | None = None,
) -> dict[str, Any]:
    """Build a task entry."""
    return {
        "key": key,
        "agent_name": agent_name,
        "depends_on": [] if depends_on is None else depends_on,
    }


def test_orchestrator_executes_agents_in_dependency_order() -> None:
    first = FakeAgent("analysis_agent", output={"value": "analysis"})
    second = FakeAgent("report_agent", output={"value": "report"})
    registry = make_registry(first, second)

    plan = make_plan(
        [
            task("report", "report_agent", ["analysis"]),
            task("analysis", "analysis_agent"),
        ]
    )

    result = AgentOrchestrator(registry).run(plan, actor_role="operator")

    assert result.status == "succeeded"
    assert [item.key for item in result.tasks] == ["analysis", "report"]
    assert len(first.calls) == 1
    assert len(second.calls) == 1


def test_orchestrator_passes_dependency_results_to_next_agent() -> None:
    first = FakeAgent("analysis_agent", output={"value": "delays"})
    second = FakeAgent("report_agent")
    registry = make_registry(first, second)

    plan = make_plan(
        [
            task("analysis", "analysis_agent"),
            task("report", "report_agent", ["analysis"]),
        ]
    )

    result = AgentOrchestrator(registry).run(plan, actor_role="operator")

    assert result.status == "succeeded"
    context = second.calls[0]
    assert context.prior_results["analysis"]["output"] == {"value": "delays"}


def test_orchestrator_skips_dependents_after_failure() -> None:
    first = FakeAgent("analysis_agent", fail=True)
    second = FakeAgent("report_agent")
    registry = make_registry(first, second)

    plan = make_plan(
        [
            task("analysis", "analysis_agent"),
            task("report", "report_agent", ["analysis"]),
        ]
    )

    result = AgentOrchestrator(registry).run(plan, actor_role="operator")

    outcomes = {item.key: item for item in result.tasks}

    assert result.status == "failed"
    assert outcomes["analysis"].status == "failed"
    assert outcomes["report"].status == "skipped"
    assert second.calls == []


def test_orchestrator_continues_independent_tasks_after_failure() -> None:
    failing = FakeAgent("analysis_agent", fail=True)
    independent = FakeAgent("report_agent")
    registry = make_registry(failing, independent)

    plan = make_plan(
        [
            task("analysis", "analysis_agent"),
            task("independent_report", "report_agent"),
        ]
    )

    result = AgentOrchestrator(registry).run(plan, actor_role="operator")

    outcomes = {item.key: item for item in result.tasks}

    assert result.status == "failed"
    assert outcomes["analysis"].status == "failed"
    assert outcomes["independent_report"].status == "succeeded"
    assert len(independent.calls) == 1


def test_orchestrator_rejects_unauthorized_agent_before_execution() -> None:
    first = FakeAgent("analysis_agent")
    restricted = FakeAgent(
        "restricted_agent",
        allowed_roles=frozenset({"admin"}),
    )
    registry = make_registry(first, restricted)

    plan = make_plan(
        [
            task("analysis", "analysis_agent"),
            task("restricted", "restricted_agent", ["analysis"]),
        ]
    )

    with pytest.raises(AgentOrchestrationError, match="cannot use agent"):
        AgentOrchestrator(registry).run(plan, actor_role="operator")

    # Preflight authorization prevents partial execution of the plan.
    assert first.calls == []
    assert restricted.calls == []


def test_orchestrator_rejects_unregistered_agent_before_execution() -> None:
    first = FakeAgent("analysis_agent")
    registry = make_registry(first)

    plan = make_plan(
        [
            task("analysis", "analysis_agent"),
            task("missing", "missing_agent", ["analysis"]),
        ]
    )

    with pytest.raises(AgentOrchestrationError, match="cannot use agent"):
        AgentOrchestrator(registry).run(plan, actor_role="operator")

    assert first.calls == []


def test_orchestrator_validates_dependency_cycles() -> None:
    with pytest.raises(ValueError, match="dependency cycle"):
        make_plan(
            [
                task("first", "analysis_agent", ["second"]),
                task("second", "report_agent", ["first"]),
            ]
        )


def test_orchestrator_rejects_unknown_dependencies() -> None:
    with pytest.raises(ValueError, match="unknown task"):
        make_plan(
            [
                task("analysis", "analysis_agent", ["missing"]),
            ]
        )


def test_orchestrator_rejects_duplicate_task_keys() -> None:
    with pytest.raises(ValueError, match="duplicate task keys"):
        make_plan(
            [
                task("analysis", "analysis_agent"),
                task("analysis", "report_agent"),
            ]
        )


def test_orchestration_result_can_be_serialized() -> None:
    agent = FakeAgent("analysis_agent")
    plan = make_plan([task("analysis", "analysis_agent")])

    result: OrchestrationResult = AgentOrchestrator(make_registry(agent)).run(
        plan, actor_role="operator"
    )

    serialized = result.model_dump(mode="json")

    assert serialized["status"] == "succeeded"
    assert serialized["tasks"][0]["agent_name"] == "analysis_agent"

def test_orchestrator_retries_explicitly_retryable_failures() -> None:
    agent = RetryableFakeAgent(
        "analysis_agent",
        failures_before_success=1,
    )

    result = AgentOrchestrator(
        make_registry(agent),
        max_attempts=2,
    ).run(
        make_plan([task("analysis", "analysis_agent")]),
        actor_role="operator",
    )

    assert result.status == "succeeded"
    assert result.tasks[0].status == "succeeded"
    assert len(agent.calls) == 2


def test_orchestrator_stops_after_maximum_attempts() -> None:
    agent = RetryableFakeAgent(
        "analysis_agent",
        failures_before_success=3,
    )

    result = AgentOrchestrator(
        make_registry(agent),
        max_attempts=2,
    ).run(
        make_plan([task("analysis", "analysis_agent")]),
        actor_role="operator",
    )

    assert result.status == "failed"
    assert result.tasks[0].status == "failed"
    assert result.tasks[0].error_type == "RetryableAgentExecutionError"
    assert len(agent.calls) == 2


def test_orchestrator_rejects_invalid_max_attempts() -> None:
    registry = make_registry(FakeAgent("analysis_agent"))

    for invalid_value in (0, 4, -1, True):
        with pytest.raises(ValueError, match="max_attempts"):
            AgentOrchestrator(
                registry,
                max_attempts=invalid_value,
            )
            
def test_orchestrator_does_not_expose_internal_exception_message() -> None:
    class ExplodingAgent(FakeAgent):
        """Agent that raises an exception containing sensitive details."""

        def run(self, context: AgentContext) -> AgentResult:
            self.calls.append(context)
            raise ValueError(
                "Internal provider response containing sensitive details"
            )

    agent = ExplodingAgent("analysis_agent")
    plan = make_plan([task("analysis", "analysis_agent")])

    result = AgentOrchestrator(make_registry(agent)).run(
        plan,
        actor_role="operator",
    )

    outcome = result.tasks[0]

    assert result.status == "failed"
    assert outcome.status == "failed"
    assert outcome.error_type == "ValueError"
    assert outcome.error_message == "Agent execution failed."
    assert "sensitive details" not in (outcome.error_message or "")