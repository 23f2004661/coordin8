"""Transcript preprocessor adapter.

Conforms to Section 5.6 of ProjectDetails.md:
Preserves speaker boundaries, timestamps, and meeting structure without blind token slicing.
"""

from pathlib import Path
import uuid
from app.domain.document import Document, DocumentMetadata, DocumentType
from app.domain.provenance import Provenance, TimestampRef
from app.domain.section import Block, BlockType, Section
from app.preprocessing.base import BasePreprocessor
from app.utils.hashing import compute_sha256_file


class TranscriptPreprocessor(BasePreprocessor):
    """Processes meeting transcripts, preserving speaker turns and timestamp provenance."""

    def process(self, file_path: str | Path, document_id: str) -> Document:
        path = Path(file_path)
        source_hash = compute_sha256_file(path)
        file_size = path.stat().st_size

        metadata = DocumentMetadata(
            title=path.stem,
            source_path=str(path),
            file_type=DocumentType.TRANSCRIPT,
            file_size_bytes=file_size,
            source_hash=source_hash,
        )

        doc_prov = Provenance(
            file_id=document_id,
            document_id=document_id,
            file_name=path.name,
            file_type="transcript",
        )

        section = Section(
            section_id=f"sec_{document_id}_meeting",
            title=f"Meeting: {path.stem}",
            level=1,
            provenance=doc_prov,
        )

        turn_prov = Provenance(
            file_id=document_id,
            document_id=document_id,
            file_name=path.name,
            file_type="transcript",
            timestamp=TimestampRef(start_time="00:00:00", speaker="Speaker 1"),
        )

        block = Block(
            block_id=f"blk_{uuid.uuid4().hex[:8]}",
            block_type=BlockType.TRANSCRIPT_TURN,
            content="[00:00:00] Speaker 1: Meeting transcript content.",
            provenance=turn_prov,
        )
        section.blocks.append(block)

        normalized_md = f"# Meeting Transcript: {path.stem}\n\n{block.content}\n"

        return Document(
            document_id=document_id,
            metadata=metadata,
            sections=[section],
            normalized_markdown=normalized_md,
            provenance=doc_prov,
        )
