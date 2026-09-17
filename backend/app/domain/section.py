"""Section and Block domain models for Coordin8.

Represents the structural units of a document (sections, headings, tables, turns).
Conforms to Sections 3 and 8 of ProjectDetails.md.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from app.domain.provenance import Provenance


class BlockType(str, Enum):
    HEADING = "heading"
    TEXT = "text"
    TABLE = "table"
    IMAGE = "image"
    CHART = "chart"
    CODE = "code"
    TRANSCRIPT_TURN = "transcript_turn"


@dataclass
class Block:
    """Atomic structural unit within a document section."""
    block_id: str
    block_type: BlockType
    content: str  # Markdown, raw text, or serialized tabular JSON
    provenance: Provenance | None = None
    level: int = 1  # e.g. heading level 1..6
    asset_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SectionSummary:
    """Retrieval-oriented summary of a section, slide, or sheet."""
    summary: str
    topics: list[str] = field(default_factory=list)
    entities: list[str] = field(default_factory=list)
    key_findings: list[str] = field(default_factory=list)


@dataclass
class Section:
    """Logical section or container in a document (e.g. chapter, slide, sheet)."""
    section_id: str
    title: str
    level: int = 1
    blocks: list[Block] = field(default_factory=list)
    summary: SectionSummary | None = None
    parent_section_id: str | None = None
    provenance: Provenance | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
