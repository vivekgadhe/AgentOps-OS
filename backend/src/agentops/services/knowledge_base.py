"""Persist documents and perform owner-scoped pgvector similarity search."""

import hashlib
from collections.abc import Sequence
from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from agentops.db.models.knowledge import KnowledgeChunk, KnowledgeDocument
from agentops.services.document_processing import (
    chunk_document_pages,
    extract_document_pages,
    sanitize_filename,
)
from agentops.services.embeddings import OllamaEmbeddingClient


class DuplicateDocumentError(ValueError):
    """Raised when the same document has already been indexed by this user."""


class KnowledgeDocumentNotFoundError(LookupError):
    """Raised when a document does not exist or is not owned by the user."""


@dataclass(frozen=True, slots=True)
class RetrievedChunk:
    """A nearest-neighbor chunk and its source metadata."""

    document_id: UUID
    filename: str
    chunk_index: int
    page_number: int | None
    content: str
    similarity: float


class KnowledgeBaseService:
    """Coordinate extraction, chunking, embedding, persistence, and retrieval."""

    def __init__(
        self,
        session: Session,
        embeddings: OllamaEmbeddingClient,
        *,
        chunk_size: int = 1200,
        chunk_overlap: int = 200,
        max_pdf_pages: int = 200,
        max_chunks_per_document: int = 5000,
    ) -> None:
        self._session = session
        self._embeddings = embeddings
        self._chunk_size = chunk_size
        self._chunk_overlap = chunk_overlap
        self._max_pdf_pages = max_pdf_pages
        self._max_chunks_per_document = max_chunks_per_document

    def ingest_document(
        self,
        *,
        owner_id: UUID,
        filename: str,
        content: bytes,
    ) -> KnowledgeDocument:
        """Extract and index a document atomically after embeddings are ready."""

        safe_filename = sanitize_filename(filename)

        media_type, pages = extract_document_pages(
            safe_filename,
            content,
            max_pdf_pages=self._max_pdf_pages,
        )

        chunks = chunk_document_pages(
            pages,
            chunk_size=self._chunk_size,
            overlap=self._chunk_overlap,
            max_chunks=self._max_chunks_per_document,
        )

        digest = hashlib.sha256(content).hexdigest()

        existing = self._session.scalar(
            select(KnowledgeDocument.id).where(
                KnowledgeDocument.owner_id == owner_id,
                KnowledgeDocument.sha256 == digest,
            )
        )

        if existing is not None:
            raise DuplicateDocumentError("This document has already been uploaded.")

        vectors = self._embeddings.embed_documents(
            [chunk.content for chunk in chunks],
            title=safe_filename,
        )

        if len(vectors) != len(chunks):
            raise RuntimeError("Embedding count does not match document chunk count.")

        document = KnowledgeDocument(
            owner_id=owner_id,
            filename=safe_filename,
            media_type=media_type,
            sha256=digest,
            page_count=len(pages),
            chunk_count=len(chunks),
        )

        try:
            self._session.add(document)
            self._session.flush()

            self._session.add_all(
                [
                    KnowledgeChunk(
                        document_id=document.id,
                        chunk_index=chunk.chunk_index,
                        page_number=chunk.page_number,
                        start_char=chunk.start_char,
                        end_char=chunk.end_char,
                        content=chunk.content,
                        embedding=vector,
                        chunk_metadata={"filename": safe_filename},
                    )
                    for chunk, vector in zip(
                        chunks,
                        vectors,
                        strict=True,
                    )
                ]
            )

            self._session.commit()
            self._session.refresh(document)

        except IntegrityError as exc:
            self._session.rollback()

            original_error = exc.orig
            sqlstate = getattr(original_error, "sqlstate", None)

            diagnostic = getattr(original_error, "diag", None)
            constraint_name = getattr(
                diagnostic,
                "constraint_name",
                None,
            )

            if sqlstate == "23505" and constraint_name == "uq_knowledge_documents_owner_sha256":
                raise DuplicateDocumentError("This document has already been uploaded.") from exc

            raise

        except Exception:
            self._session.rollback()
            raise

        return document

    def list_documents(
        self,
        owner_id: UUID,
    ) -> list[KnowledgeDocument]:
        """List only documents owned by the requesting user."""

        return list(
            self._session.scalars(
                select(KnowledgeDocument)
                .where(KnowledgeDocument.owner_id == owner_id)
                .order_by(KnowledgeDocument.created_at.desc())
            ).all()
        )

    def delete_document(
        self,
        *,
        owner_id: UUID,
        document_id: UUID,
    ) -> None:
        """Delete a user's document and let the FK cascade remove its chunks."""

        document = self._session.scalar(
            select(KnowledgeDocument).where(
                KnowledgeDocument.id == document_id,
                KnowledgeDocument.owner_id == owner_id,
            )
        )

        if document is None:
            raise KnowledgeDocumentNotFoundError("Knowledge document not found.")

        self._session.delete(document)
        self._session.commit()

    def search(
        self,
        *,
        owner_id: UUID,
        query: str,
        top_k: int = 5,
        document_ids: Sequence[UUID] | None = None,
    ) -> list[RetrievedChunk]:
        """Return cosine-nearest passages, strictly filtered by document owner."""

        normalized_query = query.strip()

        if not normalized_query:
            raise ValueError("Search query cannot be blank.")

        if not 1 <= top_k <= 20:
            raise ValueError("top_k must be between 1 and 20.")

        query_vector = self._embeddings.embed_query(normalized_query)

        distance = KnowledgeChunk.embedding.cosine_distance(query_vector)

        statement = (
            select(
                KnowledgeChunk,
                KnowledgeDocument,
                distance.label("distance"),
            )
            .join(
                KnowledgeDocument,
                KnowledgeDocument.id == KnowledgeChunk.document_id,
            )
            .where(KnowledgeDocument.owner_id == owner_id)
            .order_by(distance)
            .limit(top_k)
        )

        if document_ids is not None:
            if not document_ids:
                return []

            statement = statement.where(KnowledgeDocument.id.in_(document_ids))

        rows = self._session.execute(statement).all()

        hits: list[RetrievedChunk] = []

        for chunk, document, raw_distance in rows:
            similarity = max(
                -1.0,
                min(1.0, 1.0 - float(raw_distance)),
            )

            hits.append(
                RetrievedChunk(
                    document_id=document.id,
                    filename=document.filename,
                    chunk_index=chunk.chunk_index,
                    page_number=chunk.page_number,
                    content=chunk.content,
                    similarity=similarity,
                )
            )

        return hits
