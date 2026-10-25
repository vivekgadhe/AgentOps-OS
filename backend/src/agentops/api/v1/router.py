"""Aggregates all v1 routers. Each new resource adds one line here."""

from fastapi import APIRouter

from agentops.api.v1 import health

api_router = APIRouter()
api_router.include_router(health.router)
