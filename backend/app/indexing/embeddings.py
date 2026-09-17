"""Dense vector embedding provider interface and local/remote clients."""

from abc import ABC, abstractmethod
import math
from app.core.config import get_settings


class EmbeddingProvider(ABC):
    """Abstract embedding provider contract."""

    @abstractmethod
    def embed_text(self, text: str) -> list[float]:
        """Generate a dense embedding vector for a single string."""
        pass

    @abstractmethod
    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate dense embedding vectors for a batch of strings."""
        pass


class MockEmbeddingProvider(EmbeddingProvider):
    """Deterministic local embedding generator for testing and standalone operation."""

    def __init__(self, dimension: int = 1024) -> None:
        self.dimension = dimension

    def embed_text(self, text: str) -> list[float]:
        # Generate deterministic normalized vector based on character hashes
        vec = [0.0] * self.dimension
        for i, char in enumerate(text[:500]):
            vec[i % self.dimension] += ord(char)
        # Normalize
        norm = math.sqrt(sum(x * x for x in vec)) or 1.0
        return [x / norm for x in vec]

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [self.embed_text(t) for t in texts]


def get_embedding_provider() -> EmbeddingProvider:
    """Factory for obtaining the active embedding provider."""
    settings = get_settings()
    # In production, can instantiate HuggingFace / OpenAI / LM Studio embedding client
    return MockEmbeddingProvider(dimension=settings.embedding_dimensions)
