"""Unit tests for Ollama structured generation."""

import json

import httpx

from agentops.schemas.agent_outputs import AnalysisOutput
from agentops.services.ollama_generation import OllamaStructuredGenerator


def test_ollama_generator_sends_json_schema_and_validates_response() -> None:
    captured: list[dict] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured.append(json.loads(request.content))
        return httpx.Response(
            200,
            json={
                "message": {
                    "content": json.dumps(
                        {
                            "summary": "Source material describes delivery delays.",
                            "findings": ["Delivery delays are mentioned [S1]."],
                            "recommendations": [],
                        }
                    )
                }
            },
        )

    # Inject the HTTPX client after construction to keep this test fully offline.
    generator = OllamaStructuredGenerator(
        base_url="http://ollama.test",
        model="qwen3.5:0.8b",
    )
    generator._client.close()
    generator._client = httpx.Client(
        base_url="http://ollama.test",
        transport=httpx.MockTransport(handler),
    )
    try:
        result = generator.generate_structured(
            "Analyze retrieved knowledge.",
            output_model=AnalysisOutput,
            instructions="Use retrieved sources.",
        )
    finally:
        generator.close()

    assert isinstance(result, AnalysisOutput)
    assert result.findings[0].endswith("[S1].")
    assert captured[0]["model"] == "qwen3.5:0.8b"
    assert captured[0]["format"]["type"] == "object"
    assert captured[0]["stream"] is False
    assert captured[0]["think"] is False
