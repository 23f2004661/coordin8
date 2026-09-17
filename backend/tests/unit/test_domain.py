"""Unit tests for Canonical Document models and Provenance."""

import unittest
from app.domain.asset import Asset, AssetDescription, AssetType
from app.domain.chunk import Chunk, ChunkMetadata
from app.domain.document import Document, DocumentMetadata, DocumentType
from app.domain.provenance import PageRef, Provenance, SheetRef, SlideRef, TimestampRef
from app.domain.section import Block, BlockType, Section, SectionSummary


class TestCanonicalDomain(unittest.TestCase):
    def test_provenance_citation_formatting(self):
        # Page citation
        prov_page = Provenance(
            file_id="doc_1",
            document_id="doc_1",
            file_name="Report.pdf",
            file_type="pdf",
            page=PageRef(page_number=14),
        )
        self.assertEqual(prov_page.to_citation_string(), "Report.pdf — Page 14")

        # Slide citation
        prov_slide = Provenance(
            file_id="doc_2",
            document_id="doc_2",
            file_name="Strategy.pptx",
            file_type="pptx",
            slide=SlideRef(slide_number=17),
        )
        self.assertEqual(prov_slide.to_citation_string(), "Strategy.pptx — Slide 17")

        # Spreadsheet citation
        prov_sheet = Provenance(
            file_id="doc_3",
            document_id="doc_3",
            file_name="Sales.xlsx",
            file_type="xlsx",
            sheet=SheetRef(sheet_name="Sales", cell_range="B2042:H5831"),
        )
        self.assertEqual(prov_sheet.to_citation_string(), "Sales.xlsx — Sheet 'Sales'!B2042:H5831")

        # Meeting timestamp citation
        prov_transcript = Provenance(
            file_id="doc_4",
            document_id="doc_4",
            file_name="Meeting.vtt",
            file_type="transcript",
            timestamp=TimestampRef(start_time="00:18:32", end_time="00:21:10", speaker="Priya"),
        )
        self.assertEqual(prov_transcript.to_citation_string(), "Meeting.vtt — [00:18:32–00:21:10] Priya")

    def test_chunk_metadata_serialization(self):
        meta = ChunkMetadata(
            chunk_id="chk_123",
            document_id="doc_456",
            parent_id="sec_789",
            document_type="pdf",
            content_type="text",
            page=14,
            token_count=120,
            summary="Test summary",
            entities=["Redis", "FastAPI"],
            topics=["Architecture"],
        )
        d = meta.to_dict()
        self.assertEqual(d["chunk_id"], "chk_123")
        self.assertEqual(d["page"], 14)
        self.assertIn("Redis", d["entities"])

    def test_document_hierarchy(self):
        meta = DocumentMetadata(
            title="Architecture",
            source_path="/docs/arch.pdf",
            file_type=DocumentType.PDF,
            file_size_bytes=1024,
            source_hash="abcd1234efgh5678",
        )
        sec = Section(
            section_id="sec_1",
            title="Introduction",
            summary=SectionSummary(summary="Overview section"),
        )
        doc = Document(document_id="doc_1", metadata=meta, sections=[sec])
        self.assertEqual(len(doc.sections), 1)
        self.assertEqual(doc.sections[0].title, "Introduction")


if __name__ == "__main__":
    unittest.main()
