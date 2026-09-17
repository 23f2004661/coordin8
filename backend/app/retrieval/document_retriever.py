"""Stage 2: Coarse document summary retrieval conforming to Section 11."""

from dataclasses import dataclass
from sqlalchemy.orm import Session
from app.db.models import DocumentRecord
from app.indexing.embeddings import EmbeddingProvider, get_embedding_provider
from app.retrieval.query_parser import ParsedQuery


@dataclass
class DocumentCandidate:
    document_id: str
    title: str
    summary: str | None
    score: float


class DocumentRetriever:
    """Retrieves top candidate documents by searching document-level summaries."""

    def __init__(self, embeddings: EmbeddingProvider | None = None) -> None:
        self.embeddings = embeddings or get_embedding_provider()

    def retrieve_candidates(self, db: Session, parsed_query: ParsedQuery, limit: int = 5) -> list[DocumentCandidate]:
        """Fetch candidate documents, prioritizing matching modalities but searching all available documents."""
        all_records = db.query(DocumentRecord).filter(DocumentRecord.status == "READY").all()
        if not all_records:
            return []

        candidates = []
        for r in all_records:
            score = 0.5
            # Modality boost if matching
            if parsed_query.modalities and r.file_type in parsed_query.modalities:
                score += 0.2

            text_to_check = f"{r.title} {r.summary or ''}".lower()
            for kw in parsed_query.keywords:
                if kw.lower() in text_to_check:
                    score += 0.15

            candidates.append(
                DocumentCandidate(
                    document_id=r.document_id,
                    title=r.title,
                    summary=r.summary,
                    score=min(1.0, score),
                )
            )

        candidates.sort(key=lambda x: x.score, reverse=True)
        return candidates[:limit]
