"""Unit tests for ordered AI provider fallback."""

from typing import TypeVar

import pytest
from pydantic import BaseModel

from agentops.core.observability_context import observability_scope
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


class _RecordingTelemetry:
    def __init__(self) -> None:
        self.events: list[dict[str, object]] = []

    def record_llm_attempt(self, **kwargs: object) -> None:
        self.events.append(kwargs)


def test_manager_records_successful_provider_attempt_without_prompt_content() -> None:
    telemetry = _RecordingTelemetry()
    manager = ProviderManager(
        [ProviderAttempt("ollama", "local-model", _WorkingProvider())],
        telemetry=telemetry,  # type: ignore[arg-type]
    )

    with observability_scope(component="agent", agent_name="analysis_agent"):
        manager.generate_structured("private prompt text", output_model=_Output)

    assert len(telemetry.events) == 1
    event = telemetry.events[0]
    assert event["provider"] == "ollama"
    assert event["outcome"] == "success"
    assert event["attempt_number"] == 1
    assert event["used_fallback"] is False
    assert "private prompt text" not in str(event)


def test_manager_records_provider_failures_before_fallback() -> None:
    telemetry = _RecordingTelemetry()
    manager = ProviderManager(
        [
            ProviderAttempt("openai", "first-model", _FailingProvider()),
            ProviderAttempt("ollama", "local-model", _WorkingProvider()),
        ],
        telemetry=telemetry,  # type: ignore[arg-type]
    )

    manager.generate_structured("prompt", output_model=_Output)

    assert [event["outcome"] for event in telemetry.events] == ["failure", "success"]
    assert [event["attempt_number"] for event in telemetry.events] == [1, 2]
    assert telemetry.events[1]["used_fallback"] is True
