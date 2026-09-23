"""Integration tests for FastAPI endpoints."""

import unittest
from app.main import app


class TestAPIEndpoints(unittest.TestCase):
    def test_app_creation_and_routes(self):
        # Verify routes registered
        paths = list(app.openapi()["paths"].keys())
        self.assertIn("/health", paths)
        self.assertIn("/", paths)
        self.assertIn("/api/documents", paths)
        self.assertIn("/api/search", paths)
        self.assertIn("/api/answer", paths)


if __name__ == "__main__":
    unittest.main()
