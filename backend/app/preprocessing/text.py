"""Text and Markdown preprocessor adapter.

Conforms to Section 5 of ProjectDetails.md.
"""

from pathlib import Path
import uuid
from app.domain.document import Document, DocumentMetadata, DocumentType
from app.domain.provenance import PageRef, Provenance
from app.domain.section import Block, BlockType, Section
from app.preprocessing.base import BasePreprocessor
from app.utils.hashing import compute_sha256_file


class TextPreprocessor(BasePreprocessor):
    """Processes Plaintext and Markdown documents into canonical representation."""

    def process(self, file_path: str | Path, document_id: str) -> Document:
        path = Path(file_path)
        content_text = path.read_text(encoding="utf-8", errors="replace")
        source_hash = compute_sha256_file(path)
        file_size = path.stat().st_size

        ft = DocumentType.MARKDOWN if path.suffix.lower() == ".md" else DocumentType.TXT

        metadata = DocumentMetadata(
            title=path.stem,
            source_path=str(path),
            file_type=ft,
            file_size_bytes=file_size,
            source_hash=source_hash,
            page_count=1,
        )

        doc_prov = Provenance(
            file_id=document_id,
            document_id=document_id,
            file_name=path.name,
            file_type=path.suffix.lstrip(".").lower() or "txt",
        )

        # Split content by double newlines or headers into meaningful blocks
        raw_paragraphs = [p.strip() for p in content_text.split("\n\n") if p.strip()]
        if not raw_paragraphs:
            raw_paragraphs = [content_text.strip() or f"Content of {path.name}"]

        blocks = []
        for p in raw_paragraphs:
            btype = BlockType.HEADING if p.startswith("#") else BlockType.TEXT
            blocks.append(
                Block(
                    block_id=f"blk_{uuid.uuid4().hex[:8]}",
                    block_type=btype,
                    content=p,
                    provenance=doc_prov,
                )
            )

        section = Section(
            section_id=f"sec_{document_id}_main",
            title=path.stem,
            level=1,
            blocks=blocks,
            provenance=doc_prov,
        )

        return Document(
            document_id=document_id,
            metadata=metadata,
            sections=[section],
            normalized_markdown=content_text,
            provenance=doc_prov,
        )
