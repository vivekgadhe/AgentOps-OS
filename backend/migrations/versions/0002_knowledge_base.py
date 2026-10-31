"""Add user-owned knowledge documents and pgvector chunks.

Revision ID: 0002
Revises: 0001
Create Date: 2026-10-30
"""

from collections.abc import Sequence
import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import VECTOR
from sqlalchemy.dialects import postgresql

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

EMBEDDING_DIMENSIONS = 768


def upgrade() -> None:
    # The database image must include pgvector before this migration is run.
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "knowledge_documents",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("owner_id", sa.Uuid(), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("media_type", sa.String(length=100), nullable=False),
        sa.Column("sha256", sa.String(length=64), nullable=False),
        sa.Column("page_count", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("chunk_count", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_knowledge_documents")),
        sa.ForeignKeyConstraint(
            ["owner_id"], ["users.id"],
            name=op.f("fk_knowledge_documents_owner_id_users"),
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint(
            "owner_id", "sha256", name=op.f("uq_knowledge_documents_owner_sha256")
        ),
        sa.CheckConstraint(
            "length(btrim(filename)) > 0",
            name=op.f("ck_knowledge_documents_filename_not_blank"),
        ),
        sa.CheckConstraint(
            "media_type IN ('application/pdf', 'text/plain', 'text/markdown')",
            name=op.f("ck_knowledge_documents_media_type_valid"),
        ),
        sa.CheckConstraint(
            "length(sha256) = 64",
            name=op.f("ck_knowledge_documents_sha256_length_valid"),
        ),
        sa.CheckConstraint(
            "page_count >= 0",
            name=op.f("ck_knowledge_documents_page_count_non_negative"),
        ),
        sa.CheckConstraint(
            "chunk_count > 0",
            name=op.f("ck_knowledge_documents_chunk_count_positive"),
        ),
    )
    op.create_index(
        op.f("ix_knowledge_documents_owner_created_at"),
        "knowledge_documents",
        ["owner_id", "created_at"],
    )

    op.create_table(
        "knowledge_chunks",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("document_id", sa.Uuid(), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("page_number", sa.Integer(), nullable=True),
        sa.Column("start_char", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("end_char", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("embedding", VECTOR(EMBEDDING_DIMENSIONS), nullable=False),
        sa.Column("chunk_metadata", postgresql.JSONB(none_as_null=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_knowledge_chunks")),
        sa.ForeignKeyConstraint(
            ["document_id"], ["knowledge_documents.id"],
            name=op.f("fk_knowledge_chunks_document_id_knowledge_documents"),
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint(
            "document_id", "chunk_index",
            name=op.f("uq_knowledge_chunks_document_index"),
        ),
        sa.CheckConstraint(
            "chunk_index >= 0",
            name=op.f("ck_knowledge_chunks_chunk_index_non_negative"),
        ),
        sa.CheckConstraint(
            "page_number IS NULL OR page_number >= 1",
            name=op.f("ck_knowledge_chunks_page_number_positive"),
        ),
        sa.CheckConstraint(
            "start_char >= 0",
            name=op.f("ck_knowledge_chunks_start_char_non_negative"),
        ),
        sa.CheckConstraint(
            "end_char >= start_char",
            name=op.f("ck_knowledge_chunks_end_after_start"),
        ),
        sa.CheckConstraint(
            "length(btrim(content)) > 0",
            name=op.f("ck_knowledge_chunks_content_not_blank"),
        ),
    )
    op.create_index(
        op.f("ix_knowledge_chunks_document_id"),
        "knowledge_chunks",
        ["document_id"],
    )
    op.create_index(
        "ix_knowledge_chunks_embedding_hnsw",
        "knowledge_chunks",
        ["embedding"],
        postgresql_using="hnsw",
        postgresql_with={"m": 16, "ef_construction": 64},
        postgresql_ops={"embedding": "vector_cosine_ops"},
    )


def downgrade() -> None:
    op.drop_index("ix_knowledge_chunks_embedding_hnsw", table_name="knowledge_chunks")
    op.drop_index(op.f("ix_knowledge_chunks_document_id"), table_name="knowledge_chunks")
    op.drop_table("knowledge_chunks")
    op.drop_index(
        op.f("ix_knowledge_documents_owner_created_at"),
        table_name="knowledge_documents",
    )
    op.drop_table("knowledge_documents")
    # Keep the vector extension installed: other schemas may use it.
