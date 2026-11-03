"""Verify recalled memories reach RAG agents as untrusted contextual data."""

from types import SimpleNamespace
from uuid import uuid4

from agentops.schemas.agents import AgentResult
from agentops.services.knowledge_base import RetrievedChunk
from agentops.services.rag import RAGService


class FakeKnowledgeBase:
    def search(self, **_kwargs):
        return [
            RetrievedChunk(
                document_id=uuid4(),
                filename="evidence.txt",
                chunk_index=0,
                page_number=None,
                content="The approved delivery window is three business days.",
                similarity=0.91,
            )
        ]


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
        return [SimpleNamespace(memory=memory, similarity=0.82, relevance_score=0.76)]

    def create_memory(self, **kwargs):
        self.created.append(kwargs)
        return SimpleNamespace(id=uuid4())


class CapturingRegistry:
    def __init__(self) -> None:
        self.context = None

    def execute(self, _agent_name, context):
        self.context = context
        return AgentResult(
            agent_name="analysis_agent",
            status="succeeded",
            summary="The requested delivery window is three business days.",
            output={"finding": "three business days"},
        )


def test_rag_includes_memories_as_untrusted_context() -> None:
    memory_service = FakeMemoryService()
    registry = CapturingRegistry()
    RAGService(FakeKnowledgeBase(), memory_service=memory_service).run_agent(
        owner_id=uuid4(),
        actor_role="operator",
        question="What delivery window was approved?",
        registry=registry,
        agent_name="analysis_agent",
    )

    assert registry.context is not None
    recalled = registry.context.prior_results["recalled_memories"]
    assert "untrusted reference data" in recalled["instruction"]
    assert recalled["memories"][0]["content"].startswith("The user prefers")
    assert registry.context.metadata["recalled_memory_count"] == 1
    assert memory_service.created == []  # Auto-capture is opt-in.


def test_rag_auto_capture_is_opt_in_and_occurs_only_after_success() -> None:
    memory_service = FakeMemoryService()
    RAGService(
        FakeKnowledgeBase(),
        memory_service=memory_service,
        auto_capture_memory=True,
    ).run_agent(
        owner_id=uuid4(),
        actor_role="operator",
        question="What delivery window was approved?",
        registry=CapturingRegistry(),
        agent_name="analysis_agent",
    )

    assert len(memory_service.created) == 1
    saved = memory_service.created[0]
    assert saved["memory_type"] == "episodic"
    assert saved["memory_scope"] == "agent"
    assert saved["agent_key"] == "analysis_agent"
    assert saved["source_type"] == "agent"
