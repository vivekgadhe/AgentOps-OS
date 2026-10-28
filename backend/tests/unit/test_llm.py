"""Unit tests for the LLM service."""

from typing import cast
from unittest.mock import Mock

import pytest
from openai import OpenAI, OpenAIError
from pydantic import BaseModel

from agentops.core.config import Settings
from agentops.services.llm import (
    LLMConfigurationError,
    LLMProviderError,
    LLMService,
)


class StructuredAnswer(BaseModel):
    """Sample structured response model used by tests."""

    answer: str


def make_settings(api_key: str | None = "unit-test-key") -> Settings:
    """Build isolated settings without loading local environment files."""
    return Settings(
        _env_file=None,
        app_env="dev",
        openai_api_key=api_key,
        openai_model="unit-test-model",
        llm_timeout_s=12,
    )


@pytest.fixture
def fake_client() -> Mock:
    """Return a mock client with a successful text response."""
    client = Mock()
    client.responses.create.return_value.output_text = "  Generated answer  "
    return client


def test_generate_text_uses_configured_model_and_returns_clean_text(
    fake_client: Mock,
) -> None:
    service = LLMService(
        make_settings(),
        client=cast(OpenAI, fake_client),
    )

    result = service.generate_text(
        "  Explain AI agents.  ",
        instructions="  Be concise.  ",
    )

    assert result == "Generated answer"
    fake_client.responses.create.assert_called_once_with(
        model="unit-test-model",
        instructions="Be concise.",
        input="Explain AI agents.",
    )


def test_generate_text_uses_default_instructions(
    fake_client: Mock,
) -> None:
    service = LLMService(
        make_settings(),
        client=cast(OpenAI, fake_client),
    )

    service.generate_text("Explain tool calling.")

    request = fake_client.responses.create.call_args.kwargs
    assert request["model"] == "unit-test-model"
    assert request["input"] == "Explain tool calling."
    assert "AgentOps OS" in request["instructions"]


def test_generate_text_rejects_blank_prompt(
    fake_client: Mock,
) -> None:
    service = LLMService(
        make_settings(),
        client=cast(OpenAI, fake_client),
    )

    with pytest.raises(ValueError, match="Prompt cannot be blank"):
        service.generate_text(" \n ")

    fake_client.responses.create.assert_not_called()


def test_generate_text_rejects_blank_instructions(
    fake_client: Mock,
) -> None:
    service = LLMService(
        make_settings(),
        client=cast(OpenAI, fake_client),
    )

    with pytest.raises(ValueError, match="Instructions cannot be blank"):
        service.generate_text("Valid prompt", instructions="  ")

    fake_client.responses.create.assert_not_called()


def test_generate_text_requires_api_key_without_injected_client() -> None:
    service = LLMService(make_settings(api_key=None))

    with pytest.raises(LLMConfigurationError, match="OPENAI_API_KEY"):
        service.generate_text("Hello")


def test_generate_text_wraps_provider_errors(
    fake_client: Mock,
) -> None:
    fake_client.responses.create.side_effect = OpenAIError("Provider-specific details")
    service = LLMService(
        make_settings(),
        client=cast(OpenAI, fake_client),
    )

    with pytest.raises(
        LLMProviderError,
        match="OpenAI provider request failed",
    ):
        service.generate_text("Hello")


def test_generate_text_rejects_empty_provider_output(
    fake_client: Mock,
) -> None:
    fake_client.responses.create.return_value.output_text = " \n "
    service = LLMService(
        make_settings(),
        client=cast(OpenAI, fake_client),
    )

    with pytest.raises(
        LLMProviderError,
        match="returned no text output",
    ):
        service.generate_text("Hello")


def test_generate_structured_returns_parsed_model(
    fake_client: Mock,
) -> None:
    expected = StructuredAnswer(answer="42")
    fake_client.responses.parse.return_value.output_parsed = expected

    service = LLMService(
        make_settings(),
        client=cast(OpenAI, fake_client),
    )

    result = service.generate_structured(
        "What is the answer?",
        output_model=StructuredAnswer,
        instructions="Return an answer.",
    )

    assert result == expected
    fake_client.responses.parse.assert_called_once_with(
        model="unit-test-model",
        instructions="Return an answer.",
        input="What is the answer?",
        text_format=StructuredAnswer,
    )


def test_generate_structured_uses_default_instructions(
    fake_client: Mock,
) -> None:
    fake_client.responses.parse.return_value.output_parsed = StructuredAnswer(answer="done")
    service = LLMService(
        make_settings(),
        client=cast(OpenAI, fake_client),
    )

    result = service.generate_structured(
        "Respond.",
        output_model=StructuredAnswer,
    )

    assert result.answer == "done"
    assert (
        fake_client.responses.parse.call_args.kwargs["instructions"]
        == "You are an assistant for AgentOps OS. "
        "Provide accurate, clear, and concise responses."
    )


def test_generate_structured_rejects_blank_prompt(
    fake_client: Mock,
) -> None:
    service = LLMService(
        make_settings(),
        client=cast(OpenAI, fake_client),
    )

    with pytest.raises(ValueError, match="Prompt cannot be blank"):
        service.generate_structured(
            " \n ",
            output_model=StructuredAnswer,
        )

    fake_client.responses.parse.assert_not_called()


def test_generate_structured_rejects_missing_parsed_output(
    fake_client: Mock,
) -> None:
    fake_client.responses.parse.return_value.output_parsed = None
    service = LLMService(
        make_settings(),
        client=cast(OpenAI, fake_client),
    )

    with pytest.raises(
        LLMProviderError,
        match="no valid structured output",
    ):
        service.generate_structured(
            "Return an answer.",
            output_model=StructuredAnswer,
        )


def test_generate_structured_wraps_provider_errors(
    fake_client: Mock,
) -> None:
    fake_client.responses.parse.side_effect = OpenAIError("Provider-specific details")
    service = LLMService(
        make_settings(),
        client=cast(OpenAI, fake_client),
    )

    with pytest.raises(
        LLMProviderError,
        match="OpenAI provider request failed",
    ):
        service.generate_structured(
            "Return an answer.",
            output_model=StructuredAnswer,
        )


def test_generate_structured_requires_api_key_without_injected_client() -> None:
    service = LLMService(make_settings(api_key=None))

    with pytest.raises(LLMConfigurationError, match="OPENAI_API_KEY"):
        service.generate_structured(
            "Return an answer.",
            output_model=StructuredAnswer,
        )
