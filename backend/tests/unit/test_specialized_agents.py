"""Unit tests for the specialized agents."""

from typing import TypeVar, cast
from unittest.mock import Mock

import pytest
from pydantic import BaseModel

from agentops.schemas.agent_outputs import (
    AnalysisOutput,
    ReportOutput,
    ReportSection,
)
from agentops.schemas.agents import AgentContext
from agentops.schemas.planning import WorkflowPlan
from agentops.services.agent_registry import AgentRegistry
from agentops.services.handlers import build_builtin_tool_registry
from agentops.services.llm import LLMProviderError
from agentops.services.planner import StructuredTextGenerator, WorkflowPlanner
from agentops.services.specialized_agents import (
    AnalysisAgent,
    PlanningAgent,
    ReportAgent,
    register_specialized_agents,
)
from agentops.services.tool_registry import ToolRegistry

ModelT = TypeVar("ModelT", bound=BaseModel)


class FakeLLM:
    """Return prepared Pydantic objects without external API requests."""

    def __init__(self, responses: dict[type[BaseModel], BaseModel]) -> None:
        self.responses = responses
        self.calls: list[dict[str, object]] = []

    def generate_structured(
        self,
        prompt: str,
        *,
        output_model: type[ModelT],
        instructions: str | None = None,
    ) -> ModelT:
        self.calls.append(
            {
                "prompt": prompt,
                "output_model": output_model,
                "instructions": instructions,
            }
        )

        response = self.responses[output_model]

        return cast(ModelT, response)


def make_context(
    *,
    role: str = "operator",
    prior_results: dict[str, dict[str, object]] | None = None,
) -> AgentContext:
    return AgentContext(
        goal="Analyze customer feedback",
        actor_role=role,
        prior_results={} if prior_results is None else prior_results,
    )


def make_analysis_output() -> AnalysisOutput:
    return AnalysisOutput(
        summary="Several customers mention delivery delays.",
        findings=["Delivery delays appear in the supplied feedback."],
        recommendations=["Review the delivery process."],
    )


def make_report_output() -> ReportOutput:
    return ReportOutput(
        title="Customer Feedback Report",
        executive_summary="Delivery delays are a recurring concern.",
        sections=[
            ReportSection(
                heading="Key finding",
                content="Several supplied comments mention delays.",
            )
        ],
        conclusion="Review delivery performance using additional data.",
    )


def make_tool_registry() -> ToolRegistry:
    return build_builtin_tool_registry()


def test_analysis_agent_returns_structured_findings() -> None:
    llm = FakeLLM({AnalysisOutput: make_analysis_output()})
    agent = AnalysisAgent(cast(StructuredTextGenerator, llm))

    result = agent.run(make_context())

    assert result.status == "succeeded"
    assert result.agent_name == "analysis_agent"
    assert result.output["findings"] == ["Delivery delays appear in the supplied feedback."]
    assert len(llm.calls) == 1


def test_analysis_agent_receives_prior_results() -> None:
    llm = FakeLLM({AnalysisOutput: make_analysis_output()})
    agent = AnalysisAgent(cast(StructuredTextGenerator, llm))

    agent.run(
        make_context(
            prior_results={
                "research_agent": {"feedback": "Multiple comments mention delivery delays."}
            }
        )
    )

    assert "research_agent" in str(llm.calls[0]["prompt"])
    assert "delivery delays" in str(llm.calls[0]["prompt"])


def test_analysis_agent_returns_failure_on_provider_error() -> None:
    llm = Mock()
    llm.generate_structured.side_effect = LLMProviderError("The OpenAI provider request failed.")

    agent = AnalysisAgent(cast(StructuredTextGenerator, llm))
    result = agent.run(make_context())

    assert result.status == "failed"
    assert result.error_type == "LLMProviderError"


