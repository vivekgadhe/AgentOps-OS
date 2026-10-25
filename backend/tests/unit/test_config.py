import pytest
from pydantic import ValidationError

from agentops.core.config import INSECURE_DEV_JWT_SECRET, Settings

STRONG_SECRET = "x" * 32


def test_dev_allows_the_default_secret() -> None:
    settings = Settings(_env_file=None, app_env="dev")
    assert settings.jwt_secret.get_secret_value() == INSECURE_DEV_JWT_SECRET


def test_prod_rejects_the_default_secret() -> None:
    with pytest.raises(ValidationError):
        Settings(_env_file=None, app_env="prod", jwt_secret=INSECURE_DEV_JWT_SECRET)


def test_test_environment_rejects_the_default_secret() -> None:
    # Regression test: non-dev environments always require an explicit strong secret.
    with pytest.raises(ValidationError):
        Settings(_env_file=None, app_env="test")


def test_prod_rejects_a_short_secret() -> None:
    with pytest.raises(ValidationError):
        Settings(_env_file=None, app_env="prod", jwt_secret="too-short")


def test_prod_accepts_a_long_secret() -> None:
    settings = Settings(_env_file=None, app_env="prod", jwt_secret=STRONG_SECRET)
    assert settings.app_env == "prod"


def test_test_environment_accepts_an_explicit_secret() -> None:
    settings = Settings(_env_file=None, app_env="test", jwt_secret=STRONG_SECRET)
    assert settings.app_env == "test"


def test_database_url_must_use_psycopg3_driver() -> None:
    with pytest.raises(ValidationError):
        Settings(_env_file=None, database_url="postgresql://u:p@localhost/db")


def test_log_level_is_case_insensitive() -> None:
    assert Settings(_env_file=None, log_level="debug").log_level == "DEBUG"
