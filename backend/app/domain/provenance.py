"""Provenance models for Coordin8.

Preserves the complete lineage back to the exact source file location:
page, slide, sheet, cell/range, timestamp, or block id.
Conforms to Sections 3 and 20 of ProjectDetails.md.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class PageRef:
    """Provenance pointer to a specific document page (e.g. PDF)."""
    page_number: int
    bounding_box: list[float] | None = None  # [x0, y0, x1, y1] normalized


@dataclass
class SlideRef:
    """Provenance pointer to a presentation slide (e.g. PPTX)."""
    slide_number: int
    slide_title: str | None = None


@dataclass
class SheetRef:
    """Provenance pointer to a spreadsheet sheet and cell/range (e.g. XLSX)."""
    sheet_name: str
    cell_range: str | None = None  # e.g. "B2042:H5831"


@dataclass
class TimestampRef:
    """Provenance pointer to an audio/video/meeting timestamp range."""
    start_time: str  # "HH:MM:SS" or seconds
    end_time: str | None = None
    speaker: str | None = None


@dataclass
class Provenance:
    """Complete provenance citation record for an evidence unit."""
    file_id: str
    document_id: str
    file_name: str
    file_type: str
    section_id: str | None = None
    block_id: str | None = None
    chunk_id: str | None = None

    # Modality-specific anchors
    page: PageRef | None = None
    slide: SlideRef | None = None
    sheet: SheetRef | None = None
    timestamp: TimestampRef | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    def to_citation_string(self) -> str:
        """Format human-readable citation string conforming to Section 20."""
        parts = [self.file_name]
        if self.page:
            parts.append(f"Page {self.page.page_number}")
        if self.slide:
            parts.append(f"Slide {self.slide.slide_number}")
        if self.sheet:
            loc = f"Sheet '{self.sheet.sheet_name}'"
            if self.sheet.cell_range:
                loc += f"!{self.sheet.cell_range}"
            parts.append(loc)
        if self.timestamp:
            ts = self.timestamp.start_time
            if self.timestamp.end_time:
                ts += f"–{self.timestamp.end_time}"
            if self.timestamp.speaker:
                parts.append(f"[{ts}] {self.timestamp.speaker}")
            else:
                parts.append(f"[{ts}]")
        if self.section_id:
            parts.append(f"Section {self.section_id}")
        return " — ".join(parts)
