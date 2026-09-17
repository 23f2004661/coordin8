"""Unit tests for OCR fallback and Mistral provider contracts."""

import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch
from app.ocr.base import OCRPageResult, OCRResult
from app.ocr.fallback_ocr import FallbackOCRProvider
from app.ocr.mistral_ocr import MistralOCRProvider
from app.ocr.unlimited_ocr import UnlimitedOCRProvider


class TestOCRFallback(unittest.TestCase):
    def test_mistral_not_available_without_key(self):
        provider = MistralOCRProvider(api_key="")
        self.assertFalse(provider.is_available())
        result = provider.parse_image(Path("dummy.png"))
        self.assertEqual(result.text_markdown, "")
        self.assertTrue(any("not configured" in w for w in result.warnings))

    def test_fallback_engages_when_primary_unhealthy(self):
        mock_primary = MagicMock()
        mock_primary.client.health_check.return_value = False

        mock_backup = MagicMock(spec=MistralOCRProvider)
        mock_backup.is_available.return_value = True
        mock_backup.parse_image.return_value = OCRResult(
            text_markdown="# Mistral Parsed Content",
            raw_text="Mistral Parsed Content",
            model_name="mistral-ocr-latest",
        )

        fallback = FallbackOCRProvider(primary=mock_primary, backup=mock_backup)
        res = fallback.parse_image("test_image.png")

        self.assertEqual(res.text_markdown, "# Mistral Parsed Content")
        mock_backup.parse_image.assert_called_once()


if __name__ == "__main__":
    unittest.main()
