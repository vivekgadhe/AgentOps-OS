"""OpenAI-backed text generation service."""

from typing import Any, TypeVar

from openai import APITimeoutError, OpenAI, OpenAIError
from pydantic import BaseModel, ValidationError

from agentops.core.config import Settings, get_settings

ModelT = TypeVar("ModelT", bound=BaseModel)


class LLMError(RuntimeError):
    """Base error for LLM operations."""


class LLMConfigurationError(LLMError):
    """Raised when the LLM service is not configured."""


class LLMProviderError(LLMError):
    """Raised when the model provider fails or returns unusable output."""


class LLMTimeoutError(LLMProviderError):
    """Raised when an OpenAI request times out."""


class LLMRefusalError(LLMProviderError):
    """Raised when the model refuses a request."""


class LLMIncompleteResponseError(LLMProviderError):
    """Raised when the model response is incomplete."""


DEFAULT_INSTRUCTIONS = (
    "You are an assistant for AgentOps OS. Provide accurate, clear, and concise responses."
)


class LLMService:
    """Generate text and structured responses using an OpenAI model."""

    def __init__(
        self,
        settings: Settings | None = None,
        *,
        client: OpenAI | None = None,
    ) -> None:
        self._settings = settings if settings is not None else get_settings()
        self._client = client

    def generate_text(
        self,
        prompt: str,
        *,
        instructions: str | None = None,
    ) -> str:
        """Generate text and return the cleaned response."""
        normalized_prompt, resolved_instructions = self._prepare_request(
            prompt,
            instructions,
        )
        client = self._get_client()

        try:
            response = client.responses.create(
                model=self._settings.openai_model,
                instructions=resolved_instructions,
                input=normalized_prompt,
            )
        except APITimeoutError as exc:
            raise LLMTimeoutError("The OpenAI provider request timed out.") from exc
        except OpenAIError as exc:
            raise LLMProviderError("The OpenAI provider request failed.") from exc

        self._check_response(response)

        output = response.output_text

        if not isinstance(output, str) or not output.strip():
            raise LLMProviderError("The OpenAI provider returned no text output.")

        return output.strip()

    def generate_structured(
        self,
        prompt: str,
        *,
        output_model: type[ModelT],
        instructions: str | None = None,
    ) -> ModelT:
        """Generate a response constrained to a Pydantic model."""
        normalized_prompt, resolved_instructions = self._prepare_request(
            prompt,
            instructions,
        )
        client = self._get_client()

        try:
            response = client.responses.parse(
                model=self._settings.openai_model,
                instructions=resolved_instructions,
                input=normalized_prompt,
                text_format=output_model,
            )
        except APITimeoutError as exc:
            raise LLMTimeoutError("The OpenAI provider request timed out.") from exc
        except OpenAIError as exc:
            raise LLMProviderError("The OpenAI provider request failed.") from exc
        except (ValidationError, ValueError) as exc:
            raise LLMProviderError(
                "The OpenAI response could not be parsed into the required schema."
            ) from exc

        self._check_response(response)

        parsed = response.output_parsed

        if not isinstance(parsed, output_model):
            raise LLMProviderError("The OpenAI provider returned no valid structured output.")

        return parsed

    @staticmethod
    def _prepare_request(
        prompt: str,
        instructions: str | None,
    ) -> tuple[str, str]:
        """Validate and normalize request fields."""
        normalized_prompt = prompt.strip()

        if not normalized_prompt:
            raise ValueError("Prompt cannot be blank.")

        if instructions is None:
            resolved_instructions = DEFAULT_INSTRUCTIONS
        else:
            resolved_instructions = instructions.strip()

            if not resolved_instructions:
                raise ValueError("Instructions cannot be blank.")

        return normalized_prompt, resolved_instructions

    @staticmethod
    def _check_response(response: Any) -> None:
        """Reject unsuccessful, incomplete, or refused model responses."""
        response_status = getattr(response, "status", None)

        if response_status == "incomplete":
            details = getattr(response, "incomplete_details", None)
            reason = getattr(details, "reason", None)

            message = "The OpenAI provider returned an incomplete response."

            if reason:
                message += f" Reason: {reason}."

            raise LLMIncompleteResponseError(message)

        if response_status == "failed":
            raise LLMProviderError("The OpenAI provider returned a failed response.")

        output = getattr(response, "output", None)

        if not isinstance(output, list):
            return

        for item in output:
            if getattr(item, "type", None) != "message":
                continue

            content = getattr(item, "content", None)

            if not isinstance(content, list):
                continue

            if any(getattr(part, "type", None) == "refusal" for part in content):
                raise LLMRefusalError("The model refused to fulfill the request.")

    def _get_client(self) -> OpenAI:
        """Create the provider client lazily when credentials are available."""
        if self._client is not None:
            return self._client

        api_key = self._settings.openai_api_key

        if api_key is None or not api_key.get_secret_value().strip():
            raise LLMConfigurationError("OPENAI_API_KEY must be configured before generating text.")

        self._client = OpenAI(
            api_key=api_key.get_secret_value(),
            timeout=self._settings.llm_timeout_s,
            max_retries=0,
        )

        return self._client
