"""Asset domain models for Coordin8.

Represents visual, tabular, and render artifacts extracted from documents.
Conforms to Sections 3, 5.5, and 8 of ProjectDetails.md.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from app.domain.provenance import Provenance


class AssetType(str, Enum):
    PAGE_IMAGE = "page_image"
    SLIDE_RENDER = "slide_render"
    EMBEDDED_IMAGE = "embedded_image"
    CHART = "chart"
    DIAGRAM = "diagram"
    SCREENSHOT = "screenshot"
    TABLE_IMAGE = "table_image"


@dataclass
class AssetDescription:
    """Distinct content and retrieval descriptions conforming to Section 5.5."""
    caption: str | None = None
    visual_description: str = ""  # What is visibly present (for human inspection/grounding)
    retrieval_description: str = ""  # Concepts, entities, questions answered (for retrieval)
    entities: list[str] = field(default_factory=list)
    key_labels: list[str] = field(default_factory=list)


@dataclass
class Asset:
    """An asset belonging to a canonical document."""
    asset_id: str
    document_id: str
    asset_type: AssetType
    file_path: str  # Local path or URI in storage
    mime_type: str = "image/png"
    description: AssetDescription | None = None
    provenance: Provenance | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
