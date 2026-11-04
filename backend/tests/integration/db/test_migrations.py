"""Migrations, run only in DISPOSABLE databases (never dev, never agentops_test).

Each test asks ``disposable_database`` for a brand-new ``agentops_mig_<hex>``
database, which is dropped afterwards even if the test fails.
"""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.runtime.migration import MigrationContext
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import URL, Engine
from sqlalchemy.pool import NullPool

from agentops.db.base import Base
from agentops.db.guards import UnsafeDatabaseTargetError
from tests.integration.db.factories import AlembicConfigFactory, DisposableDatabaseFactory

EXPECTED_TABLES = {
    "users",
    "workflow_runs",
    "task_runs",
    "task_dependencies",
    "execution_events",
    "audit_logs",
    "knowledge_documents",
    "knowledge_chunks",
    "ai_provider_configs",
    "approval_requests",
    "agent_memories",
    "telemetry_events",
}

EXPECTED_AUDIT_TRIGGERS = {"audit_logs_no_update_delete", "audit_logs_no_truncate"}
HEAD_REVISION = "0005"


def _ignore_version_table(
    _obj: object, name: str | None, type_: str, _reflected: bool, _compare: object
) -> bool:
    return not (type_ == "table" and name == "alembic_version")


def _engine(url: URL) -> Engine:
    return create_engine(
        url,
        poolclass=NullPool,
        connect_args={"connect_timeout": 5},
    )


def _tables(engine: Engine) -> set[str]:
    return set(inspect(engine).get_table_names())


def _upgrade(engine: Engine, make_config: AlembicConfigFactory, revision: str = "head") -> None:
    with engine.begin() as connection:
        command.upgrade(make_config(connection), revision)


def _downgrade(engine: Engine, make_config: AlembicConfigFactory, revision: str = "base") -> None:
    with engine.begin() as connection:
        command.downgrade(make_config(connection), revision)


@pytest.fixture
def scratch_engine(
    disposable_database: DisposableDatabaseFactory,
) -> Iterator[Engine]:
    """Engine bound to a brand-new, empty agentops_mig_<hex> database."""
    engine = _engine(disposable_database("agentops_mig"))
    try:
        yield engine
    finally:
        engine.dispose()


def test_upgrade_creates_every_table_and_records_the_revision(
    scratch_engine: Engine, make_alembic_config: AlembicConfigFactory
) -> None:
    _upgrade(scratch_engine, make_alembic_config)
    assert _tables(scratch_engine) == EXPECTED_TABLES | {"alembic_version"}
    with scratch_engine.connect() as connection:
        current = MigrationContext.configure(connection).get_current_revision()
    assert current == HEAD_REVISION


def test_upgrade_downgrade_upgrade_round_trip(
    scratch_engine: Engine, make_alembic_config: AlembicConfigFactory
) -> None:
    _upgrade(scratch_engine, make_alembic_config)
    _downgrade(scratch_engine, make_alembic_config, "base")
    assert _tables(scratch_engine) == {"alembic_version"}
    with scratch_engine.connect() as connection:
        leftover = connection.execute(
            text("SELECT count(*) FROM pg_proc WHERE proname = 'audit_logs_reject_mutation'")
        ).scalar_one()
    assert leftover == 0

    _upgrade(scratch_engine, make_alembic_config)
    assert _tables(scratch_engine) == EXPECTED_TABLES | {"alembic_version"}


def test_upgrade_is_idempotent_when_already_at_head(
    scratch_engine: Engine, make_alembic_config: AlembicConfigFactory
) -> None:
    _upgrade(scratch_engine, make_alembic_config)
    _upgrade(scratch_engine, make_alembic_config)
    assert _tables(scratch_engine) == EXPECTED_TABLES | {"alembic_version"}


def test_audit_triggers_are_installed(
    scratch_engine: Engine, make_alembic_config: AlembicConfigFactory
) -> None:
    _upgrade(scratch_engine, make_alembic_config)
    with scratch_engine.connect() as connection:
        names = set(
            connection.execute(
                text(
                    "SELECT tgname FROM pg_trigger "
                    "WHERE tgrelid = 'audit_logs'::regclass AND NOT tgisinternal"
                )
            ).scalars()
        )
    assert names == EXPECTED_AUDIT_TRIGGERS


def test_no_drift_between_models_and_migrations(
    scratch_engine: Engine, make_alembic_config: AlembicConfigFactory
) -> None:
    """If this fails, the ORM models and migration chain disagree.

    The assertion message lists exactly what differs: fix the model, or add a
    new migration. (Server-default comparison is the most likely source of a
    false positive; read the diff before changing anything.)
    """
    _upgrade(scratch_engine, make_alembic_config)
    with scratch_engine.connect() as connection:
        context = MigrationContext.configure(
            connection,
            opts={
                "compare_type": True,
                "compare_server_default": True,
                "include_object": _ignore_version_table,
            },
        )
        differences = compare_metadata(context, Base.metadata)
    assert differences == [], f"Model/migration drift detected: {differences}"


def test_env_py_refuses_a_non_test_database_while_pytest_is_running(
    disposable_database: DisposableDatabaseFactory,
    make_alembic_config: AlembicConfigFactory,
) -> None:
    """End-to-end proof that env.py enforces the guard on the REAL database name.

    ``agentops_guard_<hex>`` is a disposable database whose name does not look
    like a test database, so env.py must refuse to migrate it, and must do so
    before creating any table.
    """
    engine = _engine(disposable_database("agentops_guard"))
    try:
        with pytest.raises(UnsafeDatabaseTargetError):
            _upgrade(engine, make_alembic_config)
        assert _tables(engine) == set()
    finally:
        engine.dispose()
