"""Tests for comprehensive multi-agent orchestration evaluation."""

import json
from dataclasses import replace

import pytest

from agentops.schemas.agents import AgentResult
from agentops.schemas.orchestration import (
    OrchestrationPlan,
    OrchestrationResult,
    OrchestrationTaskResult,
)
from agentops.services.orchestration_evaluation import (
    OrchestrationEvaluationCase,
    OrchestrationEvaluationSample,
    build_orchestration_evaluation_report,
    evaluate_orchestration,
    evaluate_orchestration_benchmark,
)


def make_plan() -> OrchestrationPlan:
    """Create a standard two-agent workflow."""
    return OrchestrationPlan(
        goal="Analyze customer feedback",
        tasks=[
            {
                "key": "analysis",
                "agent_name": "analysis_agent",
            },
            {
                "key": "report",
                "agent_name": "report_agent",
                "depends_on": ["analysis"],
            },
        ],
    )


def make_successful_task(
    key: str,
    agent_name: str,
    output: dict | None = None,
) -> OrchestrationTaskResult:
    """Create a successful task result."""
    return OrchestrationTaskResult(
        key=key,
        agent_name=agent_name,
        status="succeeded",
        result=AgentResult(
            agent_name=agent_name,
            status="succeeded",
            summary=f"{agent_name} completed successfully.",
            output=(
                {"value": "completed"}
                if output is None
                else output
            ),
        ),
    )


def make_result(
    tasks: list[OrchestrationTaskResult] | None = None,
    *,
    status: str = "succeeded",
) -> OrchestrationResult:
    """Create a standard orchestration result."""
    if tasks is None:
        tasks = [
            make_successful_task(
                "analysis",
                "analysis_agent",
                {
                    "findings": ["Delivery delays"],
                    "summary": "Delivery delays were identified.",
                },
            ),
            make_successful_task(
                "report",
                "report_agent",
                {
                    "title": "Customer Feedback Report",
                },
            ),
        ]

    return OrchestrationResult(
        goal="Analyze customer feedback",
        status=status,
        tasks=tasks,
    )


def make_case() -> OrchestrationEvaluationCase:
    """Create a standard evaluation case."""
    return OrchestrationEvaluationCase(
        name="customer-feedback-analysis",
        goal="Analyze customer feedback",
        required_agents=frozenset(
            {"analysis_agent", "report_agent"}
        ),
        required_successful_tasks=frozenset(
            {"analysis", "report"}
        ),
        required_dependencies=frozenset(
            {("report", "analysis")}
        ),
        required_output_fields=frozenset(
            {
                ("analysis", "findings"),
                ("report", "title"),
            }
        ),
    )


def make_sample(
    case: OrchestrationEvaluationCase | None = None,
    *,
    plan: OrchestrationPlan | None = None,
    result: OrchestrationResult | None = None,
) -> OrchestrationEvaluationSample:
    """Create a complete evaluation sample."""
    return OrchestrationEvaluationSample(
        case=make_case() if case is None else case,
        plan=make_plan() if plan is None else plan,
        result=make_result() if result is None else result,
    )


def test_evaluator_accepts_a_valid_multi_agent_workflow() -> None:
    result = evaluate_orchestration(
        make_case(),
        make_plan(),
        make_result(),
    )

    assert result.passed
    assert result.score == 1.0
    assert result.failures == ()
    assert all(result.checks.values())


def test_evaluator_detects_goal_mismatch() -> None:
    case = replace(
        make_case(),
        goal="Different workflow goal",
    )

    result = evaluate_orchestration(
        case,
        make_plan(),
        make_result(),
    )

    assert not result.passed
    assert not result.checks["goal_matches"]


def test_evaluator_detects_missing_task_results() -> None:
    result = evaluate_orchestration(
        make_case(),
        make_plan(),
        make_result(
            [
                make_successful_task(
                    "analysis",
                    "analysis_agent",
                )
            ],
            status="failed",
        ),
    )

    assert not result.passed
    assert not result.checks["all_planned_tasks_have_results"]


