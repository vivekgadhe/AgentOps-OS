"""Authenticated APIs for document ingestion, semantic search, and RAG."""

from typing import cast
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, Request, Response, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from agentops.api.deps import get_current_user, get_db
from agentops.core.config import Settings
from agentops.db.models.knowledge import KnowledgeDocument
from agentops.db.models.user import User
from agentops.schemas.knowledge import (
    KnowledgeAnswerResponse,
    KnowledgeCitation,
    KnowledgeDocumentResponse,
    KnowledgeSearchRequest,
    KnowledgeSearchResponse,
)
from agentops.services.agent_registry import AgentAccessDeniedError, AgentRegistry
from agentops.services.document_processing import DocumentProcessingError
from agentops.services.embeddings import EmbeddingServiceError, OllamaEmbeddingClient
from agentops.services.handlers import build_application_tool_registry
from agentops.services.knowledge_base import (
    DuplicateDocumentError,
    KnowledgeBaseService,
    RetrievedChunk,
)
from agentops.services.providers.provider_manager import build_provider_manager
from agentops.services.rag import NoRelevantKnowledgeError, RAGGenerationError, RAGService
from agentops.services.specialized_agents import AnalysisAgent, ReportAgent

router = APIRouter(prefix="/knowledge", tags=["knowledge"])


def _settings(request: Request) -> Settings:
    return cast(Settings, request.app.state.settings)


def _require_operator(user: User) -> None:
    if user.role not in {"admin", "operator"}:
        raise HTTPException(status_code=403, detail="An admin or operator role is required.")


def _knowledge_service(
    db: Session,
    settings: Settings,
    embeddings: OllamaEmbeddingClient,
) -> KnowledgeBaseService:
    return KnowledgeBaseService(
        db,
        embeddings,
        chunk_size=settings.knowledge_chunk_size_chars,
        chunk_overlap=settings.knowledge_chunk_overlap_chars,
        max_pdf_pages=settings.knowledge_max_pdf_pages,
        max_chunks_per_document=settings.knowledge_max_chunks_per_document,
    )


def _citation_response(source: RetrievedChunk, index: int) -> KnowledgeCitation:
    return KnowledgeCitation(
        source_id=f"S{index}",
        document_id=source.document_id,
        filename=source.filename,
        page_number=source.page_number,
        chunk_index=source.chunk_index,
        content=source.content,
        similarity=source.similarity,
    )


