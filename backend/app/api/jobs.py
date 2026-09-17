"""Job status endpoints conforming to Section 17 of ProjectDetails.md."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.models import JobRecord
from app.db.session import get_db

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/{job_id}")
def get_job_status(job_id: str, db: Session = Depends(get_db)):
    """Check processing job progress and pipeline stage."""
    job = db.query(JobRecord).filter(JobRecord.job_id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return {
        "job_id": job.job_id,
        "document_id": job.document_id,
        "status": job.status,
        "stage": job.stage,
        "progress": job.progress,
        "error_message": job.error_message,
        "processing_duration": job.processing_duration,
        "created_at": job.created_at.isoformat() if job.created_at else None,
        "updated_at": job.updated_at.isoformat() if job.updated_at else None,
    }
