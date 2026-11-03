"""Persistent memory storage, owner-scoped vector retrieval and lifecycle."""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any, Literal, Protocol
from uuid import UUID

from sqlalchemy import delete, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from agentops.db.models.memory import AgentMemory
from agentops.db.models.workflow import WorkflowRun
from agentops.services.memory_safety import (
    MemoryValidationError,
    validate_memory_content,
    validate_memory_metadata,
    validate_memory_scope,
)


class MemoryEmbeddingProvider(Protocol):
    """Small structural interface shared by the local embedding client and tests."""

    model: str

    def embed_documents(self, texts: Sequence[str], *, title: str) -> list[list[float]]:
        """Embed one or more memory documents."""
        ...

    def embed_query(self, query: str) -> list[float]:
        """Embed a retrieval query."""
        ...


class AgentMemoryError(RuntimeError):
    """Base error for persistent agent-memory operations."""


class AgentMemoryNotFoundError(AgentMemoryError):
    """Raised when a memory is absent, expired or not owned by the caller."""


class MemoryEmbeddingUnavailableError(AgentMemoryError):
    """Raised when an operation needs embeddings but no provider is configured."""


@dataclass(frozen=True, slots=True)
class MemorySearchHit:
    """One retrieved memory and its deterministic ranking values."""

    memory: AgentMemory
    similarity: float
    relevance_score: float


def calculate_relevance_score(
    *,
    similarity: float,
    importance: float,
    confidence: float,
    age_days: float,
) -> float:
    """Blend semantic similarity with importance, confidence and recency."""
    similarity_value = max(0.0, min(1.0, similarity))
    importance_value = max(0.0, min(1.0, importance))
    confidence_value = max(0.0, min(1.0, confidence))
    recency_value = math.exp(-max(0.0, age_days) / 90.0)
    return (
        0.70 * similarity_value
        + 0.15 * importance_value
        + 0.10 * confidence_value
        + 0.05 * recency_value
    )


