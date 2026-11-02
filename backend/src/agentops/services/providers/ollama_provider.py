"""Ollama local structured-generation adapter."""

from typing import TypeVar

from pydantic import BaseModel

from agentops.services.llm import LLMProviderError
from agentops.services.ollama_generation import OllamaStructuredGenerator
from agentops.services.providers.base import ProviderUnavailableError

ModelT = TypeVar("ModelT", bound=BaseModel)


class OllamaProvider:
    """Adapt the existing Ollama generator to the common provider contract."""

    def __init__(self, *, base_url: str, model: str, timeout_s: int = 180) -> None:
        self.model = model
        self._generator = OllamaStructuredGenerator(
            base_url=base_url,
            model=model,
            timeout_s=timeout_s,
        )

    def generate_structured(
        self,
        prompt: str,
        *,
        output_model: type[ModelT],
        instructions: str | None = None,
    ) -> ModelT:
        try:
            return self._generator.generate_structured(
                prompt,
                output_model=output_model,
                instructions=instructions,
            )
        except LLMProviderError as exc:
            raise ProviderUnavailableError("Local Ollama generation failed.") from exc

    def close(self) -> None:
        self._generator.close()