def test_report_agent_returns_structured_report() -> None:
    llm = FakeLLM({ReportOutput: make_report_output()})
    agent = ReportAgent(cast(StructuredTextGenerator, llm))

    result = agent.run(make_context())

    assert result.status == "succeeded"
    assert result.agent_name == "report_agent"
    assert result.output["title"] == "Customer Feedback Report"
    assert len(result.output["sections"]) == 1


def test_planning_agent_returns_workflow_proposal() -> None:
    tool_registry = make_tool_registry()
    workflow_plan = WorkflowPlan.model_validate(
        {
            "tasks": [
                {
                    "key": "summarize",
                    "name": "Summarize supplied text",
                    "tool_name": "summarize_input",
                    "input_data": {"text": "Customer feedback"},
                    "depends_on": [],
                }
            ]
        }
    )
    llm = FakeLLM({WorkflowPlan: workflow_plan})
    planner = WorkflowPlanner(
        cast(StructuredTextGenerator, llm),
        tool_registry,
    )
    agent = PlanningAgent(planner, tool_registry)

    result = agent.run(make_context(role="viewer"))

    assert result.status == "succeeded"
    assert result.agent_name == "planning_agent"
    assert len(result.output["tasks"]) == 1
    assert result.output["tasks"][0]["tool_name"] == "summarize_input"


def test_planning_agent_does_not_execute_the_proposal() -> None:
    tool_registry = make_tool_registry()
    workflow_plan = WorkflowPlan.model_validate(
        {
            "tasks": [
                {
                    "key": "summarize",
                    "name": "Summarize supplied text",
                    "tool_name": "summarize_input",
                    "input_data": {"text": "Customer feedback"},
                }
            ]
        }
    )
    llm = FakeLLM({WorkflowPlan: workflow_plan})
    planner = WorkflowPlanner(
        cast(StructuredTextGenerator, llm),
        tool_registry,
    )
    agent = PlanningAgent(planner, tool_registry)

    result = agent.run(make_context(role="viewer"))

    assert result.status == "succeeded"
    # A planning agent creates a proposal; persistence and task execution
    # remain the responsibility of the existing application endpoints.


def test_specialized_agents_register_with_agent_registry() -> None:
    tool_registry = make_tool_registry()
    llm = FakeLLM(
        {
            WorkflowPlan: WorkflowPlan.model_validate(
                {
                    "tasks": [
                        {
                            "key": "summarize",
                            "name": "Summarize text",
                            "tool_name": "summarize_input",
                            "input_data": {"text": "Example"},
                        }
                    ]
                }
            ),
            AnalysisOutput: make_analysis_output(),
            ReportOutput: make_report_output(),
        }
    )
    planner = WorkflowPlanner(
        cast(StructuredTextGenerator, llm),
        tool_registry,
    )
    registry = AgentRegistry(tool_registry)

    register_specialized_agents(
        registry,
        planner=planner,
        llm=cast(StructuredTextGenerator, llm),
        tool_registry=tool_registry,
    )

    assert [agent.name for agent in registry.list_agents()] == [
        "analysis_agent",
        "planning_agent",
        "report_agent",
    ]


def test_agent_registry_validates_specialized_agent_output() -> None:
    tool_registry = make_tool_registry()
    llm = FakeLLM({AnalysisOutput: make_analysis_output()})
    registry = AgentRegistry(tool_registry)
    registry.register(AnalysisAgent(cast(StructuredTextGenerator, llm)))

    result = registry.execute(
        "analysis_agent",
        make_context(),
    )

    assert result.status == "succeeded"
    assert result.output["summary"] == ("Several customers mention delivery delays.")


def test_analysis_agent_rejects_viewer_role() -> None:
    tool_registry = make_tool_registry()
    llm = FakeLLM({AnalysisOutput: make_analysis_output()})
    registry = AgentRegistry(tool_registry)
    registry.register(AnalysisAgent(cast(StructuredTextGenerator, llm)))

    from agentops.services.agent_registry import AgentAccessDeniedError

    with pytest.raises(AgentAccessDeniedError):
        registry.execute(
            "analysis_agent",
            make_context(role="viewer"),
        )
