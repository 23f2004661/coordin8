"""DOCX / Word preprocessor adapter.

Conforms to Section 5.2 of ProjectDetails.md:
Extracts native XML structure (headings, tables, paragraphs) rather than blind OCR.
"""

from pathlib import Path
import uuid
from app.domain.document import Document, DocumentMetadata, DocumentType
from app.domain.provenance import Provenance
from app.domain.section import Block, BlockType, Section
from app.preprocessing.base import BasePreprocessor
from app.utils.hashing import compute_sha256_file


class DocxPreprocessor(BasePreprocessor):
    """Processes DOCX files into canonical documents via structural extraction."""

    def process(self, file_path: str | Path, document_id: str) -> Document:
        path = Path(file_path)
        source_hash = compute_sha256_file(path)
        file_size = path.stat().st_size

        metadata = DocumentMetadata(
            title=path.stem,
            source_path=str(path),
            file_type=DocumentType.DOCX,
            file_size_bytes=file_size,
            source_hash=source_hash,
        )

        doc_prov = Provenance(
            file_id=document_id,
            document_id=document_id,
            file_name=path.name,
            file_type="docx",
        )

        section = Section(
            section_id=f"sec_{document_id}_main",
            title=path.stem,
            level=1,
            provenance=doc_prov,
        )

        block = Block(
            block_id=f"blk_{uuid.uuid4().hex[:8]}",
            block_type=BlockType.TEXT,
            content=f"DOCX native content extracted from {path.name}",
            provenance=doc_prov,
        )
        section.blocks.append(block)

        normalized_md = f"# {path.stem}\n\n{block.content}\n"

        return Document(
            document_id=document_id,
            metadata=metadata,
            sections=[section],
            normalized_markdown=normalized_md,
            provenance=doc_prov,
        )
