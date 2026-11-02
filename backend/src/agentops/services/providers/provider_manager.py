"""Resolve configured providers and transparently fail over on provider failures."""

from __future__ import annotations

import logging
from collections.abc import Sequence
from typing import TypeVar
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from agentops.core.config import Settings
from agentops.core.encryption import CredentialCipher, CredentialEncryptionError
from agentops.db.models.ai_provider import AIProviderConfig
from agentops.services.providers.base import (
    AllProvidersFailed,
    ProviderAttempt,
    ProviderConfigurationError,
    ProviderError,
    ProviderRefusalError,
    StructuredGenerator,
)
from agentops.services.providers.groq_provider import GroqProvider
from agentops.services.providers.ollama_provider import OllamaProvider
from agentops.services.providers.openai_provider import OpenAICompatibleProvider

logger = logging.getLogger(__name__)
ModelT = TypeVar("ModelT", bound=BaseModel)


class ProviderManager:
    """Structured generation with an ordered, observable provider fallback chain."""

    def __init__(self, providers: Sequence[ProviderAttempt]) -> None:
        if not providers:
            raise ValueError("At least one AI provider must be configured.")
        names = [provider.name for provider in providers]
        if len(names) != len(set(names)):
            raise ValueError("Provider names in the fallback chain must be unique.")
        self._providers = tuple(providers)
        self.last_provider: str | None = None
        self.last_model: str | None = None
        self.last_attempts: tuple[str, ...] = ()

    @property
    def configured_providers(self) -> tuple[str, ...]:
        return tuple(item.name for item in self._providers)

    def generate_structured(
        self,
        prompt: str,
        *,
        output_model: type[ModelT],
        instructions: str | None = None,
    ) -> ModelT:
        """Try providers in priority order; stop on explicit model refusals."""
        attempted: list[str] = []
        errors: list[ProviderError] = []
        self.last_provider = None
        self.last_model = None

        for item in self._providers:
            attempted.append(item.name)
            try:
                result = item.generator.generate_structured(
                    prompt,
                    output_model=output_model,
                    instructions=instructions,
                )
                self.last_provider = item.name
                self.last_model = item.model
                self.last_attempts = tuple(attempted)
                if attempted[:-1]:
                    logger.warning(
                        "ai_provider_fallback_succeeded",
                        extra={
                            "provider": item.name,
                            "failed_providers": attempted[:-1],
                        },
                    )
                return result
            except ProviderRefusalError:
                self.last_attempts = tuple(attempted)
                raise
            except ProviderError as exc:
                errors.append(exc)
                logger.warning(
                    "ai_provider_attempt_failed",
                    extra={
                        "provider": item.name,
                        "error_type": type(exc).__name__,
                    },
                )

        self.last_attempts = tuple(attempted)
        raise AllProvidersFailed(attempted) from (errors[-1] if errors else None)

    def close(self) -> None:
        for item in self._providers:
            try:
                item.generator.close()
            except Exception:
                logger.warning(
                    "ai_provider_close_failed",
                    extra={"provider": item.name},
                )

    def __enter__(self) -> ProviderManager:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()


class _ConfigurationFailureGenerator:
    """Preserve an invalid provider in the chain so later fallbacks still run."""

    def __init__(self, message: str) -> None:
        self._message = message

    def generate_structured(
        self,
        prompt: str,
        *,
        output_model: type[ModelT],
        instructions: str | None = None,
    ) -> ModelT:
        raise ProviderConfigurationError(self._message)

    def close(self) -> None:
        return None


