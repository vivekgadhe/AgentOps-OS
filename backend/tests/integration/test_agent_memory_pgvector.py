"""PostgreSQL/pgvector integration tests for persistent agent memory."""

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from sqlalchemy import delete, text
from sqlalchemy.orm import Session

from agentops.core.config import Settings
from agentops.db.models.memory import AgentMemory
from agentops.db.models.user import User
from agentops.db.session import create_db_engine
from agentops.services.agent_memory import AgentMemoryService


class FixedEmbeddingProvider:
    """Deterministic 768-dimensional embeddings for database integration tests."""

    model = "embeddinggemma:test-fixture"

    def embed_documents(self, texts: list[str], *, title: str) -> list[list[float]]:
        return [[1.0] + [0.0] * 767 for _ in texts]

    def embed_query(self, query: str) -> list[float]:
        return [1.0] + [0.0] * 767


@pytest.mark.integration
def test_memory_vector_retrieval_obeys_user_and_agent_scope(
    integration_settings: Settings,
) -> None:
    engine = create_db_engine(integration_settings)
    owner_id = uuid4()
    other_user_id = uuid4()
    try:
        with engine.connect() as connection:
            extension = connection.execute(
                text("SELECT extname FROM pg_extension WHERE extname = 'vector'")
            ).scalar_one_or_none()
            assert extension == "vector", "Run `uv run alembic upgrade head` first."

        with Session(engine) as session:
            session.add_all(
                [
                    User(
                        id=owner_id,
                        email=f"memory-owner-{owner_id.hex}@example.invalid",
                        password_hash="integration-test-hash",
                        role="operator",
                        is_active=True,
                    ),
                    User(
                        id=other_user_id,
                        email=f"memory-other-{other_user_id.hex}@example.invalid",
                        password_hash="integration-test-hash",
                        role="operator",
                        is_active=True,
                    ),
                ]
            )
            session.commit()
            service = AgentMemoryService(
                session,
                FixedEmbeddingProvider(),  # type: ignore[arg-type]
            )

            shared = service.create_memory(
                owner_user_id=owner_id,
                memory_type="semantic",
                memory_scope="user",
                content="The user prefers short operational summaries.",
                ttl_days=0,
            )
            analysis = service.create_memory(
                owner_user_id=owner_id,
                memory_type="episodic",
                memory_scope="agent",
                agent_key="analysis_agent",
                content="The analysis agent previously reviewed a delivery-delay report.",
            )
            report = service.create_memory(
                owner_user_id=owner_id,
                memory_type="episodic",
                memory_scope="agent",
                agent_key="report_agent",
                content="The report agent previously created a delivery-delay summary.",
            )
            other_user = service.create_memory(
                owner_user_id=other_user_id,
                memory_type="semantic",
                memory_scope="user",
                content="Another user prefers detailed technical reports.",
            )

            analysis_hits = service.search_memories(
                owner_user_id=owner_id,
                query="delivery delays",
                agent_key="analysis_agent",
                top_k=10,
            )
            analysis_contents = {hit.memory.content for hit in analysis_hits}
            assert shared.content in analysis_contents
            assert analysis.content in analysis_contents
            assert report.content not in analysis_contents
            assert other_user.content not in analysis_contents

            report_hits = service.search_memories(
                owner_user_id=owner_id,
                query="delivery delays",
                agent_key="report_agent",
                top_k=10,
            )
            report_contents = {hit.memory.content for hit in report_hits}
            assert shared.content in report_contents
            assert report.content in report_contents
            assert analysis.content not in report_contents

            visible = service.list_memories(owner_user_id=owner_id, limit=100)
            assert {item.id for item in visible} == {shared.id, analysis.id, report.id}
    finally:
        with Session(engine) as session:
            session.execute(
                delete(AgentMemory).where(AgentMemory.owner_user_id.in_([owner_id, other_user_id]))
            )
            session.execute(delete(User).where(User.id.in_([owner_id, other_user_id])))
            session.commit()
        engine.dispose()


@pytest.mark.integration
def test_memory_update_expiry_purge_and_delete(
    integration_settings: Settings,
) -> None:
    engine = create_db_engine(integration_settings)
    owner_id = uuid4()
    try:
        with Session(engine) as session:
            user = User(
                id=owner_id,
                email=f"memory-lifecycle-{owner_id.hex}@example.invalid",
                password_hash="integration-test-hash",
                role="operator",
                is_active=True,
            )
            session.add(user)
            session.commit()

            service = AgentMemoryService(
                session,
                FixedEmbeddingProvider(),  # type: ignore[arg-type]
            )
            memory = service.create_memory(
                owner_user_id=owner_id,
                memory_type="semantic",
                memory_scope="user",
                content="The user prefers weekly summaries.",
                ttl_days=0,
            )

            updated = service.update_memory(
                owner_user_id=owner_id,
                memory_id=memory.id,
                content="The user prefers monthly operational summaries.",
                importance=0.9,
            )
            assert updated.content.startswith("The user prefers monthly")
            assert updated.importance == 0.9
            assert updated.embedding_model == FixedEmbeddingProvider.model

            updated.expires_at = datetime.now(UTC) - timedelta(minutes=1)
            session.commit()
            assert service.list_memories(owner_user_id=owner_id) == []
            assert service.purge_expired(owner_user_id=owner_id) == 1
            assert service.list_memories(owner_user_id=owner_id) == []

            remaining = service.create_memory(
                owner_user_id=owner_id,
                memory_type="episodic",
                memory_scope="user",
                content="A previous analysis completed successfully.",
            )
            service.delete_memory(owner_user_id=owner_id, memory_id=remaining.id)
            assert service.list_memories(owner_user_id=owner_id) == []
    finally:
        with Session(engine) as session:
            session.execute(delete(AgentMemory).where(AgentMemory.owner_user_id == owner_id))
            session.execute(delete(User).where(User.id == owner_id))
            session.commit()
        engine.dispose()
