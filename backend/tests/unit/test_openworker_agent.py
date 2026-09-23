"""Unit tests for OpenWorkerAgent and OpenWorkerHarness."""

from pathlib import Path
import tempfile
import unittest

from app.openworker import OpenWorkerAgent, OpenWorkerHarness


class TestOpenWorkerAgent(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.workspace_root = Path(self.temp_dir.name)
        self.harness = OpenWorkerHarness(base_workspace_dir=self.workspace_root)

    def tearDown(self):
        self.harness.close_all()
        self.temp_dir.cleanup()

    def test_agent_initialization_and_private_db(self):
        """Verify that agent dynamically creates private vector DB and scoped SQLite DB."""
        agent = self.harness.create_agent(
            agent_id="test_worker_01",
            role="DevOps Specialist",
        )

        self.assertEqual(agent.agent_id, "test_worker_01")
        self.assertTrue(agent.workspace_path.exists())
        self.assertEqual(agent.kb.collection_prefix, "ow_test_worker_01")

        # Database and artifacts directory created
        self.assertTrue((agent.workspace_path / "metadata.db").exists())
        self.assertTrue((agent.workspace_path / "artifacts").exists())

    def test_agent_ingest_and_retrieval(self):
        """Verify that an agent can ingest materials into its private DB and retrieve them."""
        agent = self.harness.create_agent(agent_id="doc_worker")

        doc_bytes = (
            "# Service Mesh Architecture\n\n"
            "## Traffic Routing\n"
            "Canary deployments route 10% of production traffic through Istio envoy filters.\n\n"
            "## Circuit Breakers\n"
            "Consecutive 5xx errors exceeding 5 will trigger a 30s ejection window."
        ).encode("utf-8")

        res = agent.ingest_bytes(
            content=doc_bytes,
            filename="service_mesh.md",
            title="Service Mesh Specs",
        )

        self.assertTrue(res["success"])
        self.assertIn(res["file_type"], ["md", "markdown"])

        # Retrieval check
        search_res = agent.search("Canary deployment traffic percentage", limit=2)
        self.assertGreater(len(search_res["results"]), 0)
        self.assertIn("10%", search_res["results"][0]["content"])

        # Context query check
        ctx = agent.query_context("circuit breaker 5xx errors", limit=2)
        self.assertIn("formatted_context", ctx)
        self.assertIn("ejection window", ctx["formatted_context"])

    def test_agent_tool_calling_interface(self):
        """Verify agent tool definitions and execute_tool dispatch."""
        agent = self.harness.create_agent(agent_id="tool_worker")

        tools = agent.get_tool_definitions()
        tool_names = [t["name"] for t in tools]
        self.assertIn("search_knowledge", tool_names)
        self.assertIn("query_context", tool_names)
        self.assertIn("ingest_file", tool_names)
        self.assertIn("get_agent_info", tool_names)

        # Execute get_agent_info tool
        info = agent.execute_tool("get_agent_info", {})
        self.assertEqual(info["agent_id"], "tool_worker")
        self.assertEqual(info["total_documents"], 0)

    def test_agent_autonomous_task_reasoning(self):
        """Verify autonomous run_task creates step trajectory and grounded answer."""
        agent = self.harness.create_agent(agent_id="task_worker")

        # Ingest document
        agent.ingest_bytes(
            content=b"# API Policies\nRate limiting is strictly 100 requests per minute per tenant.",
            filename="api_limits.md",
            title="API Rate Limits",
        )

        task_result = agent.run_task("What is the rate limit per tenant?")
        self.assertEqual(task_result.agent_id, "task_worker")
        self.assertGreaterEqual(len(task_result.steps), 2)
        self.assertIn("rate limit", task_result.answer.lower())

    def test_strict_multi_agent_isolation(self):
        """Verify two agents maintain isolated vector stores and never leak data."""
        agent_alpha = self.harness.create_agent(agent_id="agent_alpha")
        agent_beta = self.harness.create_agent(agent_id="agent_beta")

        # Ingest only into Alpha
        agent_alpha.ingest_bytes(
            content=b"# Secret Alpha Plan\nProject codename is Chimera.",
            filename="secret.md",
            title="Alpha Secret",
        )

        # Check document listings
        self.assertEqual(len(agent_alpha.list_documents()), 1)
        self.assertEqual(len(agent_beta.list_documents()), 0)

        # Alpha search succeeds
        alpha_res = agent_alpha.search("Chimera", limit=2)
        self.assertEqual(len(alpha_res["results"]), 1)

        # Beta search has 0 results
        beta_res = agent_beta.search("Chimera", limit=2)
        self.assertEqual(len(beta_res["results"]), 0)


if __name__ == "__main__":
    unittest.main()