class AgentMemoryService:
    """Store and retrieve long-lived memories without crossing user boundaries."""

    def __init__(
        self,
        session: Session,
        embeddings: MemoryEmbeddingProvider | None = None,
        *,
        max_content_chars: int = 5_000,
        default_ttl_days: int = 90,
        max_metadata_bytes: int = 4_096,
    ) -> None:
        if max_content_chars < 1:
            raise ValueError("max_content_chars must be positive.")
        if not 1 <= default_ttl_days <= 3_650:
            raise ValueError("default_ttl_days must be between 1 and 3650.")
        self._session = session
        self._embeddings = embeddings
        self._max_content_chars = max_content_chars
        self._default_ttl_days = default_ttl_days
        self._max_metadata_bytes = max_metadata_bytes

    def create_memory(
        self,
        *,
        owner_user_id: UUID,
        memory_type: Literal["episodic", "semantic"],
        memory_scope: Literal["user", "agent"],
        content: str,
        agent_key: str | None = None,
        importance: float = 0.5,
        confidence: float = 1.0,
        source_type: Literal["user", "agent", "workflow"] = "user",
        source_workflow_run_id: UUID | None = None,
        metadata_json: dict[str, Any] | None = None,
        ttl_days: int | None = None,
    ) -> AgentMemory:
        """Embed and persist a validated memory for exactly one user."""
        normalized_content = validate_memory_content(
            content,
            max_chars=self._max_content_chars,
        )
        normalized_agent_key = validate_memory_scope(memory_scope, agent_key)
        metadata = validate_memory_metadata(
            metadata_json or {},
            max_bytes=self._max_metadata_bytes,
        )
        self._validate_scores(importance=importance, confidence=confidence)
        if memory_type not in {"episodic", "semantic"}:
            raise MemoryValidationError("Memory type must be 'episodic' or 'semantic'.")
        if source_type not in {"user", "agent", "workflow"}:
            raise MemoryValidationError("Invalid memory source type.")
        if source_type == "workflow" and source_workflow_run_id is None:
            raise MemoryValidationError("Workflow memories require a source workflow ID.")
        if source_type != "workflow" and source_workflow_run_id is not None:
            raise MemoryValidationError("Only workflow memories may specify a source workflow ID.")
        if source_type == "workflow":
            owned_workflow = self._session.scalar(
                select(WorkflowRun.id).where(
                    WorkflowRun.id == source_workflow_run_id,
                    WorkflowRun.created_by == owner_user_id,
                )
            )
            if owned_workflow is None:
                raise MemoryValidationError(
                    "The source workflow must exist and belong to the memory owner."
                )
        if ttl_days is not None and (
            isinstance(ttl_days, bool)
            or not isinstance(ttl_days, int)
            or not 0 <= ttl_days <= 3_650
        ):
            raise MemoryValidationError("ttl_days must be between 0 and 3650.")

        vector = self._embed_content(normalized_content, memory_scope, normalized_agent_key)
        now = datetime.now(UTC)
        effective_ttl = self._default_ttl_days if ttl_days is None else ttl_days
        expires_at = now + timedelta(days=effective_ttl) if effective_ttl else None

        memory = AgentMemory(
            owner_user_id=owner_user_id,
            memory_type=memory_type,
            memory_scope=memory_scope,
            agent_key=normalized_agent_key,
            content=normalized_content,
            embedding=vector,
            embedding_model=self._embedding_model,
            importance=float(importance),
            confidence=float(confidence),
            source_type=source_type,
            source_workflow_run_id=source_workflow_run_id,
            metadata_json=metadata,
            last_accessed_at=now,
            expires_at=expires_at,
        )
        try:
            self._session.add(memory)
            self._session.commit()
            self._session.refresh(memory)
        except IntegrityError as exc:
            self._session.rollback()
            raise MemoryValidationError(
                "Memory could not be saved because it conflicts with a database constraint."
            ) from exc
        except Exception:
            self._session.rollback()
            raise
        return memory

    def list_memories(
        self,
        *,
        owner_user_id: UUID,
        memory_type: Literal["episodic", "semantic"] | None = None,
        memory_scope: Literal["user", "agent"] | None = None,
        agent_key: str | None = None,
        limit: int = 50,
    ) -> list[AgentMemory]:
        """List active memories belonging to the requesting user only."""
        if not 1 <= limit <= 100:
            raise ValueError("limit must be between 1 and 100.")
        now = datetime.now(UTC)
        statement = select(AgentMemory).where(
            AgentMemory.owner_user_id == owner_user_id,
            or_(AgentMemory.expires_at.is_(None), AgentMemory.expires_at > now),
        )
        if memory_type is not None:
            statement = statement.where(AgentMemory.memory_type == memory_type)
        if memory_scope is not None:
            statement = statement.where(AgentMemory.memory_scope == memory_scope)
        if agent_key is not None:
            validate_memory_scope("agent", agent_key)
            statement = statement.where(AgentMemory.agent_key == agent_key)
        statement = statement.order_by(AgentMemory.created_at.desc()).limit(limit)
        return list(self._session.scalars(statement).all())

    def get_memory(self, *, owner_user_id: UUID, memory_id: UUID) -> AgentMemory:
        """Get an active memory without revealing whether another user's row exists."""
        now = datetime.now(UTC)
        memory = self._session.scalar(
            select(AgentMemory).where(
                AgentMemory.id == memory_id,
                AgentMemory.owner_user_id == owner_user_id,
                or_(AgentMemory.expires_at.is_(None), AgentMemory.expires_at > now),
            )
        )
        if memory is None:
            raise AgentMemoryNotFoundError("Memory not found.")
        return memory

    def update_memory(
        self,
        *,
        owner_user_id: UUID,
        memory_id: UUID,
        content: str | None = None,
        importance: float | None = None,
        ttl_days: int | None | Literal["unchanged"] = "unchanged",
    ) -> AgentMemory:
        """Update an owned memory and regenerate its vector when content changes."""
        if ttl_days != "unchanged" and ttl_days is not None:
            if (
                isinstance(ttl_days, bool)
                or not isinstance(ttl_days, int)
                or not 0 <= ttl_days <= 3_650
            ):
                raise MemoryValidationError("ttl_days must be between 0 and 3650.")
        memory = self.get_memory(owner_user_id=owner_user_id, memory_id=memory_id)
        if content is not None:
            normalized = validate_memory_content(content, max_chars=self._max_content_chars)
            memory.embedding = self._embed_content(
                normalized,
                memory.memory_scope,
                memory.agent_key,
            )
            memory.content = normalized
            memory.embedding_model = self._embedding_model
        if importance is not None:
            self._validate_scores(importance=importance, confidence=memory.confidence)
            memory.importance = float(importance)
        if ttl_days != "unchanged":
            if ttl_days is None or ttl_days == 0:
                memory.expires_at = None
            else:
                memory.expires_at = datetime.now(UTC) + timedelta(days=ttl_days)
        try:
            self._session.commit()
            self._session.refresh(memory)
        except Exception:
            self._session.rollback()
            raise
        return memory

    def delete_memory(self, *, owner_user_id: UUID, memory_id: UUID) -> None:
        """Permanently delete one memory owned by the authenticated user."""
        memory = self.get_memory(owner_user_id=owner_user_id, memory_id=memory_id)
        self._session.delete(memory)
        self._session.commit()

    def purge_expired(self, *, owner_user_id: UUID) -> int:
        """Permanently remove expired memories owned by the requesting user."""
        statement = (
            delete(AgentMemory)
            .where(
                AgentMemory.owner_user_id == owner_user_id,
                AgentMemory.expires_at.is_not(None),
                AgentMemory.expires_at <= datetime.now(UTC),
            )
            .returning(AgentMemory.id)
        )
        try:
            deleted_ids = self._session.scalars(statement).all()
            self._session.commit()
        except Exception:
            self._session.rollback()
            raise
        return len(deleted_ids)

    def search_memories(
        self,
        *,
        owner_user_id: UUID,
        query: str,
        agent_key: str | None = None,
        memory_type: Literal["episodic", "semantic"] | None = None,
        top_k: int = 5,
        min_similarity: float = 0.0,
    ) -> list[MemorySearchHit]:
        """Retrieve the best active user-wide and matching agent memories."""
        normalized_query = query.strip()
        if not normalized_query:
            raise MemoryValidationError("Memory search query cannot be blank.")
        if not 1 <= top_k <= 20:
            raise ValueError("top_k must be between 1 and 20.")
        if not 0.0 <= min_similarity <= 1.0:
            raise ValueError("min_similarity must be between 0 and 1.")
        if agent_key is not None:
            validate_memory_scope("agent", agent_key)

        query_vector = self._require_embeddings().embed_query(normalized_query)
        now = datetime.now(UTC)
        scope_filter = AgentMemory.memory_scope == "user"
        if agent_key is not None:
            scope_filter = or_(
                AgentMemory.memory_scope == "user",
                (AgentMemory.memory_scope == "agent") & (AgentMemory.agent_key == agent_key),
            )
        distance = AgentMemory.embedding.cosine_distance(query_vector)
        statement = (
            select(AgentMemory, distance.label("distance"))
            .where(
                AgentMemory.owner_user_id == owner_user_id,
                scope_filter,
                or_(AgentMemory.expires_at.is_(None), AgentMemory.expires_at > now),
            )
            .order_by(distance)
            .limit(min(100, top_k * 5))
        )
        if memory_type is not None:
            statement = statement.where(AgentMemory.memory_type == memory_type)

        rows = self._session.execute(statement).all()
        hits: list[MemorySearchHit] = []
        for memory, raw_distance in rows:
            similarity = max(-1.0, min(1.0, 1.0 - float(raw_distance)))
            if similarity < min_similarity:
                continue
            age_days = max(0.0, (now - memory.created_at).total_seconds() / 86_400.0)
            relevance = calculate_relevance_score(
                similarity=similarity,
                importance=memory.importance,
                confidence=memory.confidence,
                age_days=age_days,
            )
            hits.append(
                MemorySearchHit(
                    memory=memory,
                    similarity=similarity,
                    relevance_score=relevance,
                )
            )

        hits.sort(key=lambda item: item.relevance_score, reverse=True)
        selected = hits[:top_k]
        for hit in selected:
            hit.memory.last_accessed_at = now
        if selected:
            self._session.commit()
        return selected

    @property
    def _embedding_model(self) -> str:
        return self._require_embeddings().model

    def _embed_content(
        self,
        content: str,
        memory_scope: str,
        agent_key: str | None,
    ) -> list[float]:
        title = f"agent-memory:{memory_scope}:{agent_key or 'user'}"
        vectors = self._require_embeddings().embed_documents([content], title=title)
        if len(vectors) != 1 or len(vectors[0]) != 768:
            raise AgentMemoryError("The embedding provider returned an invalid memory vector.")
        return vectors[0]

    def _require_embeddings(self) -> MemoryEmbeddingProvider:
        if self._embeddings is None:
            raise MemoryEmbeddingUnavailableError(
                "This memory operation requires the configured embedding provider."
            )
        return self._embeddings

    @staticmethod
    def _validate_scores(*, importance: float, confidence: float) -> None:
        if isinstance(importance, bool) or not 0.0 <= float(importance) <= 1.0:
            raise MemoryValidationError("importance must be between 0 and 1.")
        if isinstance(confidence, bool) or not 0.0 <= float(confidence) <= 1.0:
            raise MemoryValidationError("confidence must be between 0 and 1.")
