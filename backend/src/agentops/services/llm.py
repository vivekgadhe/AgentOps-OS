"""OpenAI-backed text generation service."""

from openai import OpenAI, OpenAIError

from agentops.core.config import Settings, get_settings


class LLMError(RuntimeError):
    """Base error for LLM operations."""


class LLMConfigurationError(LLMError):
    """Raised when the LLM service is not configured."""


class LLMProviderError(LLMError):
    """Raised when the model provider fails or returns no usable text."""


DEFAULT_INSTRUCTIONS = (
    "You are an assistant for AgentOps OS. Provide accurate, clear, and concise responses."
)


class LLMService:
    """Generate text using a configured OpenAI model."""

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
        """Generate text for a prompt and return the validated text result.

        An injected client allows unit tests to run without credentials or
        external API requests.
        """
        if not prompt.strip():
            raise ValueError("Prompt cannot be blank.")

        if instructions is None:
            resolved_instructions = DEFAULT_INSTRUCTIONS
        else:
            resolved_instructions = instructions.strip()

            if not resolved_instructions:
                raise ValueError("Instructions cannot be blank.")

        client = self._get_client()

        try:
            response = client.responses.create(
                model=self._settings.openai_model,
                instructions=resolved_instructions,
                input=prompt.strip(),
            )
        except OpenAIError as exc:
            # Avoid exposing provider response details to API consumers.
            raise LLMProviderError("The OpenAI provider request failed.") from exc

        output = response.output_text

        if not isinstance(output, str) or not output.strip():
            raise LLMProviderError("The OpenAI provider returned no text output.")

        return output.strip()

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
