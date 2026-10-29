"""Orchestrate specialized agents using validated dependency graphs."""

from collections.abc import Sequence
from typing import Any

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


class AgentOrchestrationError(RuntimeError):
    """Raised when an orchestration cannot be safely prepared."""


class AgentOrchestrator:
    """Coordinate registered agents without bypassing registry authorization."""

    def __init__(self, registry: AgentRegistry) -> None:
        self._registry = registry

    def run(
        self,
        plan: OrchestrationPlan,
        *,
        actor_role: str,
    ) -> OrchestrationResult:
        """Execute an orchestration plan in dependency order."""
        # Preflight all agents before starting work. An authorization failure
        # must not occur after earlier tasks have already executed.
        for task in plan.tasks:
            try:
                self._registry.authorize(task.agent_name, actor_role)
            except (AgentAccessDeniedError, AgentNotFoundError) as exc:
                raise AgentOrchestrationError(
                    f"Task '{task.key}' cannot use agent '{task.agent_name}'."
                ) from exc

        ordered_tasks = self._topological_order(plan.tasks)
        tasks_by_key = {task.key: task for task in plan.tasks}
        dependencies_by_key = {task.key: task.depends_on for task in plan.tasks}

        outcomes: dict[str, OrchestrationTaskResult] = {}
        successful_results: dict[str, AgentResult] = {}

        for task in ordered_tasks:
            blocked_by = [
                dependency
                for dependency in task.depends_on
                if outcomes[dependency].status != "succeeded"
            ]

            if blocked_by:
                outcomes[task.key] = OrchestrationTaskResult(
                    key=task.key,
                    agent_name=task.agent_name,
                    status="skipped",
                    error_type="DependencyFailed",
                    error_message=(
                        "Task skipped because dependencies did not succeed: "
                        + ", ".join(blocked_by)
                    ),
                )
                continue

            prior_results = self._collect_ancestor_results(
                task.key,
                dependencies_by_key,
                tasks_by_key,
                successful_results,
                ordered_tasks,
            )

            context = AgentContext(
                goal=task.goal or plan.goal,
                actor_role=actor_role,
                prior_results=prior_results,
                metadata={
                    "task_key": task.key,
                    "agent_name": task.agent_name,
                    "depends_on": task.depends_on,
                },
            )

            try:
                agent_result = self._registry.execute(task.agent_name, context)
            except Exception as exc:
                # Record the task failure and allow independent branches to
                # proceed. Dependents are skipped by the dependency check.
                message = str(exc).strip() or "Agent execution failed."

                outcomes[task.key] = OrchestrationTaskResult(
                    key=task.key,
                    agent_name=task.agent_name,
                    status="failed",
                    error_type=type(exc).__name__,
                    error_message=message[:1000],
                )
                continue

            outcomes[task.key] = OrchestrationTaskResult(
                key=task.key,
                agent_name=task.agent_name,
                status=agent_result.status,
                result=agent_result,
                error_type=agent_result.error_type,
                error_message=agent_result.error_message,
            )

            if agent_result.status == "succeeded":
                successful_results[task.key] = agent_result

        task_results = [outcomes[task.key] for task in ordered_tasks]
        workflow_succeeded = all(task.status == "succeeded" for task in task_results)

        return OrchestrationResult(
            goal=plan.goal,
            status="succeeded" if workflow_succeeded else "failed",
            tasks=task_results,
        )

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
        tasks_by_key: dict[str, OrchestrationTask],
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
