"""Document endpoints conforming to Section 17 of ProjectDetails.md."""

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session
from app.db.models import DocumentRecord
from app.db.session import get_db
from app.ingestion.detector import detect_file_type
from app.ingestion.jobs import JobManager
from app.ingestion.pipeline import IngestionPipeline
from app.ingestion.registry import DocumentRegistry
from app.storage.artifacts import ArtifactStorage

router = APIRouter(prefix="/documents", tags=["documents"])
registry = DocumentRegistry()
pipeline = IngestionPipeline()
storage = ArtifactStorage()


@router.post("", status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Upload and register a new file into the knowledge system."""
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    file_type = detect_file_type(file.filename or "unknown", content[:1024])
    record, is_new = registry.register_document(
        db=db,
        filename=file.filename or "unnamed",
        content=content,
        file_type=file_type,
    )

    # Automatically create ingestion job and run processing pipeline
    job = JobManager.create_job(db, record.document_id)
    pipeline.run_pipeline(db, record.document_id, job.job_id)
    db.refresh(record)

    return {
        "document_id": record.document_id,
        "title": record.title,
        "file_type": record.file_type,
        "file_size_bytes": record.file_size_bytes,
        "source_hash": record.source_hash,
        "status": record.status,
        "summary": record.summary,
        "job_id": job.job_id,
        "is_new": is_new,
    }


@router.get("")
def list_documents(db: Session = Depends(get_db)):
    """List registered documents."""
    records = db.query(DocumentRecord).order_by(DocumentRecord.created_at.desc()).all()
    return [
        {
            "document_id": r.document_id,
            "title": r.title,
            "file_type": r.file_type,
            "file_size_bytes": r.file_size_bytes,
            "status": r.status,
            "created_at": r.created_at.isoformat() if r.created_at else None,
            "summary": r.summary,
        }
        for r in records
    ]


@router.get("/{document_id}")
def get_document(document_id: str, db: Session = Depends(get_db)):
    """Retrieve details and processing status for a specific document."""
    record = db.query(DocumentRecord).filter(DocumentRecord.document_id == document_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Document not found")
    normalized_md = storage.get_normalized_markdown(document_id)
    return {
        "document_id": record.document_id,
        "title": record.title,
        "file_type": record.file_type,
        "file_size_bytes": record.file_size_bytes,
        "source_hash": record.source_hash,
        "status": record.status,
        "summary": record.summary,
        "normalized_markdown": normalized_md,
        "created_at": record.created_at.isoformat() if record.created_at else None,
    }


@router.get("/{document_id}/summary")
def get_document_summary(document_id: str, db: Session = Depends(get_db)):
    """Retrieve the document-level summary."""
    record = db.query(DocumentRecord).filter(DocumentRecord.document_id == document_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Document not found")
    return {
        "document_id": record.document_id,
        "title": record.title,
        "summary": record.summary,
    }


@router.post("/{document_id}/process")
def trigger_processing(document_id: str, db: Session = Depends(get_db)):
    """Trigger the ingestion and indexing pipeline for a document."""
    record = db.query(DocumentRecord).filter(DocumentRecord.document_id == document_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Document not found")

    job = JobManager.create_job(db, document_id)
    success = pipeline.run_pipeline(db, document_id, job.job_id)
    return {"job_id": job.job_id, "status": "COMPLETED" if success else "FAILED"}


@router.delete("/{document_id}")
def delete_document(document_id: str, db: Session = Depends(get_db)):
    """Delete a document and trigger deletion propagation."""
    record = db.query(DocumentRecord).filter(DocumentRecord.document_id == document_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Document not found")
    db.delete(record)
    db.commit()
    return {"status": "deleted", "document_id": document_id}
