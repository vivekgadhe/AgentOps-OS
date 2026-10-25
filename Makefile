.DEFAULT_GOAL := help
.PHONY: help env up down logs install run test test-unit test-integration lint format typecheck

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-12s %s\n", $$1, $$2}'

env: ## Create .env from .env.example if missing
	@test -f .env || cp .env.example .env

up: env ## Start PostgreSQL and wait until it is healthy
	docker compose up -d --wait db

down: ## Stop containers (data volume is kept)
	docker compose down

logs: ## Tail database logs
	docker compose logs -f db

install: ## Install backend dependencies with uv
	cd backend && uv sync --extra dev

run: ## Run the API with auto-reload on http://localhost:8000
	cd backend && uv run uvicorn agentops.main:create_app --factory --reload --reload-dir src --port 8000

test: ## Run all tests (integration tests skip if PostgreSQL is down)
	cd backend && uv run pytest

test-unit: ## Run tests that do not need PostgreSQL
	cd backend && uv run pytest -m "not integration"

test-integration: ## Integration tests; FAILS (not skips) if the test DB is unreachable
	cd backend && REQUIRE_DB_TESTS=1 uv run pytest -m integration
	
lint: ## Static checks (ruff)
	cd backend && uv run ruff check src tests

format: ## Auto-format and fix import order
	cd backend && uv run ruff check --fix src tests && uv run ruff format src tests

typecheck: ## Type-check with mypy (strict)
	cd backend && uv run mypy src