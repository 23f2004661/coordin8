"""Chunk domain models for Coordin8.

Represents retrieval units produced after structural preprocessing.
Conforms directly to Section 9 of ProjectDetails.md.
"""

from dataclasses import dataclass, field
from typing import Any
from app.domain.provenance import Provenance


@dataclass
class ChunkMetadata:
    """Explicit metadata payload matching Section 9.2 of ProjectDetails.md."""
    chunk_id: str
    document_id: str
    parent_id: str | None = None  # Section ID or parent chunk ID
    document_type: str = "unknown"
    section_id: str | None = None
    content_type: str = "text"  # text, table, transcript, code
    page: int | None = None
    slide: int | None = None
    sheet: str | None = None
    source_range: str | None = None
    token_count: int = 0
    summary: str | None = None
    entities: list[str] = field(default_factory=list)
    topics: list[str] = field(default_factory=list)
    asset_ids: list[str] = field(default_factory=list)
    pipeline_version: str = "v1.0"
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize chunk metadata for vector database storage payloads."""
        return {
            "chunk_id": self.chunk_id,
            "document_id": self.document_id,
            "parent_id": self.parent_id,
            "document_type": self.document_type,
            "section_id": self.section_id,
            "content_type": self.content_type,
            "page": self.page,
            "slide": self.slide,
            "sheet": self.sheet,
            "source_range": self.source_range,
            "token_count": self.token_count,
            "summary": self.summary,
            "entities": self.entities,
            "topics": self.topics,
            "asset_ids": self.asset_ids,
            "pipeline_version": self.pipeline_version,
            **self.extra,
        }


@dataclass
class Chunk:
    """First-class retrieval chunk with provenance and parent references."""
    chunk_id: str
    document_id: str
    content: str
    metadata: ChunkMetadata
    provenance: Provenance | None = None
    embedding: list[float] | None = None
    sparse_vector: dict[int, float] | None = None  # indices -> weights
