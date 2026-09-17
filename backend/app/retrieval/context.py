"""Context assembly and provenance grounding conforming to Sections 19 and 20 of ProjectDetails.md."""

from dataclasses import dataclass, field
from app.core.security import sanitize_untrusted_text
from app.retrieval.chunk_retriever import RetrievedChunk


@dataclass
class EvidenceUnit:
    """Individual retrieved evidence block with clear source provenance."""
    evidence_id: str
    document_id: str
    citation: str
    content: str
    score: float


@dataclass
class AssembledContext:
    """Complete context package ready for LLM/VLM generation."""
    evidence_units: list[EvidenceUnit]
    formatted_prompt_context: str
    total_estimated_tokens: int


class ContextAssembler:
    """Assembles retrieved evidence into clean context with parent expansion and untrusted data sanitization."""

    def assemble(self, retrieved_chunks: list[RetrievedChunk], include_parent_expansion: bool = True) -> AssembledContext:
        evidence_units: list[EvidenceUnit] = []
        formatted_blocks: list[str] = []
        total_chars = 0

        for i, chunk in enumerate(retrieved_chunks, start=1):
            # Format provenance citation string conforming to Section 20
            loc_parts = []
            if chunk.page is not None:
                loc_parts.append(f"Page {chunk.page}")
            if chunk.slide is not None:
                loc_parts.append(f"Slide {chunk.slide}")
            if chunk.sheet:
                loc_parts.append(f"Sheet '{chunk.sheet}'")
            if chunk.section_id:
                loc_parts.append(f"Section {chunk.section_id}")

            loc_str = ", ".join(loc_parts) if loc_parts else "General"
            citation = f"Doc {chunk.document_id} ({loc_str})"

            # Sanitize untrusted content (Section 23)
            clean_content = sanitize_untrusted_text(chunk.content)

            evidence_units.append(
                EvidenceUnit(
                    evidence_id=f"ev_{i}",
                    document_id=chunk.document_id,
                    citation=citation,
                    content=clean_content,
                    score=chunk.score,
                )
            )

            formatted_blocks.append(
                f"--- EVIDENCE ITEM [{i}] ---\n"
                f"Source: {citation}\n"
                f"Content:\n{clean_content}\n"
            )
            total_chars += len(clean_content)

        formatted_context = "\n".join(formatted_blocks)
        estimated_tokens = max(1, total_chars // 4)

        return AssembledContext(
            evidence_units=evidence_units,
            formatted_prompt_context=formatted_context,
            total_estimated_tokens=estimated_tokens,
        )
