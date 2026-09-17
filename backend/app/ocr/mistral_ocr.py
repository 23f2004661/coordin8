"""Mistral OCR provider adapter implementing the OCRProvider interface.

Conforms to Section 6 of ProjectDetails.md.
Uses the official Mistral OCR API (mistral-ocr-latest) as a reliable cloud fallback.
"""

import base64
import mimetypes
from pathlib import Path
import time
from typing import Any
import httpx
from app.core.config import get_settings
from app.core.logging import logger
from app.ocr.base import OCRPageResult, OCRProvider, OCRResult


class MistralOCRProvider(OCRProvider):
    """Adapter for Mistral Document and Image OCR API."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        base_url: str | None = None,
        timeout: float = 60.0,
    ) -> None:
        settings = get_settings()
        self.api_key = api_key or settings.mistral_api_key
        self.model = model or settings.mistral_ocr_model
        self.base_url = (base_url or settings.mistral_ocr_base_url).rstrip("/")
        self.timeout = timeout

    def is_available(self) -> bool:
        """Check if an API key is configured for Mistral OCR."""
        return bool(self.api_key and self.api_key.strip())

    def _encode_file_to_data_uri(self, file_path: Path, default_mime: str) -> str:
        """Read file and encode into base64 data URI."""
        mime_type, _ = mimetypes.guess_type(str(file_path))
        mime_type = mime_type or default_mime
        with file_path.open("rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")
        return f"data:{mime_type};base64,{encoded}"

    def parse_image(self, image_path: str | Path) -> OCRResult:
        path = Path(image_path)
        start_time = time.time()
        if not self.is_available():
            return OCRResult(
                text_markdown="",
                raw_text="",
                processing_time=0.0,
                warnings=["Mistral OCR skipped: MISTRAL_API_KEY is not configured."],
            )

        data_uri = self._encode_file_to_data_uri(path, default_mime="image/png")
        payload: dict[str, Any] = {
            "model": self.model,
            "document": {
                "type": "image_url",
                "image_url": data_uri,
            },
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            with httpx.Client(timeout=self.timeout) as client:
                res = client.post(f"{self.base_url}/ocr", json=payload, headers=headers)
                res.raise_for_status()
                data = res.json()

            pages = data.get("pages", [])
            full_md = "\n\n".join(p.get("markdown", "") for p in pages)
            page_results = [
                OCRPageResult(
                    page_number=p.get("index", 0) + 1,
                    text_markdown=p.get("markdown", ""),
                    raw_text=p.get("markdown", ""),
                    regions=p.get("images", []),
                )
                for p in pages
            ]

            return OCRResult(
                text_markdown=full_md,
                raw_text=full_md,
                page_number=1,
                pages=page_results,
                model_name=data.get("model", self.model),
                model_version="cloud",
                processing_time=time.time() - start_time,
                regions=[],
                warnings=[],
            )
        except Exception as exc:
            logger.warning("Mistral OCR call failed for %s: %s", path.name, exc)
            return OCRResult(
                text_markdown="",
                raw_text="",
                processing_time=time.time() - start_time,
                warnings=[f"Mistral OCR failed: {exc}"],
            )

    def parse_pdf(self, pdf_path: str | Path) -> list[OCRPageResult]:
        path = Path(pdf_path)
        if not self.is_available():
            return [
                OCRPageResult(
                    page_number=1,
                    text_markdown="",
                    warnings=["Mistral OCR skipped: MISTRAL_API_KEY is not configured."],
                )
            ]

        data_uri = self._encode_file_to_data_uri(path, default_mime="application/pdf")
        payload: dict[str, Any] = {
            "model": self.model,
            "document": {
                "type": "document_url",
                "document_url": data_uri,
            },
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            with httpx.Client(timeout=self.timeout) as client:
                res = client.post(f"{self.base_url}/ocr", json=payload, headers=headers)
                res.raise_for_status()
                data = res.json()

            pages = data.get("pages", [])
            return [
                OCRPageResult(
                    page_number=p.get("index", 0) + 1,
                    text_markdown=p.get("markdown", ""),
                    raw_text=p.get("markdown", ""),
                    regions=p.get("images", []),
                )
                for p in pages
            ]
        except Exception as exc:
            logger.warning("Mistral OCR PDF call failed for %s: %s", path.name, exc)
            return [
                OCRPageResult(
                    page_number=1,
                    text_markdown="",
                    warnings=[f"Mistral OCR failed: {exc}"],
                )
            ]
