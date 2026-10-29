"""Orchestrate specialized agents using validated dependency graphs."""

import logging
from collections.abc import Sequence
from typing import Any, Protocol
from uuid import UUID

from agentops.schemas.agents import AgentContext, AgentResult
from agentops.schemas.orchestration import (
    OrchestrationPlan,
    OrchestrationResult,
    OrchestrationTask,
    OrchestrationTaskResult,
)
from agentops.services.agent_registry import (
    AgentAccessDeniedError,
    AgentNotFoundError,
    AgentRegistry,
)

logger = logging.getLogger(__name__)


class AgentOrchestrationError(RuntimeError):
    """Raised when an orchestration cannot be safely prepared."""


class RetryableAgentExecutionError(RuntimeError):
    """An explicitly retryable agent execution failure."""


class AgentExecutionBudgetExceeded(RuntimeError):
    """Raised when an orchestration exceeds its execution-attempt budget."""


class AgentContextBudgetExceeded(RuntimeError):
    """Raised when cumulative agent context exceeds its size budget."""


class AgentStateWriter(Protocol):
    """Interface for optional persistent agent-state storage."""

    workflow_id: UUID

    def save_task_result(
        self,
        task_result: OrchestrationTaskResult,
    ) -> None:
        """Persist an agent-task outcome."""
        ...


class _RunExecutionBudget:
    """Track cumulative agent attempts and context bytes for one run."""

    def __init__(
        self,
        max_total_attempts: int,
        max_total_context_bytes: int,
    ) -> None:
        self.max_total_attempts = max_total_attempts
        self.max_total_context_bytes = max_total_context_bytes
        self.attempts_used = 0
        self.context_bytes_used = 0

    @property
    def attempts_remaining(self) -> int:
        """Return the number of agent attempts remaining."""
        return self.max_total_attempts - self.attempts_used

    def consume_attempt(self, context_bytes: int) -> None:
        """Reserve one attempt and its serialized context size."""
        if self.attempts_used >= self.max_total_attempts:
            raise AgentExecutionBudgetExceeded(
                "The orchestration execution-attempt budget was exceeded."
            )

        if self.context_bytes_used + context_bytes > self.max_total_context_bytes:
            raise AgentContextBudgetExceeded("The orchestration context budget was exceeded.")

        self.attempts_used += 1
        self.context_bytes_used += context_bytes


