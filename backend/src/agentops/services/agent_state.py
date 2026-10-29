"""Persistent storage for multi-agent execution state."""

from collections.abc import Callable
from uuid import UUID

from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from agentops.db.models.enums import EventLevel
from agentops.db.models.workflow import ExecutionEvent, WorkflowRun
from agentops.schemas.orchestration import OrchestrationTaskResult

SessionFactory = Callable[[], Session]

_EVENT_TYPES = (
    "agent.task.succeeded",
    "agent.task.failed",
    "agent.task.skipped",
)


class AgentStateStoreError(RuntimeError):
    """Raised when agent state cannot be safely persisted or loaded."""


class AgentStateStore:
    """Persist and retrieve agent-task results using workflow execution events."""

    def __init__(
        self,
        session_factory: SessionFactory,
        workflow_id: UUID,
    ) -> None:
        self._session_factory = session_factory
        self.workflow_id = workflow_id

    def save_task_result(
        self,
        task_result: OrchestrationTaskResult,
    ) -> None:
        """Persist one agent-task outcome as an append-only workflow event."""
        event_type = f"agent.task.{task_result.status}"

        if task_result.status == "failed":
            level = EventLevel.ERROR.value
        elif task_result.status == "skipped":
            level = EventLevel.WARNING.value
        else:
            level = EventLevel.INFO.value

        data = {
            "task_key": task_result.key,
            "agent_name": task_result.agent_name,
            "status": task_result.status,
            "task_result": task_result.model_dump(mode="json"),
        }

        try:
            with self._session_factory() as session:
                if session.get(WorkflowRun, self.workflow_id) is None:
                    raise AgentStateStoreError(
                        "Cannot persist agent state for an unknown workflow."
                    )

                session.add(
                    ExecutionEvent(
                        workflow_run_id=self.workflow_id,
                        task_run_id=None,
                        event_type=event_type,
                        level=level,
                        message=(
                            f"Agent task '{task_result.key}' finished "
                            f"with status '{task_result.status}'."
                        ),
                        data=data,
                    )
                )

                try:
                    # Each outcome is committed independently so completed
                    # results can survive a later process failure.
                    session.commit()
                except Exception:
                    session.rollback()
                    raise

        except AgentStateStoreError:
            raise
        except Exception as exc:
            raise AgentStateStoreError("Could not persist the agent-task outcome.") from exc

    def load_task_results(
        self,
    ) -> dict[str, OrchestrationTaskResult]:
        """Load the latest recorded outcome for each task in this workflow."""
        try:
            with self._session_factory() as session:
                if session.get(WorkflowRun, self.workflow_id) is None:
                    raise AgentStateStoreError("Cannot load agent state for an unknown workflow.")

                events = list(
                    session.scalars(
                        select(ExecutionEvent)
                        .where(
                            ExecutionEvent.workflow_run_id == self.workflow_id,
                            ExecutionEvent.event_type.in_(_EVENT_TYPES),
                        )
                        .order_by(ExecutionEvent.id)
                    ).all()
                )

        except AgentStateStoreError:
            raise
        except Exception as exc:
            raise AgentStateStoreError("Could not load persisted agent state.") from exc

        latest: dict[str, OrchestrationTaskResult] = {}

        for event in events:
            data = event.data

            if not isinstance(data, dict):
                raise AgentStateStoreError("Stored agent state has an invalid data format.")

            raw_result = data.get("task_result")

            if not isinstance(raw_result, dict):
                raise AgentStateStoreError("Stored agent state is missing its task result.")

            try:
                result = OrchestrationTaskResult.model_validate(raw_result)
            except ValidationError as exc:
                raise AgentStateStoreError(
                    "Stored agent state does not match the current schema."
                ) from exc

            latest[result.key] = result

        return latest
