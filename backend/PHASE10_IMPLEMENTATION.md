# Phase 10 — Observability and Analytics

**Baseline:** Phase 9 persistent agent memory; provided reference commit
`69a18ef` (the uploaded archive omitted `.git`, so the commit cannot be verified
from this package).

**Migration:** `0005_observability_telemetry.py`, following `0004`.

## Scope delivered

Phase 10 adds a privacy-conscious telemetry layer and authenticated analytics
APIs while reusing existing workflow/task records for execution metrics.

### 1. Persistent telemetry

New table: `telemetry_events`.

Each row represents one structured LLM provider attempt and records:

- Owning user and optional workflow ID.
- Request ID and component attribution.
- Optional agent name.
- Provider and model identifiers.
- `success`, `failure` or `refused` outcome.
- Duration in milliseconds.
- Optional token counts (currently null because the provider protocol does not
  expose usage metadata).
- Error class name, never the provider exception message.
- Small, allow-listed JSON attributes: attempt number, fallback indicator and
  output schema name.

Indexes support owner/date, provider/date, agent/date and workflow lookups.
Foreign keys preserve user ownership and null the workflow reference if a
workflow is removed.

### 2. Instrumentation

`ProviderManager` times each provider attempt, including attempts that fail
before a fallback succeeds. The instrumentation records provider/model,
outcome, latency and safe attribution. Context-local scopes distinguish
planner, agent and RAG generation calls. `request_id` comes from the existing
request middleware; an orchestration workflow ID is attached when a state store
supplies it.

The telemetry recorder uses a separate SQLAlchemy session and is best-effort.
It catches persistence failures so telemetry cannot become a dependency for
successful generation. It logs only the exception class.

### 3. Analytics API

All endpoints require authentication and return only the current user's data.
The default date window is the prior 30 days; explicit ranges must be
timezone-aware and have `start_at < end_at`.

- `GET /api/v1/observability/overview`
- `GET /api/v1/observability/providers`
- `GET /api/v1/observability/agents`
- `GET /api/v1/observability/workflows`
- `GET /api/v1/observability/events`
- `POST /api/v1/observability/telemetry/purge`

The purge endpoint requires `admin` or `operator` and deletes only the current
user's telemetry older than `TELEMETRY_RETENTION_DAYS`.

### 4. Privacy boundaries and known limitations

Prompts, instructions, generated text, credentials, provider response bodies
and arbitrary user content are never passed to the recorder. Error messages are
not persisted. Agent usage is an aggregate of model-generation attempts
attributed to agents; it is not a complete count of agent invocations. Workflow
and task metrics are calculated from the established workflow tables.

Token counts and provider cost estimates are intentionally not reported. The
current `StructuredGenerator` abstraction returns validated Pydantic objects
but does not surface reliable usage metadata. A later provider-contract change
can add token usage without changing the telemetry privacy boundary.

The uploaded repository contained no frontend, so this phase exposes APIs but
does not claim a dashboard UI.

## Configuration

- `OBSERVABILITY_ENABLED=true` enables provider-attempt instrumentation.
- `TELEMETRY_RETENTION_DAYS=90` configures the retention cutoff used by the
  manual purge endpoint.

Both settings have validated defaults in `agentops.core.config.Settings`.

## Database migration

From `backend/`:

```powershell
uv run alembic upgrade head
uv run alembic current
```

The migration inherits the project's existing database target guard. Confirm
the target database before running migrations; do not bypass the guard.

## Verification

From `backend/`:

```powershell
uv run pytest -m "not integration"
uv run pytest -m integration
uv run pytest
uv run ruff check src tests
uv run ruff format --check src tests
uv run mypy src
```

Integration tests use the guarded `agentops_test` database and disposable
`agentops_mig_*` databases for migration round trips. Set
`AGENTOPS_REQUIRE_DB=1` to fail rather than skip when PostgreSQL is unavailable.

## Suggested manual smoke test

1. Upgrade the intended development database to `head`.
2. Start Ollama locally and configure the user's Ollama provider, or use the
   configured local fallback.
3. Call `POST /api/v1/runs/plan` with an authorized workflow goal.
4. Call `GET /api/v1/observability/overview` and
   `GET /api/v1/observability/providers` using the same bearer token.
5. Confirm provider attempts appear with latency and outcome, while prompts and
   model outputs do not appear in telemetry.
6. Configure another user and verify that their analytics endpoints cannot
   return the first user's rows.

A planner attempt is recorded only when `OBSERVABILITY_ENABLED=true` and the
`telemetry_events` migration has been applied.
