"""Evaluate multi-agent orchestration quality and reliability."""

import json
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from agentops.schemas.orchestration import (
    OrchestrationPlan,
    OrchestrationResult,
)


@dataclass(frozen=True, slots=True)
class OrchestrationEvaluationCase:
    """Expected characteristics of a multi-agent workflow."""

    name: str
    goal: str

    required_agents: frozenset[str] = frozenset()
    forbidden_agents: frozenset[str] = frozenset()

    required_successful_tasks: frozenset[str] = frozenset()

    # Each pair is (dependent_task_key, prerequisite_task_key).
    required_dependencies: frozenset[tuple[str, str]] = frozenset()

    # Each pair is (task_key, required_output_field).
    required_output_fields: frozenset[tuple[str, str]] = frozenset()

    # Each pair is (task_key, forbidden_output_field).
    forbidden_output_fields: frozenset[tuple[str, str]] = frozenset()

    # Each pair is (task_key, required_text_phrase).
    required_output_phrases: frozenset[tuple[str, str]] = frozenset()

    # Each pair is (task_key, forbidden_text_phrase).
    forbidden_output_phrases: frozenset[tuple[str, str]] = frozenset()

    # Each tuple is (task_key, field_name, expected_value).
    expected_output_values: frozenset[tuple[str, str, str]] = frozenset()


@dataclass(frozen=True, slots=True)
class OrchestrationEvaluationResult:
    """Evaluation score and individual quality checks."""

    case_name: str
    passed: bool
    score: float
    checks: dict[str, bool]
    failures: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        """Convert the evaluation result into JSON-compatible data."""
        return {
            "case_name": self.case_name,
            "passed": self.passed,
            "score": self.score,
            "checks": dict(self.checks),
            "failures": list(self.failures),
        }


@dataclass(frozen=True, slots=True)
class OrchestrationEvaluationSample:
    """One workflow execution submitted to the benchmark."""

    case: OrchestrationEvaluationCase
    plan: OrchestrationPlan
    result: OrchestrationResult


@dataclass(frozen=True, slots=True)
class OrchestrationBenchmarkResult:
    """Aggregate evaluation metrics across multiple workflows."""

    total_cases: int
    passed_cases: int
    pass_rate: float
    average_score: float
    check_pass_rates: dict[str, float]
    case_results: tuple[OrchestrationEvaluationResult, ...]


@dataclass(frozen=True, slots=True)
class OrchestrationEvaluationReport:
    """Structured report for a multi-agent evaluation benchmark."""

    total_cases: int
    passed_cases: int
    failed_cases: int
    pass_rate: float
    average_score: float
    check_pass_rates: dict[str, float]
    case_results: tuple[OrchestrationEvaluationResult, ...]

    def to_dict(self) -> dict[str, Any]:
        """Convert the report into JSON-compatible data."""
        return {
            "summary": {
                "total_cases": self.total_cases,
                "passed_cases": self.passed_cases,
                "failed_cases": self.failed_cases,
                "pass_rate": self.pass_rate,
                "average_score": self.average_score,
            },
            "check_pass_rates": dict(self.check_pass_rates),
            "cases": [result.to_dict() for result in self.case_results],
        }

    def to_json(self) -> str:
        """Serialize the complete evaluation report into JSON."""
        return json.dumps(
            self.to_dict(),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
            allow_nan=False,
        )


def _collect_output_text(value: Any) -> str:
    """Collect string values from nested output data."""
    if isinstance(value, str):
        return value

    if isinstance(value, dict):
        return " ".join(_collect_output_text(child) for child in value.values())

    if isinstance(value, list):
        return " ".join(_collect_output_text(child) for child in value)

    return ""


