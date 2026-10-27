"""Fixtures for the schema tests.

SAFETY RULES implemented here
-----------------------------
* The test database URL comes from ``TEST_DATABASE_URL`` or, if that is unset,
  from the application's DATABASE_URL with the database name FORCED to
  ``agentops_test``. The dev database name is never used.
* Whatever URL results is checked with ``assert_test_database`` before any
  connection is opened. A bad value fails the run loudly; it never falls back.
* If PostgreSQL is unreachable the tests are SKIPPED with a visible reason, or
  FAIL when ``AGENTOPS_REQUIRE_DB=1`` (use that in CI).
* Migration tests run in disposable ``agentops_mig_<hex>`` databases created
  and dropped here, never in ``agentops`` or ``agentops_test``.
"""

from __future__ import annotations

import os
import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.engine import URL, Connection, make_url
from sqlalchemy.exc import DBAPIError, IntegrityError, OperationalError
from sqlalchemy.orm import Session
from sqlalchemy.pool import NullPool

from agentops.db.guards import (
    TEST_DATABASE_NAME,
    assert_disposable_database,
    assert_test_database,
    load_runtime_target,
)
from tests.integration.db.factories import (
    AlembicConfigFactory,
    DisposableDatabaseFactory,
    ExpectDbError,
    Factory,
)

BACKEND_DIR = Path(__file__).resolve().parents[3]
REQUIRED_DRIVER = "postgresql+psycopg"


# --------------------------------------------------------------------------
# Test database location (guarded)
# --------------------------------------------------------------------------
@pytest.fixture(scope="session")
def pg_test_url() -> URL:
    explicit = os.environ.get("TEST_DATABASE_URL")
    if explicit:
        url = make_url(explicit)
    else:
        url = make_url(load_runtime_target().database_url).set(database=TEST_DATABASE_NAME)
    assert url.drivername == REQUIRED_DRIVER, (
        f"Test database URL must use {REQUIRED_DRIVER!r}, got {url.drivername!r}."
    )
    assert_test_database(url.database)  # raises UnsafeDatabaseTargetError
    return url


@pytest.fixture(scope="session")
def pg_test_engine(pg_test_url: URL) -> Iterator[Engine]:
    engine = create_engine(
    pg_test_url,
    poolclass=NullPool,
    connect_args={"connect_timeout": 5},
)
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except OperationalError as exc:
        engine.dispose()
        message = (
            f"PostgreSQL not reachable at {pg_test_url.host}:{pg_test_url.port} "
            f"(database {pg_test_url.database}). Start it with "
            "'docker compose up -d --wait db'."
        )
        if os.environ.get("AGENTOPS_REQUIRE_DB") == "1":
            pytest.fail(f"{message} ({exc.__class__.__name__})")
        pytest.skip(message)
    yield engine
    engine.dispose()


# --------------------------------------------------------------------------
# Alembic helpers
# --------------------------------------------------------------------------
@pytest.fixture(scope="session")
def make_alembic_config() -> AlembicConfigFactory:
    def build(connection: Connection) -> Config:
        config = Config(str(BACKEND_DIR / "alembic.ini"))
        config.attributes["connection"] = connection
        config.attributes["configure_logger"] = False
        return config

    return build


# --------------------------------------------------------------------------
# Disposable databases for migration tests
# --------------------------------------------------------------------------
@pytest.fixture
def disposable_database(
    pg_test_engine: Engine, pg_test_url: URL
) -> Iterator[DisposableDatabaseFactory]:
    """Create throw-away databases and always drop them afterwards."""
    created: list[str] = []
    admin = create_engine(
    pg_test_url,
    isolation_level="AUTOCOMMIT",
    poolclass=NullPool,
    connect_args={"connect_timeout": 5},
)

    def create(prefix: str) -> URL:
        name = f"{prefix}_{uuid.uuid4().hex[:12]}"
        assert_disposable_database(name)  # name pattern is validated BEFORE use
        with admin.connect() as connection:
            connection.execute(text(f'CREATE DATABASE "{name}"'))
        created.append(name)
        return pg_test_url.set(database=name)

    try:
        yield create
    finally:
        for name in created:
            assert_disposable_database(name)
            with admin.connect() as connection:
                connection.execute(text(f'DROP DATABASE IF EXISTS "{name}" WITH (FORCE)'))
        admin.dispose()


# --------------------------------------------------------------------------
# agentops_test at head + per-test rollback sessions
# --------------------------------------------------------------------------
@pytest.fixture(scope="session")
def migrated_engine(pg_test_engine: Engine, make_alembic_config: AlembicConfigFactory) -> Engine:
    """``agentops_test`` upgraded to head through Alembic (the real migration)."""
    with pg_test_engine.begin() as connection:
        command.upgrade(make_alembic_config(connection), "head")
    return pg_test_engine


@pytest.fixture
def orm_session(migrated_engine: Engine) -> Iterator[Session]:
    """A session whose work is rolled back at the end of each test."""
    connection = migrated_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection, join_transaction_mode="create_savepoint")
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def expect_db_error(orm_session: Session) -> ExpectDbError:
    """``with expect_db_error(match="ck_users_role_valid"): ...``

    Runs the block in a SAVEPOINT so the session stays usable afterwards, and
    requires the database error message to mention the expected constraint.
    """

    @contextmanager
    def expect(exc: type[DBAPIError] = IntegrityError, match: str | None = None) -> Iterator[None]:
        with pytest.raises(exc, match=match):
            with orm_session.begin_nested():
                yield

    return expect


@pytest.fixture
def factory(orm_session: Session) -> Factory:
    return Factory(orm_session)
