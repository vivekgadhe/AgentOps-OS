"""Fixtures for tests that need a real PostgreSQL. Never touches the dev database."""

import os
from pathlib import Path

import pytest
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import make_url

from agentops.core.config import Settings
from agentops.db.session import check_database, create_db_engine

# backend/tests/integration/conftest.py -> parents[3] is the repository root
REPO_ROOT_ENV = Path(__file__).resolve().parents[3] / ".env"
DEFAULT_TEST_DATABASE_URL = "postgresql+psycopg://agentops:agentops@localhost:5432/agentops_test"


class IntegrationEnv(BaseSettings):
    """Reads only TEST_DATABASE_URL (environment variable first, then the root .env)."""

    model_config = SettingsConfigDict(env_file=REPO_ROOT_ENV, extra="ignore")

    test_database_url: str = DEFAULT_TEST_DATABASE_URL


@pytest.fixture
def integration_settings(jwt_secret_for_tests: str) -> Settings:
    url = IntegrationEnv().test_database_url
    database_name = make_url(url).database or ""
    if not database_name.endswith("_test"):
        pytest.fail(
            f"Refusing to run integration tests against database {database_name!r}: "
            "TEST_DATABASE_URL must point to a database whose name ends in '_test'.",
            pytrace=False,
        )

    # _env_file=None plus explicit arguments: the dev DATABASE_URL in .env is never read.
    settings = Settings(
        _env_file=None,
        app_env="test",
        database_url=url,
        jwt_secret=jwt_secret_for_tests,
    )

    engine = create_db_engine(settings)
    try:
        reachable = check_database(engine)
    finally:
        engine.dispose()
    if not reachable:
        message = (
            "Test database not reachable. Run `make up`. If the Postgres volume was created "
            "before the init script existed, create it with: docker compose exec db psql "
            '-U agentops -d agentops -c "CREATE DATABASE agentops_test;"'
        )
        if os.environ.get("REQUIRE_DB_TESTS") == "1":
            pytest.fail(message, pytrace=False)
        pytest.skip(message)
    return settings
