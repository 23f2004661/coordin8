"""Unit tests for hashing utilities."""

import unittest
from app.utils.hashing import compute_sha256_bytes


class TestHashing(unittest.TestCase):
    def test_compute_sha256_bytes(self):
        data = b"Coordin8 Multimodal RAG"
        digest1 = compute_sha256_bytes(data)
        digest2 = compute_sha256_bytes(data)
        self.assertEqual(digest1, digest2)
        self.assertEqual(len(digest1), 64)

    def test_different_data_produces_different_hashes(self):
        h1 = compute_sha256_bytes(b"content 1")
        h2 = compute_sha256_bytes(b"content 2")
        self.assertNotEqual(h1, h2)


if __name__ == "__main__":
    unittest.main()
