"""PostgreSQL/pgvector integration coverage; requires migrations at head."""

from uuid import uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session

from agentops.core.config import Settings
from agentops.db.models.user import User
from agentops.db.session import create_db_engine
from agentops.services.knowledge_base import KnowledgeBaseService


class FixedEmbeddingProvider:
    """Deterministic embeddings for database integration tests."""

    def embed_documents(
        self,
        texts: list[str],
        *,
        title: str,
    ) -> list[list[float]]:
        return [[1.0] + [0.0] * 767 for _ in texts]

    def embed_query(self, query: str) -> list[float]:
        return [1.0] + [0.0] * 767


@pytest.mark.integration
def test_pgvector_document_ingestion_and_owner_scoped_search(
    integration_settings: Settings,
) -> None:
    """Test document ingestion, vector search, ownership, and deletion."""

    engine = create_db_engine(integration_settings)

    owner_id = uuid4()
    other_owner_id = uuid4()

    try:
        with engine.connect() as connection:
            extension = connection.execute(
                text("SELECT extname FROM pg_extension WHERE extname = 'vector'")
            ).scalar_one_or_none()

            assert extension == "vector", "Run `uv run alembic upgrade head` first."

        with Session(engine) as session:
            user = User(
                id=owner_id,
                email=f"rag-test-{owner_id.hex}@example.invalid",
                password_hash="integration-test-hash",
                role="operator",
                is_active=True,
            )

            other_user = User(
                id=other_owner_id,
                email=f"rag-other-{other_owner_id.hex}@example.invalid",
                password_hash="integration-test-hash",
                role="operator",
                is_active=True,
            )

            session.add_all([user, other_user])
            session.commit()

            service = KnowledgeBaseService(
                session,
                FixedEmbeddingProvider(),  # type: ignore[arg-type]
                chunk_size=300,
                chunk_overlap=40,
            )

            document = service.ingest_document(
                owner_id=owner_id,
                filename="feedback.txt",
                content=(b"Customers reported late deliveries and missing updates."),
            )

            # The document owner must be able to retrieve its document.
            hits = service.search(
                owner_id=owner_id,
                query="late deliveries",
                top_k=3,
            )

            # A different user must not be able to retrieve that document.
            other_hits = service.search(
                owner_id=other_owner_id,
                query="late deliveries",
                top_k=3,
            )

            assert document.chunk_count == 1
            assert len(hits) == 1
            assert hits[0].filename == "feedback.txt"
            assert hits[0].page_number is None

            assert other_hits == []

            # Verify document deletion and clean up both test users.
            service.delete_document(
                owner_id=owner_id,
                document_id=document.id,
            )

            session.delete(user)
            session.delete(other_user)
            session.commit()

    finally:
        engine.dispose()
