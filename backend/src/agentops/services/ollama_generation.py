"""Structured local text generation through Ollama's /api/chat endpoint."""

from typing import TypeVar

import httpx
from pydantic import BaseModel, ValidationError

from agentops.services.llm import LLMProviderError

ModelT = TypeVar("ModelT", bound=BaseModel)


class OllamaStructuredGenerator:
    """Implement the existing structured-text generator contract locally."""

    def __init__(self, *, base_url: str, model: str, timeout_s: int = 180) -> None:
        self.model = model
        self._client = httpx.Client(
            base_url=base_url.rstrip("/"),
            timeout=httpx.Timeout(timeout_s),
        )

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "OllamaStructuredGenerator":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def generate_structured(
        self,
        prompt: str,
        *,
        output_model: type[ModelT],
        instructions: str | None = None,
    ) -> ModelT:
        """Generate JSON constrained by the Pydantic output schema."""
        messages: list[dict[str, str]] = []
        if instructions:
            messages.append({"role": "system", "content": instructions})
        messages.append({"role": "user", "content": prompt})

        try:
            response = self._client.post(
                "/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "format": output_model.model_json_schema(),
                    "stream": False,
                    "think": False,
                    "options": {"temperature": 0},
                },
            )
            response.raise_for_status()
            payload = response.json()
            content = payload["message"]["content"]
            if not isinstance(content, str) or not content.strip():
                raise ValueError("The local model returned an empty response.")
            return output_model.model_validate_json(content)
        except (httpx.HTTPError, KeyError, TypeError, ValueError, ValidationError) as exc:
            raise LLMProviderError(
                "The local Ollama generation request failed or returned invalid structured output."
            ) from exc
