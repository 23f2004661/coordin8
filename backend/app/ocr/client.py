"""HTTP Client for communicating with the isolated UnlimitedOCR microservice."""

from pathlib import Path
from typing import Any
import httpx
from app.core.config import get_settings
from app.core.logging import logger


class OCRServiceClient:
    """Client for the isolated UnlimitedOCR HTTP worker."""

    def __init__(self, base_url: str | None = None, timeout: float | None = None) -> None:
        settings = get_settings()
        self.base_url = (base_url or settings.ocr_base_url).rstrip("/")
        self.timeout = timeout or settings.ocr_timeout_seconds

    def health_check(self) -> bool:
        """Check if the OCR service is reachable."""
        try:
            with httpx.Client(timeout=3.0) as client:
                res = client.get(f"{self.base_url}/health")
                return res.status_code == 200
        except Exception:
            return False

    def request_parse_image(self, image_path: str | Path) -> dict[str, Any]:
        """Send image to OCR service for parsing."""
        path = Path(image_path)
        with path.open("rb") as f:
            files = {"file": (path.name, f, "image/png")}
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(f"{self.base_url}/parse_image", files=files)
                response.raise_for_status()
                return response.json()

    def request_parse_pdf(self, pdf_path: str | Path) -> list[dict[str, Any]]:
        """Send PDF to OCR service for multi-page parsing."""
        path = Path(pdf_path)
        with path.open("rb") as f:
            files = {"file": (path.name, f, "application/pdf")}
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(f"{self.base_url}/parse_pdf", files=files)
                response.raise_for_status()
                return response.json()
