"""Unit tests for retrieval-augmented agent context construction."""

from uuid import uuid4

import pytest

from agentops.schemas.agents import AgentResult
from agentops.services.knowledge_base import RetrievedChunk
from agentops.services.rag import NoRelevantKnowledgeError, RAGService


class FakeKnowledgeBase:
    def __init__(self, sources: list[RetrievedChunk]) -> None:
        self.sources = sources
        self.kwargs: dict = {}

    def search(self, **kwargs: object) -> list[RetrievedChunk]:
        self.kwargs = dict(kwargs)
        return self.sources


class FakeRegistry:
    def __init__(self) -> None:
        self.context = None

    def execute(self, agent_name: str, context: object) -> AgentResult:
        self.context = context
        return AgentResult(
            agent_name=agent_name,
            status="succeeded",
            summary="Answer grounded in [S1].",
            output={"findings": ["Delivery delays are noted [S1]."]},
        )


def make_source() -> RetrievedChunk:
    return RetrievedChunk(
        document_id=uuid4(),
        filename="customer-feedback.pdf",
        chunk_index=0,
        page_number=2,
        content="Several customers reported delivery delays.",
        similarity=0.91,
    )


def test_rag_injects_source_metadata_into_agent_context() -> None:
    source = make_source()
    knowledge = FakeKnowledgeBase([source])
    registry = FakeRegistry()

    result = RAGService(knowledge).run_agent(
        owner_id=uuid4(),
        actor_role="operator",
        question="What problems were reported?",
        registry=registry,  # type: ignore[arg-type]
        agent_name="analysis_agent",
        top_k=4,
    )

    assert result.answer.status == "succeeded"
    assert result.sources == (source,)
    assert registry.context is not None
    context = registry.context
    assert context.prior_results["retrieved_knowledge"]["sources"][0]["source_id"] == "S1"
    assert context.prior_results["retrieved_knowledge"]["sources"][0]["page_number"] == 2


def test_rag_rejects_viewer_role() -> None:
    with pytest.raises(PermissionError, match="admin or operator"):
        RAGService(FakeKnowledgeBase([make_source()])).run_agent(
            owner_id=uuid4(),
            actor_role="viewer",
            question="question",
            registry=FakeRegistry(),  # type: ignore[arg-type]
            agent_name="analysis_agent",
        )


def test_rag_rejects_queries_without_matching_sources() -> None:
    with pytest.raises(NoRelevantKnowledgeError, match="No matching passages"):
        RAGService(FakeKnowledgeBase([])).run_agent(
            owner_id=uuid4(),
            actor_role="operator",
            question="question",
            registry=FakeRegistry(),  # type: ignore[arg-type]
            agent_name="analysis_agent",
        )
