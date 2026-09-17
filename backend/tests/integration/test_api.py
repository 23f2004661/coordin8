"""Integration tests for FastAPI endpoints."""

import unittest
from app.main import app


class TestAPIEndpoints(unittest.TestCase):
    def test_app_creation_and_routes(self):
        # Verify routes registered
        route_paths = [r.path for r in app.routes]
        self.assertIn("/health", route_paths)
        self.assertIn("/", route_paths)
        self.assertIn("/api/documents", route_paths)
        self.assertIn("/api/search", route_paths)
        self.assertIn("/api/answer", route_paths)


if __name__ == "__main__":
    unittest.main()