@router.post(
    "/documents",
    response_model=KnowledgeDocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
def upload_document(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> KnowledgeDocumentResponse:
    """Upload and index a PDF, TXT, or Markdown file for the current user."""
    _require_operator(user)
    settings = _settings(request)
    filename = file.filename or ""
    content = file.file.read(settings.knowledge_max_upload_bytes + 1)
    if len(content) > settings.knowledge_max_upload_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Document exceeds the configured upload size limit.",
        )

    try:
        with OllamaEmbeddingClient(
            base_url=settings.ollama_base_url,
            model=settings.ollama_embedding_model,
            timeout_s=settings.ollama_timeout_s,
        ) as embeddings:
            document = _knowledge_service(db, settings, embeddings).ingest_document(
                owner_id=user.id,
                filename=filename,
                content=content,
            )
    except DocumentProcessingError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except DuplicateDocumentError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except EmbeddingServiceError as exc:
        raise HTTPException(
            status_code=503,
            detail="Local embedding service is unavailable or returned invalid vectors.",
        ) from exc

    return KnowledgeDocumentResponse.model_validate(document)


@router.get("/documents", response_model=list[KnowledgeDocumentResponse])
def list_documents(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[KnowledgeDocumentResponse]:
    """List only documents owned by the authenticated user."""
    documents = db.scalars(
        select(KnowledgeDocument)
        .where(KnowledgeDocument.owner_id == user.id)
        .order_by(KnowledgeDocument.created_at.desc())
    ).all()
    return [KnowledgeDocumentResponse.model_validate(item) for item in documents]


@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Response:
    """Delete an owned document; its chunks are removed by FK cascade."""
    _require_operator(user)
    document = db.scalar(
        select(KnowledgeDocument).where(
            KnowledgeDocument.id == document_id,
            KnowledgeDocument.owner_id == user.id,
        )
    )
    if document is None:
        raise HTTPException(status_code=404, detail="Knowledge document not found.")
    db.delete(document)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def _search(
    payload: KnowledgeSearchRequest,
    request: Request,
    db: Session,
    user: User,
) -> KnowledgeSearchResponse:
    settings = _settings(request)
    try:
        with OllamaEmbeddingClient(
            base_url=settings.ollama_base_url,
            model=settings.ollama_embedding_model,
            timeout_s=settings.ollama_timeout_s,
        ) as embeddings:
            hits = _knowledge_service(db, settings, embeddings).search(
                owner_id=user.id,
                query=payload.query,
                top_k=payload.top_k,
                document_ids=payload.document_ids,
            )
    except EmbeddingServiceError as exc:
        raise HTTPException(
            status_code=503, detail="Local embedding service is unavailable."
        ) from exc

    return KnowledgeSearchResponse(
        query=payload.query,
        results=[_citation_response(hit, index) for index, hit in enumerate(hits, start=1)],
    )


@router.post("/search", response_model=KnowledgeSearchResponse)
def search_knowledge(
    payload: KnowledgeSearchRequest,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> KnowledgeSearchResponse:
    """Return semantically similar passages from the current user's documents."""
    return _search(payload, request, db, user)


def _run_rag(
    payload: KnowledgeSearchRequest,
    request: Request,
    db: Session,
    user: User,
    *,
    agent_name: str,
) -> KnowledgeAnswerResponse:
    if user.role not in {"admin", "operator"}:
        raise HTTPException(
            status_code=403, detail="This agent requires an admin or operator role."
        )

    settings = _settings(request)
    try:
        with (
            OllamaEmbeddingClient(
                base_url=settings.ollama_base_url,
                model=settings.ollama_embedding_model,
                timeout_s=settings.ollama_timeout_s,
            ) as embeddings,
            build_provider_manager(db, user.id, settings) as generator,
        ):
            knowledge_base = _knowledge_service(db, settings, embeddings)
            registry = AgentRegistry(
                build_application_tool_registry(request.app.state.tool_registrars)
            )
            if agent_name == "analysis_agent":
                registry.register(AnalysisAgent(generator))
            elif agent_name == "report_agent":
                registry.register(ReportAgent(generator))
            else:
                raise ValueError("Unsupported RAG agent.")

            result = RAGService(knowledge_base).run_agent(
                owner_id=user.id,
                actor_role=user.role,
                question=payload.query,
                registry=registry,
                agent_name=agent_name,
                top_k=payload.top_k,
                document_ids=payload.document_ids,
            )
    except NoRelevantKnowledgeError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except EmbeddingServiceError as exc:
        raise HTTPException(
            status_code=503, detail="Local embedding service is unavailable."
        ) from exc
    except (RAGGenerationError, ValueError) as exc:
        raise HTTPException(status_code=502, detail="Local agent generation failed.") from exc
    except AgentAccessDeniedError as exc:
        raise HTTPException(status_code=403, detail="Agent access denied.") from exc

    return KnowledgeAnswerResponse(
        query=payload.query,
        answer=result.answer,
        citations=[
            _citation_response(source, index)
            for index, source in enumerate(result.sources, start=1)
        ],
    )


@router.post("/query", response_model=KnowledgeAnswerResponse)
def query_knowledge(
    payload: KnowledgeSearchRequest,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> KnowledgeAnswerResponse:
    """Retrieve knowledge and ask the Analysis Agent for a grounded answer."""
    return _run_rag(payload, request, db, user, agent_name="analysis_agent")


@router.post("/report", response_model=KnowledgeAnswerResponse)
def create_knowledge_report(
    payload: KnowledgeSearchRequest,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> KnowledgeAnswerResponse:
    """Retrieve knowledge and ask the Report Agent for a grounded report."""
    return _run_rag(payload, request, db, user, agent_name="report_agent")
