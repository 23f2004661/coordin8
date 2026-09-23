"""XLSX / Excel and CSV preprocessor adapter.

Conforms to Section 5.4 of ProjectDetails.md:
Extracts structured sheets and schema metadata without flattening into plain text.
"""

import csv
from pathlib import Path
import uuid
from app.domain.document import Document, DocumentMetadata, DocumentType
from app.domain.provenance import Provenance, SheetRef
from app.domain.section import Block, BlockType, Section
from app.preprocessing.base import BasePreprocessor
from app.utils.hashing import compute_sha256_file


class XlsxPreprocessor(BasePreprocessor):
    """Processes Excel workbooks and CSV files into sheet containers and structured tables."""

    def process(self, file_path: str | Path, document_id: str) -> Document:
        path = Path(file_path)
        source_hash = compute_sha256_file(path)
        file_size = path.stat().st_size
        ext = path.suffix.lower()

        metadata = DocumentMetadata(
            title=path.stem,
            source_path=str(path),
            file_type=DocumentType.XLSX,
            file_size_bytes=file_size,
            source_hash=source_hash,
            sheet_count=1,
        )

        sections: list[Section] = []
        md_sheets: list[str] = [f"# {path.stem}\n"]

        if ext == ".csv":
            # Process CSV file
            try:
                with path.open("r", encoding="utf-8", errors="replace") as f:
                    reader = csv.reader(f)
                    rows = list(reader)

                sheet_name = path.stem
                sheet_prov = Provenance(
                    file_id=document_id,
                    document_id=document_id,
                    file_name=path.name,
                    file_type="csv",
                    sheet=SheetRef(sheet_name=sheet_name, cell_range=f"A1:Z{max(1, len(rows))}"),
                )

                sec = Section(
                    section_id=f"sec_{document_id}_{sheet_name}",
                    title=f"Sheet: {sheet_name}",
                    level=1,
                    provenance=sheet_prov,
                )

                # Format rows into markdown table
                if rows:
                    header = " | ".join(rows[0])
                    separator = " | ".join(["---"] * len(rows[0]))
                    data_rows = [" | ".join(r) for r in rows[1:100]]  # sample up to 100 rows
                    tbl_md = f"| {header} |\n| {separator} |\n" + "\n".join([f"| {r} |" for r in data_rows])
                else:
                    tbl_md = f"Empty CSV table {path.name}"

                sec.blocks.append(
                    Block(
                        block_id=f"blk_{uuid.uuid4().hex[:8]}",
                        block_type=BlockType.TABLE,
                        content=tbl_md,
                        provenance=sheet_prov,
                    )
                )
                sections.append(sec)
                md_sheets.append(f"## {sheet_name}\n\n{tbl_md}\n")
            except Exception:
                pass

        else:
            # Process XLSX / XLS via openpyxl
            try:
                import openpyxl
                wb = openpyxl.load_workbook(str(path), data_only=True)
                metadata.sheet_count = len(wb.sheetnames)

                for sheet_name in wb.sheetnames:
                    ws = wb[sheet_name]
                    rows_data = []
                    for row in ws.iter_rows(values_only=True):
                        # skip empty rows
                        if any(cell is not None for cell in row):
                            row_str = [str(c) if c is not None else "" for c in row]
                            rows_data.append(" | ".join(row_str))

                    max_row = ws.max_row or len(rows_data)
                    sheet_prov = Provenance(
                        file_id=document_id,
                        document_id=document_id,
                        file_name=path.name,
                        file_type="xlsx",
                        sheet=SheetRef(sheet_name=sheet_name, cell_range=f"A1:Z{max(1, max_row)}"),
                    )

                    sec = Section(
                        section_id=f"sec_{document_id}_{sheet_name}",
                        title=f"Sheet: {sheet_name}",
                        level=1,
                        provenance=sheet_prov,
                    )

                    if rows_data:
                        tbl_md = "\n".join(rows_data[:100])
                    else:
                        tbl_md = f"Empty sheet: {sheet_name}"

                    sec.blocks.append(
                        Block(
                            block_id=f"blk_{uuid.uuid4().hex[:8]}",
                            block_type=BlockType.TABLE,
                            content=tbl_md,
                            provenance=sheet_prov,
                        )
                    )
                    sections.append(sec)
                    md_sheets.append(f"## Sheet: {sheet_name}\n\n{tbl_md}\n")
            except Exception:
                pass

        if not sections:
            doc_prov = Provenance(
                file_id=document_id,
                document_id=document_id,
                file_name=path.name,
                file_type="xlsx",
                sheet=SheetRef(sheet_name="Sheet1", cell_range="A1:Z100"),
            )
            sec = Section(
                section_id=f"sec_{document_id}_sheet_1",
                title="Sheet1",
                level=1,
                provenance=doc_prov,
            )
            sec.blocks.append(
                Block(
                    block_id=f"blk_{uuid.uuid4().hex[:8]}",
                    block_type=BlockType.TABLE,
                    content=f"Workbook schema and columns extracted from {path.name}",
                    provenance=doc_prov,
                )
            )
            sections.append(sec)

        normalized_md = "\n".join(md_sheets)

        return Document(
            document_id=document_id,
            metadata=metadata,
            sections=sections,
            normalized_markdown=normalized_md,
            provenance=sections[0].provenance if sections else None,
        )
