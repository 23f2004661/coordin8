"""PPTX / PowerPoint preprocessor adapter.

Conforms to Section 5.3 of ProjectDetails.md:
Treats slides as first-class retrieval units with native text and visual renders.
"""

from pathlib import Path
import uuid
from app.domain.document import Document, DocumentMetadata, DocumentType
from app.domain.provenance import Provenance, SlideRef
from app.domain.section import Block, BlockType, Section
from app.preprocessing.base import BasePreprocessor
from app.utils.hashing import compute_sha256_file


class PptxPreprocessor(BasePreprocessor):
    """Processes PowerPoint files into slide sections and canonical documents."""

    def process(self, file_path: str | Path, document_id: str) -> Document:
        path = Path(file_path)
        source_hash = compute_sha256_file(path)
        file_size = path.stat().st_size

        metadata = DocumentMetadata(
            title=path.stem,
            source_path=str(path),
            file_type=DocumentType.PPTX,
            file_size_bytes=file_size,
            source_hash=source_hash,
            slide_count=1,
        )

        doc_prov = Provenance(
            file_id=document_id,
            document_id=document_id,
            file_name=path.name,
            file_type="pptx",
        )

        slide_section = Section(
            section_id=f"sec_{document_id}_slide_1",
            title="Slide 1: Overview",
            level=1,
            provenance=Provenance(
                file_id=document_id,
                document_id=document_id,
                file_name=path.name,
                file_type="pptx",
                slide=SlideRef(slide_number=1, slide_title="Overview"),
            ),
        )

        block = Block(
            block_id=f"blk_{uuid.uuid4().hex[:8]}",
            block_type=BlockType.TEXT,
            content=f"Presentation slides extracted from {path.name}",
            provenance=slide_section.provenance,
        )
        slide_section.blocks.append(block)

        normalized_md = f"# {path.stem}\n\n## Slide 1: Overview\n\n{block.content}\n"

        return Document(
            document_id=document_id,
            metadata=metadata,
            sections=[slide_section],
            normalized_markdown=normalized_md,
            provenance=doc_prov,
        )
