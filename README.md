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


---

## Frontend Documentation

# AgentOps-OS Frontend â€” Phase 1

Phase 1 delivers the React/TypeScript application foundation, shared design
tokens and UI primitives, login experience, protected routing, API client,
session restoration and an authenticated workspace shell.

## Stack

- React 19 + TypeScript
- Vite 8
- Tailwind CSS 4 (official Vite plugin)
- React Router 7
- TanStack Query 5
- Axios and Lucide React
- Vitest

Node.js 22.12 or newer is required by this Vite toolchain. The included
`.nvmrc` selects Node 22.16.0.

## Run locally

Start the existing backend from `backend/`:

```powershell
uv run uvicorn agentops.main:create_app --factory --reload --reload-dir src --port 8000
```

In a second terminal from `frontend/`:

```powershell
if (-not (Test-Path .env.local)) { Copy-Item .env.example .env.local }
npm install
npm run dev
```

Open `http://127.0.0.1:5173/login`. The Vite proxy forwards `/api/*` to
`http://127.0.0.1:8000` during development, avoiding permissive CORS settings.

## Backend authentication contract

| Method | Route | Request / response |
|---|---|---|
| POST | `/api/v1/auth/login` | `{ email, password }` â†’ `{ access_token, token_type }` |
| GET | `/api/v1/auth/me` | Bearer token â†’ `{ id, email, role, is_active }` |

The client validates a stored token against `/auth/me` on startup. It uses local
storage for the access token when Remember me is enabled and session storage
otherwise. The current backend issues expiring access tokens but has no refresh
route.

Account creation is public self-service. A visitor requests a six-digit,
single-use registration code by email, verifies it on `/register`, creates an
account with the default `operator` role, and is signed in automatically. The
public registration flow does not allow users to choose an administrator role.
The optional administrator invitation endpoints remain available for backward
compatibility but are not required for registration. Password recovery uses a
single-use email OTP on `/forgot-password`. SMTP must be configured in the
backend for registration and recovery emails. Use the backend user-management
CLI to bootstrap the initial administrator. See the Phase 1 implementation
documentation for the current API contract, CLI commands and migration
instructions.

## Validation

```powershell
npm run typecheck
npm test
npm run build
```

## Phase 1 boundary

This package includes authentication, API/session infrastructure, shared UI,
and a signed-in workspace shell. The functional dashboard, workflow designer,
knowledge screens, agent chat, memory, analytics and administration views are
part of the later agreed frontend implementation packages.


## Phase 2 â€” Dashboard, workflows and approvals

Phase 2 adds the authenticated operations dashboard, a React Flow workflow
builder, workflow run history and execution details, plus the human-approval
inbox and decision views.

Install the added graph dependency after extracting the Phase 2 package:

```powershell
npm install
```

If your package manager reports a lockfile mismatch, `npm install` will update
`package-lock.json` for the added `@xyflow/react` dependency. The project uses
React Flow from `@xyflow/react` (MIT-licensed).

### Backend APIs used

| Method | Route | Frontend use |
|---|---|---|
| GET | `/api/v1/observability/overview` | Workflow/task status counts for the dashboard chart and metrics |
| GET | `/api/v1/observability/workflows` | Recent workflow activity and workflow list summaries |
| GET | `/api/v1/knowledge/documents` | Knowledge document count |
| GET | `/api/v1/approvals` | Approval inbox and pending approval count |
| GET | `/api/v1/approvals/{approval_id}` | Approval details |
| POST | `/api/v1/approvals/{approval_id}/approve` | Admin approval decision |
| POST | `/api/v1/approvals/{approval_id}/reject` | Admin rejection decision |
| POST | `/api/v1/approvals/{approval_id}/cancel` | Requester/admin cancellation of a pending approval |
| POST | `/api/v1/runs` | Persist a workflow run and its task dependency graph |
| GET | `/api/v1/runs/{run_id}` | Fetch task-level run state and results |
| POST | `/api/v1/runs/{run_id}/execute` | Execute a workflow run |

### Execution model and current backend boundaries

The backend `WorkflowCreate` contract contains `goal` and `tasks`. Each task
contains `key`, `name`, optional `tool_name`, `input_data`, retry/timeout
settings and `depends_on`. The builder converts React Flow edges to
`depends_on` keys and validates that the graph is acyclic before sending it.
The executor decides task readiness from those dependencies.

