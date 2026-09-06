import asyncio
import os
import unittest
from unittest.mock import AsyncMock, patch

from core.embeddings import EmbeddingGenerator


class TestEmbeddingFailClosed(unittest.TestCase):
    def tearDown(self) -> None:
        for key in (
            "EMBEDDING_PROVIDER",
            "USE_LOCAL_EMBEDDINGS",
            "OLLAMA_BASE_URL",
            "OLLAMA_EMBEDDING_MODEL",
        ):
            os.environ.pop(key, None)

    def test_local_mode_does_not_fallback_to_gemini(self) -> None:
        os.environ["EMBEDDING_PROVIDER"] = "ollama"
        os.environ["USE_LOCAL_EMBEDDINGS"] = "1"
        generator = EmbeddingGenerator()

        with patch.object(generator, "_generate_ollama", AsyncMock(side_effect=RuntimeError("ollama down"))) as mock_local:
            with self.assertRaises(RuntimeError):
                asyncio.run(generator.generate("hello"))

        self.assertTrue(mock_local.called)


if __name__ == "__main__":
    unittest.main()
