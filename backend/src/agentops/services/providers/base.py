"""Common contracts and safe error types for generation providers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, TypeVar

from pydantic import BaseModel

from agentops.services.llm import LLMProviderError

ModelT = TypeVar("ModelT", bound=BaseModel)


class ProviderError(LLMProviderError):
    """Base class for provider execution failures."""


class ProviderUnavailableError(ProviderError):
    """The provider could not complete a request; trying a fallback is safe."""


class ProviderRefusalError(ProviderError):
    """The model refused the request; this must not be bypassed by failover."""


class ProviderConfigurationError(ProviderError):
    """A provider is incorrectly configured."""


class AllProvidersFailed(ProviderError):
    """No configured provider completed the generation request."""

    def __init__(self, providers: list[str]) -> None:
        self.providers = tuple(providers)
        super().__init__("All configured AI providers failed: " + ", ".join(providers))


class StructuredGenerator(Protocol):
    """Provider contract matching the application's planner and agents."""

    def generate_structured(
        self,
        prompt: str,
        *,
        output_model: type[ModelT],
        instructions: str | None = None,
    ) -> ModelT: ...

    def close(self) -> None: ...


@dataclass(frozen=True, slots=True)
class ProviderAttempt:
    """Resolved provider information in configured fallback order."""

    name: str
    model: str
    generator: StructuredGenerator