def test_evaluator_detects_unplanned_task_results() -> None:
    tasks = [
        make_successful_task(
            "analysis",
            "analysis_agent",
        ),
        make_successful_task(
            "report",
            "report_agent",
        ),
        make_successful_task(
            "unexpected",
            "report_agent",
        ),
    ]

    result = evaluate_orchestration(
        make_case(),
        make_plan(),
        make_result(tasks, status="failed"),
    )

    assert not result.passed
    assert not result.checks["no_unplanned_task_results"]


def test_evaluator_detects_duplicate_result_task_keys() -> None:
    analysis = make_successful_task(
        "analysis",
        "analysis_agent",
    )

    result = evaluate_orchestration(
        make_case(),
        make_plan(),
        make_result(
            [
                analysis,
                analysis,
                make_successful_task(
                    "report",
                    "report_agent",
                ),
            ],
            status="failed",
        ),
    )

    assert not result.passed
    assert not result.checks["result_task_keys_are_unique"]


def test_evaluator_detects_agent_assignment_mismatch() -> None:
    tasks = [
        make_successful_task(
            "analysis",
            "report_agent",
        ),
        make_successful_task(
            "report",
            "report_agent",
        ),
    ]

    result = evaluate_orchestration(
        make_case(),
        make_plan(),
        make_result(tasks),
    )

    assert not result.passed
    assert not result.checks["task_agent_assignments_match"]


def test_evaluator_detects_missing_required_success() -> None:
    failed_task = OrchestrationTaskResult(
        key="analysis",
        agent_name="analysis_agent",
        status="failed",
        error_type="TestFailure",
        error_message="Analysis failed.",
    )

    result = evaluate_orchestration(
        make_case(),
        make_plan(),
        make_result(
            [
                failed_task,
                make_successful_task(
                    "report",
                    "report_agent",
                ),
            ],
            status="failed",
        ),
    )

    assert not result.passed
    assert not result.checks["required_tasks_succeeded"]


def test_evaluator_detects_dependency_execution_violation() -> None:
    failed_analysis = OrchestrationTaskResult(
        key="analysis",
        agent_name="analysis_agent",
        status="failed",
        error_type="TestFailure",
        error_message="Analysis failed.",
    )

    result = evaluate_orchestration(
        make_case(),
        make_plan(),
        make_result(
            [
                failed_analysis,
                make_successful_task(
                    "report",
                    "report_agent",
                ),
            ],
            status="failed",
        ),
    )

    assert not result.passed
    assert not result.checks["dependencies_respected"]


def test_evaluator_detects_missing_output_fields() -> None:
    result = evaluate_orchestration(
        make_case(),
        make_plan(),
        make_result(
            [
                make_successful_task(
                    "analysis",
                    "analysis_agent",
                    {"summary": "Analysis completed."},
                ),
                make_successful_task(
                    "report",
                    "report_agent",
                    {"title": "Customer Feedback Report"},
                ),
            ]
        ),
    )

    assert not result.passed
    assert not result.checks["required_output_fields_are_present"]


def test_evaluator_detects_forbidden_output_fields() -> None:
    case = replace(
        make_case(),
        forbidden_output_fields=frozenset(
            {("analysis", "internal_secret")}
        ),
    )

    result = evaluate_orchestration(
        case,
        make_plan(),
        make_result(
            [
                make_successful_task(
                    "analysis",
                    "analysis_agent",
                    {
                        "findings": ["Delivery delays"],
                        "internal_secret": "hidden",
                    },
                ),
                make_successful_task(
                    "report",
                    "report_agent",
                    {"title": "Customer Feedback Report"},
                ),
            ]
        ),
    )

    assert not result.passed
    assert not result.checks["forbidden_output_fields_are_absent"]


def test_evaluator_checks_required_output_phrases() -> None:
    case = replace(
        make_case(),
        required_output_phrases=frozenset(
            {("analysis", "delivery delays")}
        ),
    )

    result = evaluate_orchestration(
        case,
        make_plan(),
        make_result(),
    )

    assert result.passed
    assert result.checks["required_output_phrases_are_present"]


def test_evaluator_detects_forbidden_output_phrases() -> None:
    case = replace(
        make_case(),
        forbidden_output_phrases=frozenset(
            {("analysis", "guaranteed outcome")}
        ),
    )

    workflow_result = make_result(
        [
            make_successful_task(
                "analysis",
                "analysis_agent",
                {
                    "findings": ["A guaranteed outcome is expected."],
                },
            ),
            make_successful_task(
                "report",
                "report_agent",
                {"title": "Customer Feedback Report"},
            ),
        ]
    )

    result = evaluate_orchestration(
        case,
        make_plan(),
        workflow_result,
    )

    assert not result.passed
    assert not result.checks["forbidden_output_phrases_are_absent"]


