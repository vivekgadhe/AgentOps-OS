"""Tests for bounded agent payloads."""

import pytest
from pydantic import ValidationError

from agentops.schemas.agents import AgentContext, AgentResult
from agentops.schemas.payload_limits import (
    MAX_AGENT_OUTPUT_BYTES,
    MAX_CONTEXT_METADATA_BYTES,
    MAX_CONTEXT_PRIOR_RESULTS_BYTES,
)


def make_context(
    *,
    prior_results: dict | None = None,
    metadata: dict | None = None,
) -> AgentContext:
    """Build a context for payload-validation tests."""
    return AgentContext(
        goal="Analyze customer feedback",
        actor_role="operator",
        prior_results={} if prior_results is None else prior_results,
        metadata={} if metadata is None else metadata,
    )


def test_context_accepts_small_payloads() -> None:
    context = make_context(
        prior_results={
            "analysis": {
                "summary": "Analysis completed.",
                "output": {"count": 3},
            }
        },
        metadata={"task_key": "analysis"},
    )

    assert context.prior_results["analysis"]["output"]["count"] == 3


def test_context_rejects_oversized_prior_results() -> None:
    with pytest.raises(ValidationError, match="maximum allowed size"):
        make_context(
            prior_results={
                "analysis": {
                    "content": "x" * (MAX_CONTEXT_PRIOR_RESULTS_BYTES + 1)
                }
            }
        )


def test_context_rejects_oversized_metadata() -> None:
    with pytest.raises(ValidationError, match="maximum allowed size"):
        make_context(
            metadata={
                "description": "x" * (MAX_CONTEXT_METADATA_BYTES + 1)
            }
        )


def test_context_rejects_excessive_nesting() -> None:
    payload: dict = {}
    current = payload

    for _ in range(14):
        child: dict = {}
        current["child"] = child
        current = child

    with pytest.raises(ValidationError, match="nesting depth"):
        make_context(metadata=payload)


def test_context_rejects_too_many_payload_values() -> None:
    with pytest.raises(ValidationError, match="too many values"):
        make_context(metadata={"items": list(range(10_001))})


def test_agent_result_rejects_oversized_output() -> None:
    with pytest.raises(ValidationError, match="maximum allowed size"):
        AgentResult(
            agent_name="analysis_agent",
            status="succeeded",
            summary="Analysis completed.",
            output={
                "content": "x" * (MAX_AGENT_OUTPUT_BYTES + 1)
            },
        )


def test_agent_result_accepts_small_output() -> None:
    result = AgentResult(
        agent_name="analysis_agent",
        status="succeeded",
        summary="Analysis completed.",
        output={"findings": ["Finding one", "Finding two"]},
    )

    assert result.output["findings"] == ["Finding one", "Finding two"]


def test_context_rejects_non_json_payload_values() -> None:
    with pytest.raises(ValidationError, match="JSON-compatible"):
        make_context(metadata={"unexpected": object()})