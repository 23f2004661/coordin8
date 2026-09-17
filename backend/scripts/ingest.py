"""CLI script to ingest documents into Coordin8."""

import argparse
import sys
from pathlib import Path

# Ensure backend root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.db.session import SessionLocal, init_db
from app.ingestion.detector import detect_file_type
from app.ingestion.jobs import JobManager
from app.ingestion.pipeline import IngestionPipeline
from app.ingestion.registry import DocumentRegistry


def main():
    parser = argparse.ArgumentParser(description="Ingest a document into Coordin8")
    parser.add_argument("file_path", type=str, help="Path to file to ingest")
    args = parser.parse_args()

    init_db()
    db = SessionLocal()
    path = Path(args.file_path)

    if not path.exists():
        print(f"Error: File '{path}' does not exist.")
        return

    content = path.read_bytes()
    file_type = detect_file_type(path.name, content[:1024])

    registry = DocumentRegistry()
    record, is_new = registry.register_document(db, path.name, content, file_type)
    print(f"Document Registered: ID={record.document_id}, is_new={is_new}")

    job = JobManager.create_job(db, record.document_id)
    pipeline = IngestionPipeline()
    print(f"Running Ingestion Pipeline (Job={job.job_id})...")
    success = pipeline.run_pipeline(db, record.document_id, job.job_id)
    print(f"Result: {'SUCCESS' if success else 'FAILED'}")


if __name__ == "__main__":
    main()
