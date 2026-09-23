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

        sections: list[Section] = []
        md_slides: list[str] = [f"# {path.stem}\n"]
        slide_count = 1

        try:
            import pptx
            prs = pptx.Presentation(str(path))
            slide_count = max(1, len(prs.slides))

            for idx, slide in enumerate(prs.slides, start=1):
                slide_title = f"Slide {idx}"
                if slide.shapes.title and slide.shapes.title.text.strip():
                    slide_title = slide.shapes.title.text.strip()

                slide_prov = Provenance(
                    file_id=document_id,
                    document_id=document_id,
                    file_name=path.name,
                    file_type="pptx",
                    slide=SlideRef(slide_number=idx, slide_title=slide_title),
                )

                slide_section = Section(
                    section_id=f"sec_{document_id}_slide_{idx}",
                    title=f"Slide {idx}: {slide_title}",
                    level=1,
                    provenance=slide_prov,
                )

                slide_text_blocks = []
                for shape in slide.shapes:
                    if shape.has_text_frame:
                        for p in shape.text_frame.paragraphs:
                            text = p.text.strip()
                            if text:
                                slide_text_blocks.append(text)
                                slide_section.blocks.append(
                                    Block(
                                        block_id=f"blk_{uuid.uuid4().hex[:8]}",
                                        block_type=BlockType.TEXT,
                                        content=text,
                                        provenance=slide_prov,
                                    )
                                )
                    elif shape.has_table:
                        table_rows = []
                        for row in shape.table.rows:
                            cells = [c.text.strip() for c in row.cells]
                            table_rows.append(" | ".join(cells))
                        if table_rows:
                            t_str = "\n".join(table_rows)
                            slide_text_blocks.append(t_str)
                            slide_section.blocks.append(
                                Block(
                                    block_id=f"blk_{uuid.uuid4().hex[:8]}",
                                    block_type=BlockType.TABLE,
                                    content=t_str,
                                    provenance=slide_prov,
                                )
                            )

                if not slide_section.blocks:
                    # Fallback for slide without text
                    slide_section.blocks.append(
                        Block(
                            block_id=f"blk_{uuid.uuid4().hex[:8]}",
                            block_type=BlockType.TEXT,
                            content=f"Slide {idx}: {slide_title}",
                            provenance=slide_prov,
                        )
                    )

                sections.append(slide_section)
                content_joined = "\n\n".join(slide_text_blocks) if slide_text_blocks else slide_title
                md_slides.append(f"## Slide {idx}: {slide_title}\n\n{content_joined}\n")
        except Exception:
            pass

        if not sections:
            doc_prov = Provenance(
                file_id=document_id,
                document_id=document_id,
                file_name=path.name,
                file_type="pptx",
                slide=SlideRef(slide_number=1, slide_title="Overview"),
            )
            sec = Section(
                section_id=f"sec_{document_id}_slide_1",
                title="Slide 1",
                level=1,
                provenance=doc_prov,
            )
            sec.blocks.append(
                Block(
                    block_id=f"blk_{uuid.uuid4().hex[:8]}",
                    block_type=BlockType.TEXT,
                    content=f"Presentation slides extracted from {path.name}",
                    provenance=doc_prov,
                )
            )
            sections.append(sec)

        metadata.slide_count = slide_count
        normalized_md = "\n".join(md_slides)

        return Document(
            document_id=document_id,
            metadata=metadata,
            sections=sections,
            normalized_markdown=normalized_md,
            provenance=sections[0].provenance if sections else None,
        )
