# AgentOps-OS

AgentOps-OS is a Python-based AI agent execution platform for planning,
executing, verifying and analysing multi-step workflows. Its backend combines
FastAPI, PostgreSQL, SQLAlchemy, Alembic, a typed tool registry, multi-agent
orchestration, RAG and persistent agent memory.

**Project baseline:** Phase 9 (persistent agent memory), provided commit
`69a18ef`. The source archive intentionally excludes Git metadata, so that
commit identifier is the supplied baseline reference rather than an independently
verified Git revision.

**Phase 10 in this package:** observability and analytics, including a new
PostgreSQL telemetry table, provider-attributed LLM instrumentation, agent/RAG
attribution, authenticated analytics APIs, tests and documentation.

## Phase roadmap

| Phase | Scope | Source status |
|---|---|---|
| 1 | Requirements and architecture | Foundation |
| 2 | Database design, API contracts and project structure | Implemented |
| 3 | Workflow execution engine | Implemented |
| 4 | Tool registry, verification and failure recovery | Implemented |
| 5 | Dashboard and human approval interface | Backend approval capability exists; no frontend was included in the supplied archive |
| 6 | Testing, evaluation and security foundations | Implemented |
| 6.6 | Multi-agent workflow evaluation, quality checks, benchmarks and structured reports | Present in source |
| 7 | RAG and knowledge integration | Implemented |
| 8 | AI provider management and human approvals | Implemented |
| 9 | Persistent agent memory | Implemented |
| 10 | Observability and analytics | Implemented in this package; verify against the local database and commands below |
| 11 | Background execution and automation | Planned |
| 12 | Production readiness and deployment | Planned |

## Technology

- Python 3.12+
- FastAPI, Pydantic 2 and SQLAlchemy 2
- PostgreSQL with pgvector
- Alembic migrations
- Docker Compose
- Ollama for locally hosted generation and embeddings
- Pytest, Ruff and Mypy for quality checks

The default generation path can use local Ollama; hosted providers remain
optional and are not required for the Phase 10 telemetry layer.

## Quick start (Windows PowerShell)

From the repository root:

```powershell
Copy-Item .env.example .env -ErrorAction SilentlyContinue
# Adjust POSTGRES_PORT and DATABASE_URL in .env if the default port is occupied.
docker compose up -d --wait db
cd backend
uv sync --extra dev
uv run alembic upgrade head
uv run uvicorn agentops.main:create_app --factory --reload --port 8000
```

The existing Alembic target guard is still enforced. Run migrations only
against the intended development database; integration tests use a guarded
`agentops_test` database and disposable migration databases.

API docs are available at `http://localhost:8000/docs` in development mode.

## Phase 10 observability

All endpoints require a valid bearer token. Data is isolated by authenticated
user; each query filters by `owner_user_id` or the workflow creator.

| Endpoint | Purpose |
|---|---|
| `GET /api/v1/observability/overview` | Workflow/task status counts, success rates, average workflow/task duration and LLM latency |
| `GET /api/v1/observability/providers` | Generation attempts, outcomes and latency grouped by provider/model |
| `GET /api/v1/observability/agents` | LLM generation attempts attributed to each agent/RAG agent |
| `GET /api/v1/observability/workflows` | Paginated workflow summaries and task outcome counts |
| `GET /api/v1/observability/events` | Paginated safe telemetry event feed |
| `POST /api/v1/observability/telemetry/purge` | Operator/admin action to purge the current user's telemetry outside retention |

Analytics endpoints accept optional timezone-aware `start_at` and `end_at`
query parameters. The default reporting window is the previous 30 days.

### What is captured

- Provider and model identifier.
- Success, failure or refusal outcome.
- Generation-attempt duration.
- Request ID, and workflow ID when the caller supplies workflow context.
- Component attribution (`planner`, `agent`, `rag` or generic `llm`).
- Agent name when calls are made inside an attributed agent/RAG scope.
- Attempt number, fallback indicator and output schema name.

### Privacy and metric limitations

Telemetry intentionally does **not** retain prompts, instructions, model outputs,
API keys, provider response bodies or user-supplied content. The current
provider abstraction does not expose token usage, so `input_tokens` and
`output_tokens` remain null; token-based cost metrics are not claimed. Agent
analytics represent model-generation attempts attributed to an agent, not a
complete count of every agent invocation. Workflow/task metrics are sourced
from the existing workflow tables.

Telemetry persistence is best-effort and uses an independent short-lived
session: telemetry write failures are logged by error class and do not fail the
LLM request. The default retention setting is 90 days. Purging is an explicit
operator/admin API action and only affects the authenticated user's telemetry.

## Configuration

| Variable | Default | Purpose |
|---|---:|---|
| `APP_ENV` | `dev` | `dev`, `test` or `prod`; non-dev requires a strong JWT secret |
| `LOG_LEVEL` | `INFO` | Application log level |
| `LOG_FORMAT` | `console` | `console` or `json` |
| `DATABASE_URL` | Local PostgreSQL | Must use `postgresql+psycopg://` |
| `JWT_SECRET` | Dev placeholder | JWT signing secret; replace outside local development |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Local Ollama endpoint |
| `OLLAMA_CHAT_MODEL` | `qwen3.5:0.8b` | Default local chat model |
| `OLLAMA_EMBEDDING_MODEL` | `embeddinggemma` | Local embedding model |
| `OBSERVABILITY_ENABLED` | `true` | Enable provider-attempt telemetry instrumentation |
| `TELEMETRY_RETENTION_DAYS` | `90` | Retention cutoff used by the purge endpoint |

## Tests and quality checks

From the repository root:

```powershell
cd backend
uv run pytest -m "not integration"
uv run pytest -m integration
uv run pytest
uv run ruff check src tests
uv run ruff format --check src tests
uv run mypy src
```

Integration tests need a running PostgreSQL test database. Set
`AGENTOPS_REQUIRE_DB=1` to make an unreachable database fail the integration
run instead of being skipped. The integration fixture refuses non-test
 database names and creates disposable databases for migration tests.

## Phase documentation

- `PHASE8_IMPLEMENTATION.md`
- `backend/PHASE9_IMPLEMENTATION.md`
- `backend/PHASE10_IMPLEMENTATION.md`

## Important archive note

The supplied Phase 9 archive did not contain a frontend directory. This Phase
10 package therefore provides the observability backend APIs and does not
claim that a dashboard UI has been implemented.
