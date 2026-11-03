# AgentOps-OS Phase 9 — Persistent Agent Memory

Phase 9 adds a persistent memory subsystem alongside (not inside) the Phase 7
uploaded-document knowledge base. Memory records are owned by a user and can be
shared across that user's agents or scoped to one agent key.

## Memory types and scopes

- **Episodic** memories record concise outcomes or experiences from earlier work.
- **Semantic** memories record reusable facts or preferences.
- **User scope** makes a memory available to all of that user's agents.
- **Agent scope** makes a memory available only to the matching agent key, in
  addition to user-scoped memories.

All memory vectors use the existing 768-dimensional `embeddinggemma` model and
PostgreSQL/pgvector infrastructure. Embeddings are generated locally through
Ollama. The vector is never returned from the API.

## API

All routes require a valid bearer token. Memory writes and deletions require an
`admin` or `operator` role. Each operation is scoped to the authenticated user.

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/v1/memories` | Create a semantic or episodic memory |
| GET | `/api/v1/memories` | List active owned memories |
| POST | `/api/v1/memories/search` | Search user and optional matching-agent memories |
| GET | `/api/v1/memories/{memory_id}` | Retrieve one owned memory |
| PATCH | `/api/v1/memories/{memory_id}` | Update content, importance or TTL |
| DELETE | `/api/v1/memories/{memory_id}` | Permanently forget one owned memory |
| DELETE | `/api/v1/memories/expired` | Permanently purge expired owned memories |

Example create request:

```json
{
  "memory_type": "semantic",
  "memory_scope": "user",
  "content": "The user prefers concise operational summaries.",
  "importance": 0.7,
  "ttl_days": 90,
  "metadata_json": {"category": "format_preference"}
}
```

For an agent-scoped record, set `memory_scope` to `agent` and supply a lowercase
`agent_key`, such as `analysis_agent`. A `ttl_days` value of zero disables
expiration. On create, an omitted TTL uses `MEMORY_DEFAULT_TTL_DAYS` (90 days by
default). On PATCH, omitted TTL leaves the current expiry unchanged; explicit
`null` or zero removes expiry.

Search request:

```json
{
  "query": "How should I format operational summaries?",
  "agent_key": "analysis_agent",
  "top_k": 5
}
```

Search includes user-scoped memories plus memories for the specified agent key.
Without an `agent_key`, only user-scoped memories are considered.

## Retrieval and ranking

The service performs cosine-distance retrieval over active vectors, then ranks
candidates using a bounded weighted score:

- 70% semantic similarity
- 15% importance
- 10% confidence
- 5% recency (90-day exponential decay)

Only the authenticated user's rows can be considered. Agent-specific rows are
included only when the matching `agent_key` is provided. This retrieval is wired
into both the RAG Analysis/Report API agents and `AgentOrchestrator` when a trusted
owner ID and memory service are supplied. Expired memories are excluded from reads
and retrieval; the purge endpoint physically deletes them.

## Safety and retention

- The API never accepts `source_type` or `source_workflow_run_id`; manual API
  writes are tagged as user-sourced by trusted server code.
- Stored text and metadata are screened for common credential patterns before
  embedding and persistence. This is best-effort screening, not a guarantee;
  never intentionally save credentials or secrets in memory.
- Retrieved memories are passed to agents as **untrusted reference data**. They
  cannot authorize tools, override system instructions, or supersede the
  current request. Agents are instructed not to follow instructions found in
  memories and to verify factual claims against current evidence.
- Automatic capture of successful RAG interactions is opt-in and defaults to
  off. Enable it with `MEMORY_AUTO_CAPTURE_RAG=true` after deciding that the
  retention behavior is appropriate. Captures are compact episodic memories
  scoped to the agent that produced them.
- `AgentOrchestrator` also supports injected memory retrieval. Its constructor
  accepts `memory_service`, `auto_capture_memory` and `memory_top_k`; its `run`
  method requires `owner_user_id` whenever memory is enabled. Orchestration-task
  auto-capture is off unless explicitly enabled by trusted application code.
- The default TTL is 90 days. Change `MEMORY_DEFAULT_TTL_DAYS` to adjust it.

## Migration and configuration

Phase 9 adds Alembic revision `0004` after revision `0003`. It creates
`agent_memories` and its user/scope, expiry and HNSW vector indexes.

New environment settings:

| Setting | Default | Purpose |
|---|---:|---|
| `MEMORY_MAX_CONTENT_CHARS` | `5000` | Maximum content length |
| `MEMORY_DEFAULT_TTL_DAYS` | `90` | Default memory retention |
| `MEMORY_AUTO_CAPTURE_RAG` | `false` | Opt in to capturing successful RAG interactions |
| `MEMORY_RETRIEVAL_TOP_K` | `5` | Number of memories supplied to RAG agents |

No hosted model API is required for memory embeddings or retrieval.

## Verification

Run commands from `backend/`. The migration is additive; it creates the new
`agent_memories` table and indexes. Do not run Alembic downgrade commands.

First, apply the migration to the development database configured by
`DATABASE_URL`:

```powershell
uv sync --extra dev
uv run alembic upgrade head
```

Before integration tests, apply the same migration to the dedicated test
database. This reads `TEST_DATABASE_URL` from the process environment or the
repository-root `.env`, checks that the URL's database name ends in `_test`,
and temporarily uses it as Alembic's `DATABASE_URL` without printing it:

```powershell
$testDbUrl = $env:TEST_DATABASE_URL
if (-not $testDbUrl) {
    $testDbLine = Get-Content ..\.env | Where-Object { $_ -match '^\s*TEST_DATABASE_URL\s*=' } | Select-Object -First 1
    if ($testDbLine) {
        $testDbUrl = ($testDbLine -split '=', 2)[1].Trim().Trim('"').Trim("'")
    }
}
if (-not $testDbUrl -or $testDbUrl -notmatch '/[^/?]+_test(?:\?.*)?$') {
    throw 'TEST_DATABASE_URL must point to a database whose name ends in _test.'
}
$previousDatabaseUrl = $env:DATABASE_URL
try {
    $env:DATABASE_URL = $testDbUrl
    uv run alembic upgrade head
}
finally {
    if ($null -eq $previousDatabaseUrl) {
        Remove-Item Env:DATABASE_URL -ErrorAction SilentlyContinue
    }
    else {
        $env:DATABASE_URL = $previousDatabaseUrl
    }
}
```

Then run verification:

```powershell
uv run pytest -m "not integration"
$env:REQUIRE_DB_TESTS = "1"
uv run pytest -m integration
Remove-Item Env:REQUIRE_DB_TESTS
uv run ruff check src tests
uv run ruff format --check src tests
uv run mypy src
```

The integration fixture independently reads `TEST_DATABASE_URL` and refuses
to run unless its database name ends in `_test`. Keep development and test
database URLs separate. No data-volume deletion or database downgrade is
required for this phase.
