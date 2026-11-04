"""Unit tests for best-effort telemetry persistence and attribution."""

from __future__ import annotations

from uuid import uuid4

import pytest
from sqlalchemy import create_engine

from agentops.core.context import request_id_var
from agentops.core.observability_context import (
    current_observability_context,
    observability_scope,
)
from agentops.db.models.telemetry import TelemetryEvent
from agentops.services import telemetry as telemetry_module
from agentops.services.telemetry import TelemetryRecorder


class _SessionStub:
    def __init__(self, _bind: object, *, fail_commit: bool = False) -> None:
        self.events: list[TelemetryEvent] = []
        self.fail_commit = fail_commit

    def __enter__(self) -> _SessionStub:
        return self

    def __exit__(self, *_: object) -> None:
        return None

    def add(self, event: TelemetryEvent) -> None:
        self.events.append(event)

    def commit(self) -> None:
        if self.fail_commit:
            raise RuntimeError("simulated database outage")


def test_recorder_persists_only_safe_operational_attributes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    engine = create_engine("sqlite://")
    owner_id = uuid4()
    sessions: list[_SessionStub] = []

    def session_factory(bind: object) -> _SessionStub:
        session = _SessionStub(bind)
        sessions.append(session)
        return session

    monkeypatch.setattr(telemetry_module, "Session", session_factory)
    request_token = request_id_var.set("request-12345678")
    try:
        with observability_scope(
            component="agent",
            agent_name="analysis_agent",
            workflow_run_id=uuid4(),
        ):
            recorder = TelemetryRecorder(engine, owner_id)
            recorder.record_llm_attempt(
                provider="ollama",
                model="local-model",
                outcome="success",
                duration_ms=12.5,
                attempt_number=2,
                used_fallback=True,
                output_schema="AnalysisOutput",
            )
    finally:
        request_id_var.reset(request_token)
        engine.dispose()

    event = sessions[0].events[0]
    assert event.owner_user_id == owner_id
    assert event.component == "agent"
    assert event.agent_name == "analysis_agent"
    assert event.request_id == "request-12345678"
    assert event.attributes == {
        "attempt_number": 2,
        "used_fallback": True,
        "output_schema": "AnalysisOutput",
    }
    assert "prompt" not in str(event.attributes).lower()


def test_recorder_swallows_telemetry_database_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    engine = create_engine("sqlite://")

    class FailingSession(_SessionStub):
        def __init__(self, bind: object) -> None:
            super().__init__(bind, fail_commit=True)

    monkeypatch.setattr(telemetry_module, "Session", FailingSession)
    try:
        TelemetryRecorder(engine, uuid4()).record_llm_attempt(
            provider="ollama",
            model="local-model",
            outcome="failure",
            duration_ms=1,
            error_type="ProviderUnavailableError",
            attempt_number=1,
            used_fallback=False,
            output_schema="ExampleOutput",
        )
    finally:
        engine.dispose()


def test_default_observability_context_is_generic_llm() -> None:
    context = current_observability_context()
    assert context.component == "llm"
    assert context.agent_name is None
    assert context.workflow_run_id is None


def test_observability_scope_restores_parent_context() -> None:
    with observability_scope(component="planner"):
        with observability_scope(component="agent", agent_name="report_agent"):
            context = current_observability_context()
            assert context.component == "agent"
            assert context.agent_name == "report_agent"
        context = current_observability_context()
        assert context.component == "planner"
        assert context.agent_name is None


def test_nested_scopes_preserve_agent_and_workflow_attribution() -> None:
    workflow_id = uuid4()
    with observability_scope(
        component="agent",
        agent_name="planning_agent",
        workflow_run_id=workflow_id,
    ):
        with observability_scope(component="planner"):
            context = current_observability_context()
            assert context.component == "planner"
            assert context.agent_name == "planning_agent"
            assert context.workflow_run_id == workflow_id
