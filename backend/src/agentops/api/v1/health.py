"""Liveness and readiness probes."""

from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import Engine

from agentops.api.deps import get_engine
from agentops.db.session import check_database
from agentops.schemas.health import LiveResponse, ReadyResponse

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/live", response_model=LiveResponse)
def live() -> LiveResponse:
    """The process is up. Deliberately checks nothing else."""
    return LiveResponse(status="ok")


@router.get(
    "/ready",
    response_model=ReadyResponse,
    responses={503: {"model": ReadyResponse}},
)
def ready(response: Response, engine: Annotated[Engine, Depends(get_engine)]) -> ReadyResponse:
    """The service can do useful work: the database answers a query."""
    if check_database(engine):
        return ReadyResponse(status="ok", db="up")
    response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return ReadyResponse(status="unavailable", db="down")
