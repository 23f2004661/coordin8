"""Stage 6: Candidate Reranking conforming to Section 11."""

from abc import ABC, abstractmethod
from app.core.config import get_settings
from app.retrieval.chunk_retriever import RetrievedChunk


class BaseReranker(ABC):
    """Abstract cross-encoder / late-interaction reranker interface."""

    @abstractmethod
    def rerank(self, query: str, candidates: list[RetrievedChunk], top_n: int = 5) -> list[RetrievedChunk]:
        pass


class PassThroughReranker(BaseReranker):
    """Default lightweight reranker ordering by existing score."""

    def rerank(self, query: str, candidates: list[RetrievedChunk], top_n: int = 5) -> list[RetrievedChunk]:
        # Sort candidates by current score
        sorted_candidates = sorted(candidates, key=lambda c: c.score, reverse=True)
        return sorted_candidates[:top_n]


def get_reranker() -> BaseReranker:
    settings = get_settings()
    return PassThroughReranker()
