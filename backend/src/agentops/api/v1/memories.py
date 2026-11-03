"""Authenticated API for persistent agent memory management and retrieval."""

from typing import Literal, cast
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from sqlalchemy.orm import Session

from agentops.api.deps import get_current_user, get_db
from agentops.core.config import Settings
from agentops.db.models.user import User
from agentops.schemas.memories import (
    MemoryCreateRequest,
    MemoryPurgeResponse,
    MemoryResponse,
    MemorySearchHitResponse,
    MemorySearchRequest,
    MemorySearchResponse,
    MemoryUpdateRequest,
)
from agentops.services.agent_memory import (
    AgentMemoryNotFoundError,
    AgentMemoryService,
    MemoryEmbeddingUnavailableError,
)
from agentops.services.embeddings import EmbeddingServiceError, OllamaEmbeddingClient
from agentops.services.memory_safety import MemoryValidationError

router = APIRouter(prefix="/memories", tags=["agent memory"])


def _settings(request: Request) -> Settings:
    return cast(Settings, request.app.state.settings)


def _require_operator(user: User) -> None:
    if user.role not in {"admin", "operator"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="An admin or operator role is required to modify memories.",
        )


def _memory_service(
    db: Session,
    settings: Settings,
    embeddings: OllamaEmbeddingClient | None = None,
) -> AgentMemoryService:
    return AgentMemoryService(
        db,
        embeddings,
        max_content_chars=settings.memory_max_content_chars,
        default_ttl_days=settings.memory_default_ttl_days,
    )


def _map_memory_error(exc: Exception) -> HTTPException:
    if isinstance(exc, MemoryValidationError):
        return HTTPException(status_code=422, detail=str(exc))
    if isinstance(exc, AgentMemoryNotFoundError):
        return HTTPException(status_code=404, detail="Memory not found.")
    if isinstance(exc, (EmbeddingServiceError, MemoryEmbeddingUnavailableError)):
        return HTTPException(status_code=503, detail="Local embedding service is unavailable.")
    return HTTPException(status_code=503, detail="Memory service is temporarily unavailable.")


@router.post(
    "",
    response_model=MemoryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_memory(
    payload: MemoryCreateRequest,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> MemoryResponse:
    """Create a memory owned by the authenticated user."""
    _require_operator(user)
    settings = _settings(request)
    try:
        with OllamaEmbeddingClient(
            base_url=settings.ollama_base_url,
            model=settings.ollama_embedding_model,
            timeout_s=settings.ollama_timeout_s,
        ) as embeddings:
            memory = _memory_service(db, settings, embeddings).create_memory(
                owner_user_id=user.id,
                memory_type=payload.memory_type,
                memory_scope=payload.memory_scope,
                agent_key=payload.agent_key,
                content=payload.content,
                importance=payload.importance,
                metadata_json=payload.metadata_json,
                ttl_days=payload.ttl_days,
                source_type="user",
            )
    except (MemoryValidationError, EmbeddingServiceError, MemoryEmbeddingUnavailableError) as exc:
        raise _map_memory_error(exc) from exc
    return MemoryResponse.model_validate(memory)


@router.get("", response_model=list[MemoryResponse])
def list_memories(
    memory_type: Literal["episodic", "semantic"] | None = Query(default=None),
    memory_scope: Literal["user", "agent"] | None = Query(default=None),
    agent_key: str | None = Query(
        default=None,
        min_length=1,
        max_length=100,
        pattern="^[a-z][a-z0-9_]{0,99}$",
    ),
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[MemoryResponse]:
    """List active memories owned by the authenticated user."""
    memories = AgentMemoryService(db).list_memories(
        owner_user_id=user.id,
        memory_type=memory_type,
        memory_scope=memory_scope,
        agent_key=agent_key,
        limit=limit,
    )
    return [MemoryResponse.model_validate(item) for item in memories]


@router.post("/search", response_model=MemorySearchResponse)
def search_memories(
    payload: MemorySearchRequest,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> MemorySearchResponse:
    """Retrieve the most relevant active memories visible to this user/agent."""
    settings = _settings(request)
    try:
        with OllamaEmbeddingClient(
            base_url=settings.ollama_base_url,
            model=settings.ollama_embedding_model,
            timeout_s=settings.ollama_timeout_s,
        ) as embeddings:
            hits = _memory_service(db, settings, embeddings).search_memories(
                owner_user_id=user.id,
                query=payload.query,
                agent_key=payload.agent_key,
                memory_type=payload.memory_type,
                top_k=payload.top_k,
                min_similarity=payload.min_similarity,
            )
    except (MemoryValidationError, EmbeddingServiceError, MemoryEmbeddingUnavailableError) as exc:
        raise _map_memory_error(exc) from exc

    return MemorySearchResponse(
        query=payload.query,
        results=[
            MemorySearchHitResponse(
                memory=MemoryResponse.model_validate(hit.memory),
                similarity=round(hit.similarity, 6),
                relevance_score=round(hit.relevance_score, 6),
            )
            for hit in hits
        ],
    )


@router.delete("/expired", response_model=MemoryPurgeResponse)
def purge_expired_memories(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> MemoryPurgeResponse:
    """Permanently remove expired memories belonging to the current user."""
    _require_operator(user)
    count = AgentMemoryService(db).purge_expired(owner_user_id=user.id)
    return MemoryPurgeResponse(deleted_count=count)


@router.get("/{memory_id}", response_model=MemoryResponse)
def get_memory(
    memory_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> MemoryResponse:
    """Get an active memory without disclosing other users' records."""
    try:
        memory = AgentMemoryService(db).get_memory(owner_user_id=user.id, memory_id=memory_id)
    except AgentMemoryNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Memory not found.") from exc
    return MemoryResponse.model_validate(memory)


@router.patch("/{memory_id}", response_model=MemoryResponse)
def update_memory(
    memory_id: UUID,
    payload: MemoryUpdateRequest,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> MemoryResponse:
    """Update an owned memory; content changes regenerate its embedding."""
    _require_operator(user)
    settings = _settings(request)
    ttl: int | None | Literal["unchanged"] = "unchanged"
    if "ttl_days" in payload.model_fields_set:
        ttl = payload.ttl_days
    needs_embeddings = payload.content is not None
    try:
        if needs_embeddings:
            with OllamaEmbeddingClient(
                base_url=settings.ollama_base_url,
                model=settings.ollama_embedding_model,
                timeout_s=settings.ollama_timeout_s,
            ) as embeddings:
                memory = _memory_service(db, settings, embeddings).update_memory(
                    owner_user_id=user.id,
                    memory_id=memory_id,
                    content=payload.content,
                    importance=payload.importance,
                    ttl_days=ttl,
                )
        else:
            memory = AgentMemoryService(db).update_memory(
                owner_user_id=user.id,
                memory_id=memory_id,
                importance=payload.importance,
                ttl_days=ttl,
            )
    except (AgentMemoryNotFoundError, MemoryValidationError) as exc:
        raise _map_memory_error(exc) from exc
    except (EmbeddingServiceError, MemoryEmbeddingUnavailableError) as exc:
        raise _map_memory_error(exc) from exc
    return MemoryResponse.model_validate(memory)


@router.delete("/{memory_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_memory(
    memory_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Response:
    """Forget one memory owned by the authenticated user."""
    _require_operator(user)
    try:
        AgentMemoryService(db).delete_memory(owner_user_id=user.id, memory_id=memory_id)
    except AgentMemoryNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Memory not found.") from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)
