"""Tests for deterministic workflow-planning evaluation."""

from agentops.schemas.workflows import TaskCreate, WorkflowCreate
from agentops.services.handlers import build_builtin_tool_registry
from agentops.services.planner_evaluation import (
    PlannerEvaluationCase,
    evaluate_workflow_plan,
)


def make_task(
    key: str,
    tool_name: str,
    input_data: dict[str, str],
    *,
    depends_on: list[str] | None = None,
) -> TaskCreate:
    """Create a task for an evaluation case."""
    return TaskCreate(
        key=key,
        name=f"Run {tool_name}",
        tool_name=tool_name,
        input_data=input_data,
        depends_on=[] if depends_on is None else depends_on,
    )


def make_case(
    *,
    required_tools: frozenset[str] = frozenset(),
    forbidden_tools: frozenset[str] = frozenset(),
    required_dependencies: frozenset[tuple[str, str]] = frozenset(),
    actor_role: str = "operator",
) -> PlannerEvaluationCase:
    """Create a standard workflow evaluation case."""
    return PlannerEvaluationCase(
        name="text-processing",
        goal="Process text",
        actor_role=actor_role,
        required_tools=required_tools,
        forbidden_tools=forbidden_tools,
        required_dependencies=required_dependencies,
    )


def make_workflow(
    tasks: list[TaskCreate],
    *,
    goal: str = "Process text",
) -> WorkflowCreate:
    """Construct a proposed workflow."""
    return WorkflowCreate(goal=goal, tasks=tasks)


def test_evaluator_passes_a_valid_plan() -> None:
    registry = build_builtin_tool_registry()
    case = make_case(required_tools=frozenset({"normalize_whitespace"}))
    plan = make_workflow(
        [
            make_task(
                "normalize",
                "normalize_whitespace",
                {"text": "  Hello   world  "},
            )
        ]
    )

    result = evaluate_workflow_plan(case, plan, registry)

    assert result.passed
    assert result.score == 1.0
    assert result.failures == ()
    assert all(result.checks.values())


def test_evaluator_detects_a_missing_required_tool() -> None:
    registry = build_builtin_tool_registry()
    case = make_case(required_tools=frozenset({"text_statistics"}))
    plan = make_workflow(
        [
            make_task(
                "normalize",
                "normalize_whitespace",
                {"text": "Hello world"},
            )
        ]
    )

    result = evaluate_workflow_plan(case, plan, registry)

    assert not result.passed
    assert not result.checks["required_tools_are_present"]
    assert "required_tools_are_present" in result.failures
    assert result.score < 1.0


def test_evaluator_detects_a_forbidden_tool() -> None:
    registry = build_builtin_tool_registry()
    case = make_case(forbidden_tools=frozenset({"find_matching_lines"}))
    plan = make_workflow(
        [
            make_task(
                "search",
                "find_matching_lines",
                {"text": "Hello AI", "query": "AI"},
            )
        ]
    )

    result = evaluate_workflow_plan(case, plan, registry)

    assert not result.passed
    assert not result.checks["forbidden_tools_are_absent"]


def test_evaluator_checks_required_dependencies() -> None:
    registry = build_builtin_tool_registry()
    case = make_case(
        required_tools=frozenset({"normalize_whitespace", "text_statistics"}),
        required_dependencies=frozenset({("statistics", "normalize")}),
    )
    plan = make_workflow(
        [
            make_task(
                "normalize",
                "normalize_whitespace",
                {"text": "  Hello   world  "},
            ),
            make_task(
                "statistics",
                "text_statistics",
                {"text": "Hello world"},
            ),
        ]
    )

    result = evaluate_workflow_plan(case, plan, registry)

    assert not result.passed
    assert not result.checks["required_dependencies_are_present"]


def test_evaluator_accepts_the_expected_dependency() -> None:
    registry = build_builtin_tool_registry()
    case = make_case(
        required_tools=frozenset({"normalize_whitespace", "text_statistics"}),
        required_dependencies=frozenset({("statistics", "normalize")}),
    )
    plan = make_workflow(
        [
            make_task(
                "normalize",
                "normalize_whitespace",
                {"text": "  Hello   world  "},
            ),
            make_task(
                "statistics",
                "text_statistics",
                {"text": "Hello world"},
                depends_on=["normalize"],
            ),
        ]
    )

    result = evaluate_workflow_plan(case, plan, registry)

    assert result.passed
    assert result.score == 1.0


def test_evaluator_detects_an_invalid_dependency_graph() -> None:
    registry = build_builtin_tool_registry()
    case = make_case()
    plan = make_workflow(
        [
            make_task(
                "first",
                "normalize_whitespace",
                {"text": "Hello"},
                depends_on=["second"],
            ),
            make_task(
                "second",
                "normalize_whitespace",
                {"text": "World"},
                depends_on=["first"],
            ),
        ]
    )

    result = evaluate_workflow_plan(case, plan, registry)

    assert not result.passed
    assert not result.checks["dependency_graph_is_valid"]


def test_evaluator_detects_an_unauthorized_tool() -> None:
    registry = build_builtin_tool_registry()
    case = make_case(
        required_tools=frozenset({"text_statistics"}),
        actor_role="viewer",
    )
    plan = make_workflow(
        [
            make_task(
                "statistics",
                "text_statistics",
                {"text": "Hello world"},
            )
        ]
    )

    result = evaluate_workflow_plan(case, plan, registry)

    assert not result.passed
    assert not result.checks["tool_contracts_and_permissions_are_valid"]


def test_evaluator_detects_invalid_tool_input() -> None:
    registry = build_builtin_tool_registry()
    case = make_case(required_tools=frozenset({"text_statistics"}))
    plan = make_workflow(
        [
            make_task(
                "statistics",
                "text_statistics",
                {"unexpected": "value"},
            )
        ]
    )

    result = evaluate_workflow_plan(case, plan, registry)

    assert not result.passed
    assert not result.checks["tool_contracts_and_permissions_are_valid"]


def test_evaluator_detects_goal_mismatch() -> None:
    registry = build_builtin_tool_registry()
    case = make_case()
    plan = make_workflow(
        [
            make_task(
                "normalize",
                "normalize_whitespace",
                {"text": "Hello"},
            )
        ],
        goal="Different goal",
    )

    result = evaluate_workflow_plan(case, plan, registry)

    assert not result.passed
    assert not result.checks["goal_matches"]


def test_evaluator_score_matches_passed_checks() -> None:
    registry = build_builtin_tool_registry()
    case = make_case(required_tools=frozenset({"text_statistics"}))
    plan = make_workflow(
        [
            make_task(
                "normalize",
                "normalize_whitespace",
                {"text": "Hello"},
            )
        ]
    )

    result = evaluate_workflow_plan(case, plan, registry)

    expected_score = sum(result.checks.values()) / len(result.checks)
    assert result.score == expected_score
