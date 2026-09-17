"""PDF Preprocessor with layout extraction and OCR routing hook.

Conforms to Section 5.1 of ProjectDetails.md.
"""

from pathlib import Path
import uuid
from app.domain.document import Document, DocumentMetadata, DocumentType
from app.domain.provenance import PageRef, Provenance
from app.domain.section import Block, BlockType, Section
from app.ocr import get_ocr_provider
from app.preprocessing.base import BasePreprocessor
from app.utils.hashing import compute_sha256_file


class PdfPreprocessor(BasePreprocessor):
    """Processes PDF files into canonical documents, preserving page boundaries and layout."""

    def __init__(self, ocr_provider=None) -> None:
        self.ocr_provider = ocr_provider or get_ocr_provider()

    def process(self, file_path: str | Path, document_id: str) -> Document:
        path = Path(file_path)
        source_hash = compute_sha256_file(path)
        file_size = path.stat().st_size

        metadata = DocumentMetadata(
            title=path.stem,
            source_path=str(path),
            file_type=DocumentType.PDF,
            file_size_bytes=file_size,
            source_hash=source_hash,
            page_count=1,
        )

        doc_provenance = Provenance(
            file_id=document_id,
            document_id=document_id,
            file_name=path.name,
            file_type="pdf",
        )

        sections: list[Section] = []
        md_pages: list[str] = []
        page_count = 1
        total_extracted_chars = 0

        try:
            import pypdf
            reader = pypdf.PdfReader(str(path))
            page_count = max(1, len(reader.pages))
            for idx, page in enumerate(reader.pages, start=1):
                text = page.extract_text() or ""
                clean_text = text.strip()
                total_extracted_chars += len(clean_text)
                sec_prov = Provenance(
                    file_id=document_id,
                    document_id=document_id,
                    file_name=path.name,
                    file_type="pdf",
                    page=PageRef(page_number=idx),
                )
                sec = Section(
                    section_id=f"sec_{document_id}_p{idx}",
                    title=f"Page {idx}",
                    level=1,
                    provenance=sec_prov,
                )
                if clean_text:
                    blk = Block(
                        block_id=f"blk_{uuid.uuid4().hex[:8]}",
                        block_type=BlockType.TEXT,
                        content=clean_text,
                        provenance=sec_prov,
                    )
                    sec.blocks.append(blk)
                sections.append(sec)
                md_pages.append(f"[PAGE {idx}]\n\n{clean_text}")
        except Exception:
            pass

        # If scanned PDF (less than 50 text chars), invoke OCR fallback
        if total_extracted_chars < 50 and self.ocr_provider:
            try:
                ocr_results = self.ocr_provider.parse_pdf(path)
                ocr_sections: list[Section] = []
                ocr_md_pages: list[str] = []
                for r in ocr_results:
                    if not r.text_markdown.strip():
                        continue
                    sec_prov = Provenance(
                        file_id=document_id,
                        document_id=document_id,
                        file_name=path.name,
                        file_type="pdf",
                        page=PageRef(page_number=r.page_number),
                    )
                    sec = Section(
                        section_id=f"sec_{document_id}_p{r.page_number}",
                        title=f"Page {r.page_number}",
                        level=1,
                        provenance=sec_prov,
                    )
                    blk = Block(
                        block_id=f"blk_{uuid.uuid4().hex[:8]}",
                        block_type=BlockType.TEXT,
                        content=r.text_markdown.strip(),
                        provenance=sec_prov,
                    )
                    sec.blocks.append(blk)
                    ocr_sections.append(sec)
                    ocr_md_pages.append(f"[PAGE {r.page_number}]\n\n{r.text_markdown.strip()}")
                if ocr_sections:
                    sections = ocr_sections
                    md_pages = ocr_md_pages
                    page_count = len(ocr_sections)
            except Exception:
                pass

        if not sections:
            # Fallback placeholder if entirely empty
            sec_prov = Provenance(
                file_id=document_id,
                document_id=document_id,
                file_name=path.name,
                file_type="pdf",
                page=PageRef(page_number=1),
            )
            sec = Section(
                section_id=f"sec_{document_id}_p1",
                title="Page 1",
                level=1,
                provenance=sec_prov,
            )
            blk = Block(
                block_id=f"blk_{uuid.uuid4().hex[:8]}",
                block_type=BlockType.TEXT,
                content=f"PDF document {path.name}",
                provenance=sec_prov,
            )
            sec.blocks.append(blk)
            sections.append(sec)
            md_pages.append(f"[PAGE 1]\n\n{blk.content}")

        metadata.page_count = page_count
        normalized_md = f"# {path.stem}\n\n" + "\n\n".join(md_pages) + "\n"

        return Document(
            document_id=document_id,
            metadata=metadata,
            sections=sections,
            normalized_markdown=normalized_md,
            provenance=doc_provenance,
        )
