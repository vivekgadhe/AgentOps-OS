"""API schemas for document ingestion, semantic search, and RAG."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from agentops.schemas.agents import AgentResult


class KnowledgeDocumentResponse(BaseModel):
    """Metadata returned for a successfully indexed document."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    filename: str
    media_type: str
    sha256: str
    page_count: int
    chunk_count: int
    created_at: datetime


class KnowledgeSearchRequest(BaseModel):
    """Request to retrieve relevant document passages."""

    model_config = ConfigDict(extra="forbid")

    query: str = Field(min_length=1, max_length=10_000)
    top_k: int = Field(default=5, ge=1, le=20)
    document_ids: list[UUID] | None = Field(default=None, max_length=50)

    @field_validator("query")
    @classmethod
    def normalize_query(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Search query cannot be blank.")
        return normalized

    @field_validator("document_ids")
    @classmethod
    def reject_duplicate_document_ids(cls, value: list[UUID] | None) -> list[UUID] | None:
        if value is not None and len(value) != len(set(value)):
            raise ValueError("Document IDs must be unique.")
        return value


class KnowledgeCitation(BaseModel):
    """A retrieved source passage with stable document/page coordinates."""

    model_config = ConfigDict(extra="forbid")

    source_id: str
    document_id: UUID
    filename: str
    page_number: int | None
    chunk_index: int
    content: str
    similarity: float = Field(ge=-1.0, le=1.0)


class KnowledgeSearchResponse(BaseModel):
    """Semantic search results scoped to the current user."""

    query: str
    results: list[KnowledgeCitation]


class KnowledgeQueryRequest(KnowledgeSearchRequest):
    """RAG answer request; uses the Analysis Agent by default."""


class KnowledgeAnswerResponse(BaseModel):
    """Structured agent answer plus the exact retrieved source passages."""

    query: str
    answer: AgentResult
    citations: list[KnowledgeCitation]
