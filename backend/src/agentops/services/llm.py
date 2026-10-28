"""OpenAI-backed text generation service."""

from typing import TypeVar

from openai import OpenAI, OpenAIError
from pydantic import BaseModel, ValidationError

from agentops.core.config import Settings, get_settings

ModelT = TypeVar("ModelT", bound=BaseModel)


class LLMError(RuntimeError):
    """Base error for LLM operations."""


class LLMConfigurationError(LLMError):
    """Raised when the LLM service is not configured."""


class LLMProviderError(LLMError):
    """Raised when the model provider fails or returns unusable output."""


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
        """Generate text and return the cleaned response.

        An injected client allows tests to run without API credentials or
        external requests.
        """
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
        except OpenAIError as exc:
            raise LLMProviderError("The OpenAI provider request failed.") from exc

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
        """Generate a response constrained to a Pydantic model.

        Refusals, incomplete results, and responses without a successfully
        parsed structured result are reported as provider errors.
        """
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
        except OpenAIError as exc:
            raise LLMProviderError("The OpenAI provider request failed.") from exc
        except (ValidationError, ValueError) as exc:
            raise LLMProviderError(
                "The OpenAI response could not be parsed into the required schema."
            ) from exc

        parsed = response.output_parsed

        if not isinstance(parsed, output_model):
            raise LLMProviderError("The OpenAI provider returned no valid structured output.")

        return parsed

    @staticmethod
    def _prepare_request(
        prompt: str,
        instructions: str | None,
    ) -> tuple[str, str]:
        """Validate and normalize common request fields."""
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
