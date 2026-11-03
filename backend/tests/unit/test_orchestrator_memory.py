"""Persistent-memory integration at the multi-agent orchestration boundary."""

from types import SimpleNamespace
from uuid import uuid4

import pytest

from agentops.services.orchestrator import AgentOrchestrationError, AgentOrchestrator
from tests.unit.test_orchestrator import FakeAgent, make_plan, make_registry, task


class FakeMemoryService:
    def __init__(self) -> None:
        self.created: list[dict] = []

    def search_memories(self, **_kwargs):
        memory = SimpleNamespace(
            id=uuid4(),
            memory_type="semantic",
            memory_scope="user",
            content="The user prefers concise operational summaries.",
        )
        return [SimpleNamespace(memory=memory, similarity=0.85, relevance_score=0.8)]

    def create_memory(self, **kwargs):
        self.created.append(kwargs)
        return SimpleNamespace(id=uuid4())


def test_orchestrator_requires_trusted_owner_when_memory_is_enabled() -> None:
    agent = FakeAgent("analysis_agent")
    orchestrator = AgentOrchestrator(make_registry(agent), memory_service=FakeMemoryService())
    with pytest.raises(AgentOrchestrationError, match="authenticated memory owner"):
        orchestrator.run(
            make_plan([task("analysis", "analysis_agent")]),
            actor_role="operator",
        )


def test_orchestrator_supplies_matching_memories_to_agent() -> None:
    agent = FakeAgent("analysis_agent")
    orchestrator = AgentOrchestrator(
        make_registry(agent),
        memory_service=FakeMemoryService(),
    )
    orchestrator.run(
        make_plan([task("analysis", "analysis_agent")]),
        actor_role="operator",
        owner_user_id=uuid4(),
    )

    recalled = agent.calls[0].prior_results["recalled_memories"]
    assert "untrusted reference data" in recalled["instruction"]
    assert recalled["memories"][0]["content"].startswith("The user prefers")
    assert agent.calls[0].metadata["recalled_memory_count"] == 1


def test_orchestrator_auto_capture_is_opt_in() -> None:
    agent = FakeAgent("analysis_agent")
    memory_service = FakeMemoryService()
    AgentOrchestrator(
        make_registry(agent),
        memory_service=memory_service,
    ).run(
        make_plan([task("analysis", "analysis_agent")]),
        actor_role="operator",
        owner_user_id=uuid4(),
    )
    assert memory_service.created == []


def test_orchestrator_can_capture_successful_task_as_episode() -> None:
    agent = FakeAgent("analysis_agent")
    memory_service = FakeMemoryService()
    AgentOrchestrator(
        make_registry(agent),
        memory_service=memory_service,
        auto_capture_memory=True,
    ).run(
        make_plan([task("analysis", "analysis_agent")]),
        actor_role="operator",
        owner_user_id=uuid4(),
    )

    assert len(memory_service.created) == 1
    saved = memory_service.created[0]
    assert saved["memory_type"] == "episodic"
    assert saved["memory_scope"] == "agent"
    assert saved["agent_key"] == "analysis_agent"
    assert saved["source_type"] == "agent"
