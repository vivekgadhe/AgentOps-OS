"""Aggregates all v1 API routers."""

from fastapi import APIRouter

from agentops.api.v1 import auth, health, knowledge, runs

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(runs.router)
api_router.include_router(knowledge.router)