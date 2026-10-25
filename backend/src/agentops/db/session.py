"""Database engine creation and connectivity check."""

import logging

from sqlalchemy import Engine, create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from agentops.core.config import Settings

logger = logging.getLogger(__name__)


def create_db_engine(settings: Settings) -> Engine:
    return create_engine(
        settings.database_url,
        pool_size=settings.db_pool_size,
        pool_pre_ping=True,  # drop dead pooled connections instead of failing a request
        connect_args={"connect_timeout": settings.db_connect_timeout_s},
    )


def check_database(engine: Engine) -> bool:
    """True if a trivial query succeeds. Never raises, never leaks details to callers."""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except SQLAlchemyError as exc:
        # Log only the error class: driver messages can include host/user details.
        logger.warning("database_check_failed", extra={"error": type(exc).__name__})
        return False
