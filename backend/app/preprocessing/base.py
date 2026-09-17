"""Base interface for all modality preprocessors in Coordin8.

Conforms to Section 5 of ProjectDetails.md:
All adapters must convert input files into the canonical Document model.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from app.domain.document import Document


class BasePreprocessor(ABC):
    """Abstract preprocessor contract for transforming a source file into a canonical Document."""

    @abstractmethod
    def process(self, file_path: str | Path, document_id: str) -> Document:
        """Parse source file into the canonical document model with sections, blocks, and provenance."""
        pass
