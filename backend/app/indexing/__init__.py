"""Indexing package for Coordin8."""

from app.indexing.embeddings import (
    EmbeddingProvider,
    MockEmbeddingProvider,
    get_embedding_provider,
)
from app.indexing.index_pipeline import IndexPipeline
from app.indexing.qdrant import QdrantManager
from app.indexing.sparse import SparseVectorProvider

__all__ = [
    "EmbeddingProvider",
    "MockEmbeddingProvider",
    "get_embedding_provider",
    "SparseVectorProvider",
    "QdrantManager",
    "IndexPipeline",
]
