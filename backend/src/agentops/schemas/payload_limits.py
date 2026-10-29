"""Safety limits for JSON-compatible agent payloads."""

import json
import math
from typing import Any

MAX_PAYLOAD_DEPTH = 12
MAX_PAYLOAD_NODES = 10_000

MAX_CONTEXT_PRIOR_RESULTS_BYTES = 512 * 1024
MAX_CONTEXT_METADATA_BYTES = 32 * 1024
MAX_AGENT_OUTPUT_BYTES = 256 * 1024


def validate_json_payload_size[PayloadT](
    value: PayloadT,
    *,
    field_name: str,
    max_bytes: int,
) -> PayloadT:
    """Validate JSON-compatible data against depth, item, and size limits."""
    if max_bytes < 1:
        raise ValueError("max_bytes must be positive.")

    stack: list[tuple[Any, int]] = [(value, 0)]
    node_count = 0
    estimated_bytes = 2

    while stack:
        item, depth = stack.pop()
        node_count += 1

        if node_count > MAX_PAYLOAD_NODES:
            raise ValueError(f"{field_name} contains too many values.")

        if depth > MAX_PAYLOAD_DEPTH:
            raise ValueError(f"{field_name} exceeds the maximum nesting depth.")

        if item is None:
            estimated_bytes += 4

        elif isinstance(item, bool):
            estimated_bytes += 5 if item else 6

        elif isinstance(item, int):
            estimated_bytes += len(str(item))

        elif isinstance(item, float):
            if not math.isfinite(item):
                raise ValueError(f"{field_name} contains a non-finite number.")
            estimated_bytes += len(repr(item))

        elif isinstance(item, str):
            if len(item) > max_bytes:
                raise ValueError(f"{field_name} exceeds the maximum allowed size.")
            estimated_bytes += len(item.encode("utf-8")) + 2

        elif isinstance(item, list):
            if node_count + len(stack) + len(item) > MAX_PAYLOAD_NODES:
                raise ValueError(f"{field_name} contains too many values.")

            estimated_bytes += 2 + max(0, len(item) - 1)
            stack.extend((child, depth + 1) for child in item)

        elif isinstance(item, dict):
            if node_count + len(stack) + len(item) > MAX_PAYLOAD_NODES:
                raise ValueError(f"{field_name} contains too many values.")

            estimated_bytes += 2 + max(0, len(item) - 1)

            for key, child in item.items():
                if not isinstance(key, str):
                    raise ValueError(f"{field_name} must use string keys.")

                if len(key) > max_bytes:
                    raise ValueError(f"{field_name} exceeds the maximum allowed size.")

                estimated_bytes += len(key.encode("utf-8")) + 3
                stack.append((child, depth + 1))

        else:
            raise ValueError(f"{field_name} must contain only JSON-compatible values.")

        if estimated_bytes > max_bytes:
            raise ValueError(f"{field_name} exceeds the maximum allowed size.")

    try:
        serialized = json.dumps(
            value,
            ensure_ascii=False,
            separators=(",", ":"),
            allow_nan=False,
        )
    except (TypeError, ValueError, OverflowError, RecursionError) as exc:
        raise ValueError(f"{field_name} must contain valid JSON-compatible values.") from exc

    if len(serialized.encode("utf-8")) > max_bytes:
        raise ValueError(f"{field_name} exceeds the maximum allowed size.")

    return value
