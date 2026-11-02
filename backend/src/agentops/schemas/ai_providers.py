"""Request and response schemas for per-user AI provider settings."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, SecretStr, field_validator


class AIProviderName(StrEnum):
    OPENAI = "openai"
    GROQ = "groq"
    OLLAMA = "ollama"


class AIProviderUpsert(BaseModel):
    """Configure a provider and its position in the fallback chain."""

    model_config = ConfigDict(extra="forbid")

    model_name: str = Field(min_length=1, max_length=120)
    api_key: SecretStr | None = None
    base_url: str | None = Field(default=None, max_length=500)
    priority: int = Field(default=0, ge=0, le=100)
    enabled: bool = True

    @field_validator("model_name")
    @classmethod
    def normalize_model(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Model name cannot be blank.")
        return normalized

    @field_validator("base_url")
    @classmethod
    def normalize_base_url(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip().rstrip("/")
        if not normalized.startswith(("http://", "https://")):
            raise ValueError("base_url must use HTTP or HTTPS.")
        return normalized


class AIProviderResponse(BaseModel):
    """Safe provider configuration response; the secret is never returned."""

    id: str
    provider: AIProviderName
    model_name: str
    api_key_configured: bool
    base_url: str | None
    priority: int
    enabled: bool


class AIProviderTestResponse(BaseModel):
    provider: AIProviderName
    model_name: str
    success: bool
    message: str
