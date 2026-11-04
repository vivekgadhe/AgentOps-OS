"""Database integration tests for Phase 10 telemetry storage and constraints."""

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from agentops.db.models.telemetry import TelemetryEvent
from tests.integration.db.factories import Factory

pytestmark = pytest.mark.integration


def test_telemetry_event_is_persisted_and_owner_scoped(
    orm_session,
    factory: Factory,
) -> None:
    owner = factory.user()
    other_user = factory.user()
    workflow = factory.workflow(created_by=owner)
    event = TelemetryEvent(
        owner_user_id=owner.id,
        workflow_run_id=workflow.id,
        request_id="request-12345678",
        component="agent",
        agent_name="analysis_agent",
        provider="ollama",
        model="local-model",
        outcome="success",
        duration_ms=42.5,
        attributes={"attempt_number": 1, "used_fallback": False},
    )
    orm_session.add(event)
    orm_session.flush()

    owner_events = list(
        orm_session.scalars(
            select(TelemetryEvent).where(TelemetryEvent.owner_user_id == owner.id)
        ).all()
    )
    other_events = list(
        orm_session.scalars(
            select(TelemetryEvent).where(TelemetryEvent.owner_user_id == other_user.id)
        ).all()
    )

    assert len(owner_events) == 1
    assert owner_events[0].workflow_run_id == workflow.id
    assert owner_events[0].duration_ms == 42.5
    assert other_events == []


def test_telemetry_rejects_invalid_outcome(orm_session, factory: Factory) -> None:
    owner = factory.user()
    event = TelemetryEvent(
        owner_user_id=owner.id,
        provider="ollama",
        model="local-model",
        outcome="unknown",
        duration_ms=1,
    )
    with pytest.raises(IntegrityError, match="ck_telemetry_events_outcome_valid"):
        with orm_session.begin_nested():
            orm_session.add(event)
            orm_session.flush()
