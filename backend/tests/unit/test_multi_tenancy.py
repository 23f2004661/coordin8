"""Unit tests for multi-KB isolation and KnowledgeBaseManager."""

import tempfile
import unittest
from pathlib import Path

from app.knowledge_base import KnowledgeBaseManager


class TestMultiTenancy(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_path = Path(self.temp_dir.name)
        self.manager = KnowledgeBaseManager(base_storage_dir=self.base_path)

    def tearDown(self):
        for kb_id in list(self.manager._instances.keys()):
            self.manager.delete_kb(kb_id)
        self.temp_dir.cleanup()

    def test_strict_isolation_between_kbs(self):
        """Verify that searches in one KB never leak data into another KB."""
        kb_alpha = self.manager.get_or_create("project_alpha")
        kb_beta = self.manager.get_or_create("project_beta")

        # Ingest distinct documents
        kb_alpha.ingest_bytes(
            content=b"# Secret Alpha Document\nThe codename for project Alpha is SuperNova.\nDo not share.",
            filename="alpha_specs.md",
            title="Alpha Confidential",
        )

        kb_beta.ingest_bytes(
            content=b"# Secret Beta Document\nThe codename for project Beta is DeepSpace.\nRestricted access.",
            filename="beta_specs.md",
            title="Beta Confidential",
        )

        # Search in Alpha
        res_alpha = kb_alpha.search("codename for project")
        self.assertEqual(res_alpha["kb_id"], "project_alpha")
        self.assertTrue(any("SuperNova" in r["content"] for r in res_alpha["results"]))
        self.assertFalse(any("DeepSpace" in r["content"] for r in res_alpha["results"]))

        # Search in Beta
        res_beta = kb_beta.search("codename for project")
        self.assertEqual(res_beta["kb_id"], "project_beta")
        self.assertTrue(any("DeepSpace" in r["content"] for r in res_beta["results"]))
        self.assertFalse(any("SuperNova" in r["content"] for r in res_beta["results"]))

    def test_manager_lifecycle_and_deletion(self):
        """Test listing, retrieving, and deleting knowledge bases via manager."""
        self.manager.get_or_create("kb_one")
        self.manager.get_or_create("kb_two")

        kbs = self.manager.list_kbs()
        self.assertIn("kb_one", kbs)
        self.assertIn("kb_two", kbs)

        # Delete kb_one
        deleted = self.manager.delete_kb("kb_one")
        self.assertTrue(deleted)

        remaining = self.manager.list_kbs()
        self.assertNotIn("kb_one", remaining)
        self.assertIn("kb_two", remaining)


if __name__ == "__main__":
    unittest.main()
