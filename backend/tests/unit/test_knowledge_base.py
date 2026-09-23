"""Unit tests for the instantiable KnowledgeBase class."""

import tempfile
import unittest
from pathlib import Path

from app.knowledge_base import KnowledgeBase


class TestKnowledgeBase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.storage_path = Path(self.temp_dir.name)
        self.kb = KnowledgeBase(
            kb_id="test_kb",
            storage_dir=self.storage_path,
            db_url=f"sqlite:///{self.storage_path / 'kb_test.db'}",
            collection_prefix="test_kb_qdrant",
        )

    def tearDown(self):
        self.kb.close()
        self.temp_dir.cleanup()

    def test_instantiation_creates_isolated_artifacts_and_db(self):
        """Verify that KnowledgeBase creates its isolated database and folders."""
        self.assertTrue((self.storage_path / "kb_test.db").exists())
        self.assertTrue((self.storage_path / "artifacts" / "raw").exists())
        self.assertTrue((self.storage_path / "artifacts" / "derived").exists())
        self.assertEqual(self.kb.kb_id, "test_kb")
        self.assertEqual(self.kb.collection_prefix, "test_kb_qdrant")

    def test_ingest_bytes_markdown(self):
        """Test ingesting markdown bytes end-to-end through the pipeline."""
        sample_md = (
            "# Architecture Overview\n\n"
            "## System Design\n"
            "Coordin8 uses a multimodal hierarchical retrieval model.\n\n"
            "## Constraints\n"
            "Target latency is sub-100ms for hybrid search."
        ).encode("utf-8")

        result = self.kb.ingest_bytes(
            content=sample_md,
            filename="architecture.md",
            title="System Architecture",
        )

        self.assertTrue(result["success"])
        self.assertTrue(result["is_new"])
        self.assertEqual(result["title"], "System Architecture")
        self.assertEqual(result["file_type"], "md")
        self.assertEqual(result["status"], "READY")

        # Verify normalized markdown was saved
        doc_id = result["document_id"]
        normalized_content = self.kb.read_document(doc_id)
        self.assertIsNotNone(normalized_content)
        self.assertIn("Architecture Overview", normalized_content)

    def test_ingest_file_on_disk(self):
        """Test ingesting a file from disk."""
        test_file = self.storage_path / "sample_notes.txt"
        test_file.write_text(
            "Project Delta Notes\n"
            "Key milestones include MCP integration by Q4.\n"
            "All agent tool calling must conform to OpenWorker contracts.",
            encoding="utf-8",
        )

        res = self.kb.ingest_file(test_file)
        self.assertTrue(res["success"])
        self.assertEqual(res["file_type"], "txt")

        doc = self.kb.get_document(res["document_id"])
        self.assertIsNotNone(doc)
        self.assertEqual(doc["title"], "sample_notes")
        self.assertEqual(doc["status"], "READY")

    def test_deduplication_idempotency(self):
        """Test that re-uploading the exact same document does not duplicate it."""
        content = b"Single source of truth document for idempotency test."
        res1 = self.kb.ingest_bytes(content=content, filename="truth.txt")
        self.assertTrue(res1["is_new"])

        res2 = self.kb.ingest_bytes(content=content, filename="truth_duplicate.txt")
        self.assertFalse(res2["is_new"])
        self.assertEqual(res1["document_id"], res2["document_id"])

    def test_list_and_delete_documents(self):
        """Test listing and deleting documents cleanly removes records and files."""
        c1 = b"Doc 1 content for deletion test."
        c2 = b"Doc 2 content to remain."

        r1 = self.kb.ingest_bytes(c1, "doc1.txt")
        r2 = self.kb.ingest_bytes(c2, "doc2.txt")

        docs = self.kb.list_documents()
        self.assertEqual(len(docs), 2)

        # Delete doc1
        deleted = self.kb.delete_document(r1["document_id"])
        self.assertTrue(deleted)

        # Confirm doc1 is gone and doc2 remains
        docs_after = self.kb.list_documents()
        self.assertEqual(len(docs_after), 1)
        self.assertEqual(docs_after[0]["document_id"], r2["document_id"])
        self.assertIsNone(self.kb.get_document(r1["document_id"]))
        self.assertIsNone(self.kb.read_document(r1["document_id"]))

    def test_analyze_spreadsheet(self):
        """Test spreadsheet calculation tool call execution."""
        res = self.kb.analyze_spreadsheet(
            document_id="doc_financials",
            sheet_name="Q3_Revenue",
            operation="sum",
            column="Amount",
        )
        self.assertIn("value", res)
        self.assertIn("provenance_citation", res)
        self.assertEqual(res["operation_performed"], "sum(Amount)")


if __name__ == "__main__":
    unittest.main()
