"""Document registration and duplicate prevention."""

from pathlib import Path
import uuid
from sqlalchemy.orm import Session
from app.db.models import DocumentRecord
from app.domain.document import DocumentType
from app.storage.artifacts import ArtifactStorage
from app.utils.hashing import compute_sha256_bytes


class DocumentRegistry:
    """Handles document deduplication and database registration."""

    def __init__(self, storage: ArtifactStorage | None = None) -> None:
        self.storage = storage or ArtifactStorage()

    def register_document(
        self,
        db: Session,
        filename: str,
        content: bytes,
        file_type: DocumentType,
    ) -> tuple[DocumentRecord, bool]:
        """Register a document if not duplicate.

        Returns (DocumentRecord, is_new).
        """
        source_hash = compute_sha256_bytes(content)

        # Idempotent check (Section 15)
        existing = db.query(DocumentRecord).filter(DocumentRecord.source_hash == source_hash).first()
        if existing:
            return existing, False

        doc_id = f"doc_{uuid.uuid4().hex[:12]}"
        saved_path = self.storage.save_raw_file(doc_id, filename, content)

        record = DocumentRecord(
            document_id=doc_id,
            title=Path(filename).stem,
            file_type=file_type.value,
            file_size_bytes=len(content),
            source_hash=source_hash,
            status="REGISTERED",
            source_path=str(saved_path),
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record, True
