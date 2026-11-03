"""Pure unit coverage for memory safety, schema contracts and ranking."""

import pytest
from pydantic import ValidationError

from agentops.schemas.memories import MemoryCreateRequest, MemoryUpdateRequest
from agentops.services.agent_memory import calculate_relevance_score
from agentops.services.memory_safety import (
    MemoryValidationError,
    validate_memory_content,
    validate_memory_metadata,
    validate_memory_scope,
)


def test_memory_content_is_trimmed_and_kept_when_safe() -> None:
    assert validate_memory_content("  User prefers concise reports.  ") == (
        "User prefers concise reports."
    )


@pytest.mark.parametrize(
    "content",
    [
        "api_key=sk-12345678901234567890",
        "password: my-super-secret-password",
        "Authorization: Bearer abcdefghijklmnopqrstuvwxyz012345",
        "postgresql://agent:very-secret-password@localhost/db",
        "-----BEGIN PRIVATE KEY-----\\nabc\\n-----END PRIVATE KEY-----",
    ],
)
def test_memory_content_rejects_credential_patterns(content: str) -> None:
    with pytest.raises(MemoryValidationError, match="credential or secret"):
        validate_memory_content(content)


def test_memory_content_enforces_size_and_non_blank() -> None:
    with pytest.raises(MemoryValidationError, match="cannot be blank"):
        validate_memory_content("  ")
    with pytest.raises(MemoryValidationError, match="character limit"):
        validate_memory_content("x" * 11, max_chars=10)


def test_memory_metadata_is_bounded_and_secret_screened() -> None:
    assert validate_memory_metadata({"category": "preference"}) == {"category": "preference"}
    with pytest.raises(MemoryValidationError, match="credential or secret"):
        validate_memory_metadata({"config": "password=supersecret123"})
    with pytest.raises(MemoryValidationError, match="credential or secret"):
        validate_memory_metadata({"password": "1234567890"})
    with pytest.raises(MemoryValidationError, match="maximum allowed size"):
        validate_memory_metadata({"notes": "x" * 100}, max_bytes=20)


def test_memory_scope_requires_agent_key_only_for_agent_scope() -> None:
    assert validate_memory_scope("user", None) is None
    assert validate_memory_scope("agent", "analysis_agent") == "analysis_agent"
    with pytest.raises(MemoryValidationError, match="must not specify"):
        validate_memory_scope("user", "analysis_agent")
    with pytest.raises(MemoryValidationError, match="require a valid"):
        validate_memory_scope("agent", "Analysis Agent")


def test_create_schema_rejects_inconsistent_scope() -> None:
    with pytest.raises(ValidationError):
        MemoryCreateRequest(
            memory_type="semantic",
            memory_scope="agent",
            content="User prefers CSV reports.",
        )


def test_update_schema_allows_explicit_expiration_removal() -> None:
    payload = MemoryUpdateRequest(ttl_days=None)
    assert payload.model_fields_set == {"ttl_days"}


def test_update_schema_rejects_empty_patch() -> None:
    with pytest.raises(ValidationError):
        MemoryUpdateRequest()


def test_relevance_ranking_uses_similarity_importance_confidence_and_recency() -> None:
    recent = calculate_relevance_score(
        similarity=0.8,
        importance=0.9,
        confidence=0.9,
        age_days=1,
    )
    old = calculate_relevance_score(
        similarity=0.8,
        importance=0.9,
        confidence=0.9,
        age_days=365,
    )
    assert 0 <= old < recent <= 1


def test_relevance_ranking_clamps_out_of_range_inputs() -> None:
    score = calculate_relevance_score(
        similarity=2.0,
        importance=-1.0,
        confidence=1.0,
        age_days=-10.0,
    )
    assert 0 <= score <= 1
