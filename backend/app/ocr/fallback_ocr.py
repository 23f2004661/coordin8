"""Composite OCR provider with automatic cloud fallback.

Attempts local Unlimited-OCR first. If unavailable or fails, falls back to Mistral OCR.
"""

from pathlib import Path
from typing import Any
from app.core.logging import logger
from app.ocr.base import OCRPageResult, OCRProvider, OCRResult
from app.ocr.mistral_ocr import MistralOCRProvider
from app.ocr.unlimited_ocr import UnlimitedOCRProvider


class FallbackOCRProvider(OCRProvider):
    """Orchestrates local Unlimited-OCR with Mistral OCR as an automatic backup."""

    def __init__(
        self,
        primary: UnlimitedOCRProvider | None = None,
        backup: MistralOCRProvider | None = None,
    ) -> None:
        self.primary = primary or UnlimitedOCRProvider()
        self.backup = backup or MistralOCRProvider()

    def _is_primary_healthy(self) -> bool:
        try:
            if hasattr(self.primary, "client") and hasattr(self.primary.client, "health_check"):
                return bool(self.primary.client.health_check())
        except Exception:
            return False
        return False

    def parse_image(self, image_path: str | Path) -> OCRResult:
        primary_healthy = self._is_primary_healthy()

        if primary_healthy:
            result = self.primary.parse_image(image_path)
            if result.text_markdown and not result.warnings:
                return result
            logger.info("Local Unlimited-OCR returned empty or warned; checking fallback...")

        # If primary is not healthy or failed, check if backup is configured
        if self.backup.is_available():
            logger.info("Engaging Mistral OCR backup for image parsing: %s", image_path)
            backup_result = self.backup.parse_image(image_path)
            if backup_result.text_markdown:
                return backup_result

        # If backup not available or failed, return primary result or fallback
        if primary_healthy:
            return result
        return self.primary.parse_image(image_path)

    def parse_pdf(self, pdf_path: str | Path) -> list[OCRPageResult]:
        primary_healthy = self._is_primary_healthy()

        if primary_healthy:
            results = self.primary.parse_pdf(pdf_path)
            has_content = any(p.text_markdown for p in results)
            has_warnings = any(p.warnings for p in results)
            if has_content and not has_warnings:
                return results
            logger.info("Local Unlimited-OCR returned empty or warned for PDF; checking fallback...")

        if self.backup.is_available():
            logger.info("Engaging Mistral OCR backup for PDF parsing: %s", pdf_path)
            backup_results = self.backup.parse_pdf(pdf_path)
            if any(p.text_markdown for p in backup_results):
                return backup_results

        if primary_healthy:
            return results
        return self.primary.parse_pdf(pdf_path)


def get_ocr_provider() -> OCRProvider:
    """Factory returning the configured OCR provider with fallback."""
    return FallbackOCRProvider()
