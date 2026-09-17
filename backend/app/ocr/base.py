"""OCR provider interface and data contracts conforming to Section 6 of ProjectDetails.md."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class OCRPageResult:
    """OCR extraction result for a single page."""
    page_number: int
    text_markdown: str
    raw_text: str = ""
    regions: list[dict[str, Any]] = field(default_factory=list)
    confidence: float = 1.0
    warnings: list[str] = field(default_factory=list)


@dataclass
class OCRResult:
    """Comprehensive OCR response conforming to Section 6."""
    text_markdown: str
    raw_text: str
    page_number: int = 1
    pages: list[OCRPageResult] = field(default_factory=list)
    model_name: str = "Unlimited-OCR"
    model_version: str = "2026-07"
    processing_time: float = 0.0
    warnings: list[str] = field(default_factory=list)
    regions: list[dict[str, Any]] = field(default_factory=list)


class OCRProvider(ABC):
    """Abstract adapter contract isolating UnlimitedOCR from main backend."""

    @abstractmethod
    def parse_image(self, image_path: str | Path) -> OCRResult:
        """Parse a single image."""
        pass

    @abstractmethod
    def parse_pdf(self, pdf_path: str | Path) -> list[OCRPageResult]:
        """Parse a multi-page PDF rendering pages to images."""
        pass
