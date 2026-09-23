"""Unit tests for agent tool schemas and tool execution via KnowledgeBase."""

import tempfile
import unittest
from pathlib import Path

from app.knowledge_base import KnowledgeBase


class TestAgentTools(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.storage_path = Path(self.temp_dir.name)
        self.kb = KnowledgeBase(
            kb_id="agent_tool_kb",
            storage_dir=self.storage_path,
            db_url=f"sqlite:///{self.storage_path / 'agent.db'}",
        )

        # Ingest a seed document
        self.seed_file = self.storage_path / "system_policy.md"
        self.seed_file.write_text(
            "# System Policy\n\n"
            "## Backup Schedule\n"
            "Incremental backups are taken every 4 hours.\n\n"
            "## Retention\n"
            "Full snapshots are retained for 90 days in cold storage.",
            encoding="utf-8",
        )

    def tearDown(self):
        self.kb.close()
        self.temp_dir.cleanup()

    def test_as_tools_schema_generation(self):
        """Verify that as_tools exports valid function call definitions."""
        tools = self.kb.as_tools()
        self.assertIsInstance(tools, list)

        tool_names = [t["name"] for t in tools]
        self.assertIn("search_knowledge", tool_names)
        self.assertIn("query_context", tool_names)
        self.assertIn("read_document", tool_names)
        self.assertIn("list_documents", tool_names)
        self.assertIn("ingest_file", tool_names)
        self.assertIn("analyze_spreadsheet", tool_names)

        # Check search_knowledge schema
        search_tool = next(t for t in tools if t["name"] == "search_knowledge")
        self.assertEqual(search_tool["parameters"]["type"], "object")
        self.assertIn("query", search_tool["parameters"]["required"])

    def test_execute_tool_workflow(self):
        """Simulate an OpenWorker agent tool-call execution loop."""
        # 1. Agent calls ingest_file tool
        ingest_res = self.kb.execute_tool(
            "ingest_file",
            {"file_path": str(self.seed_file), "title": "System Backup Policy"},
        )
        self.assertTrue(ingest_res["success"])
        doc_id = ingest_res["document_id"]

        # 2. Agent calls list_documents tool
        list_res = self.kb.execute_tool("list_documents", {})
        self.assertEqual(list_res["kb_id"], "agent_tool_kb")
        self.assertEqual(len(list_res["documents"]), 1)

        # 3. Agent calls search_knowledge tool
        search_res = self.kb.execute_tool(
            "search_knowledge",
            {"query": "How long are snapshots retained?", "limit": 2},
        )
        self.assertGreater(len(search_res["results"]), 0)
        top_match = search_res["results"][0]
        self.assertIn("Retention", top_match["content"])

        # 4. Agent calls read_document tool
        read_res = self.kb.execute_tool("read_document", {"document_id": doc_id})
        self.assertIn("Backup Schedule", read_res["content"])

        # 5. Agent calls query_context tool
        ctx_res = self.kb.execute_tool(
            "query_context",
            {"query": "backup frequency", "limit": 2},
        )
        self.assertIn("formatted_context", ctx_res)

        # 6. Invalid tool call raises ValueError
        with self.assertRaises(ValueError):
            self.kb.execute_tool("non_existent_tool", {})


if __name__ == "__main__":
    unittest.main()
