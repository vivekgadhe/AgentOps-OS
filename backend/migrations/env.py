"""Alembic environment: online-only, with a mandatory safety check.

How the target database is chosen
---------------------------------
Only from the application settings (``DATABASE_URL``). Nothing is read from
``alembic.ini``, and there is no ``-x`` override for the URL.

What is verified before any migration runs
------------------------------------------
The database PostgreSQL itself reports via ``SELECT current_database()`` is
passed to ``assert_safe_migration_target`` (see ``agentops.db.guards``).
Tests may supply their own connection through
``config.attributes["connection"]``; the same check still runs on it.
"""

from __future__ import annotations

import logging
from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool, text
from sqlalchemy.engine import Connection, make_url

import agentops.db.models  # noqa: F401  (registers every table on the metadata)
from agentops.db.base import Base
from agentops.db.guards import (
    assert_safe_migration_target,
    command_name,
    is_under_pytest,
    load_runtime_target,
)

config = context.config
if config.config_file_name is not None and config.attributes.get("configure_logger", True):
    fileConfig(config.config_file_name, disable_existing_loggers=False)

logger = logging.getLogger("alembic.env")


def _verify_target(connection: Connection, app_env: str) -> None:
    database_name = str(connection.execute(text("SELECT current_database()")).scalar_one())
    command = command_name(config.cmd_opts)
    assert_safe_migration_target(
        database_name=database_name,
        app_env=app_env,
        under_pytest=is_under_pytest(),
        command=command,
        confirmed_database=context.get_x_argument(as_dictionary=True).get("confirm_db"),
    )
    logger.info(
        "Migration target verified: database=%s app_env=%s command=%s",
        database_name,
        app_env,
        command or "programmatic",
    )


def _configure_and_run(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=Base.metadata,
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    target = load_runtime_target()

    supplied: Connection | None = config.attributes.get("connection")
    if supplied is not None:
        # Test path: the caller owns the connection and its transaction.
        _verify_target(supplied, target.app_env)
        _configure_and_run(supplied)
        return

    url = make_url(target.database_url)
    if url.drivername != "postgresql+psycopg":
        raise RuntimeError(f"Unsupported driver {url.drivername!r}; use 'postgresql+psycopg'.")

    engine = create_engine(url, poolclass=pool.NullPool)
    try:
        # Verify on a separate connection so the migration connection does not
        # start with an implicit transaction (Alembic would then not commit).
        with engine.connect() as probe:
            _verify_target(probe, target.app_env)
        with engine.connect() as connection:
            _configure_and_run(connection)
    finally:
        engine.dispose()


if context.is_offline_mode():
    raise RuntimeError(
        "Offline (--sql) mode is not supported: the safety check must inspect "
        "the live target database."
    )
run_migrations_online()
