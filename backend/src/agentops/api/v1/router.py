"""Aggregates all v1 API routers."""

from fastapi import APIRouter

from agentops.api.v1 import ai_providers, approvals, auth, health, knowledge, runs

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(runs.router)
api_router.include_router(knowledge.router)
api_router.include_router(ai_providers.router)
api_router.include_router(approvals.router)
