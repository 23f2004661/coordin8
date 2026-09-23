"""File type and format detection for Coordin8 ingestion."""

from pathlib import Path
from app.domain.document import DocumentType

EXTENSION_MAP: dict[str, DocumentType] = {
    ".pdf": DocumentType.PDF,
    ".docx": DocumentType.DOCX,
    ".doc": DocumentType.DOCX,
    ".pptx": DocumentType.PPTX,
    ".ppt": DocumentType.PPTX,
    ".xlsx": DocumentType.XLSX,
    ".xls": DocumentType.XLSX,
    ".csv": DocumentType.XLSX,
    ".png": DocumentType.IMAGE,
    ".jpg": DocumentType.IMAGE,
    ".jpeg": DocumentType.IMAGE,
    ".webp": DocumentType.IMAGE,
    ".tiff": DocumentType.IMAGE,
    ".txt": DocumentType.TXT,
    ".md": DocumentType.MARKDOWN,
    ".html": DocumentType.TXT,
    ".htm": DocumentType.TXT,
    ".py": DocumentType.TXT,
    ".js": DocumentType.TXT,
    ".ts": DocumentType.TXT,
    ".json": DocumentType.TXT,
    ".sql": DocumentType.TXT,
    ".sh": DocumentType.TXT,
    ".yaml": DocumentType.TXT,
    ".yml": DocumentType.TXT,
    ".css": DocumentType.TXT,
    ".vtt": DocumentType.TRANSCRIPT,
    ".srt": DocumentType.TRANSCRIPT,
}


def detect_file_type(filename: str, sample_bytes: bytes | None = None) -> DocumentType:
    """Detect DocumentType from file extension and optional magic byte inspection."""
    ext = Path(filename).suffix.lower()
    detected = EXTENSION_MAP.get(ext)
    if detected:
        return detected

    # Inspect header bytes if available
    if sample_bytes:
        if sample_bytes.startswith(b"%PDF"):
            return DocumentType.PDF
        if sample_bytes.startswith(b"\x89PNG") or sample_bytes.startswith(b"\xff\xd8\xff"):
            return DocumentType.IMAGE
        if sample_bytes.startswith(b"PK\x03\x04"):
            # Zip-based format (DOCX, PPTX, XLSX)
            return DocumentType.DOCX

    return DocumentType.UNKNOWN
