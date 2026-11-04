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


def test_llm_settings_have_safe_defaults() -> None:
    settings = Settings(
        _env_file=None,
        app_env="dev",
        openai_api_key=None,
        openai_model="gpt-5.5",
        llm_timeout_s=30,
    )

    assert settings.openai_api_key is None
    assert settings.openai_model == "gpt-5.5"
    assert settings.llm_timeout_s == 30


def test_llm_settings_accept_explicit_values() -> None:
    settings = Settings(
        _env_file=None,
        app_env="dev",
        openai_api_key="unit-test-key",
        openai_model="  unit-test-model  ",
        llm_timeout_s=45,
    )

    assert settings.openai_api_key is not None
    assert settings.openai_api_key.get_secret_value() == "unit-test-key"
    assert settings.openai_model == "unit-test-model"
    assert settings.llm_timeout_s == 45


def test_openai_model_rejects_blank_value() -> None:
    with pytest.raises(ValidationError):
        Settings(_env_file=None, openai_model="   ")


@pytest.mark.parametrize("timeout", [0, 301])
def test_llm_timeout_must_be_between_one_and_300_seconds(
    timeout: int,
) -> None:
    with pytest.raises(ValidationError):
        Settings(_env_file=None, llm_timeout_s=timeout)


def test_observability_settings_have_safe_defaults() -> None:
    settings = Settings(_env_file=None, app_env="dev")
    assert settings.observability_enabled is True
    assert settings.telemetry_retention_days == 90


def test_telemetry_retention_days_are_bounded() -> None:
    with pytest.raises(ValidationError):
        Settings(_env_file=None, telemetry_retention_days=0)
    with pytest.raises(ValidationError):
        Settings(_env_file=None, telemetry_retention_days=3_651)
