"""Stage 4: Fine chunk retrieval conforming to Section 11."""

from dataclasses import dataclass
from sqlalchemy.orm import Session
from app.core.logging import logger
from app.db.models import ChunkRecord
from app.indexing.embeddings import get_embedding_provider
from app.indexing.qdrant import QdrantManager
from app.retrieval.query_parser import ParsedQuery
from app.retrieval.section_retriever import SectionCandidate


@dataclass
class RetrievedChunk:
    chunk_id: str
    document_id: str
    content: str
    section_id: str | None
    page: int | None
    slide: int | None
    sheet: str | None
    score: float
    dense_score: float = 0.0
    sparse_score: float = 0.0
    retriever_type: str = "Dense (Qdrant BGE-M3)"
    fusion_rank: int = 1
    reranker_score: float = 0.0
    provenance: str = ""


class ChunkRetriever:
    """Retrieves raw chunks, tables, and turns from candidate sections using hybrid scoring."""

    def __init__(self, qdrant: QdrantManager | None = None, embeddings=None) -> None:
        self.qdrant = qdrant or QdrantManager()
        self.embeddings = embeddings or get_embedding_provider()

    def retrieve_chunks(
        self,
        db: Session,
        candidate_sections: list[SectionCandidate],
        parsed_query: ParsedQuery,
        limit: int = 15,
    ) -> list[RetrievedChunk]:
        # Vector search in Qdrant if running
        qdrant_scores: dict[str, float] = {}
        try:
            if self.qdrant.client and parsed_query.raw_query:
                query_vec = self.embeddings.embed_text(parsed_query.raw_query)
                hits = self.qdrant.search_points(f"{self.qdrant.prefix}_chunks", query_vec, limit=limit * 2)
                for h in hits:
                    cid = h.get("payload", {}).get("chunk_id")
                    if cid:
                        qdrant_scores[cid] = float(h.get("score", 0.0))
        except Exception as exc:
            logger.warning("Qdrant chunk search failed: %s", exc)

        doc_ids = [s.document_id for s in candidate_sections if s.document_id]

        chunks_map: dict[str, ChunkRecord] = {}
        if doc_ids:
            for chk in db.query(ChunkRecord).filter(ChunkRecord.document_id.in_(doc_ids)).all():
                chunks_map[chk.chunk_id] = chk

        if qdrant_scores:
            extra = db.query(ChunkRecord).filter(ChunkRecord.chunk_id.in_(list(qdrant_scores.keys()))).all()
            for chk in extra:
                chunks_map[chk.chunk_id] = chk

        if not chunks_map:
            for chk in db.query(ChunkRecord).limit(limit * 3).all():
                chunks_map[chk.chunk_id] = chk

        chunks = list(chunks_map.values())
        if not chunks:
            return []

        q_lower = parsed_query.raw_query.lower()
        scored_chunks: list[tuple[float, float, float, str, str, ChunkRecord]] = []

        for chk in chunks:
            has_qdrant = chk.chunk_id in qdrant_scores
            dense = float(qdrant_scores.get(chk.chunk_id, 0.0))
            sparse = 0.0
            content_lower = (chk.content or "").lower()

            # Exact phrase match boost
            if q_lower in content_lower:
                sparse += 0.5

            # Keyword matches
            for kw in parsed_query.keywords:
                if kw.lower() in content_lower:
                    sparse += 0.2

            if chk.summary and any(kw.lower() in chk.summary.lower() for kw in parsed_query.keywords):
                sparse += 0.15

            sparse = min(1.0, sparse)

            if has_qdrant and sparse > 0:
                retriever_type = "Hybrid (Dense + Lexical)"
                total_score = min(1.0, (dense * 0.6) + (sparse * 0.4))
            elif has_qdrant:
                retriever_type = "Dense (Qdrant BGE-M3)"
                total_score = min(1.0, dense)
            elif sparse > 0:
                retriever_type = "Lexical BM25 / Keyword"
                total_score = min(1.0, 0.3 + (sparse * 0.7))
            else:
                retriever_type = "Structural Context"
                total_score = 0.2

            # Determine human-readable provenance location
            if chk.page_number is not None:
                prov = f"Page {chk.page_number}"
            elif chk.slide_number is not None:
                prov = f"Slide {chk.slide_number}"
            elif chk.sheet_name:
                prov = f"Sheet '{chk.sheet_name}'"
            elif chk.content_type == "image":
                prov = "Image OCR / Visual Region"
            elif chk.section_id:
                prov = f"Section {chk.section_id}"
            else:
                prov = "Main Document Content"

            scored_chunks.append((total_score, dense, sparse, retriever_type, prov, chk))

        scored_chunks.sort(key=lambda x: x[0], reverse=True)

        retrieved = []
        for rank, (score, dense, sparse, rtype, prov, chk) in enumerate(scored_chunks[:limit], start=1):
            retrieved.append(
                RetrievedChunk(
                    chunk_id=chk.chunk_id,
                    document_id=chk.document_id,
                    content=chk.content,
                    section_id=chk.section_id,
                    page=chk.page_number,
                    slide=chk.slide_number,
                    sheet=chk.sheet_name,
                    score=min(1.0, score),
                    dense_score=round(dense, 4),
                    sparse_score=round(sparse, 4),
                    retriever_type=rtype,
                    fusion_rank=rank,
                    reranker_score=round(score, 4),
                    provenance=prov,
                )
            )
        return retrieved
