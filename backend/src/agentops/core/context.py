"""Per-request context shared by logging, audit records, and (later) the engine."""

from contextvars import ContextVar

request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)
user_id_var: ContextVar[str | None] = ContextVar("user_id", default=None)
run_id_var: ContextVar[str | None] = ContextVar("run_id", default=None)
