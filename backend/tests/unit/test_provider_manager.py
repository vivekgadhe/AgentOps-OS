"""Unit tests for ordered AI provider fallback."""

from typing import TypeVar

import pytest
from pydantic import BaseModel

from agentops.services.providers.base import (
    AllProvidersFailed,
    ProviderAttempt,
    ProviderRefusalError,
    ProviderUnavailableError,
)
from agentops.services.providers.provider_manager import ProviderManager

ModelT = TypeVar("ModelT", bound=BaseModel)


class _Output(BaseModel):
    value: str


class _FailingProvider:
    def generate_structured(
        self,
        prompt: str,
        *,
        output_model: type[ModelT],
        instructions: str | None = None,
    ) -> ModelT:
        raise ProviderUnavailableError("temporary provider outage")

    def close(self) -> None:
        pass


class _WorkingProvider:
    def generate_structured(
        self,
        prompt: str,
        *,
        output_model: type[ModelT],
        instructions: str | None = None,
    ) -> ModelT:
        return output_model.model_validate({"value": "fallback-ok"})

    def close(self) -> None:
        pass


class _RefusingProvider:
    def generate_structured(
        self,
        prompt: str,
        *,
        output_model: type[ModelT],
        instructions: str | None = None,
    ) -> ModelT:
        raise ProviderRefusalError("request refused")

    def close(self) -> None:
        pass


def test_manager_falls_back_in_priority_order() -> None:
    manager = ProviderManager(
        [
            ProviderAttempt("openai", "first-model", _FailingProvider()),
            ProviderAttempt("groq", "backup-model", _WorkingProvider()),
        ]
    )

    result = manager.generate_structured("test", output_model=_Output)

    assert result.value == "fallback-ok"
    assert manager.last_provider == "groq"
    assert manager.last_model == "backup-model"
    assert manager.last_attempts == ("openai", "groq")


def test_manager_reports_all_providers_failed() -> None:
    manager = ProviderManager(
        [
            ProviderAttempt("openai", "test-model", _FailingProvider()),
            ProviderAttempt("ollama", "test-model", _FailingProvider()),
        ]
    )

    with pytest.raises(AllProvidersFailed) as exc_info:
        manager.generate_structured("test", output_model=_Output)

    assert exc_info.value.providers == ("openai", "ollama")
    assert manager.last_attempts == ("openai", "ollama")


def test_manager_does_not_bypass_a_model_refusal() -> None:
    backup = _WorkingProvider()
    manager = ProviderManager(
        [
            ProviderAttempt("openai", "first-model", _RefusingProvider()),
            ProviderAttempt("groq", "backup-model", backup),
        ]
    )

    with pytest.raises(ProviderRefusalError, match="refused"):
        manager.generate_structured("test", output_model=_Output)

    assert manager.last_attempts == ("openai",)
    assert manager.last_provider is None


def test_manager_rejects_empty_provider_chain() -> None:
    with pytest.raises(ValueError, match="At least one"):
        ProviderManager([])


def test_manager_rejects_duplicate_provider_names() -> None:
    with pytest.raises(ValueError, match="unique"):
        ProviderManager(
            [
                ProviderAttempt("ollama", "one", _WorkingProvider()),
                ProviderAttempt("ollama", "two", _WorkingProvider()),
            ]
        )
