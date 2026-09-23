"""Unit tests for MCPServer and tool integration."""

import tempfile
import unittest
from pathlib import Path

from app.knowledge_base import KnowledgeBaseManager
from app.mcp.server import MCPServer
from app.mcp.tools import Coordin8Tools


class TestMCPServer(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_dir = Path(self.temp_dir.name)
        self.manager = KnowledgeBaseManager(base_storage_dir=self.base_dir)
        self.tools = Coordin8Tools(manager=self.manager)
        self.server = MCPServer(tools=self.tools)

        # Create a sample document file
        self.sample_doc = self.base_dir / "onboarding.txt"
        self.sample_doc.write_text(
            "Welcome to the Engineering Team.\n"
            "All pull requests require two peer reviews before merge.\n"
            "Production deployments occur on Tuesdays and Thursdays.",
            encoding="utf-8",
        )

    def tearDown(self):
        self.manager.close_all()
        self.temp_dir.cleanup()

    def test_list_tools_returns_full_milestone_9_catalog(self):
        """Verify list_tools exposes all MCP tools expected by OpenWorker."""
        tools = self.server.list_tools()
        self.assertIsInstance(tools, list)

        names = [t["name"] for t in tools]
        expected = [
            "create_knowledge_base",
            "list_knowledge_bases",
            "ingest_document",
            "search_knowledge",
            "query_context",
            "find_documents",
            "read_document",
            "read_section",
            "analyze_spreadsheet",
        ]
        for exp in expected:
            self.assertIn(exp, names)

    def test_call_tool_end_to_end_mcp_flow(self):
        """Verify calling MCP tools through the server dispatcher."""
        # 1. Create a custom knowledge base
        res_create = self.server.call_tool("create_knowledge_base", {"kb_id": "eng_docs"})
        self.assertTrue(res_create["success"])
        self.assertEqual(res_create["kb_id"], "eng_docs")

        # 2. Ingest document via MCP
        res_ingest = self.server.call_tool(
            "ingest_document",
            {
                "kb_id": "eng_docs",
                "file_path": str(self.sample_doc),
                "title": "Engineering Onboarding",
            },
        )
        self.assertTrue(res_ingest["success"])
        doc_id = res_ingest["document_id"]

        # 3. Search via MCP
        res_search = self.server.call_tool(
            "search_knowledge",
            {
                "kb_id": "eng_docs",
                "query": "deployment schedule",
                "limit": 2,
            },
        )
        self.assertGreater(len(res_search["results"]), 0)
        self.assertIn("deployments occur on Tuesdays", res_search["results"][0]["content"])

        # 4. Read document via MCP
        res_read = self.server.call_tool(
            "read_document",
            {"kb_id": "eng_docs", "document_id": doc_id},
        )
        self.assertTrue(res_read["found"])
        self.assertIn("Engineering Team", res_read["content"])

        # 5. Spreadsheet calculation via MCP
        res_calc = self.server.call_tool(
            "analyze_spreadsheet",
            {
                "kb_id": "eng_docs",
                "document_id": doc_id,
                "sheet_name": "Summary",
                "operation": "sum",
                "column": "PRs",
            },
        )
        self.assertIn("value", res_calc)

        # 6. Unknown tool handling
        err_res = self.server.call_tool("invalid_tool", {})
        self.assertIn("error", err_res)


if __name__ == "__main__":
    unittest.main()