def build_provider_manager(
    session: Session,
    owner_user_id: UUID,
    settings: Settings,
) -> ProviderManager:
    """Build a user's enabled fallback chain from encrypted database settings.

    If no per-user rows exist, use the legacy OpenAI environment key when set,
    then retain local Ollama as the final no-hosted-key option.
    """
    configured_rows = list(
        session.scalars(
            select(AIProviderConfig)
            .where(AIProviderConfig.owner_user_id == owner_user_id)
            .order_by(AIProviderConfig.priority, AIProviderConfig.provider)
        ).all()
    )
    rows = [row for row in configured_rows if row.enabled]
    attempts: list[ProviderAttempt] = []

    if configured_rows and not rows:
        raise ProviderConfigurationError("All saved AI provider configurations are disabled.")

    if rows:
        cipher: CredentialCipher | None = None
        cipher_error: CredentialEncryptionError | None = None
        if any(row.api_key_ciphertext for row in rows):
            try:
                cipher = CredentialCipher(settings)
            except CredentialEncryptionError as exc:
                cipher_error = exc

        for row in rows:
            if row.api_key_ciphertext and cipher_error is not None:
                attempts.append(
                    ProviderAttempt(
                        name=row.provider,
                        model=row.model_name,
                        generator=_ConfigurationFailureGenerator(
                            "Stored provider credentials cannot be decrypted. "
                            "Check AI_CREDENTIAL_ENCRYPTION_KEY."
                        ),
                    )
                )
                continue

            try:
                api_key = (
                    cipher.decrypt(row.api_key_ciphertext)
                    if row.api_key_ciphertext and cipher is not None
                    else None
                )
                attempt = _build_attempt(
                    provider=row.provider,
                    model=row.model_name,
                    api_key=api_key,
                    base_url=row.base_url,
                    timeout_s=settings.ai_provider_timeout_s,
                    ollama_default_url=settings.ollama_base_url,
                )
            except (CredentialEncryptionError, ProviderConfigurationError) as exc:
                logger.warning(
                    "ai_provider_configuration_invalid",
                    extra={"provider": row.provider, "error_type": type(exc).__name__},
                )
                attempt = ProviderAttempt(
                    name=row.provider,
                    model=row.model_name,
                    generator=_ConfigurationFailureGenerator(
                        "A saved provider configuration is invalid or cannot be decrypted."
                    ),
                )
            attempts.append(attempt)
    else:
        if (
            settings.openai_api_key is not None
            and settings.openai_api_key.get_secret_value().strip()
        ):
            attempts.append(
                ProviderAttempt(
                    name="openai",
                    model=settings.openai_model,
                    generator=OpenAICompatibleProvider(
                        api_key=settings.openai_api_key.get_secret_value(),
                        model=settings.openai_model,
                        timeout_s=settings.ai_provider_timeout_s,
                    ),
                )
            )
        attempts.append(
            ProviderAttempt(
                name="ollama",
                model=settings.ollama_chat_model,
                generator=OllamaProvider(
                    base_url=settings.ollama_base_url,
                    model=settings.ollama_chat_model,
                    timeout_s=settings.ollama_timeout_s,
                ),
            )
        )

    return ProviderManager(attempts)


def _build_attempt(
    *,
    provider: str,
    model: str,
    api_key: str | None,
    base_url: str | None,
    timeout_s: int,
    ollama_default_url: str,
) -> ProviderAttempt:
    if provider == "openai":
        if not api_key:
            raise ProviderConfigurationError("OpenAI provider is missing its configured API key.")
        generator: StructuredGenerator = OpenAICompatibleProvider(
            api_key=api_key,
            model=model,
            timeout_s=timeout_s,
        )
    elif provider == "groq":
        if not api_key:
            raise ProviderConfigurationError("Groq provider is missing its configured API key.")
        generator = GroqProvider(
            api_key=api_key,
            model=model,
            timeout_s=timeout_s,
        )
    elif provider == "ollama":
        generator = OllamaProvider(
            base_url=base_url or ollama_default_url,
            model=model,
            timeout_s=timeout_s,
        )
    else:
        raise ProviderConfigurationError(f"Unsupported provider: {provider}")

    return ProviderAttempt(name=provider, model=model, generator=generator)
