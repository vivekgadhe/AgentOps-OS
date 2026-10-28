"""Unit tests for validated AI workflow planning."""

import json
from typing import Any

import pytest
from pydantic import BaseModel, ConfigDict

from agentops.schemas.planning import WorkflowPlan
from agentops.services.planner import (
    PlanningOutputError,
    PlanningValidationError,
    WorkflowPlanner,
)
from agentops.services.tool_registry import ToolDefinition, ToolRegistry


class TextInput(BaseModel):
    """Input contract for the test tool."""

    model_config = ConfigDict(extra="forbid")

    text: str


class TextOutput(BaseModel):
    """Output contract for the test tool."""

    model_config = ConfigDict(extra="forbid")

    value: str


def echo_text(data: dict[str, Any]) -> dict[str, Any]:
    """Return the supplied text."""
    return {"value": data["text"]}


class FakeLLM:
    """Return a predetermined response without contacting a provider."""

    def __init__(self, response: str) -> None:
        self.response = response
        self.last_prompt = ""
        self.last_instructions: str | None = None

    def generate_text(
        self,
        prompt: str,
        *,
        instructions: str | None = None,
    ) -> str:
        self.last_prompt = prompt
        self.last_instructions = instructions
        return self.response


def make_registry() -> ToolRegistry:
    """Create registered tools with different role permissions."""
    registry = ToolRegistry()

    registry.register(
        ToolDefinition(
            name="echo_text",
            description="Accept and return text.",
            input_model=TextInput,
            output_model=TextOutput,
            handler=echo_text,
            allowed_roles=frozenset({"admin", "operator"}),
        )
    )

    registry.register(
        ToolDefinition(
            name="admin_action",
            description="An administrator-only example tool.",
            input_model=TextInput,
            output_model=TextOutput,
            handler=echo_text,
            allowed_roles=frozenset({"admin"}),
        )
    )

    return registry


def make_plan(
    *,
    tool_name: str = "echo_text",
    input_data: dict[str, Any] | None = None,
    depends_on: list[str] | None = None,
) -> str:
    """Return a serialized single-task plan."""
    return json.dumps(
        {
            "tasks": [
                {
                    "key": "process",
                    "name": "Process text",
                    "tool_name": tool_name,
                    "input_data": ({"text": "hello"} if input_data is None else input_data),
                    "max_attempts": 2,
                    "timeout_seconds": 10,
                    "depends_on": [] if depends_on is None else depends_on,
                }
            ]
        }
    )


def test_planner_returns_a_validated_workflow() -> None:
    llm = FakeLLM(make_plan())
    planner = WorkflowPlanner(llm, make_registry())

    result = planner.plan(
        "  Process some text  ",
        actor_role="operator",
    )

    assert result.goal == "Process some text"
    assert len(result.tasks) == 1
    assert result.tasks[0].tool_name == "echo_text"
    assert result.tasks[0].input_data == {"text": "hello"}

    prompt_data = json.loads(llm.last_prompt)
    tool_names = [tool["name"] for tool in prompt_data["available_tools"]]

    assert tool_names == ["echo_text"]
    assert llm.last_instructions is not None


def test_planner_rejects_blank_goal() -> None:
    planner = WorkflowPlanner(FakeLLM("{}"), make_registry())

    with pytest.raises(PlanningValidationError, match="goal cannot be blank"):
        planner.plan("   ", actor_role="operator")


def test_planner_rejects_invalid_actor_role() -> None:
    planner = WorkflowPlanner(FakeLLM(make_plan()), make_registry())

    with pytest.raises(PlanningValidationError, match="Invalid actor role"):
        planner.plan("Process text", actor_role="unknown-role")


def test_planner_rejects_invalid_json() -> None:
    planner = WorkflowPlanner(FakeLLM("not JSON"), make_registry())

    with pytest.raises(PlanningOutputError, match="valid JSON"):
        planner.plan("Process text", actor_role="operator")


def test_planner_rejects_unexpected_plan_fields() -> None:
    response = json.dumps(
        {
            "tasks": [],
            "execute_immediately": True,
        }
    )
    planner = WorkflowPlanner(FakeLLM(response), make_registry())

    with pytest.raises(PlanningOutputError, match="required schema"):
        planner.plan("Process text", actor_role="operator")


def test_planner_rejects_unknown_tool() -> None:
    planner = WorkflowPlanner(
        FakeLLM(make_plan(tool_name="unknown_tool")),
        make_registry(),
    )

    with pytest.raises(PlanningValidationError, match="unknown tool"):
        planner.plan("Process text", actor_role="operator")


def test_planner_rejects_tool_not_permitted_for_actor() -> None:
    planner = WorkflowPlanner(
        FakeLLM(make_plan(tool_name="admin_action")),
        make_registry(),
    )

    with pytest.raises(PlanningValidationError, match="not authorized"):
        planner.plan("Process text", actor_role="operator")


def test_planner_rejects_invalid_tool_input() -> None:
    planner = WorkflowPlanner(
        FakeLLM(make_plan(input_data={"unexpected": "value"})),
        make_registry(),
    )

    with pytest.raises(PlanningValidationError, match="invalid input"):
        planner.plan("Process text", actor_role="operator")


def test_workflow_plan_rejects_dependency_cycles() -> None:
    response = {
        "tasks": [
            {
                "key": "first",
                "name": "First task",
                "tool_name": "echo_text",
                "input_data": {"text": "first"},
                "depends_on": ["second"],
            },
            {
                "key": "second",
                "name": "Second task",
                "tool_name": "echo_text",
                "input_data": {"text": "second"},
                "depends_on": ["first"],
            },
        ]
    }

    with pytest.raises(ValueError, match="dependency cycle"):
        WorkflowPlan.model_validate(response)


def test_workflow_plan_rejects_unknown_dependency() -> None:
    response = {
        "tasks": [
            {
                "key": "first",
                "name": "First task",
                "tool_name": "echo_text",
                "input_data": {"text": "first"},
                "depends_on": ["missing"],
            }
        ]
    }

    with pytest.raises(ValueError, match="unknown task"):
        WorkflowPlan.model_validate(response)
