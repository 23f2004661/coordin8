"""UnlimitedOCRProvider adapter implementing the OCRProvider interface.

Conforms to Section 6 of ProjectDetails.md.
"""

from pathlib import Path
import time
from app.core.logging import logger
from app.ocr.base import OCRPageResult, OCRProvider, OCRResult
from app.ocr.client import OCRServiceClient


class UnlimitedOCRProvider(OCRProvider):
    """Adapter for Baidu Unlimited-OCR microservice."""

    def __init__(self, client: OCRServiceClient | None = None) -> None:
        self.client = client or OCRServiceClient()

    def parse_image(self, image_path: str | Path) -> OCRResult:
        start_time = time.time()
        try:
            raw = self.client.request_parse_image(image_path)
            duration = time.time() - start_time
            return OCRResult(
                text_markdown=raw.get("text_markdown", ""),
                raw_text=raw.get("raw_text", ""),
                page_number=raw.get("page_number", 1),
                model_name=raw.get("model_name", "Unlimited-OCR"),
                model_version=raw.get("model_version", "2026-07"),
                processing_time=duration,
                warnings=raw.get("warnings", []),
                regions=raw.get("regions", []),
            )
        except Exception as exc:
            logger.warning("OCR service call failed, returning fallback: %s", exc)
            return OCRResult(
                text_markdown="",
                raw_text="",
                processing_time=time.time() - start_time,
                warnings=[f"OCR service unavailable: {exc}"],
            )

    def parse_pdf(self, pdf_path: str | Path) -> list[OCRPageResult]:
        try:
            raw_pages = self.client.request_parse_pdf(pdf_path)
            results = []
            for p in raw_pages:
                results.append(
                    OCRPageResult(
                        page_number=p.get("page_number", 1),
                        text_markdown=p.get("text_markdown", ""),
                        raw_text=p.get("raw_text", ""),
                        regions=p.get("regions", []),
                        warnings=p.get("warnings", []),
                    )
                )
            return results
        except Exception as exc:
            logger.warning("OCR service call failed for PDF: %s", exc)
            return [
                OCRPageResult(
                    page_number=1,
                    text_markdown="",
                    warnings=[f"OCR service unavailable: {exc}"],
                )
            ]
