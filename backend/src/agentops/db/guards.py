"""Safety checks that keep migrations and tests away from the wrong database.

Nothing in this module talks to a database. It only decides, from names and
flags, whether an operation is allowed, so it can be unit-tested without
PostgreSQL. ``migrations/env.py`` and the integration-test fixtures call it.

Rules, in plain words:

* Under pytest, only databases named ``*_test`` or disposable scratch
  databases (``agentops_mig_<12 hex>``) may be used.
* With ``APP_ENV=test`` the same restriction applies.
* A destructive command (``downgrade``, ``stamp``, or anything unknown) on any
  other database needs ``-x confirm_db=<exact database name>``.
"""

from __future__ import annotations

import importlib
import os
import re
import sys
from dataclasses import dataclass
from typing import Final

TEST_DATABASE_NAME: Final = "agentops_test"
SCRATCH_DATABASE_PATTERN: Final = re.compile(r"^agentops_mig_[0-9a-f]{12}$")
GUARD_PROBE_DATABASE_PATTERN: Final = re.compile(r"^agentops_guard_[0-9a-f]{12}$")

# Commands that never remove data. Anything NOT listed (including unknown or
# programmatic invocations) is treated as destructive: the guard fails closed.
NON_DESTRUCTIVE_COMMANDS: Final = frozenset({"upgrade", "current", "check", "revision"})


class UnsafeDatabaseTargetError(RuntimeError):
    """Raised when an operation would touch a database it must not touch."""


@dataclass(frozen=True)
class RuntimeTarget:
    """Database URL and environment name as resolved from application settings."""

    database_url: str
    app_env: str


def is_test_safe_database(name: str | None) -> bool:
    """True for ``*_test`` databases and disposable scratch databases."""
    if not name:
        return False
    if name.endswith("_test"):
        return True
    return SCRATCH_DATABASE_PATTERN.fullmatch(name) is not None


def assert_test_database(name: str | None) -> None:
    """Refuse to continue unless ``name`` is a test-safe database."""
    if not is_test_safe_database(name):
        raise UnsafeDatabaseTargetError(
            f"Refusing to use database {name!r} for tests: the name must end "
            "with '_test' (or be a disposable agentops_mig_* database)."
        )


def assert_disposable_database(name: str) -> None:
    """Refuse to create/drop anything that is not an agentops scratch database."""
    allowed = (
        SCRATCH_DATABASE_PATTERN.fullmatch(name) is not None
        or GUARD_PROBE_DATABASE_PATTERN.fullmatch(name) is not None
    )
    if not allowed:
        raise UnsafeDatabaseTargetError(
            f"Refusing to create or drop database {name!r}: only disposable "
            "agentops_mig_<12 hex> / agentops_guard_<12 hex> names are allowed."
        )


def is_under_pytest() -> bool:
    """True while pytest is running in this process."""
    return "PYTEST_CURRENT_TEST" in os.environ or "pytest" in sys.modules


def command_name(cmd_opts: object | None) -> str | None:
    """Name of the Alembic CLI command (``upgrade``, ``downgrade``, ...).

    Returns ``None`` when Alembic is driven programmatically; callers must
    treat that as destructive.
    """
    cmd = getattr(cmd_opts, "cmd", None)
    if not cmd:
        return None
    name = getattr(cmd[0], "__name__", None)
    return name if isinstance(name, str) else None


def assert_safe_migration_target(
    *,
    database_name: str,
    app_env: str,
    under_pytest: bool,
    command: str | None,
    confirmed_database: str | None,
) -> None:
    """Raise :class:`UnsafeDatabaseTargetError` unless the target is acceptable.

    ``database_name`` must be the name PostgreSQL reports via
    ``SELECT current_database()``, not a name parsed from a URL.
    """
    test_safe = is_test_safe_database(database_name)

    if under_pytest and not test_safe:
        raise UnsafeDatabaseTargetError(
            f"Refusing to run migrations against {database_name!r} while "
            "pytest is running. Tests may only use '*_test' or scratch databases."
        )

    if app_env.strip().lower() == "test" and not test_safe:
        raise UnsafeDatabaseTargetError(
            f"APP_ENV=test but the target database is {database_name!r}. "
            "Point DATABASE_URL at the '*_test' database."
        )

    destructive = command not in NON_DESTRUCTIVE_COMMANDS
    if destructive and not test_safe and confirmed_database != database_name:
        raise UnsafeDatabaseTargetError(
            f"'{command or 'programmatic command'}' can destroy data in "
            f"{database_name!r}. If that is really what you want, re-run with "
            f"-x confirm_db={database_name}"
        )


def _read_setting(settings: object, name: str) -> str:
    """Read a setting by name, tolerating lower/UPPER case and secret wrappers."""
    for attribute in (name.lower(), name.upper()):
        if hasattr(settings, attribute):
            value = getattr(settings, attribute)
            if hasattr(value, "get_secret_value"):
                value = value.get_secret_value()
            value = getattr(value, "value", value)
            return str(value)
    raise RuntimeError(f"Application settings have no '{name}' attribute.")


def load_runtime_target() -> RuntimeTarget:
    """Resolve the database URL and APP_ENV from the application settings.

    This is the ONE place that knows how to reach ``agentops.core.config``.
    If your settings module is named differently, adjust only this function.
    """
    module = importlib.import_module("agentops.core.config")
    factory = getattr(module, "get_settings", None)
    if callable(factory):
        settings = factory()
    elif hasattr(module, "Settings"):
        settings = module.Settings()
    else:
        raise RuntimeError("agentops.core.config exposes neither get_settings() nor Settings.")
    return RuntimeTarget(
        database_url=_read_setting(settings, "database_url"),
        app_env=_read_setting(settings, "app_env"),
    )
