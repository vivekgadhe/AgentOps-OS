"""OpenAI-compatible structured generation adapter."""

from __future__ import annotations

import json
from typing import Any, Literal, TypeVar, cast

from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    OpenAI,
    OpenAIError,
    RateLimitError,
)
from pydantic import BaseModel, ValidationError

from agentops.services.providers.base import (
    ProviderConfigurationError,
    ProviderRefusalError,
    ProviderUnavailableError,
)

ModelT = TypeVar("ModelT", bound=BaseModel)
StructuredMode = Literal["json_schema", "json_object"]


def _strict_schema(node: object) -> object:
    """Normalize a Pydantic schema for strict structured-output APIs."""
    if isinstance(node, dict):
        result = {
            key: _strict_schema(value)
            for key, value in node.items()
            if key not in {"default", "examples"}
        }
        properties = result.get("properties")
        if isinstance(properties, dict):
            result["required"] = list(properties)
            result["additionalProperties"] = False
        return result
    if isinstance(node, list):
        return [_strict_schema(value) for value in node]
    return node


class OpenAICompatibleProvider:
    """Generate Pydantic-validated JSON through OpenAI-compatible APIs."""

    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        base_url: str | None = None,
        timeout_s: int = 60,
        structured_mode: StructuredMode = "json_schema",
    ) -> None:
        if not api_key.strip():
            raise ProviderConfigurationError("Provider API key is not configured.")
        if not model.strip():
            raise ProviderConfigurationError("Provider model is not configured.")
        self.model = model
        self.structured_mode = structured_mode
        self._client = OpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout_s,
            max_retries=0,
        )

    def generate_structured(
        self,
        prompt: str,
        *,
        output_model: type[ModelT],
        instructions: str | None = None,
    ) -> ModelT:
        normalized_prompt = prompt.strip()
        if not normalized_prompt:
            raise ValueError("Prompt cannot be blank.")

        messages: list[dict[str, str]] = []
        if instructions:
            normalized_instructions = instructions.strip()
            if not normalized_instructions:
                raise ValueError("Instructions cannot be blank.")
            messages.append({"role": "system", "content": normalized_instructions})

        if self.structured_mode == "json_object":
            schema_json = json.dumps(output_model.model_json_schema(), ensure_ascii=False)
            messages.append(
                {
                    "role": "system",
                    "content": (
                        "Return JSON only. The JSON must validate against this schema: "
                        f"{schema_json}"
                    ),
                }
            )
            response_format: dict[str, Any] = {"type": "json_object"}
        else:
            response_format = {
                "type": "json_schema",
                "json_schema": {
                    "name": output_model.__name__.lower()[:64],
                    "strict": True,
                    "schema": _strict_schema(output_model.model_json_schema()),
                },
            }

        messages.append({"role": "user", "content": normalized_prompt})

        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=cast(Any, messages),
                response_format=cast(Any, response_format),
            )
        except (APITimeoutError, APIConnectionError, RateLimitError) as exc:
            raise ProviderUnavailableError("Provider connection or rate limit failure.") from exc
        except APIStatusError as exc:
            if exc.status_code in {408, 409, 429} or exc.status_code >= 500:
                raise ProviderUnavailableError("Provider returned a transient error.") from exc
            raise ProviderConfigurationError(
                f"Provider rejected the request (HTTP {exc.status_code})."
            ) from exc
        except OpenAIError as exc:
            raise ProviderUnavailableError("Provider request failed.") from exc

        try:
            message = response.choices[0].message
            if getattr(message, "refusal", None):
                raise ProviderRefusalError("The model refused the request.")
            content = message.content
            if not isinstance(content, str) or not content.strip():
                raise ValueError("Provider returned empty structured output.")
            decoded = json.loads(content)
            return output_model.model_validate(decoded)
        except ProviderRefusalError:
            raise
        except (IndexError, AttributeError, TypeError, ValueError, ValidationError) as exc:
            raise ProviderUnavailableError("Provider returned invalid structured output.") from exc

    def close(self) -> None:
        self._client.close()
