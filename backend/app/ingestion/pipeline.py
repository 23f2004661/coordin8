"""Ingestion pipeline orchestrator."""

from dataclasses import asdict
from datetime import datetime, timezone
import json
import time
from sqlalchemy.orm import Session

from app.chunking.hierarchical import HierarchicalChunker
from app.core.logging import log_ingestion_event, logger
from app.db.models import ChunkRecord, DocumentRecord, JobRecord
from app.domain.document import Document
from app.enrichment.summaries import SummaryGenerator
from app.indexing.index_pipeline import IndexPipeline
from app.ingestion.jobs import JobManager, JobStatus
from app.preprocessing import (
    DocxPreprocessor,
    ImagePreprocessor,
    PdfPreprocessor,
    PptxPreprocessor,
    TextPreprocessor,
    TranscriptPreprocessor,
    XlsxPreprocessor,
)
from app.storage.artifacts import ArtifactStorage


class IngestionPipeline:
    """Orchestrates end-to-end ingestion from raw file to indexing."""

    def __init__(self, storage: ArtifactStorage | None = None) -> None:
        self.storage = storage or ArtifactStorage()

    def run_pipeline(self, db: Session, document_id: str, job_id: str) -> bool:
        """Execute the ingestion pipeline through all defined stages."""
        start_time = time.time()
        doc = db.query(DocumentRecord).filter(DocumentRecord.document_id == document_id).first()
        if not doc:
            JobManager.update_stage(db, job_id, JobStatus.FAILED_EXTRACTION, error_message="Document not found")
            return False

        try:
            # Select appropriate modality preprocessor
            ft = (doc.file_type or "").lower()
            if ft == "pdf":
                preprocessor = PdfPreprocessor()
            elif ft in ("docx", "doc"):
                preprocessor = DocxPreprocessor()
            elif ft in ("pptx", "ppt"):
                preprocessor = PptxPreprocessor()
            elif ft in ("xlsx", "xls", "csv"):
                preprocessor = XlsxPreprocessor()
            elif ft in ("image", "png", "jpg", "jpeg"):
                preprocessor = ImagePreprocessor()
            elif ft in ("transcript", "vtt"):
                preprocessor = TranscriptPreprocessor()
            elif ft in ("txt", "text", "md", "markdown"):
                preprocessor = TextPreprocessor()
            else:
                preprocessor = TextPreprocessor()

            # Stage 1: EXTRACTING
            logger.info("Pipeline: EXTRACTING for doc %s (%s)", document_id, ft)
            JobManager.update_stage(db, job_id, JobStatus.EXTRACTING, progress=0.15)
            canonical_doc = preprocessor.process(doc.source_path, document_id)

            # Stage 2: NORMALIZED
            logger.info("Pipeline: NORMALIZED for doc %s", document_id)
            JobManager.update_stage(db, job_id, JobStatus.NORMALIZED, progress=0.35)
            if canonical_doc.normalized_markdown:
                self.storage.save_normalized_markdown(document_id, canonical_doc.normalized_markdown)
            try:
                self.storage.save_canonical_json(
                    document_id, json.dumps(asdict(canonical_doc), default=str, indent=2)
                )
            except Exception as exc:
                logger.warning("Failed to store canonical JSON: %s", exc)

            # Stage 3: ENRICHING
            logger.info("Pipeline: ENRICHING for doc %s", document_id)
            JobManager.update_stage(db, job_id, JobStatus.ENRICHING, progress=0.60)
            summary_gen = SummaryGenerator()
            doc_summary = summary_gen.generate_document_summary(canonical_doc)
            canonical_doc.summary = doc_summary
            doc.summary = doc_summary.summary

            # Stage 4: CHUNKED
            logger.info("Pipeline: CHUNKED for doc %s", document_id)
            JobManager.update_stage(db, job_id, JobStatus.CHUNKED, progress=0.80)
            chunker = HierarchicalChunker()
            chunks = chunker.chunk_document(canonical_doc)
            for chk in chunks:
                meta = chk.metadata
                chunk_rec = ChunkRecord(
                    chunk_id=chk.chunk_id,
                    document_id=document_id,
                    parent_id=meta.parent_id if meta else None,
                    section_id=meta.section_id if meta else None,
                    content_type=meta.content_type if meta else "text",
                    content=chk.content,
                    summary=meta.summary if meta else None,
                    token_count=meta.token_count if meta else 0,
                    page_number=meta.page if meta else None,
                    slide_number=meta.slide if meta else None,
                    sheet_name=meta.sheet if meta else None,
                    source_range=meta.source_range if meta else None,
                )
                db.add(chunk_rec)
            db.commit()

            # Stage 5: INDEXING
            logger.info("Pipeline: INDEXING for doc %s", document_id)
            JobManager.update_stage(db, job_id, JobStatus.INDEXING, progress=0.95)
            indexer = IndexPipeline()
            indexer.index_document(canonical_doc)

            # Final Stage: READY
            JobManager.update_stage(db, job_id, JobStatus.READY, progress=1.0)
            doc.status = "READY"
            db.commit()

            duration = time.time() - start_time
            log_ingestion_event(
                document_id=document_id,
                job_id=job_id,
                file_type=doc.file_type,
                status="READY",
                source_hash=doc.source_hash,
                file_size=doc.file_size_bytes,
                processing_duration=duration,
            )
            return True

        except Exception as exc:
            duration = time.time() - start_time
            logger.exception("Ingestion failed for doc %s: %s", document_id, exc)
            JobManager.update_stage(
                db, job_id, JobStatus.FAILED_EXTRACTION, error_message=str(exc)
            )
            doc.status = "FAILED"
            db.commit()
            log_ingestion_event(
                document_id=document_id,
                job_id=job_id,
                file_type=doc.file_type,
                status="FAILED",
                source_hash=doc.source_hash,
                file_size=doc.file_size_bytes,
                processing_duration=duration,
                error=str(exc),
            )
            return False
