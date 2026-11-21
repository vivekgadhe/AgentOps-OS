"""FastAPI application factory."""

import logging
from collections.abc import AsyncIterator, Sequence
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.engine import make_url

from agentops import __version__
from agentops.api.v1.router import api_router
from agentops.core.config import Settings, get_settings
from agentops.core.logging import configure_logging
from agentops.core.middleware import RequestContextMiddleware
from agentops.db.session import create_db_engine
from agentops.services.handlers import ToolRegistrar

logger = logging.getLogger(__name__)


def create_app(
    settings: Settings | None = None,
    *,
    tool_registrars: Sequence[ToolRegistrar] = (),
) -> FastAPI:
    settings = settings or get_settings()
    configure_logging(level=settings.log_level, json_logs=settings.log_format == "json")
    engine = create_db_engine(settings)

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        db = make_url(settings.database_url)
        logger.info(
            "app_starting",
            extra={
                "environment": settings.app_env,
                "version": __version__,
                "database": f"{db.host}:{db.port}/{db.database}",
            },
        )
        yield
        engine.dispose()
        logger.info("app_stopped")

    is_prod = settings.app_env == "prod"

    app = FastAPI(
        title=settings.app_name,
        version=__version__,
        lifespan=lifespan,
        docs_url=None if is_prod else "/docs",
        redoc_url=None if is_prod else "/redoc",
        openapi_url=None if is_prod else "/openapi.json",
    )

    app.state.settings = settings
    app.state.engine = engine

    app.state.tool_registrars = tuple(tool_registrars)

    app.add_middleware(RequestContextMiddleware)

    # Allow the deployed Vercel frontend and local development frontend.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "https://agentops-os.vercel.app",
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix=settings.api_prefix)

    return app