class AgentOrchestrator:
    """Coordinate registered agents and optionally persist task outcomes."""

    def __init__(
        self,
        registry: AgentRegistry,
        state_store: AgentStateWriter | None = None,
        *,
        max_attempts: int = 1,
        max_total_attempts: int = 100,
        max_total_context_bytes: int = 10 * 1024 * 1024,
    ) -> None:
        """Initialize orchestration with bounded retry and execution policies."""
        if (
            isinstance(max_attempts, bool)
            or not isinstance(max_attempts, int)
            or not 1 <= max_attempts <= 3
        ):
            raise ValueError("max_attempts must be between 1 and 3.")

        if (
            isinstance(max_total_attempts, bool)
            or not isinstance(max_total_attempts, int)
            or not 1 <= max_total_attempts <= 300
        ):
            raise ValueError("max_total_attempts must be between 1 and 300.")

        if (
            isinstance(max_total_context_bytes, bool)
            or not isinstance(max_total_context_bytes, int)
            or not 1 <= max_total_context_bytes <= 100 * 1024 * 1024
        ):
            raise ValueError("max_total_context_bytes must be between 1 byte and 100 MiB.")

        self._registry = registry
        self._state_store = state_store
        self._max_attempts = max_attempts
        self._max_total_attempts = max_total_attempts
        self._max_total_context_bytes = max_total_context_bytes

    def _execute_with_retries(
        self,
        agent_name: str,
        context: AgentContext,
        execution_budget: _RunExecutionBudget,
    ) -> AgentResult:
        """Retry explicitly retryable failures within the run budget."""
        context_bytes = len(context.model_dump_json().encode("utf-8"))

        for attempt in range(self._max_attempts):
            execution_budget.consume_attempt(context_bytes)

            try:
                return self._registry.execute(agent_name, context)
            except RetryableAgentExecutionError:
                if attempt + 1 == self._max_attempts:
                    raise

        raise AgentOrchestrationError("Agent execution attempts were exhausted.")

    def run(
        self,
        plan: OrchestrationPlan,
        *,
        actor_role: str,
    ) -> OrchestrationResult:
        """Execute an orchestration plan in dependency order."""
        # Authorize every requested agent before starting any work.
        for task in plan.tasks:
            try:
                self._registry.authorize(task.agent_name, actor_role)
            except (AgentAccessDeniedError, AgentNotFoundError) as exc:
                raise AgentOrchestrationError(
                    f"Task '{task.key}' cannot use agent '{task.agent_name}'."
                ) from exc

        ordered_tasks = self._topological_order(plan.tasks)
        dependencies_by_key = {task.key: task.depends_on for task in plan.tasks}

        execution_budget = _RunExecutionBudget(
            max_total_attempts=self._max_total_attempts,
            max_total_context_bytes=self._max_total_context_bytes,
        )

        outcomes: dict[str, OrchestrationTaskResult] = {}
        successful_results: dict[str, AgentResult] = {}

        for task in ordered_tasks:
            blocked_by = [
                dependency
                for dependency in task.depends_on
                if outcomes[dependency].status != "succeeded"
            ]

            # Report dependency failures accurately before checking budgets.
            if blocked_by:
                outcome = OrchestrationTaskResult(
                    key=task.key,
                    agent_name=task.agent_name,
                    status="skipped",
                    error_type="DependencyFailed",
                    error_message=(
                        "Task skipped because dependencies did not succeed: "
                        + ", ".join(blocked_by)
                    ),
                )
                self._record_outcome(outcomes, outcome)
                continue

            # Do not start new work when all agent attempts have been consumed.
            if execution_budget.attempts_remaining == 0:
                outcome = OrchestrationTaskResult(
                    key=task.key,
                    agent_name=task.agent_name,
                    status="skipped",
                    error_type="AgentExecutionBudgetExceeded",
                    error_message=(
                        "Task skipped because the execution-attempt budget was exhausted."
                    ),
                )
                self._record_outcome(outcomes, outcome)
                continue

            prior_results = self._collect_ancestor_results(
                task.key,
                dependencies_by_key,
                successful_results,
                ordered_tasks,
            )

            context = AgentContext(
                goal=task.goal or plan.goal,
                actor_role=actor_role,
                workflow_id=(
                    self._state_store.workflow_id if self._state_store is not None else None
                ),
                prior_results=prior_results,
                metadata={
                    "task_key": task.key,
                    "agent_name": task.agent_name,
                    "depends_on": task.depends_on,
                },
            )

            try:
                agent_result = self._execute_with_retries(
                    task.agent_name,
                    context,
                    execution_budget,
                )
            except Exception as exc:
                logger.exception(
                    "Agent task execution failed: task_key=%s, agent_name=%s",
                    task.key,
                    task.agent_name,
                )

                if isinstance(exc, AgentExecutionBudgetExceeded):
                    error_message = "Orchestration execution-attempt budget was exceeded."
                elif isinstance(exc, AgentContextBudgetExceeded):
                    error_message = "Orchestration context budget was exceeded."
                else:
                    error_message = "Agent execution failed."

                outcome = OrchestrationTaskResult(
                    key=task.key,
                    agent_name=task.agent_name,
                    status="failed",
                    error_type=type(exc).__name__,
                    error_message=error_message,
                )
                self._record_outcome(outcomes, outcome)
                continue

            outcome = OrchestrationTaskResult(
                key=task.key,
                agent_name=task.agent_name,
                status=agent_result.status,
                result=agent_result,
                error_type=agent_result.error_type,
                error_message=agent_result.error_message,
            )
            self._record_outcome(outcomes, outcome)

            if agent_result.status == "succeeded":
                successful_results[task.key] = agent_result

        task_results = [outcomes[task.key] for task in ordered_tasks]
        workflow_succeeded = all(task.status == "succeeded" for task in task_results)

        return OrchestrationResult(
            goal=plan.goal,
            status="succeeded" if workflow_succeeded else "failed",
            tasks=task_results,
        )

    def _record_outcome(
        self,
        outcomes: dict[str, OrchestrationTaskResult],
        outcome: OrchestrationTaskResult,
    ) -> None:
        """Record an outcome in memory and optionally persist it."""
        if self._state_store is not None:
            try:
                self._state_store.save_task_result(outcome)
            except Exception as exc:
                raise AgentOrchestrationError(
                    f"Failed to persist the outcome for task '{outcome.key}'."
                ) from exc

        outcomes[outcome.key] = outcome

    @staticmethod
    def _topological_order(
        tasks: Sequence[OrchestrationTask],
    ) -> list[OrchestrationTask]:
        """Return tasks in deterministic prerequisite-first order."""
        tasks_by_key = {task.key: task for task in tasks}
        in_degree = {task.key: len(task.depends_on) for task in tasks}
        children: dict[str, list[str]] = {task.key: [] for task in tasks}

        for task in tasks:
            for dependency in task.depends_on:
                children[dependency].append(task.key)

        ready = [task.key for task in tasks if in_degree[task.key] == 0]
        ordered: list[OrchestrationTask] = []

        while ready:
            current = ready.pop(0)
            ordered.append(tasks_by_key[current])

            for child in children[current]:
                in_degree[child] -= 1

                if in_degree[child] == 0:
                    ready.append(child)

        if len(ordered) != len(tasks):
            raise AgentOrchestrationError(
                "Cannot execute an orchestration with cyclic dependencies."
            )

        return ordered

    @staticmethod
    def _collect_ancestor_results(
        task_key: str,
        dependencies_by_key: dict[str, list[str]],
        successful_results: dict[str, AgentResult],
        ordered_tasks: Sequence[OrchestrationTask],
    ) -> dict[str, dict[str, Any]]:
        """Pass only successful results from this task's ancestors."""
        ancestors: set[str] = set()
        pending = list(dependencies_by_key[task_key])

        while pending:
            dependency = pending.pop()

            if dependency in ancestors:
                continue

            ancestors.add(dependency)
            pending.extend(dependencies_by_key[dependency])

        return {
            task.key: {
                "agent_name": successful_results[task.key].agent_name,
                "summary": successful_results[task.key].summary,
                "output": successful_results[task.key].output,
            }
            for task in ordered_tasks
            if task.key in ancestors and task.key in successful_results
        }
