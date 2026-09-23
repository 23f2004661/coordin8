"""Stage 5: Hybrid search and Reciprocal Rank Fusion (RRF) conforming to Section 11."""

from typing import Any
from app.retrieval.chunk_retriever import RetrievedChunk


class HybridFusion:
    """Combines dense and sparse retrieved candidate lists using Reciprocal Rank Fusion."""

    def __init__(self, rrf_k: int = 60) -> None:
        self.rrf_k = rrf_k

    def fuse_ranks(
        self,
        dense_results: list[RetrievedChunk],
        sparse_results: list[RetrievedChunk],
        top_k: int = 10,
    ) -> list[RetrievedChunk]:
        """Apply RRF: score(d) = sum(1 / (k + rank_i(d)))."""
        scores: dict[str, float] = {}
        chunk_map: dict[str, RetrievedChunk] = {}

        for rank, chunk in enumerate(dense_results, start=1):
            scores[chunk.chunk_id] = scores.get(chunk.chunk_id, 0.0) + (1.0 / (self.rrf_k + rank))
            chunk_map[chunk.chunk_id] = chunk

        for rank, chunk in enumerate(sparse_results, start=1):
            scores[chunk.chunk_id] = scores.get(chunk.chunk_id, 0.0) + (1.0 / (self.rrf_k + rank))
            chunk_map[chunk.chunk_id] = chunk

        sorted_chunk_ids = sorted(scores.keys(), key=lambda cid: scores[cid], reverse=True)

        fused = []
        for rank, cid in enumerate(sorted_chunk_ids[:top_k], start=1):
            chk = chunk_map[cid]
            chk.score = scores[cid]
            chk.fusion_rank = rank
            fused.append(chk)

        return fused
