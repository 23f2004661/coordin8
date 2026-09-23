"""Integration tests for OpenWorker Agent API routes."""

import io
import unittest
from fastapi.testclient import TestClient

from app.main import app
from app.openworker import get_harness


class TestOpenWorkerAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.harness = get_harness()
        self.test_agent_id = "api_test_agent"

    def tearDown(self):
        try:
            self.harness.delete_agent(self.test_agent_id)
        except Exception:
            pass

    def test_agent_api_lifecycle_and_chat(self):
        """End-to-end API test: create agent, ingest doc, chat, call tool, delete."""
        # 1. Create agent
        res = self.client.post(
            "/api/agents",
            json={"agent_id": self.test_agent_id, "role": "Compliance Officer"},
        )
        self.assertEqual(res.status_code, 201)
        data = res.json()
        self.assertEqual(data["agent_id"], self.test_agent_id)
        self.assertIn("ow_api_test_agent", data["collections_prefix"])

        # 2. List agents
        res = self.client.get("/api/agents")
        self.assertEqual(res.status_code, 200)
        agents_list = res.json()["agents"]
        self.assertTrue(any(a["agent_id"] == self.test_agent_id for a in agents_list))

        # 3. Get agent tools
        res = self.client.get(f"/api/agents/{self.test_agent_id}/tools")
        self.assertEqual(res.status_code, 200)
        tool_names = [t["name"] for t in res.json()["tools"]]
        self.assertIn("search_knowledge", tool_names)

        # 4. Ingest document via multipart upload
        file_content = (
            b"# Compliance Guidelines\n\n"
            b"## Audit Windows\n"
            b"Internal SOC2 audits are conducted biannually in May and November.\n"
        )
        files = {"file": ("guidelines.md", io.BytesIO(file_content), "text/markdown")}
        res = self.client.post(
            f"/api/agents/{self.test_agent_id}/ingest",
            files=files,
            data={"title": "Compliance Guidelines"},
        )
        self.assertEqual(res.status_code, 200)
        ingest_data = res.json()
        self.assertTrue(ingest_data["success"])
        self.assertEqual(ingest_data["title"], "Compliance Guidelines")

        # 5. Direct tool call execution via API
        res = self.client.post(
            f"/api/agents/{self.test_agent_id}/tool_call",
            json={
                "tool_name": "search_knowledge",
                "arguments": {"query": "SOC2 audits", "limit": 1},
            },
        )
        self.assertEqual(res.status_code, 200)
        tool_result = res.json()["result"]
        self.assertGreater(len(tool_result["results"]), 0)

        # 6. Chat with agent
        res = self.client.post(
            f"/api/agents/{self.test_agent_id}/chat",
            json={"query": "When are SOC2 audits conducted?", "max_steps": 3},
        )
        self.assertEqual(res.status_code, 200)
        chat_data = res.json()
        self.assertEqual(chat_data["agent_id"], self.test_agent_id)
        self.assertGreaterEqual(len(chat_data["steps"]), 1)
        self.assertIn("audit", chat_data["answer"].lower())

        # 7. Delete agent
        res = self.client.delete(f"/api/agents/{self.test_agent_id}")
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json()["success"])


if __name__ == "__main__":
    unittest.main()
