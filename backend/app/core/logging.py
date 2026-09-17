"""Structured logging and observability for Coordin8.

Implements structured JSON and standard logging conforming to Section 22
of ProjectDetails.md for both ingestion and retrieval tracing.
"""

import json
import logging
import sys
import time
from typing import Any


def setup_logger(name: str = "coordin8", level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(level)
    return logger


logger = setup_logger("coordin8")


def log_ingestion_event(
    document_id: str,
    job_id: str,
    file_type: str,
    status: str,
    source_hash: str,
    file_size: int = 0,
    preprocessor: str | None = None,
    preprocessor_version: str | None = None,
    ocr_used: bool = False,
    ocr_model_version: str | None = None,
    summary_model_version: str | None = None,
    embedding_model_version: str | None = None,
    processing_duration: float = 0.0,
    error: str | None = None,
    extra: dict[str, Any] | None = None,
) -> None:
    """Log an ingestion event conforming to Section 22 of ProjectDetails.md."""
    payload = {
        "event_type": "ingestion",
        "document_id": document_id,
        "job_id": job_id,
        "file_type": file_type,
        "file_size": file_size,
        "source_hash": source_hash,
        "preprocessor": preprocessor,
        "preprocessor_version": preprocessor_version,
        "ocr_used": ocr_used,
        "ocr_model_version": ocr_model_version,
        "summary_model_version": summary_model_version,
        "embedding_model_version": embedding_model_version,
        "processing_duration": processing_duration,
        "status": status,
        "error": error,
        **(extra or {}),
    }
    logger.info("INGESTION_EVENT: %s", json.dumps(payload))


def log_retrieval_event(
    query: str,
    candidate_document_count: int,
    candidate_chunk_count: int,
    dense_results: int,
    sparse_results: int,
    fusion_method: str,
    reranked_results: int,
    final_context_ids: list[str],
    latency_ms: float,
    query_type: str = "hybrid",
    filters: dict[str, Any] | None = None,
    model_used: str | None = None,
    extra: dict[str, Any] | None = None,
) -> None:
    """Log a retrieval event conforming to Section 22 of ProjectDetails.md."""
    payload = {
        "event_type": "retrieval",
        "query": query,
        "query_type": query_type,
        "filters": filters or {},
        "candidate_document_count": candidate_document_count,
        "candidate_chunk_count": candidate_chunk_count,
        "dense_results": dense_results,
        "sparse_results": sparse_results,
        "fusion_method": fusion_method,
        "reranked_results": reranked_results,
        "final_context_ids": final_context_ids,
        "latency_ms": latency_ms,
        "model_used": model_used,
        **(extra or {}),
    }
    logger.info("RETRIEVAL_EVENT: %s", json.dumps(payload))