def evaluate_orchestration(
    case: OrchestrationEvaluationCase,
    plan: OrchestrationPlan,
    result: OrchestrationResult,
) -> OrchestrationEvaluationResult:
    """Evaluate an executed orchestration against explicit criteria.

    Evaluation is deterministic and checks structure, dependencies,
    execution outcomes, and predefined output-quality requirements.

    It does not establish factual accuracy or general semantic quality.
    """
    plan_tasks = {task.key: task for task in plan.tasks}

    plan_keys = set(plan_tasks)

    result_keys = [task.key for task in result.tasks]

    result_key_set = set(result_keys)

    result_tasks = {task.key: task for task in result.tasks}

    planned_agents = {task.agent_name for task in plan.tasks}

    dependency_edges = {
        (task.key, dependency) for task in plan.tasks for dependency in task.depends_on
    }

    checks: dict[str, bool] = {
        "goal_matches": (
            plan.goal.strip() == case.goal.strip() and result.goal.strip() == case.goal.strip()
        ),
        "result_task_keys_are_unique": (len(result_keys) == len(result_key_set)),
        "all_planned_tasks_have_results": (plan_keys <= result_key_set),
        "no_unplanned_task_results": (result_key_set <= plan_keys),
        "task_agent_assignments_match": all(
            key in result_tasks and result_tasks[key].agent_name == task.agent_name
            for key, task in plan_tasks.items()
        ),
        "required_agents_are_present": (case.required_agents <= planned_agents),
        "forbidden_agents_are_absent": (not (case.forbidden_agents & planned_agents)),
        "required_tasks_succeeded": all(
            task_key in result_tasks and result_tasks[task_key].status == "succeeded"
            for task_key in case.required_successful_tasks
        ),
        "required_dependencies_are_present": (case.required_dependencies <= dependency_edges),
    }

    # Check whether dependent agents ran only after successful prerequisites.
    dependencies_respected = True

    for task in plan.tasks:
        outcome = result_tasks.get(task.key)

        if outcome is None or outcome.status != "succeeded":
            continue

        for dependency in task.depends_on:
            dependency_outcome = result_tasks.get(dependency)

            if dependency_outcome is None or dependency_outcome.status != "succeeded":
                dependencies_respected = False
                break

        if not dependencies_respected:
            break

    checks["dependencies_respected"] = dependencies_respected

    # Check consistency between orchestration and individual agent results.
    agent_results_consistent = True

    for outcome in result.tasks:
        agent_result = outcome.result

        if agent_result is None:
            if outcome.status == "succeeded":
                agent_results_consistent = False
                break

            continue

        if agent_result.agent_name != outcome.agent_name or agent_result.status != outcome.status:
            agent_results_consistent = False
            break

    checks["agent_results_are_consistent"] = agent_results_consistent

    # Required fields must exist in successful task outputs.
    required_fields_present = True

    for task_key, field_name in case.required_output_fields:
        outcome = result_tasks.get(task_key)

        if (
            outcome is None
            or outcome.status != "succeeded"
            or outcome.result is None
            or field_name not in outcome.result.output
        ):
            required_fields_present = False
            break

    checks["required_output_fields_are_present"] = required_fields_present

    # Forbidden fields must not occur in successful task outputs.
    forbidden_fields_absent = True

    for task_key, field_name in case.forbidden_output_fields:
        outcome = result_tasks.get(task_key)

        if (
            outcome is not None
            and outcome.status == "succeeded"
            and outcome.result is not None
            and field_name in outcome.result.output
        ):
            forbidden_fields_absent = False
            break

    checks["forbidden_output_fields_are_absent"] = forbidden_fields_absent

    # Required phrases must appear in the output text.
    required_phrases_present = True

    for task_key, phrase in case.required_output_phrases:
        outcome = result_tasks.get(task_key)

        if outcome is None or outcome.status != "succeeded" or outcome.result is None:
            required_phrases_present = False
            break

        output_text = _collect_output_text(outcome.result.output).casefold()

        if phrase.casefold() not in output_text:
            required_phrases_present = False
            break

    checks["required_output_phrases_are_present"] = required_phrases_present

    # Forbidden phrases must not appear in the output text.
    forbidden_phrases_absent = True

    for task_key, phrase in case.forbidden_output_phrases:
        outcome = result_tasks.get(task_key)

        if outcome is not None and outcome.status == "succeeded" and outcome.result is not None:
            output_text = _collect_output_text(outcome.result.output).casefold()

            if phrase.casefold() in output_text:
                forbidden_phrases_absent = False
                break

    checks["forbidden_output_phrases_are_absent"] = forbidden_phrases_absent

    # Expected reference values must match exactly.
    expected_values_match = True

    for task_key, field_name, expected_value in case.expected_output_values:
        outcome = result_tasks.get(task_key)

        if (
            outcome is None
            or outcome.status != "succeeded"
            or outcome.result is None
            or outcome.result.output.get(field_name) != expected_value
        ):
            expected_values_match = False
            break

    checks["expected_output_values_match"] = expected_values_match

    # A workflow succeeds only if every planned task has one successful result.
    complete_result = len(result_keys) == len(result_key_set) and plan_keys == result_key_set

    all_tasks_succeeded = complete_result and all(
        outcome.status == "succeeded" for outcome in result.tasks
    )

    expected_workflow_status = "succeeded" if all_tasks_succeeded else "failed"

    checks["workflow_status_is_consistent"] = result.status == expected_workflow_status

    failures = tuple(check_name for check_name, passed in checks.items() if not passed)

    score = sum(checks.values()) / len(checks)

    return OrchestrationEvaluationResult(
        case_name=case.name,
        passed=not failures,
        score=score,
        checks=checks,
        failures=failures,
    )


def evaluate_orchestration_benchmark(
    samples: Sequence[OrchestrationEvaluationSample],
) -> OrchestrationBenchmarkResult:
    """Evaluate multiple workflow executions and aggregate their scores."""
    if not samples:
        raise ValueError("An evaluation benchmark must contain at least one case.")

    case_names = [sample.case.name for sample in samples]

    if len(case_names) != len(set(case_names)):
        raise ValueError("Evaluation benchmark case names must be unique.")

    case_results = tuple(
        evaluate_orchestration(
            sample.case,
            sample.plan,
            sample.result,
        )
        for sample in samples
    )

    total_cases = len(case_results)

    passed_cases = sum(result.passed for result in case_results)

    pass_rate = passed_cases / total_cases

    average_score = sum(result.score for result in case_results) / total_cases

    check_names = case_results[0].checks

    check_pass_rates = {
        check_name: (sum(result.checks[check_name] for result in case_results) / total_cases)
        for check_name in check_names
    }

    return OrchestrationBenchmarkResult(
        total_cases=total_cases,
        passed_cases=passed_cases,
        pass_rate=pass_rate,
        average_score=average_score,
        check_pass_rates=check_pass_rates,
        case_results=case_results,
    )


def build_orchestration_evaluation_report(
    benchmark: OrchestrationBenchmarkResult,
) -> OrchestrationEvaluationReport:
    """Build a structured report from benchmark results."""
    return OrchestrationEvaluationReport(
        total_cases=benchmark.total_cases,
        passed_cases=benchmark.passed_cases,
        failed_cases=(benchmark.total_cases - benchmark.passed_cases),
        pass_rate=benchmark.pass_rate,
        average_score=benchmark.average_score,
        check_pass_rates=benchmark.check_pass_rates,
        case_results=benchmark.case_results,
    )
