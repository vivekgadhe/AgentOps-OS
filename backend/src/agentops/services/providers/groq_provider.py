"""Groq-hosted model adapter using the OpenAI-compatible API."""

from agentops.services.providers.openai_provider import OpenAICompatibleProvider

GROQ_BASE_URL = "https://api.groq.com/openai/v1"


class GroqProvider(OpenAICompatibleProvider):
    """Structured generation through Groq.

    Groq's strict JSON-schema support is model-dependent. JSON-object mode is
    therefore used for broader model compatibility, followed by local Pydantic
    validation before the result enters the application.
    """

    def __init__(self, *, api_key: str, model: str, timeout_s: int = 60) -> None:
        super().__init__(
            api_key=api_key,
            model=model,
            base_url=GROQ_BASE_URL,
            timeout_s=timeout_s,
            structured_mode="json_object",
        )
