"""Unit tests for the database safety guards (no database needed)."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from agentops.db.guards import (
    UnsafeDatabaseTargetError,
    assert_disposable_database,
    assert_safe_migration_target,
    assert_test_database,
    command_name,
    is_test_safe_database,
)

SCRATCH = "agentops_mig_0123456789ab"


def _check(
    *,
    database_name: str,
    app_env: str = "dev",
    under_pytest: bool = False,
    command: str | None = "upgrade",
    confirmed_database: str | None = None,
) -> None:
    assert_safe_migration_target(
        database_name=database_name,
        app_env=app_env,
        under_pytest=under_pytest,
        command=command,
        confirmed_database=confirmed_database,
    )


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("agentops_test", True),
        ("something_test", True),
        (SCRATCH, True),
        ("agentops", False),
        ("agentops_prod", False),
        ("agentops_test_backup", False),
        ("agentops_mig_XYZ", False),
        ("agentops_mig_0123456789abc", False),
        ("", False),
        (None, False),
    ],
)
def test_is_test_safe_database(name: str | None, expected: bool) -> None:
    assert is_test_safe_database(name) is expected


def test_assert_test_database_rejects_dev_database() -> None:
    with pytest.raises(UnsafeDatabaseTargetError, match="agentops"):
        assert_test_database("agentops")


def test_assert_test_database_accepts_test_database() -> None:
    assert_test_database("agentops_test")


@pytest.mark.parametrize("name", [SCRATCH, "agentops_guard_0123456789ab"])
def test_disposable_names_are_accepted(name: str) -> None:
    assert_disposable_database(name)


@pytest.mark.parametrize("name", ["agentops", "agentops_test", "postgres", "agentops_mig_"])
def test_non_disposable_names_are_refused(name: str) -> None:
    with pytest.raises(UnsafeDatabaseTargetError):
        assert_disposable_database(name)


def test_under_pytest_the_dev_database_is_refused_even_for_upgrade() -> None:
    with pytest.raises(UnsafeDatabaseTargetError, match="pytest"):
        _check(database_name="agentops", under_pytest=True)


@pytest.mark.parametrize("name", ["agentops_test", SCRATCH])
def test_under_pytest_test_databases_are_allowed(name: str) -> None:
    _check(database_name=name, under_pytest=True, command="downgrade")


def test_app_env_test_refuses_the_dev_database() -> None:
    with pytest.raises(UnsafeDatabaseTargetError, match="APP_ENV=test"):
        _check(database_name="agentops", app_env="test")


def test_app_env_test_is_case_insensitive() -> None:
    with pytest.raises(UnsafeDatabaseTargetError):
        _check(database_name="agentops", app_env=" TEST ")


def test_upgrade_on_dev_database_is_allowed() -> None:
    _check(database_name="agentops", app_env="dev", command="upgrade")


@pytest.mark.parametrize("command", ["downgrade", "stamp", None, "something_new"])
def test_destructive_commands_on_dev_need_confirmation(command: str | None) -> None:
    with pytest.raises(UnsafeDatabaseTargetError, match="confirm_db=agentops"):
        _check(database_name="agentops", command=command)


def test_wrong_confirmation_is_refused() -> None:
    with pytest.raises(UnsafeDatabaseTargetError):
        _check(database_name="agentops", command="downgrade", confirmed_database="other")


def test_exact_confirmation_allows_destructive_command() -> None:
    _check(database_name="agentops", command="downgrade", confirmed_database="agentops")


def test_destructive_commands_on_test_database_need_no_confirmation() -> None:
    _check(database_name="agentops_test", app_env="test", command="downgrade")


def test_command_name_reads_alembic_cli_namespace() -> None:
    def downgrade() -> None: ...

    options = SimpleNamespace(cmd=(downgrade, ["-1"], {}))
    assert command_name(options) == "downgrade"


@pytest.mark.parametrize("options", [None, SimpleNamespace(), SimpleNamespace(cmd=None)])
def test_command_name_is_none_when_unknown(options: object) -> None:
    assert command_name(options) is None
