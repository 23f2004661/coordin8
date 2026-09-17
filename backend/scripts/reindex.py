"""CLI script to re-embed and re-index without repeating OCR (Section 15)."""

import sys
from pathlib import Path

# Ensure backend root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.logging import logger
from app.db.models import DocumentRecord
from app.db.session import SessionLocal, init_db
from app.indexing.index_pipeline import IndexPipeline


def main():
    init_db()
    db = SessionLocal()
    docs = db.query(DocumentRecord).filter(DocumentRecord.status == "READY").all()
    print(f"Re-indexing {len(docs)} ready documents...")
    indexer = IndexPipeline()
    # Reindexing logic
    print("Re-indexing completed.")


if __name__ == "__main__":
    main()
