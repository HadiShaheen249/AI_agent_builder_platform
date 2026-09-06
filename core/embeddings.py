"""
Embedding Generation Module
=========================
Uses local Ollama embeddings by default and fails closed when the local runtime is
unavailable. Cloud providers are only used when explicitly configured.
"""
import os
import logging

import httpx

from core.ollama_client import default_ollama_embedding_model, ollama_base_url

logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_EMBEDDING_MODEL = "gemini-embedding-001"
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"
EMBEDDING_DIMENSION = 768


def _local_embeddings_enabled() -> bool:
    return os.getenv("USE_LOCAL_EMBEDDINGS", "1").strip().lower() not in {"0", "false", "no"}


def _embedding_provider() -> str:
    provider = os.getenv("EMBEDDING_PROVIDER", "ollama").strip().lower()
    if provider in {"", "local", "ollama", "ollama_local"}:
        return "ollama"
    return provider


class EmbeddingGenerator:
    """Generate embeddings via the configured backend. Local Ollama is the default and fails closed."""

    def __init__(self):
        self.api_key = GEMINI_API_KEY
        self.model = GEMINI_EMBEDDING_MODEL
        self.dimension = EMBEDDING_DIMENSION
        self.ollama_model = default_ollama_embedding_model()
        self.ollama_base_url = ollama_base_url()

    async def _generate_ollama(self, text: str) -> list[float]:
        if not self.ollama_base_url:
            raise RuntimeError("OLLAMA_BASE_URL is not configured")

        payload = {"model": self.ollama_model, "input": text}
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(f"{self.ollama_base_url}/api/embed", json=payload)
            response.raise_for_status()
            data = response.json()
            if "embedding" in data:
                return data["embedding"]
            if "embeddings" in data and data["embeddings"]:
                return data["embeddings"][0]
            raise ValueError(f"Unexpected Ollama embedding payload: {data}")

    def _raise_local_fail_closed(self, exc: Exception) -> None:
        message = (
            "Local Ollama embedding failed in local mode and cloud fallback is disabled. "
            "Set EMBEDDING_PROVIDER=ollama and verify OLLAMA_BASE_URL and the model."
        )
        logger.error(message)
        raise RuntimeError(message) from exc

    async def generate(self, text: str) -> list[float]:
        """Generate a 768-dim embedding vector for a single text."""
        provider = _embedding_provider()
        if provider == "gemini":
            return await self._generate_gemini(text)

        if _local_embeddings_enabled():
            try:
                return await self._generate_ollama(text)
            except Exception as exc:
                self._raise_local_fail_closed(exc)

        raise RuntimeError(
            "Local embeddings are disabled or unavailable; refusing cloud fallback. "
            "Set EMBEDDING_PROVIDER=ollama and USE_LOCAL_EMBEDDINGS=1."
        )

    async def _generate_gemini(self, text: str) -> list[float]:
        if not self.api_key:
            raise RuntimeError("GEMINI_API_KEY is not configured for EMBEDDING_PROVIDER=gemini")

        url = f"{GEMINI_BASE_URL}/models/{self.model}:embedContent?key={self.api_key}"

        payload = {
            "model": f"models/{self.model}",
            "content": {"parts": [{"text": text}]},
            "outputDimensionality": self.dimension,
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
                return data["embedding"]["values"]
            except httpx.HTTPStatusError as e:
                logger.error("Gemini Embedding API error: %s - %s", e.response.status_code, e.response.text)
                raise
            except Exception as e:
                logger.error("Embedding generation failed: %s", e)
                raise

    async def generate_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts."""
        provider = _embedding_provider()
        if provider == "gemini":
            return await self._generate_batch_gemini(texts)

        if _local_embeddings_enabled():
            try:
                payload = {"model": self.ollama_model, "input": texts}
                async with httpx.AsyncClient(timeout=60.0) as client:
                    response = await client.post(f"{self.ollama_base_url}/api/embed", json=payload)
                    response.raise_for_status()
                    data = response.json()
                    if "embeddings" in data:
                        return data["embeddings"]
            except Exception as exc:
                self._raise_local_fail_closed(exc)

        raise RuntimeError(
            "Local embeddings are disabled or unavailable; refusing cloud fallback. "
            "Set EMBEDDING_PROVIDER=ollama and USE_LOCAL_EMBEDDINGS=1."
        )

    async def _generate_batch_gemini(self, texts: list[str]) -> list[list[float]]:
        if not self.api_key:
            raise RuntimeError("GEMINI_API_KEY is not configured for EMBEDDING_PROVIDER=gemini")

        url = f"{GEMINI_BASE_URL}/models/{self.model}:batchEmbedContents?key={self.api_key}"

        requests_list = [{"model": f"models/{self.model}", "content": {"parts": [{"text": t}]}} for t in texts]
        payload = {"requests": requests_list}

        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
                return [item["values"] for item in data["embeddings"]]
            except Exception as e:
                logger.error("Batch embedding failed: %s", e)
                raise

    def generate_sync(self, text: str) -> list[float]:
        """Synchronous version for startup scripts."""
        provider = _embedding_provider()
        if provider == "gemini":
            return self._generate_sync_gemini(text)

        if _local_embeddings_enabled():
            try:
                with httpx.Client(timeout=60.0) as client:
                    response = client.post(f"{self.ollama_base_url}/api/embed", json={"model": self.ollama_model, "input": text})
                    response.raise_for_status()
                    data = response.json()
                    if "embedding" in data:
                        return data["embedding"]
                    if "embeddings" in data and data["embeddings"]:
                        return data["embeddings"][0]
            except Exception as exc:
                self._raise_local_fail_closed(exc)

        raise RuntimeError(
            "Local embeddings are disabled or unavailable; refusing cloud fallback. "
            "Set EMBEDDING_PROVIDER=ollama and USE_LOCAL_EMBEDDINGS=1."
        )

    def _generate_sync_gemini(self, text: str) -> list[float]:
        if not self.api_key:
            raise RuntimeError("GEMINI_API_KEY is not configured for EMBEDDING_PROVIDER=gemini")

        import httpx as httpx_sync

        url = f"{GEMINI_BASE_URL}/models/{self.model}:embedContent?key={self.api_key}"
        payload = {
            "model": f"models/{self.model}",
            "content": {"parts": [{"text": text}]},
            "outputDimensionality": self.dimension,
        }

        response = httpx_sync.post(url, json=payload, timeout=30.0)
        response.raise_for_status()
        data = response.json()
        return data["embedding"]["values"]


# Singleton
embedding_generator = EmbeddingGenerator()
