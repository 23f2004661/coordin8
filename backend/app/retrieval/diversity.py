"""Relevance-gated final evidence selection over already-ranked chunks."""

from collections import Counter
from math import ceil

from app.retrieval.chunk_retriever import RetrievedChunk


def normalize_chunk_text(content: str) -> str:
    return content.replace("\r\n", "\n").replace("\r", "\n").strip()


class FinalCandidateSelector:
    """Deduplicate and diversify without changing chunk content, order, or scores."""

    def select(
        self,
        candidates: list[RetrievedChunk],
        top_k: int,
        relevance_scores: dict[str, float] | None = None,
    ) -> list[RetrievedChunk]:
        if top_k <= 0 or not candidates:
            return []
        unique = []
        seen_text = set()
        for chunk in candidates:
            text = normalize_chunk_text(chunk.content)
            if text not in seen_text:
                unique.append(chunk)
                seen_text.add(text)

        def relevance(chunk):
            return relevance_scores.get(chunk.chunk_id, chunk.score) if relevance_scores is not None else chunk.score

        baseline_cutoff = max(0.0, relevance(unique[min(top_k, len(unique)) - 1]))
        eligible = [chunk for chunk in unique if relevance(chunk) >= 0.9 * baseline_cutoff]
        document_count = len({chunk.document_id for chunk in eligible})
        per_document_cap = max(2, ceil(top_k / max(1, document_count)))
        selected = []
        counts = Counter()
        for chunk in eligible:
            if counts[chunk.document_id] < per_document_cap:
                selected.append(chunk)
                counts[chunk.document_id] += 1
                if len(selected) == top_k:
                    break
        selected_ids = {chunk.chunk_id for chunk in selected}
        for chunk in unique:
            if len(selected) == top_k:
                break
            if chunk.chunk_id not in selected_ids:
                selected.append(chunk)
                selected_ids.add(chunk.chunk_id)
        selected_ids = {chunk.chunk_id for chunk in selected}
        return [chunk for chunk in unique if chunk.chunk_id in selected_ids]