"""Ingestion package for Coordin8."""

from app.ingestion.detector import detect_file_type
from app.ingestion.jobs import JobManager, JobStatus
from app.ingestion.pipeline import IngestionPipeline
from app.ingestion.registry import DocumentRegistry

__all__ = [
    "detect_file_type",
    "JobManager",
    "JobStatus",
    "DocumentRegistry",
    "IngestionPipeline",
]
