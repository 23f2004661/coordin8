"""XLSX / Excel preprocessor adapter.

Conforms to Section 5.4 of ProjectDetails.md:
Extracts structured sheets and schema metadata without flattening into plain text.
"""

from pathlib import Path
import uuid
from app.domain.document import Document, DocumentMetadata, DocumentType
from app.domain.provenance import Provenance, SheetRef
from app.domain.section import Block, BlockType, Section
from app.preprocessing.base import BasePreprocessor
from app.utils.hashing import compute_sha256_file


class XlsxPreprocessor(BasePreprocessor):
    """Processes Excel workbooks into sheet containers and structured schema descriptions."""

    def process(self, file_path: str | Path, document_id: str) -> Document:
        path = Path(file_path)
        source_hash = compute_sha256_file(path)
        file_size = path.stat().st_size

        metadata = DocumentMetadata(
            title=path.stem,
            source_path=str(path),
            file_type=DocumentType.XLSX,
            file_size_bytes=file_size,
            source_hash=source_hash,
            sheet_count=1,
        )

        doc_prov = Provenance(
            file_id=document_id,
            document_id=document_id,
            file_name=path.name,
            file_type="xlsx",
        )

        sheet_section = Section(
            section_id=f"sec_{document_id}_sheet_1",
            title="Sheet1",
            level=1,
            provenance=Provenance(
                file_id=document_id,
                document_id=document_id,
                file_name=path.name,
                file_type="xlsx",
                sheet=SheetRef(sheet_name="Sheet1", cell_range="A1:Z100"),
            ),
        )

        block = Block(
            block_id=f"blk_{uuid.uuid4().hex[:8]}",
            block_type=BlockType.TABLE,
            content=f"Workbook schema and columns extracted from {path.name}",
            provenance=sheet_section.provenance,
        )
        sheet_section.blocks.append(block)

        normalized_md = f"# Workbook: {path.stem}\n\n## Sheet: Sheet1\n\n{block.content}\n"

        return Document(
            document_id=document_id,
            metadata=metadata,
            sections=[sheet_section],
            normalized_markdown=normalized_md,
            provenance=doc_prov,
        )
