"""Best-effort persistence for privacy-conscious provider telemetry."""

from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from agentops.core.context import request_id_var
from agentops.core.observability_context import current_observability_context
from agentops.db.models.telemetry import TelemetryEvent

logger = logging.getLogger(__name__)


class TelemetryRecorder:
    """Persist only operational metadata, using an independent short-lived session.

    Recording is deliberately best-effort: a telemetry outage must never fail an
    LLM request or roll back the business transaction using the provider manager.
    Prompt text, instructions, credentials, response bodies and user content are
    not accepted by this API and are never persisted.
    """

    def __init__(self, engine: Engine, owner_user_id: UUID) -> None:
        self._engine = engine
        self._owner_user_id = owner_user_id

    def record_llm_attempt(
        self,
        *,
        provider: str,
        model: str,
        outcome: str,
        duration_ms: float,
        error_type: str | None = None,
        attempt_number: int,
        used_fallback: bool,
        output_schema: str,
    ) -> None:
        """Store a generation attempt without retaining prompts or outputs."""
        try:
            context = current_observability_context()
            safe_attributes: dict[str, Any] = {
                "attempt_number": max(1, int(attempt_number)),
                "used_fallback": bool(used_fallback),
                "output_schema": output_schema[:120],
            }
            event = TelemetryEvent(
                owner_user_id=self._owner_user_id,
                workflow_run_id=context.workflow_run_id,
                request_id=request_id_var.get(),
                event_type="llm_attempt",
                component=context.component,
                agent_name=context.agent_name,
                provider=provider[:32],
                model=model[:120],
                outcome=outcome,
                duration_ms=max(0.0, float(duration_ms)),
                error_type=error_type[:100] if error_type else None,
                attributes=safe_attributes,
            )
            with Session(self._engine) as session:
                session.add(event)
                session.commit()
        except Exception as exc:  # telemetry must not interfere with generation
            logger.warning(
                "telemetry_persist_failed",
                extra={"error_type": type(exc).__name__},
            )
