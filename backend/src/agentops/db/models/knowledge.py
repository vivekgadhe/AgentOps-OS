"""User-owned knowledge documents, chunks, and pgvector embeddings."""

from __future__ import annotations

import uuid
from typing import Any

from pgvector.sqlalchemy import VECTOR
from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from agentops.db.base import Base, TimestampMixin

EMBEDDING_DIMENSIONS = 768


class KnowledgeDocument(TimestampMixin, Base):
    """An uploaded document owned by one application user."""

    __tablename__ = "knowledge_documents"
    __table_args__ = (
        UniqueConstraint(
            "owner_id",
            "sha256",
            name="uq_knowledge_documents_owner_sha256",
        ),
        CheckConstraint(
            "length(btrim(filename)) > 0",
            name="filename_not_blank",
        ),
        CheckConstraint(
            "media_type IN ('application/pdf', 'text/plain', 'text/markdown')",
            name="media_type_valid",
        ),
        CheckConstraint(
            "length(sha256) = 64",
            name="sha256_length_valid",
        ),
        CheckConstraint(
            "page_count >= 0",
            name="page_count_non_negative",
        ),
        CheckConstraint(
            "chunk_count > 0",
            name="chunk_count_positive",
        ),
        Index(
            "ix_knowledge_documents_owner_created_at",
            "owner_id",
            "created_at",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    owner_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="RESTRICT",
            name="fk_knowledge_documents_owner_id_users",
        )
    )

    filename: Mapped[str] = mapped_column(String(255))
    media_type: Mapped[str] = mapped_column(String(100))
    sha256: Mapped[str] = mapped_column(String(64))

    page_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default="0",
    )

    chunk_count: Mapped[int] = mapped_column(Integer)

    chunks: Mapped[list[KnowledgeChunk]] = relationship(
        back_populates="document",
        cascade="all, delete-orphan",
        order_by="KnowledgeChunk.chunk_index",
    )


class KnowledgeChunk(Base):
    """A searchable text chunk and its 768-dimensional embedding."""

    __tablename__ = "knowledge_chunks"

    __table_args__ = (
        UniqueConstraint(
            "document_id",
            "chunk_index",
            name="uq_knowledge_chunks_document_index",
        ),
        CheckConstraint(
            "chunk_index >= 0",
            name="chunk_index_non_negative",
        ),
        CheckConstraint(
            "page_number IS NULL OR page_number >= 1",
            name="page_number_positive",
        ),
        CheckConstraint(
            "start_char >= 0",
            name="start_char_non_negative",
        ),
        CheckConstraint(
            "end_char >= start_char",
            name="end_after_start",
        ),
        CheckConstraint(
            "length(btrim(content)) > 0",
            name="content_not_blank",
        ),
        Index(
            "ix_knowledge_chunks_document_id",
            "document_id",
        ),
        Index(
            "ix_knowledge_chunks_embedding_hnsw",
            "embedding",
            postgresql_using="hnsw",
            postgresql_with={
                "m": 16,
                "ef_construction": 64,
            },
            postgresql_ops={
                "embedding": "vector_cosine_ops",
            },
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    document_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(
            "knowledge_documents.id",
            ondelete="CASCADE",
            name="fk_knowledge_chunks_document_id_knowledge_documents",
        )
    )

    chunk_index: Mapped[int] = mapped_column(Integer)

    page_number: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    start_char: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default="0",
    )

    end_char: Mapped[int] = mapped_column(Integer)
    content: Mapped[str] = mapped_column(Text)

    embedding: Mapped[list[float]] = mapped_column(VECTOR(EMBEDDING_DIMENSIONS))

    chunk_metadata: Mapped[dict[str, Any]] = mapped_column(
        default=dict,
    )

    document: Mapped[KnowledgeDocument] = relationship(back_populates="chunks")
