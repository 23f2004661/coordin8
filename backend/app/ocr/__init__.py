"""OCR package for Coordin8."""

from app.ocr.base import OCRPageResult, OCRProvider, OCRResult
from app.ocr.client import OCRServiceClient
from app.ocr.fallback_ocr import FallbackOCRProvider, get_ocr_provider
from app.ocr.mistral_ocr import MistralOCRProvider
from app.ocr.unlimited_ocr import UnlimitedOCRProvider

__all__ = [
    "OCRProvider",
    "OCRResult",
    "OCRPageResult",
    "OCRServiceClient",
    "UnlimitedOCRProvider",
    "MistralOCRProvider",
    "FallbackOCRProvider",
    "get_ocr_provider",
]
