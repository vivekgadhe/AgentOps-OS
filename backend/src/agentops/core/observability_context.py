"""Context-local attribution metadata for observability instrumentation."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class ObservabilityContext:
    component: str = "llm"
    agent_name: str | None = None
    workflow_run_id: UUID | None = None


observability_context_var: ContextVar[ObservabilityContext | None] = ContextVar(
    "observability_context",
    default=None,
)


def current_observability_context() -> ObservabilityContext:
    """Return the active attribution context or the default LLM context."""
    return observability_context_var.get() or ObservabilityContext()


@contextmanager
def observability_scope(
    *,
    component: str,
    agent_name: str | None = None,
    workflow_run_id: UUID | None = None,
) -> Iterator[None]:
    """Set attribution for nested provider calls and reliably restore prior context."""
    if component not in {"llm", "planner", "agent", "rag"}:
        raise ValueError("Unsupported observability component.")
    parent = current_observability_context()
    token = observability_context_var.set(
        ObservabilityContext(
            component=component,
            agent_name=agent_name if agent_name is not None else parent.agent_name,
            workflow_run_id=(
                workflow_run_id if workflow_run_id is not None else parent.workflow_run_id
            ),
        )
    )
    try:
        yield
    finally:
        observability_context_var.reset(token)
