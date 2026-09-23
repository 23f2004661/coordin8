"""Unit tests for retrieval and context assembly via KnowledgeBase."""

import tempfile
import unittest
from pathlib import Path

from app.knowledge_base import KnowledgeBase


class TestKnowledgeBaseRetrieval(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.storage_path = Path(self.temp_dir.name)
        self.kb = KnowledgeBase(
            kb_id="retrieval_test_kb",
            storage_dir=self.storage_path,
            db_url=f"sqlite:///{self.storage_path / 'retrieval.db'}",
            collection_prefix="retrieval_test_qdrant",
        )

        # Ingest test documentation
        doc1_content = (
            "# API Gateway Migration Plan\n\n"
            "## Decision Rationale\n"
            "We decided to move the API gateway migration to Q4 due to dependency on Kubernetes v1.30.\n\n"
            "## Risk Assessment\n"
            "Upstream latency must remain below 45 milliseconds during traffic switchover."
        ).encode("utf-8")

        self.doc1 = self.kb.ingest_bytes(
            content=doc1_content,
            filename="api_gateway_plan.md",
            title="Gateway Migration Strategy",
        )

    def tearDown(self):
        self.kb.close()
        self.temp_dir.cleanup()

    def test_search_hierarchical_hybrid(self):
        """Test hierarchical search across ingested chunks."""
        search_res = self.kb.search("Why was API gateway moved to Q4?", limit=3)

        self.assertEqual(search_res["kb_id"], "retrieval_test_kb")
        self.assertGreater(search_res["candidate_documents"], 0)
        self.assertGreater(len(search_res["results"]), 0)

        top_hit = search_res["results"][0]
        self.assertIn("chunk_id", top_hit)
        self.assertIn("document_id", top_hit)
        self.assertEqual(top_hit["document_title"], "Gateway Migration Strategy")
        self.assertIn("provenance", top_hit)
        self.assertIn("lineage", top_hit)
        self.assertIn("content", top_hit)

    def test_query_context_prompt_assembly(self):
        """Test that query_context formats evidence blocks and citations for LLM consumption."""
        ctx_res = self.kb.query_context("Kubernetes latency constraint", limit=3)

        self.assertEqual(ctx_res["kb_id"], "retrieval_test_kb")
        self.assertIn("formatted_context", ctx_res)
        self.assertIn("evidence_units", ctx_res)
        self.assertGreater(len(ctx_res["evidence_units"]), 0)

        # Verify evidence citations conform to Section 20
        first_evidence = ctx_res["evidence_units"][0]
        self.assertIn("citation", first_evidence)
        self.assertIn("content", first_evidence)
        self.assertIn("--- EVIDENCE ITEM", ctx_res["formatted_context"])
        self.assertGreater(ctx_res["estimated_tokens"], 0)

    def test_search_scoped_to_document_id(self):
        """Test searching with an explicit document_id filter."""
        doc2_content = b"# Unrelated Marketing Document\nQuarterly brand guidelines and logo rules."
        doc2 = self.kb.ingest_bytes(doc2_content, "marketing.md", title="Marketing Guide")

        # Search specifically within doc1
        res = self.kb.search("guidelines", document_id=self.doc1["document_id"])
        # Should not return doc2 chunks
        for item in res["results"]:
            self.assertEqual(item["document_id"], self.doc1["document_id"])


if __name__ == "__main__":
    unittest.main()
