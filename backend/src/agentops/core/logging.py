"""Structured logging with automatic request correlation."""

import json
import logging
import sys
from datetime import UTC, datetime
from typing import Any

from agentops.core.context import request_id_var, run_id_var, user_id_var

# Attributes every LogRecord has; anything else came from `extra={...}`.
_STANDARD_ATTRS = frozenset(logging.LogRecord("", 0, "", 0, "", (), None).__dict__) | {
    "message",
    "asctime",
    "taskName",
}
_CONTEXT_FIELDS = ("request_id", "user_id", "run_id")
_HANDLER_MARKER = "_agentops_handler"


class ContextFilter(logging.Filter):
    """Copies the current context variables onto every record."""

    def filter(self, record: logging.LogRecord) -> bool:
        # Written via __dict__ because LogRecord does not declare these attributes (mypy strict).
        record.__dict__.update(
            request_id=request_id_var.get(),
            user_id=user_id_var.get(),
            run_id=run_id_var.get(),
        )
        return True


def _extra_fields(record: logging.LogRecord) -> dict[str, Any]:
    return {
        key: value
        for key, value in record.__dict__.items()
        if key not in _STANDARD_ATTRS
        and key not in _CONTEXT_FIELDS
        and key != "extras"
        and not key.startswith("_")
    }


class JsonFormatter(logging.Formatter):
    """One JSON object per line, for log aggregators."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for key in _CONTEXT_FIELDS:
            value = getattr(record, key, None)
            if value is not None:
                payload[key] = value
        payload.update(_extra_fields(record))
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


class ConsoleFormatter(logging.Formatter):
    """Readable single-line format for local development."""

    def __init__(self) -> None:
        super().__init__(
            "%(asctime)s %(levelname)-7s %(name)s [%(request_id)s] %(message)s %(extras)s"
        )

    def format(self, record: logging.LogRecord) -> str:
        if not record.__dict__.get("request_id"):
            record.__dict__["request_id"] = "-"
        record.__dict__["extras"] = " ".join(f"{k}={v}" for k, v in _extra_fields(record).items())
        return super().format(record)


def configure_logging(level: str, json_logs: bool) -> None:
    """Install one stdout handler on the root logger. Safe to call repeatedly."""
    handler = logging.StreamHandler(sys.stdout)
    setattr(handler, _HANDLER_MARKER, True)
    handler.addFilter(ContextFilter())
    handler.setFormatter(JsonFormatter() if json_logs else ConsoleFormatter())

    root = logging.getLogger()
    # Remove only handlers we installed earlier, so pytest's capture handlers survive.
    root.handlers[:] = [h for h in root.handlers if not getattr(h, _HANDLER_MARKER, False)]
    root.addHandler(handler)
    root.setLevel(level)

    # Route uvicorn's own logs through our handler instead of its default format.
    for name in ("uvicorn", "uvicorn.error"):
        uvicorn_logger = logging.getLogger(name)
        uvicorn_logger.handlers.clear()
        uvicorn_logger.propagate = True
    # We emit our own request log line (with request_id), so silence uvicorn's access log.
    access_logger = logging.getLogger("uvicorn.access")
    access_logger.handlers.clear()
    access_logger.propagate = False