The backend exposes tool tasks, not a separate visual agent registry. Agent
Step and Tool Step are therefore task nodes that call a registered backend
tool. The four built-in tool names currently present in the supplied source are
`summarize_input`, `text_statistics`, `normalize_whitespace`, and
`find_matching_lines`; additional tools may be registered server-side.

An Approval Step only produces an approval request when its selected tool is
already registered by trusted backend code with `requires_approval=True`. The
frontend cannot set that security-sensitive tool policy. The approval API
allows only administrators to approve/reject, prevents requesters from
approving their own action, and supports requester/admin cancellation.

Condition and Delay can be placed on the visual canvas to help sketch a future
workflow, but are explicitly marked as visual placeholders and block save/run.
The current API schema/executor does not implement conditional edge routing or
delayed execution. A connection represents a dependency: fan-out tasks are
all eligible after their prerequisite succeeds; it is not an if/else branch.

The current API also has no workflow template update route, workflow pause or
workflow cancellation endpoint, global execution-event listing endpoint, or
live-agent process inventory. Consequently:

- Save creates a persisted pending workflow run; it is not a reusable template.
- The Running Agents card is shown as unavailable because there is no live
  agent-process inventory endpoint. Its caption shows the actual count of
  running `TaskRun` rows when that count is returned.
- Execution timeline is derived from workflow/task timestamps returned by
  `/runs/{run_id}`; it is not a full event log.
- Unsupported pause/cancel controls are not displayed.

The dashboard is owner-scoped by the existing backend APIs. The pending
approval metric reflects the approvals visible to the signed-in role (admins
see the inbox; other roles see only requests they created). The chart is a
seven-day line chart grouped from actual workflow records and their current
statuses. Recent Activity combines actual workflow, approval and document
records; document items are not linked to a Knowledge screen in this phase.

The builder includes a **Load reference layout** action. It places the same
Planning Agent â†’ Analysis Agent â†’ Approval / Report â†’ Action Agent â†’ Generate
Report graph shown in the supplied visual reference. The example is a graph
layout, not a ready-to-run business automation: configure its sample inputs
and replace the approval/action tool names with tools registered by the
backend before saving or executing it.

### Phase 2 verification

```powershell
npm install
npm run typecheck
npm test
npm run build
```

Run the FastAPI backend and PostgreSQL service using the existing Phase 1
instructions. Sign in with a seeded account, then check `/app`, `/app/workflows`,
`/app/workflows/new`, `/app/approvals` and a workflow/approval detail route.

## Phase 3 â€” Knowledge, agents and memory

Phase 3 adds owner-scoped knowledge upload/index/search, the Analysis and Report
knowledge agents, and persistent agent memory management. The current backend
exposes the Analysis and Report knowledge operations but not generic agent
discovery, chat streaming or persistent chat sessions.

## Phase 4 â€” Analytics and administration

Phase 4 adds `/app/analytics` and `/app/settings`.

Analytics calls the Phase 10 owner-scoped observability endpoints for overview,
provider usage, agent-attributed generation, workflow summaries and safe
telemetry event history. Recharts is used for workflow/provider charts. The
current API has optional per-event token fields but no validated aggregate
token or cost report, so the UI does not invent those totals or cost estimates.

Settings uses the existing provider configuration and readiness APIs. The
current API supports provider list/configure/delete/test and administrator
invitations. It does not expose a user directory or role-edit endpoint, agent
or tool mutation endpoints, workspace preference persistence, editable
approval-policy routes or billing. The interface marks these areas as
read-only/informational rather than displaying nonfunctional controls.

Install Phase 4 chart dependencies and refresh the lockfile:

```powershell
npm install
```

Then verify:

```powershell
npm run typecheck
npm test
npm run build
```

Do not use `npm ci` until `npm install` has regenerated `package-lock.json` with
the newly added `recharts` and `react-is` dependencies.


---

## Authentication Implementation Notes

# Frontend authentication completion

The auth UI now includes three public routes:

- `/login` â€” existing sign-in form.
- `/register` â€” invitation-based registration form.
- `/forgot-password` â€” reset form for an administrator-issued one-time code.

Registration requires an invitation code issued by an active administrator.
After registration, the new user is signed in automatically with a session
(non-persistent) access token.

Password recovery requires a one-time code issued by an administrator. SMTP is
not configured in this project, so the application does not claim to send
password-reset emails. Ask the administrator for a code through a trusted
channel, then enter it on `/forgot-password`.

Backend endpoints and commands are documented in the repository-root file
`PHASE1_AUTH_COMPLETION.md`.
