"""Semantic chunking based on structural document boundaries."""

import uuid
from app.domain.chunk import Chunk
from app.domain.document import Document
from app.domain.section import Block, Section
from app.chunking.metadata import ChunkMetadataBuilder


class SemanticChunker:
    """Splits document blocks into coherent semantic chunks."""

    def chunk_section(self, document: Document, section: Section, max_tokens: int = 500) -> list[Chunk]:
        chunks: list[Chunk] = []
        current_content: list[str] = []
        current_tokens: int = 0

        for block in section.blocks:
            block_tokens = max(1, len(block.content) // 4)
            if current_tokens + block_tokens > max_tokens and current_content:
                # Flush current chunk
                chunk_id = f"chk_{uuid.uuid4().hex[:10]}"
                content = "\n\n".join(current_content)
                meta = ChunkMetadataBuilder.build(
                    chunk_id=chunk_id,
                    document=document,
                    section=section,
                    content=content,
                    content_type=block.block_type.value,
                )
                chunks.append(Chunk(chunk_id=chunk_id, document_id=document.document_id, content=content, metadata=meta, provenance=block.provenance or section.provenance))
                current_content = []
                current_tokens = 0

            current_content.append(block.content)
            current_tokens += block_tokens

        if current_content:
            chunk_id = f"chk_{uuid.uuid4().hex[:10]}"
            content = "\n\n".join(current_content)
            meta = ChunkMetadataBuilder.build(
                chunk_id=chunk_id,
                document=document,
                section=section,
                content=content,
                content_type=section.blocks[-1].block_type.value if section.blocks else "text",
            )
            chunks.append(Chunk(chunk_id=chunk_id, document_id=document.document_id, content=content, metadata=meta, provenance=section.provenance))

        return chunks
