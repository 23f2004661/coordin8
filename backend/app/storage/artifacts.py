"""Filesystem storage manager for raw and derived document artifacts.

Conforms to Section 14 of ProjectDetails.md:
- 14.1 Original artifacts (raw files)
- 14.2 Derived artifacts (normalized markdown, canonical JSON, renders, OCR results)
"""

from pathlib import Path
from typing import BinaryIO
from app.core.config import get_settings


class ArtifactStorage:
    """Manages reading and writing raw, derived, and rendered artifacts on disk."""

    def __init__(self, root_dir: str | Path | None = None) -> None:
        settings = get_settings()
        self.root = Path(root_dir or settings.artifact_root)
        self.raw_dir = self.root / "raw"
        self.derived_dir = self.root / "derived"
        self.renders_dir = self.root / "renders"
        self.temp_dir = self.root / "temp"

        for directory in [self.raw_dir, self.derived_dir, self.renders_dir, self.temp_dir]:
            directory.mkdir(parents=True, exist_ok=True)

    def save_raw_file(self, document_id: str, filename: str, content: bytes | BinaryIO) -> Path:
        """Store original uploaded file unchanged (Section 14.1)."""
        doc_folder = self.raw_dir / document_id
        doc_folder.mkdir(parents=True, exist_ok=True)
        target_path = doc_folder / filename
        if isinstance(content, bytes):
            target_path.write_bytes(content)
        else:
            with target_path.open("wb") as f:
                f.write(content.read())
        return target_path

    def save_normalized_markdown(self, document_id: str, markdown_content: str) -> Path:
        """Store human-readable intermediate markdown representation (Section 7)."""
        doc_folder = self.derived_dir / document_id
        doc_folder.mkdir(parents=True, exist_ok=True)
        target_path = doc_folder / "normalized.md"
        target_path.write_text(markdown_content, encoding="utf-8")
        return target_path

    def save_canonical_json(self, document_id: str, json_content: str) -> Path:
        """Store structured canonical JSON source of truth (Section 7)."""
        doc_folder = self.derived_dir / document_id
        doc_folder.mkdir(parents=True, exist_ok=True)
        target_path = doc_folder / "canonical.json"
        target_path.write_text(json_content, encoding="utf-8")
        return target_path

    def get_raw_file_path(self, document_id: str, filename: str) -> Path:
        return self.raw_dir / document_id / filename

    def get_normalized_markdown(self, document_id: str) -> str | None:
        path = self.derived_dir / document_id / "normalized.md"
        if path.exists():
            return path.read_text(encoding="utf-8")
        return None

    def get_canonical_json(self, document_id: str) -> str | None:
        path = self.derived_dir / document_id / "canonical.json"
        if path.exists():
            return path.read_text(encoding="utf-8")
        return None

    def delete_document_artifacts(self, document_id: str) -> None:
        import shutil
        for directory in [self.raw_dir, self.derived_dir, self.renders_dir]:
            folder = directory / document_id
            if folder.exists():
                shutil.rmtree(folder, ignore_errors=True)
