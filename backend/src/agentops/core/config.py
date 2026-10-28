"""Application settings: typed, validated at startup, sourced from the environment."""

from functools import lru_cache
from typing import Any, Literal

from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

INSECURE_DEV_JWT_SECRET = "dev-insecure-secret-change-me"
MIN_SECRET_LENGTH = 32


class Settings(BaseSettings):
    # Later files win: ../.env (repo root, when running from backend/) then ./.env.
    # Real environment variables always override both.
    model_config = SettingsConfigDict(
        env_file=("../.env", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "AgentOps OS"
    app_env: Literal["dev", "test", "prod"] = "dev"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    log_format: Literal["console", "json"] = "console"
    api_prefix: str = "/api/v1"

    database_url: str = "postgresql+psycopg://agentops:agentops@localhost:5432/agentops"
    db_pool_size: int = Field(default=5, ge=1, le=50)
    db_connect_timeout_s: int = Field(default=5, ge=1, le=60)

    jwt_secret: SecretStr = SecretStr(INSECURE_DEV_JWT_SECRET)
    access_token_ttl_minutes: int = Field(default=15, ge=1, le=1440)

    # LLM integration.
    # The API key is optional so the application and unit tests can run
    # without making external API requests.
    openai_api_key: SecretStr | None = None
    openai_model: str = Field(default="gpt-5.5", min_length=1, max_length=100)
    llm_timeout_s: int = Field(default=30, ge=1, le=300)

    @field_validator("log_level", mode="before")
    @classmethod
    def _normalize_log_level(cls, value: Any) -> Any:
        return value.upper() if isinstance(value, str) else value

    @field_validator("openai_model", mode="before")
    @classmethod
    def _normalize_openai_model(cls, value: Any) -> Any:
        if isinstance(value, str):
            normalized = value.strip()
            if not normalized:
                raise ValueError("OPENAI_MODEL cannot be blank.")
            return normalized

        return value

    @field_validator("database_url")
    @classmethod
    def _require_psycopg3_driver(cls, value: str) -> str:
        # A bare "postgresql://" makes SQLAlchemy look for psycopg2.
        if not value.startswith("postgresql+psycopg://"):
            raise ValueError("DATABASE_URL must start with 'postgresql+psycopg://'")
        return value

    @model_validator(mode="after")
    def _require_real_secret_outside_dev(self) -> "Settings":
        if self.app_env != "dev":
            secret = self.jwt_secret.get_secret_value()
            if secret == INSECURE_DEV_JWT_SECRET or len(secret) < MIN_SECRET_LENGTH:
                raise ValueError(
                    f"JWT_SECRET must be a random value of at least "
                    f"{MIN_SECRET_LENGTH} characters when APP_ENV is not 'dev'"
                )
        return self


@lru_cache
def get_settings() -> Settings:
    """Process-wide settings. Tests build their own Settings explicitly."""
    return Settings()
