"""Unit tests for local Ollama embedding requests."""

import json

import httpx
import pytest

from agentops.services.embeddings import (
    EMBEDDING_DIMENSIONS,
    EmbeddingServiceError,
    OllamaEmbeddingClient,
)


def vector_response(request: httpx.Request) -> httpx.Response:
    payload = json.loads(request.content)
    inputs = payload["input"]

    return httpx.Response(
        200,
        json={"embeddings": [[0.1] * EMBEDDING_DIMENSIONS for _ in inputs]},
    )


def test_embedding_client_sends_document_prompt_and_dimensions() -> None:
    captured: list[dict] = []

    def handler(request: httpx.Request) -> httpx.Response:
        payload = json.loads(request.content)
        captured.append(payload)
        return vector_response(request)

    with OllamaEmbeddingClient(
        base_url="http://ollama.test",
        transport=httpx.MockTransport(handler),
    ) as client:
        vectors = client.embed_documents(
            ["chunk body"],
            title="notes.md",
        )

    assert len(vectors) == 1
    assert len(vectors[0]) == EMBEDDING_DIMENSIONS
    assert captured[0]["input"] == ["title: notes.md | text: chunk body"]
    assert captured[0]["dimensions"] == EMBEDDING_DIMENSIONS
    assert captured[0]["truncate"] is False


def test_embedding_client_sends_query_prompt() -> None:
    captured: list[dict] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured.append(json.loads(request.content))
        return vector_response(request)

    with OllamaEmbeddingClient(
        base_url="http://ollama.test",
        transport=httpx.MockTransport(handler),
    ) as client:
        vector = client.embed_query("Where are delivery delays discussed?")

    assert len(vector) == EMBEDDING_DIMENSIONS
    assert captured[0]["input"] == [
        "task: search result | query: Where are delivery delays discussed?"
    ]


def test_embedding_client_rejects_wrong_vector_dimension() -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={"embeddings": [[0.1, 0.2]]},
        )

    with OllamaEmbeddingClient(
        base_url="http://ollama.test",
        transport=httpx.MockTransport(handler),
    ) as client:
        with pytest.raises(
            EmbeddingServiceError,
            match="dimensional",
        ):
            client.embed_query("question")


def test_embedding_client_rejects_provider_errors() -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            503,
            json={"error": "model unavailable"},
        )

    with OllamaEmbeddingClient(
        base_url="http://ollama.test",
        transport=httpx.MockTransport(handler),
    ) as client:
        with pytest.raises(
            EmbeddingServiceError,
            match="request failed",
        ):
            client.embed_query("question")


def test_embedding_client_rejects_non_finite_values() -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        values = [0.1] * EMBEDDING_DIMENSIONS
        values[0] = float("nan")

        # Python's JSON parser accepts NaN, allowing us to verify
        # the embedding client's explicit finite-number validation.
        raw_json = json.dumps(
            {"embeddings": [values]},
            allow_nan=True,
        )

        return httpx.Response(
            200,
            content=raw_json.encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )

    with OllamaEmbeddingClient(
        base_url="http://ollama.test",
        transport=httpx.MockTransport(handler),
    ) as client:
        with pytest.raises(
            EmbeddingServiceError,
            match="non-finite",
        ):
            client.embed_query("question")


def test_embedding_client_rejects_invalid_dimensions_at_construction() -> None:
    with pytest.raises(
        ValueError,
        match="database schema requires",
    ):
        OllamaEmbeddingClient(
            base_url="http://ollama.test",
            dimensions=512,
        )
