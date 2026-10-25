"""Shared fixtures."""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from agentops.core.config import Settings
from agentops.main import create_app

# Test-only value. Long enough to pass the non-dev strength check, and deliberately
# different from the dev placeholder so tests never depend on the insecure default.
TEST_JWT_SECRET = "test-only-jwt-secret-not-for-real-use-0123456789"


@pytest.fixture(autouse=True)
def _isolate_settings_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Remove env vars Settings reads, so a developer's shell cannot change test results."""
    for field_name in Settings.model_fields:
        monkeypatch.delenv(field_name.upper(), raising=False)


@pytest.fixture
def jwt_secret_for_tests() -> str:
    return TEST_JWT_SECRET


@pytest.fixture
def settings(jwt_secret_for_tests: str) -> Settings:
    # _env_file=None: unit and smoke tests must not read a developer's local .env.
    # The database URL points at a closed port on purpose: these tests must never
    # reach any real database, development or test. Engines connect lazily, so
    # nothing connects unless a test explicitly triggers a DB query.
    return Settings(
        _env_file=None,
        app_env="test",
        log_format="json",
        jwt_secret=jwt_secret_for_tests,
        database_url="postgresql+psycopg://nobody:nobody@127.0.0.1:1/unused",
        db_connect_timeout_s=1,
    )


@pytest.fixture
def client(settings: Settings) -> Iterator[TestClient]:
    with TestClient(create_app(settings)) as test_client:
        yield test_client