def test_evaluator_checks_expected_output_values() -> None:
    case = replace(
        make_case(),
        expected_output_values=frozenset(
            {
                (
                    "report",
                    "title",
                    "Customer Feedback Report",
                )
            }
        ),
    )

    result = evaluate_orchestration(
        case,
        make_plan(),
        make_result(),
    )

    assert result.passed
    assert result.checks["expected_output_values_match"]


def test_evaluator_detects_incorrect_expected_output_value() -> None:
    case = replace(
        make_case(),
        expected_output_values=frozenset(
            {
                (
                    "report",
                    "title",
                    "Incorrect Report",
                )
            }
        ),
    )

    result = evaluate_orchestration(
        case,
        make_plan(),
        make_result(),
    )

    assert not result.passed
    assert not result.checks["expected_output_values_match"]


def test_evaluator_detects_inconsistent_agent_results() -> None:
    inconsistent_task = OrchestrationTaskResult(
        key="analysis",
        agent_name="analysis_agent",
        status="succeeded",
        result=AgentResult(
            agent_name="report_agent",
            status="succeeded",
            summary="Incorrect agent identity.",
            output={},
        ),
    )

    result = evaluate_orchestration(
        make_case(),
        make_plan(),
        make_result(
            [
                inconsistent_task,
                make_successful_task(
                    "report",
                    "report_agent",
                ),
            ]
        ),
    )

    assert not result.passed
    assert not result.checks["agent_results_are_consistent"]


def test_evaluator_detects_inconsistent_workflow_status() -> None:
    result = evaluate_orchestration(
        make_case(),
        make_plan(),
        make_result(status="failed"),
    )

    assert not result.passed
    assert not result.checks["workflow_status_is_consistent"]


def test_evaluator_score_matches_passed_checks() -> None:
    result = evaluate_orchestration(
        make_case(),
        make_plan(),
        make_result(),
    )

    expected_score = (
        sum(result.checks.values()) / len(result.checks)
    )

    assert result.score == expected_score


def test_benchmark_aggregates_multiple_workflows() -> None:
    first = make_sample()

    second_case = replace(
        make_case(),
        name="different-goal-case",
        goal="Different goal",
    )

    second = make_sample(case=second_case)

    benchmark = evaluate_orchestration_benchmark(
        [first, second]
    )

    assert benchmark.total_cases == 2
    assert benchmark.passed_cases == 1
    assert benchmark.pass_rate == 0.5
    assert 0.0 < benchmark.average_score < 1.0
    assert benchmark.check_pass_rates["goal_matches"] == 0.5


def test_benchmark_rejects_empty_cases() -> None:
    with pytest.raises(ValueError, match="at least one case"):
        evaluate_orchestration_benchmark([])


def test_benchmark_rejects_duplicate_case_names() -> None:
    sample = make_sample()

    with pytest.raises(ValueError, match="unique"):
        evaluate_orchestration_benchmark(
            [sample, sample]
        )


def test_evaluation_report_is_json_serializable() -> None:
    benchmark = evaluate_orchestration_benchmark(
        [make_sample()]
    )

    report = build_orchestration_evaluation_report(
        benchmark
    )

    data = json.loads(report.to_json())

    assert data["summary"]["total_cases"] == 1
    assert data["summary"]["passed_cases"] == 1
    assert data["summary"]["failed_cases"] == 0
    assert data["summary"]["pass_rate"] == 1.0
    assert len(data["cases"]) == 1


def test_evaluation_report_exposes_failed_case_details() -> None:
    case = replace(
        make_case(),
        goal="Incorrect goal",
    )

    benchmark = evaluate_orchestration_benchmark(
        [make_sample(case=case)]
    )

    report = build_orchestration_evaluation_report(
        benchmark
    )

    data = report.to_dict()

    assert data["summary"]["failed_cases"] == 1
    assert data["cases"][0]["passed"] is False
    assert "goal_matches" in data["cases"][0]["failures"]