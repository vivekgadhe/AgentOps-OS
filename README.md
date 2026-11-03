# AgentOps OS

An AI agent execution platform that plans, executes, verifies, and monitors
multi-step business workflows. Built incrementally; see the phase roadmap.

**Current status:** Phase 2, Step 2.1 (scaffold, config, logging, health endpoints).
There is no workflow engine yet.

## Prerequisites

- Python 3.12
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- Docker with Compose v2
- make (optional; every target is a plain command you can run by hand)

## Quick start (uv)

```bash
make up        # creates .env if missing, starts PostgreSQL, waits until healthy
make install   # uv sync --extra dev
make run       # API on http://localhost:8000
```

Check it:

```bash
curl -i http://localhost:8000/api/v1/health/live
curl -i http://localhost:8000/api/v1/health/ready
```

API docs (dev only): http://localhost:8000/docs

## Quick start (pip, no uv)

```bash
cp .env.example .env
docker compose up -d --wait db
cd backend
python3.12 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
uvicorn agentops.main:create_app --factory --reload --port 8000
```

## Tests

```bash
make test-unit   # no database needed
make test        # also runs integration tests if PostgreSQL is reachable
```

Without pip/uv wrappers: `cd backend && pytest`.

## Configuration

All settings come from environment variables (or `.env`). They are validated
at startup, and the app refuses to start with invalid values.

| Variable | Default | Purpose |
|---|---|---|
| `APP_ENV` | `dev` | `dev`, `test`, or `prod`. Non-dev requires a strong `JWT_SECRET`. |
| `LOG_LEVEL` | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `LOG_FORMAT` | `console` | `console` for humans, `json` for log aggregators |
| `DATABASE_URL` | local Postgres | Must start with `postgresql+psycopg://` |
| `JWT_SECRET` | dev placeholder | Used from Step 2.3 onward |

## Troubleshooting

- **Port 5432 already in use:** change `POSTGRES_PORT` and the port inside `DATABASE_URL`.
- **`agentops_test` database missing:** the init script only runs the first time the
  volume is created. Run `docker compose down -v` (this DELETES local DB data) then `make up`.
- **`/health/ready` returns 503:** PostgreSQL is not reachable. Check `docker compose ps`.















































































# AgentOps OS

An AI agent execution platform that plans, executes, verifies, and monitors
multi-step business workflows. Built incrementally; see the phase roadmap.

**Current status:** Phase 8 is complete; Phase 9 (Persistent Agent Memory) is in progress.
See `backend/PHASE9_IMPLEMENTATION.md` for the Phase 9 design and API details.

## Phase roadmap

1. Requirements and architecture
2. Database design, API contracts and project structure
3. Workflow execution engine
4. Tool registry, verification and failure recovery
5. Dashboard and human approval interface
6. Testing, evaluation and security foundations
7. RAG and knowledge integration — complete
8. AI provider management and human approvals — complete
9. Persistent agent memory — in progress
10. Observability and analytics
11. Background execution and automation
12. Production readiness and deployment

## Prerequisites

- Python 3.12
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- Docker with Compose v2
- make (optional; every target is a plain command you can run by hand)

## Quick start (uv)

```bash
make up        # creates .env if missing, starts PostgreSQL, waits until healthy
make install   # uv sync --extra dev
make run       # API on http://localhost:8000
```

Check it:

```bash
curl -i http://localhost:8000/api/v1/health/live
curl -i http://localhost:8000/api/v1/health/ready
```

API docs (dev only): http://localhost:8000/docs

## Quick start (pip, no uv)

```bash
cp .env.example .env
docker compose up -d --wait db
cd backend
python3.12 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
uvicorn agentops.main:create_app --factory --reload --port 8000
```

## Tests

```bash
make test-unit   # no database needed
make test        # also runs integration tests if PostgreSQL is reachable
```

Without pip/uv wrappers: `cd backend && pytest`.

## Configuration

All settings come from environment variables (or `.env`). They are validated
at startup, and the app refuses to start with invalid values.

| Variable | Default | Purpose |
|---|---|---|
| `APP_ENV` | `dev` | `dev`, `test`, or `prod`. Non-dev requires a strong `JWT_SECRET`. |
| `LOG_LEVEL` | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `LOG_FORMAT` | `console` | `console` for humans, `json` for log aggregators |
| `DATABASE_URL` | local Postgres | Must start with `postgresql+psycopg://` |
| `JWT_SECRET` | dev placeholder | Used from Step 2.3 onward |

## Troubleshooting

- **Port 5432 already in use:** change `POSTGRES_PORT` and the port inside `DATABASE_URL`.
- **`agentops_test` database missing:** the init script only runs the first time the
  volume is created. Create the test database without deleting the existing volume:
  `docker compose exec db psql -U agentops -d agentops -c "CREATE DATABASE agentops_test;"`.
- **`/health/ready` returns 503:** PostgreSQL is not reachable. Check `docker compose ps`.