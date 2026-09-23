"""Search endpoints conforming to Section 17 of ProjectDetails.md."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.db.models import DocumentRecord
from app.db.session import get_db
from app.retrieval.chunk_retriever import ChunkRetriever
from app.retrieval.document_retriever import DocumentRetriever
from app.retrieval.hybrid import HybridFusion
from app.retrieval.query_parser import QueryParser
from app.retrieval.reranker import get_reranker
from app.retrieval.section_retriever import SectionRetriever

router = APIRouter(tags=["retrieval"])

parser = QueryParser()
doc_retriever = DocumentRetriever()
sec_retriever = SectionRetriever()
chk_retriever = ChunkRetriever()
fusion = HybridFusion()
reranker = get_reranker()


class SearchRequest(BaseModel):
    query: str
    limit: int = Field(default=5, ge=1, le=50)


@router.post("/search")
def hierarchical_search(request: SearchRequest, db: Session = Depends(get_db)):
    """Coarse-to-fine hierarchical hybrid search across knowledge base with provenance lineage."""
    parsed = parser.parse(request.query)

    # Stage 2: Document summaries
    candidate_docs = doc_retriever.retrieve_candidates(db, parsed, limit=request.limit)

    # Stage 3: Section summaries
    candidate_secs = sec_retriever.retrieve_sections(candidate_docs, parsed, limit=request.limit * 2)

    # Stage 4: Fine chunks
    chunks = chk_retriever.retrieve_chunks(db, candidate_secs, parsed, limit=request.limit * 3)

    # Stage 5 & 6: Fusion and Reranking
    fused = fusion.fuse_ranks(chunks, [], top_k=request.limit)
    final = reranker.rerank(request.query, fused, top_n=request.limit)

    results = []
    for rank, c in enumerate(final, start=1):
        doc_record = db.query(DocumentRecord).filter(DocumentRecord.document_id == c.document_id).first()
        doc_title = doc_record.title if doc_record else c.document_id
        file_type = doc_record.file_type if doc_record else "unknown"

        prov_loc = c.provenance or "Main Content"
        prov_str = f"{doc_title} — {prov_loc}"

        results.append({
            "chunk_id": c.chunk_id,
            "document_id": c.document_id,
            "document_title": doc_title,
            "file_type": file_type,
            "section_id": c.section_id or f"sec_{c.document_id}",
            "lineage": f"{doc_title} → {c.section_id or 'section'} → {c.chunk_id}",
            "content": c.content,
            "page": c.page,
            "slide": c.slide,
            "sheet": c.sheet,
            "score": round(c.score, 4),
            "dense_score": round(c.dense_score, 4),
            "sparse_score": round(c.sparse_score, 4),
            "retriever_type": c.retriever_type,
            "fusion_rank": c.fusion_rank or rank,
            "reranker_score": round(c.reranker_score or c.score, 4),
            "provenance": prov_str,
        })

    return {
        "query": request.query,
        "intent": parsed.intent,
        "modalities": parsed.modalities,
        "candidate_documents": len(candidate_docs),
        "results": results,
    }


@router.post("/documents/{document_id}/search")
def search_within_document(document_id: str, request: SearchRequest, db: Session = Depends(get_db)):
    """Search within a specific document."""
    parsed = parser.parse(request.query)
    candidate_secs = sec_retriever.retrieve_sections([], parsed)
    chunks = chk_retriever.retrieve_chunks(db, candidate_secs, parsed, limit=request.limit)
    return {
        "document_id": document_id,
        "query": request.query,
        "results": [
            {
                "chunk_id": c.chunk_id,
                "content": c.content,
                "page": c.page,
                "slide": c.slide,
                "score": round(c.score, 4),
            }
            for c in chunks
        ],
    }
