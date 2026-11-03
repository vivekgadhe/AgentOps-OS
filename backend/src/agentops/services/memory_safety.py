"""Input validation for persistent agent memories.

Memory content is user-controlled or model-derived reference data. This module
provides conservative secret screening and structural validation before any
content is embedded or persisted. It is not a substitute for secret management.
"""

from __future__ import annotations

import json
import re
from typing import Any, Literal

from agentops.schemas.payload_limits import validate_json_payload_size

MemoryScope = Literal["user", "agent"]

_SECRET_PATTERNS = (
    re.compile(
        r"(?i)['\"]?\b(?:api[_ -]?key|client[_ -]?secret|password|passwd|secret|"
        r"access[_ -]?token|refresh[_ -]?token|private[_ -]?key)\b['\"]?"
        r"\s*[:=]\s*['\"]?[^\s'\",}]{8,}"
    ),
    re.compile(r"\bsk-[A-Za-z0-9_-]{16,}\b"),
    re.compile(r"\bgsk_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{12,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"(?i)-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]{16,}"),
    re.compile(r"(?i)postgres(?:ql)?://[^\s:/@]+:[^\s@]+@"),
    re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\b"),
)
_AGENT_KEY_PATTERN = re.compile(r"^[a-z][a-z0-9_]{0,99}$")


class MemoryValidationError(ValueError):
    """Raised when memory content or metadata is unsafe or invalid."""


def validate_memory_content(content: str, *, max_chars: int = 5_000) -> str:
    """Normalize and validate content before embedding or persistence."""
    if not isinstance(content, str):
        raise MemoryValidationError("Memory content must be text.")

    normalized = content.strip()
    if not normalized:
        raise MemoryValidationError("Memory content cannot be blank.")
    if len(normalized) > max_chars:
        raise MemoryValidationError(
            f"Memory content exceeds the configured {max_chars}-character limit."
        )

    for pattern in _SECRET_PATTERNS:
        if pattern.search(normalized):
            raise MemoryValidationError(
                "Memory content appears to contain a credential or secret. "
                "Remove it before saving the memory."
            )

    return normalized


def validate_memory_metadata(
    metadata: dict[str, Any],
    *,
    max_bytes: int = 4_096,
) -> dict[str, Any]:
    """Require small JSON metadata and screen string values for credentials."""
    try:
        validate_json_payload_size(
            metadata,
            field_name="Memory metadata",
            max_bytes=max_bytes,
        )
        serialized = json.dumps(metadata, ensure_ascii=False, allow_nan=False)
    except (TypeError, ValueError, RecursionError) as exc:
        message = str(exc) or "Memory metadata must be small, valid JSON."
        raise MemoryValidationError(message) from exc

    # The same conservative rules apply to metadata values, not just content.
    validate_memory_content(serialized, max_chars=max_bytes)
    return metadata


def validate_memory_scope(scope: MemoryScope, agent_key: str | None) -> str | None:
    """Enforce a coherent user-wide or agent-specific memory scope."""
    if scope == "user":
        if agent_key is not None:
            raise MemoryValidationError("User-scoped memories must not specify an agent key.")
        return None

    if scope != "agent":
        raise MemoryValidationError("Memory scope must be 'user' or 'agent'.")
    if not isinstance(agent_key, str) or not _AGENT_KEY_PATTERN.fullmatch(agent_key):
        raise MemoryValidationError("Agent-scoped memories require a valid lowercase agent key.")
    return agent_key
