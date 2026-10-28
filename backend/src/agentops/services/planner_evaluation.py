"""Evaluate workflow plans against explicit quality criteria."""

from dataclasses import dataclass

from pydantic import ValidationError

from agentops.schemas.planning import WorkflowPlan
from agentops.schemas.workflows import WorkflowCreate
from agentops.services.tool_registry import ToolRegistry, ToolRegistryError


@dataclass(frozen=True, slots=True)
class PlannerEvaluationCase:
    """Expected characteristics of a proposed workflow."""

    name: str
    goal: str
    actor_role: str
    required_tools: frozenset[str] = frozenset()
    forbidden_tools: frozenset[str] = frozenset()
    # Each pair is (dependent_task_key, prerequisite_task_key).
    required_dependencies: frozenset[tuple[str, str]] = frozenset()


@dataclass(frozen=True, slots=True)
class PlannerEvaluationResult:
    """Evaluation score and individual quality checks."""

    case_name: str
    passed: bool
    score: float
    checks: dict[str, bool]
    failures: tuple[str, ...]


def evaluate_workflow_plan(
    case: PlannerEvaluationCase,
    plan: WorkflowCreate,
    registry: ToolRegistry,
) -> PlannerEvaluationResult:
    """Score a proposed workflow against explicit acceptance criteria.

    The score is the proportion of checks that pass. This is a deterministic
    evaluation of a supplied plan, not a measurement of the LLM's general
    reasoning ability.
    """
    tasks = plan.tasks
    task_keys = [task.key for task in tasks]
    task_key_set = set(task_keys)

    tool_names = {task.tool_name for task in tasks if task.tool_name is not None}

    dependency_edges = {(task.key, dependency) for task in tasks for dependency in task.depends_on}

    checks: dict[str, bool] = {
        "goal_matches": plan.goal.strip() == case.goal.strip(),
        "workflow_is_nonempty": bool(tasks),
        "task_keys_are_unique": len(task_keys) == len(task_key_set),
        "required_tools_are_present": case.required_tools <= tool_names,
        "forbidden_tools_are_absent": not (case.forbidden_tools & tool_names),
        "required_dependencies_are_present": (case.required_dependencies <= dependency_edges),
    }

    try:
        WorkflowPlan.model_validate({"tasks": [task.model_dump() for task in tasks]})
        checks["dependency_graph_is_valid"] = True
    except ValidationError:
        checks["dependency_graph_is_valid"] = False

    tool_contracts_valid = True

    for task in tasks:
        if task.tool_name is None:
            tool_contracts_valid = False
            break

        try:
            registry.get(task.tool_name)
            registry.authorize(task.tool_name, case.actor_role)
            registry.validate_input(task.tool_name, task.input_data)
        except ToolRegistryError:
            tool_contracts_valid = False
            break

    checks["tool_contracts_and_permissions_are_valid"] = tool_contracts_valid

    failures = tuple(check_name for check_name, check_passed in checks.items() if not check_passed)

    score = sum(checks.values()) / len(checks)

    return PlannerEvaluationResult(
        case_name=case.name,
        passed=not failures,
        score=score,
        checks=checks,
        failures=failures,
    )
