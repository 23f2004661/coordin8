"""Dense vector embedding provider interface and local/remote clients."""

from abc import ABC, abstractmethod
from functools import lru_cache
import math
from app.core.config import get_settings


class EmbeddingProvider(ABC):
    """Abstract embedding provider contract."""

    dimension: int

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


@lru_cache(maxsize=2)
def _load_local_model(model_name: str):
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(model_name, device="cpu", trust_remote_code=False)


class LocalSentenceTransformerEmbeddingProvider(EmbeddingProvider):
    def __init__(self, model_name: str, dimension: int) -> None:
        if dimension <= 0:
            raise ValueError("Embedding dimension must be positive.")
        self.model_name = model_name
        self.dimension = dimension
        try:
            self.model = _load_local_model(model_name)
        except Exception as exc:
            raise RuntimeError(f"Cannot load local embedding model {model_name!r}.") from exc
        actual_dimension = self.model.get_sentence_embedding_dimension()
        if actual_dimension != dimension:
            raise ValueError(
                f"Embedding dimension mismatch: configured {dimension}, "
                f"model {model_name!r} returns {actual_dimension}."
            )

    def embed_text(self, text: str) -> list[float]:
        return self.embed_batch([text])[0]

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        vectors = self.model.encode(
            texts, normalize_embeddings=True, convert_to_numpy=True, show_progress_bar=False
        ).tolist()
        if len(vectors) != len(texts) or any(
            len(vector) != self.dimension or not all(math.isfinite(value) for value in vector)
            for vector in vectors
        ):
            raise ValueError("Local embedding model returned invalid vector dimensions or values.")
        return vectors


def get_embedding_provider() -> EmbeddingProvider:
    """Factory for obtaining the active embedding provider."""
    settings = get_settings()
    if settings.embedding_provider == "mock":
        return MockEmbeddingProvider(dimension=settings.embedding_dimensions)
    if settings.embedding_provider == "local":
        return LocalSentenceTransformerEmbeddingProvider(
            model_name=settings.embedding_model, dimension=settings.embedding_dimensions
        )
    raise ValueError(f"Unsupported embedding provider: {settings.embedding_provider!r}")
