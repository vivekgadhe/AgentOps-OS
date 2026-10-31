"""Local Ollama embedding client with strict vector validation."""

import math
from collections.abc import Sequence
from typing import Any

import httpx

EMBEDDING_DIMENSIONS = 768
DEFAULT_BATCH_SIZE = 32


class EmbeddingServiceError(RuntimeError):
    """Raised when the local embedding service is unavailable or invalid."""


class OllamaEmbeddingClient:
    """Generate embeddings through Ollama's /api/embed endpoint."""

    def __init__(
        self,
        *,
        base_url: str,
        model: str = "embeddinggemma",
        timeout_s: int = 180,
        dimensions: int = EMBEDDING_DIMENSIONS,
        batch_size: int = DEFAULT_BATCH_SIZE,
        transport: httpx.BaseTransport | None = None,
    ) -> None:

        if dimensions != EMBEDDING_DIMENSIONS:
            raise ValueError(
                f"This database schema requires {EMBEDDING_DIMENSIONS}-dimensional embeddings."
            )

        if not 1 <= batch_size <= 128:
            raise ValueError("batch_size must be between 1 and 128.")

        self.model = model
        self.dimensions = dimensions
        self.batch_size = batch_size

        self._client = httpx.Client(
            base_url=base_url.rstrip("/"),
            timeout=httpx.Timeout(timeout_s),
            transport=transport,
        )

    def __enter__(self) -> "OllamaEmbeddingClient":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def close(self) -> None:
        self._client.close()

    def embed_documents(
        self,
        texts: Sequence[str],
        *,
        title: str,
    ) -> list[list[float]]:
        """Embed document chunks using the document prompt format."""

        prepared = [f"title: {title} | text: {text}" for text in texts]

        return self._embed(prepared)

    def embed_query(self, query: str) -> list[float]:
        """Embed a search query using the retrieval query prompt."""

        prepared = f"task: search result | query: {query.strip()}"

        vectors = self._embed([prepared])

        return vectors[0]

    def _embed(
        self,
        texts: Sequence[str],
    ) -> list[list[float]]:

        if not texts:
            return []

        if any(not text.strip() for text in texts):
            raise ValueError("Embedding inputs cannot be blank.")

        vectors: list[list[float]] = []

        for start in range(0, len(texts), self.batch_size):
            batch = list(texts[start : start + self.batch_size])

            try:
                response = self._client.post(
                    "/api/embed",
                    json={
                        "model": self.model,
                        "input": batch,
                        "dimensions": self.dimensions,
                        "truncate": False,
                    },
                )

                response.raise_for_status()
                payload: Any = response.json()

            except (httpx.HTTPError, ValueError) as exc:
                raise EmbeddingServiceError("The local embedding service request failed.") from exc

            if not isinstance(payload, dict):
                raise EmbeddingServiceError("The embedding service returned an invalid response.")

            raw_vectors = payload.get("embeddings")

            if not isinstance(raw_vectors, list) or len(raw_vectors) != len(batch):
                raise EmbeddingServiceError(
                    "The embedding service returned an invalid vector count."
                )

            for raw_vector in raw_vectors:
                if not isinstance(raw_vector, list) or len(raw_vector) != self.dimensions:
                    raise EmbeddingServiceError(
                        f"The embedding service must return {self.dimensions}-dimensional vectors."
                    )

                vector: list[float] = []

                for value in raw_vector:
                    if isinstance(value, bool) or not isinstance(value, (int, float)):
                        raise EmbeddingServiceError("The embedding contains a non-numeric value.")

                    number = float(value)

                    if not math.isfinite(number):
                        raise EmbeddingServiceError("The embedding contains a non-finite value.")

                    vector.append(number)

                vectors.append(vector)

        return vectors
