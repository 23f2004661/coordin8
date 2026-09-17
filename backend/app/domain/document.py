"""Canonical Document Model for Coordin8.

Every incoming file is converted into this unified model to prevent
modality-specific logic from leaking into retrieval and generation.
Conforms to Sections 3, 7, 8, and 15 of ProjectDetails.md.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from app.domain.asset import Asset
from app.domain.chunk import Chunk
from app.domain.provenance import Provenance
from app.domain.section import Section


class DocumentType(str, Enum):
    PDF = "pdf"
    DOCX = "docx"
    PPTX = "pptx"
    XLSX = "xlsx"
    IMAGE = "image"
    TRANSCRIPT = "transcript"
    TXT = "txt"
    MARKDOWN = "md"
    UNKNOWN = "unknown"


@dataclass
class ProcessingSignature:
    """Processing version signature for idempotent re-processing (Section 15)."""
    source_hash: str
    preprocessor_version: str = "v1.0"
    ocr_model_version: str | None = None
    summary_model_version: str | None = None
    embedding_model_version: str | None = None
    chunking_version: str = "v1.0"


@dataclass
class DocumentSummary:
    """Document-level retrieval summary answering what, topics, entities, questions."""
    summary: str
    main_topics: list[str] = field(default_factory=list)
    key_entities: list[str] = field(default_factory=list)
    questions_answered: list[str] = field(default_factory=list)
    decisions_and_findings: list[str] = field(default_factory=list)


@dataclass
class DocumentMetadata:
    """Core document metadata."""
    title: str
    source_path: str
    file_type: DocumentType
    file_size_bytes: int
    source_hash: str  # sha256
    author: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    page_count: int | None = None
    slide_count: int | None = None
    sheet_count: int | None = None
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class Document:
    """Canonical Document representation across all modalities."""
    document_id: str
    metadata: DocumentMetadata
    sections: list[Section] = field(default_factory=list)
    chunks: list[Chunk] = field(default_factory=list)
    assets: list[Asset] = field(default_factory=list)
    summary: DocumentSummary | None = None
    normalized_markdown: str | None = None
    signature: ProcessingSignature | None = None
    provenance: Provenance | None = None
