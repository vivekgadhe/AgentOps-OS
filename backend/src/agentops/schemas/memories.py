"""Request and response contracts for persistent agent memories."""

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from agentops.schemas.payload_limits import validate_json_payload_size
from agentops.services.memory_safety import validate_memory_content, validate_memory_scope

MemoryType = Literal["episodic", "semantic"]
MemoryScope = Literal["user", "agent"]


class MemoryCreateRequest(BaseModel):
    """Create a user-owned memory; provenance is assigned by trusted API code."""

    model_config = ConfigDict(extra="forbid")

    memory_type: MemoryType
    memory_scope: MemoryScope = "user"
    agent_key: str | None = Field(default=None, max_length=100)
    content: str = Field(min_length=1, max_length=5_000)
    importance: float = Field(default=0.5, ge=0.0, le=1.0)
    # None uses the configured default; zero means no expiration.
    ttl_days: int | None = Field(default=None, ge=0, le=3_650)
    metadata_json: dict[str, Any] = Field(default_factory=dict)

    @field_validator("content")
    @classmethod
    def validate_content(cls, value: str) -> str:
        return validate_memory_content(value)

    @field_validator("metadata_json")
    @classmethod
    def validate_metadata(cls, value: dict[str, Any]) -> dict[str, Any]:
        validate_json_payload_size(value, field_name="Memory metadata", max_bytes=4_096)
        return value

    @model_validator(mode="after")
    def validate_scope(self) -> "MemoryCreateRequest":
        validate_memory_scope(self.memory_scope, self.agent_key)
        return self


class MemoryUpdateRequest(BaseModel):
    """Update content, importance or expiration of an owned memory."""

    model_config = ConfigDict(extra="forbid")

    content: str | None = Field(default=None, min_length=1, max_length=5_000)
    importance: float | None = Field(default=None, ge=0.0, le=1.0)
    # Omitted means unchanged; null or zero explicitly removes expiration.
    ttl_days: int | None = Field(default=None, ge=0, le=3_650)

    @field_validator("content")
    @classmethod
    def validate_content(cls, value: str | None) -> str | None:
        return None if value is None else validate_memory_content(value)

    @model_validator(mode="after")
    def require_change(self) -> "MemoryUpdateRequest":
        if not self.model_fields_set:
            raise ValueError("At least one memory field must be supplied.")
        if all(getattr(self, field) is None for field in self.model_fields_set):
            # ttl_days=null is a meaningful request to remove expiry.
            if self.model_fields_set == {"ttl_days"}:
                return self
            raise ValueError("At least one non-null memory field must be supplied.")
        return self


class MemorySearchRequest(BaseModel):
    """Search memories visible to the current user and optional agent."""

    model_config = ConfigDict(extra="forbid")

    query: str = Field(min_length=1, max_length=2_000)
    agent_key: str | None = Field(default=None, max_length=100)
    memory_type: MemoryType | None = None
    top_k: int = Field(default=5, ge=1, le=20)
    min_similarity: float = Field(default=0.0, ge=0.0, le=1.0)

    @field_validator("query")
    @classmethod
    def normalize_query(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Search query cannot be blank.")
        return normalized

    @field_validator("agent_key")
    @classmethod
    def validate_agent_key(cls, value: str | None) -> str | None:
        if value is None:
            return None
        validate_memory_scope("agent", value)
        return value


class MemoryResponse(BaseModel):
    """Safe memory representation; embedding vectors are never returned."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    owner_user_id: UUID
    memory_type: MemoryType
    memory_scope: MemoryScope
    agent_key: str | None
    content: str
    embedding_model: str
    confidence: float
    importance: float
    source_type: Literal["user", "agent", "workflow"]
    source_workflow_run_id: UUID | None
    metadata_json: dict[str, Any]
    created_at: datetime
    updated_at: datetime
    last_accessed_at: datetime
    expires_at: datetime | None


class MemorySearchHitResponse(BaseModel):
    """A retrieved memory and its ranking signals."""

    memory: MemoryResponse
    similarity: float
    relevance_score: float


class MemorySearchResponse(BaseModel):
    query: str
    results: list[MemorySearchHitResponse]


class MemoryPurgeResponse(BaseModel):
    deleted_count: int
