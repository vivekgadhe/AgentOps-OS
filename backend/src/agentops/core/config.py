"""Application settings: typed, validated at startup, sourced from the environment."""

from functools import lru_cache
from typing import Any, Literal
from urllib.parse import urlparse

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

    # SMTP delivery and short-lived email OTPs for registration, invitations and password recovery.
    smtp_host: str | None = None
    smtp_port: int = Field(default=587, ge=1, le=65535)
    smtp_username: str | None = None
    smtp_password: SecretStr | None = None
    smtp_from_email: str | None = None
    smtp_from_name: str = Field(default="AgentOps-OS", min_length=1, max_length=100)
    smtp_starttls: bool = True
    smtp_timeout_s: int = Field(default=15, ge=1, le=60)
    otp_pepper: SecretStr | None = None
    otp_expiry_minutes: int = Field(default=10, ge=3, le=30)
    otp_max_attempts: int = Field(default=5, ge=1, le=10)
    otp_resend_cooldown_seconds: int = Field(default=60, ge=15, le=600)
    otp_max_requests_per_hour: int = Field(default=5, ge=1, le=20)

    # Existing hosted LLM integration remains available to non-RAG workflows.
    openai_api_key: SecretStr | None = None
    openai_model: str = Field(default="gpt-5.5", min_length=1, max_length=100)
    llm_timeout_s: int = Field(default=30, ge=1, le=300)

    # Phase 7 local Ollama services. No hosted API key is required for RAG.
    ollama_base_url: str = Field(default="http://localhost:11434", min_length=1, max_length=500)
    ollama_chat_model: str = Field(default="qwen3.5:0.8b", min_length=1, max_length=100)
    ollama_embedding_model: str = Field(default="embeddinggemma", min_length=1, max_length=100)
    ollama_timeout_s: int = Field(default=180, ge=1, le=900)

    # Phase 8: encryption key used for API credentials stored in PostgreSQL.
    ai_credential_encryption_key: SecretStr | None = None
    ai_provider_timeout_s: int = Field(default=60, ge=1, le=300)
    approval_ttl_hours: int = Field(default=24, ge=1, le=720)

    knowledge_max_upload_bytes: int = Field(default=10 * 1024 * 1024, ge=1024, le=50 * 1024 * 1024)
    knowledge_max_pdf_pages: int = Field(default=200, ge=1, le=1000)
    knowledge_chunk_size_chars: int = Field(default=1200, ge=200, le=5000)
    knowledge_chunk_overlap_chars: int = Field(default=200, ge=0, le=1000)
    knowledge_max_chunks_per_document: int = Field(default=5000, ge=1, le=20000)

    # Phase 9: persistent agent memory. Automatic capture is opt-in to avoid
    # silently retaining user prompts or generated outputs without consent.
    memory_max_content_chars: int = Field(default=5_000, ge=100, le=20_000)
    memory_default_ttl_days: int = Field(default=90, ge=1, le=3_650)
    memory_auto_capture_rag: bool = False
    memory_retrieval_top_k: int = Field(default=5, ge=1, le=20)

    # Phase 10: telemetry stores operational metadata only, never prompts or outputs.
    observability_enabled: bool = True
    telemetry_retention_days: int = Field(default=90, ge=1, le=3_650)

    @field_validator("log_level", mode="before")
    @classmethod
    def _normalize_log_level(cls, value: Any) -> Any:
        return value.upper() if isinstance(value, str) else value

    @field_validator("openai_model", "ollama_chat_model", "ollama_embedding_model", mode="before")
    @classmethod
    def _normalize_model_name(cls, value: Any) -> Any:
        if isinstance(value, str):
            normalized = value.strip()
            if not normalized:
                raise ValueError("Model names cannot be blank.")
            return normalized
        return value

    @field_validator("ollama_base_url", mode="before")
    @classmethod
    def _normalize_ollama_url(cls, value: Any) -> Any:
        if not isinstance(value, str):
            return value
        normalized = value.strip().rstrip("/")
        parsed = urlparse(normalized)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("OLLAMA_BASE_URL must be an absolute HTTP(S) URL.")
        return normalized

    @field_validator("database_url")
    @classmethod
    def _require_psycopg3_driver(cls, value: str) -> str:
        # A bare "postgresql://" makes SQLAlchemy look for psycopg2.
        if not value.startswith("postgresql+psycopg://"):
            raise ValueError("DATABASE_URL must start with 'postgresql+psycopg://'")
        return value

    @model_validator(mode="after")
    def _validate_settings(self) -> "Settings":
        if self.knowledge_chunk_overlap_chars >= self.knowledge_chunk_size_chars:
            raise ValueError(
                "KNOWLEDGE_CHUNK_OVERLAP_CHARS must be smaller than KNOWLEDGE_CHUNK_SIZE_CHARS."
            )
        smtp_values = (self.smtp_host, self.smtp_from_email)
        if any(smtp_values) and not all(smtp_values):
            raise ValueError("SMTP_HOST and SMTP_FROM_EMAIL must be configured together.")
        if bool(self.smtp_username) != (self.smtp_password is not None):
            raise ValueError("SMTP_USERNAME and SMTP_PASSWORD must be configured together.")
        if self.app_env == "prod" and not all(smtp_values):
            raise ValueError("SMTP_HOST and SMTP_FROM_EMAIL are required in production.")
        if self.app_env == "prod" and self.otp_pepper is None:
            raise ValueError("OTP_PEPPER must be configured in production.")
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
