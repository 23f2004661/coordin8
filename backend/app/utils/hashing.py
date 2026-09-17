"""Hashing utilities for idempotent ingestion and duplicate detection."""

import hashlib
from pathlib import Path


def compute_sha256_bytes(data: bytes) -> str:
    """Calculate SHA-256 hex digest of raw bytes."""
    return hashlib.sha256(data).hexdigest()


def compute_sha256_file(file_path: str | Path) -> str:
    """Calculate SHA-256 hex digest of a file in chunks to handle large files."""
    hasher = hashlib.sha256()
    path = Path(file_path)
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            hasher.update(chunk)
    return hasher.hexdigest()
