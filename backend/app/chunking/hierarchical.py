"""Hierarchical chunking preserving Document -> Section -> Chunk lineage.

Conforms to Sections 3 and 9 of ProjectDetails.md.
"""

from app.chunking.semantic import SemanticChunker
from app.domain.chunk import Chunk
from app.domain.document import Document


class HierarchicalChunker:
    """Chunks documents hierarchically, maintaining parent-child relationships."""

    def __init__(self, semantic_chunker: SemanticChunker | None = None) -> None:
        self.semantic_chunker = semantic_chunker or SemanticChunker()

    def chunk_document(self, document: Document) -> list[Chunk]:
        """Convert all sections of a canonical document into retrieval chunks."""
        all_chunks: list[Chunk] = []
        for section in document.sections:
            section_chunks = self.semantic_chunker.chunk_section(document, section)
            all_chunks.extend(section_chunks)

        document.chunks = all_chunks
        return all_chunks
