"""Answer generation endpoint conforming to Section 17 & 34 of ProjectDetails.md."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.llm.client import LLMClient
from app.retrieval.chunk_retriever import ChunkRetriever
from app.retrieval.context import ContextAssembler
from app.retrieval.document_retriever import DocumentRetriever
from app.retrieval.hybrid import HybridFusion
from app.retrieval.query_parser import QueryParser
from app.retrieval.reranker import get_reranker
from app.retrieval.section_retriever import SectionRetriever

router = APIRouter(tags=["generation"])

parser = QueryParser()
doc_retriever = DocumentRetriever()
sec_retriever = SectionRetriever()
chk_retriever = ChunkRetriever()
fusion = HybridFusion()
reranker = get_reranker()
assembler = ContextAssembler()
llm_client = LLMClient()


class AnswerRequest(BaseModel):
    query: str
    include_citations: bool = True
    max_evidence_chunks: int = Field(default=5, ge=1, le=20)


@router.post("/answer")
def generate_grounded_answer(request: AnswerRequest, db: Session = Depends(get_db)):
    """Generate evidence-backed answer with strict provenance citations."""
    parsed = parser.parse(request.query)

    # Coarse to fine hierarchical retrieval
    docs = doc_retriever.retrieve_candidates(db, parsed, limit=request.max_evidence_chunks)
    secs = sec_retriever.retrieve_sections(docs, parsed, limit=request.max_evidence_chunks * 2)
    raw_chunks = chk_retriever.retrieve_chunks(db, secs, parsed, limit=request.max_evidence_chunks * 2)

    # Hybrid fusion & Reranking
    fused = fusion.fuse_ranks(raw_chunks, [], top_k=request.max_evidence_chunks)
    ranked = reranker.rerank(request.query, fused, top_n=request.max_evidence_chunks)

    # Context assembly & prompt construction
    context = assembler.assemble(ranked)

    # LLM generation
    answer = llm_client.generate_answer(request.query, context.formatted_prompt_context)

    citations = [e.citation for e in context.evidence_units]
    evidence_items = [
        {
            "evidence_id": e.evidence_id,
            "document_id": e.document_id,
            "citation": e.citation,
            "score": round(e.score, 4),
            "content": e.content,
        }
        for e in context.evidence_units
    ]

    return {
        "query": request.query,
        "answer": answer,
        "citations": citations,
        "evidence_items": evidence_items,
        "evidence_used": len(context.evidence_units),
        "estimated_context_tokens": context.total_estimated_tokens,
    }
