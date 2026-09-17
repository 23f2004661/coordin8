"""Stage 3: Section retrieval within candidate documents conforming to Section 11."""

from dataclasses import dataclass
from typing import Any
from app.retrieval.document_retriever import DocumentCandidate
from app.retrieval.query_parser import ParsedQuery


@dataclass
class SectionCandidate:
    document_id: str
    section_id: str
    title: str
    summary: str | None
    score: float


class SectionRetriever:
    """Searches section/slide/sheet summaries within candidate documents."""

    def retrieve_sections(
        self,
        candidate_docs: list[DocumentCandidate],
        parsed_query: ParsedQuery,
        limit: int = 10,
    ) -> list[SectionCandidate]:
        results = []
        for doc in candidate_docs:
            results.append(
                SectionCandidate(
                    document_id=doc.document_id,
                    section_id=f"sec_{doc.document_id}_main",
                    title=f"{doc.title} - Main Content",
                    summary=doc.summary,
                    score=doc.score,
                )
            )
        return results[:limit]
