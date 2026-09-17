"""Job pipeline state machine conforming to Section 16 of ProjectDetails.md."""

from enum import Enum
import uuid
from sqlalchemy.orm import Session
from app.db.models import JobRecord


class JobStatus(str, Enum):
    REGISTERED = "REGISTERED"
    EXTRACTING = "EXTRACTING"
    NORMALIZED = "NORMALIZED"
    ENRICHING = "ENRICHING"
    CHUNKED = "CHUNKED"
    INDEXING = "INDEXING"
    READY = "READY"

    # Failure states
    FAILED_EXTRACTION = "FAILED_EXTRACTION"
    FAILED_OCR = "FAILED_OCR"
    FAILED_ENRICHMENT = "FAILED_ENRICHMENT"
    FAILED_INDEXING = "FAILED_INDEXING"


class JobManager:
    """Manages tracking, transitions, and status updates for ingestion jobs."""

    @staticmethod
    def create_job(db: Session, document_id: str) -> JobRecord:
        job = JobRecord(
            job_id=f"job_{uuid.uuid4().hex[:12]}",
            document_id=document_id,
            status=JobStatus.REGISTERED.value,
            stage=JobStatus.REGISTERED.value,
            progress=0.0,
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        return job

    @staticmethod
    def update_stage(
        db: Session,
        job_id: str,
        status: JobStatus,
        progress: float | None = None,
        error_message: str | None = None,
    ) -> JobRecord | None:
        job = db.query(JobRecord).filter(JobRecord.job_id == job_id).first()
        if not job:
            return None

        job.status = status.value
        job.stage = status.value
        if progress is not None:
            job.progress = progress
        if error_message:
            job.error_message = error_message
        db.commit()
        db.refresh(job)
        return job

    @staticmethod
    def get_job(db: Session, job_id: str) -> JobRecord | None:
        return db.query(JobRecord).filter(JobRecord.job_id == job_id).first()
