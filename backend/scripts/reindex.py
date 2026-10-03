"""Approval-gated Q3 vector rebuild using stored text, without PDF extraction."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import sqlite3
import sys

BACKEND_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_ROOT))
if __name__ == "__main__":
    os.chdir(BACKEND_ROOT)

from app.core.config import get_settings
from app.indexing.embeddings import LocalSentenceTransformerEmbeddingProvider
from qdrant_client import QdrantClient, models

PROJECT_ID = "a2025c2f-9fd6-4aa3-80db-53111228503c"
MODEL = "BAAI/bge-small-en-v1.5"
DIMENSION = 384
APPROVED_ORPHAN = "chk_f54adcbbed"


def read_points(client, collection_name):
    points = []
    offset = None
    while True:
        batch, offset = client.scroll(
            collection_name, limit=256, offset=offset, with_payload=True, with_vectors=True
        )
        points.extend(batch)
        if offset is None:
            return points


def build_sources(collections, chunks):
    sources = {}
    omitted = []
    indexed_chunk_ids = set()
    for name, points in collections.items():
        entries = []
        for point in points:
            payload = point.payload or {}
            if name.endswith("_chunks"):
                chunk_id = payload.get("chunk_id")
                if chunk_id == APPROVED_ORPHAN and chunk_id not in chunks:
                    omitted.append(chunk_id)
                    continue
                if chunk_id not in chunks:
                    raise ValueError(f"Unapproved point without catalog text: {chunk_id!r}")
                chunk = chunks[chunk_id]
                if payload.get("document_id") != chunk["document_id"]:
                    raise ValueError(f"Document association mismatch: {chunk_id}")
                indexed_chunk_ids.add(chunk_id)
                text = chunk["content"]
            elif name.endswith("_document_summaries"):
                text = payload.get("summary")
            else:
                raise ValueError(f"Nonempty collection needs an explicit text mapping: {name}")
            if not isinstance(text, str) or not text.strip():
                raise ValueError(f"Point {point.id} has no valid stored text")
            entries.append((point.id, payload, text))
        sources[name] = entries
    if indexed_chunk_ids != set(chunks):
        raise ValueError("Catalog chunks and existing vector payloads do not match")
    return sources, omitted


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-id", required=True, choices=[PROJECT_ID])
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--backup-root", type=Path, default=Path("data/reindex_backups"))
    args = parser.parse_args()
    settings = get_settings()
    prefix = f"kb_{args.project_id}"
    names = [f"{prefix}_{suffix}" for suffix in (
        "chunks", "document_summaries", "section_summaries", "assets"
    )]
    catalog_path = (Path("data/knowledge_bases") / args.project_id / "metadata.db").resolve()
    with sqlite3.connect(catalog_path.as_uri() + "?mode=ro", uri=True) as db:
        db.row_factory = sqlite3.Row
        chunks = {row["chunk_id"]: dict(row) for row in db.execute("SELECT * FROM chunks")}
    catalog_hash = hashlib.sha256(catalog_path.read_bytes()).hexdigest()
    client = QdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key, timeout=60)
    try:
        before = {}
        for collection in client.get_collections().collections:
            info = client.get_collection(collection.name)
            before[collection.name] = {
                "points": client.count(collection.name, exact=True).count,
                "vectors": info.config.params.vectors.model_dump(mode="json")
                if not isinstance(info.config.params.vectors, dict) else info.config.params.vectors,
            }
        originals = {name: read_points(client, name) for name in names}
        sources, omitted = build_sources(originals, chunks)
        plan = {
            "project_id": args.project_id, "model": MODEL, "dimension": DIMENSION,
            "distance": "Cosine", "collections_before": {name: before[name] for name in names},
            "prepared_point_counts": {name: len(entries) for name, entries in sources.items()},
            "catalog_chunks": len(chunks),
            "sap_chunks": sum(chunk["document_id"] == "doc_3ca7a20cb73b" for chunk in chunks.values()),
            "omitted_chunk_ids": omitted,
        }
        print(json.dumps({"plan": plan}), flush=True)
        if not args.execute:
            print("Dry run only: no files exported, no vectors embedded, no collections changed.")
            return
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        backup = args.backup_root.resolve() / f"{args.project_id}_{stamp}"
        backup.mkdir(parents=True, exist_ok=False)
        for name, points in originals.items():
            export = {
                "config": client.get_collection(name).config.model_dump(mode="json"),
                "points": [point.model_dump(mode="json") for point in points],
            }
            (backup / f"{name}.json").write_text(json.dumps(export), encoding="utf-8")
        with sqlite3.connect(catalog_path.as_uri() + "?mode=ro", uri=True) as source_db:
            with sqlite3.connect(backup / "metadata.db") as backup_db:
                source_db.backup(backup_db)
        (backup / "manifest.json").write_text(json.dumps(plan, indent=2), encoding="utf-8")
        print(json.dumps({"backup_directory": str(backup)}), flush=True)
        provider = LocalSentenceTransformerEmbeddingProvider(MODEL, DIMENSION)
        prepared = {}
        for name, entries in sources.items():
            prepared[name] = []
            for start in range(0, len(entries), 32):
                batch = entries[start:start + 32]
                vectors = provider.embed_batch([entry[2] for entry in batch])
                for (point_id, payload, _), vector in zip(batch, vectors, strict=True):
                    if len(vector) != DIMENSION or not all(math.isfinite(value) for value in vector):
                        raise ValueError("Invalid embedding before collection replacement")
                    prepared[name].append(models.PointStruct(id=point_id, payload=payload, vector=vector))
            print(json.dumps({"embedded_collection": name, "points": len(prepared[name])}), flush=True)
        if hashlib.sha256(catalog_path.read_bytes()).hexdigest() != catalog_hash:
            raise RuntimeError("Catalog changed during preparation; nothing replaced")
        for name in names:
            current = read_points(client, name)
            if [point.model_dump(mode="json") for point in current] != [
                point.model_dump(mode="json") for point in originals[name]
            ]:
                raise RuntimeError("Collection changed during preparation; nothing replaced")
        try:
            for name in names:
                client.delete_collection(name)
                client.create_collection(
                    name, vectors_config=models.VectorParams(size=DIMENSION, distance=models.Distance.COSINE)
                )
                config = client.get_collection(name).config.params.vectors
                if config.size != DIMENSION or config.distance != models.Distance.COSINE:
                    raise ValueError("New collection configuration failed validation")
                for start in range(0, len(prepared[name]), 64):
                    client.upsert(name, points=prepared[name][start:start + 64], wait=True)
            verification = {}
            for name in names:
                points = read_points(client, name)
                expected = {point.id: point.payload for point in prepared[name]}
                if {point.id: point.payload for point in points} != expected:
                    raise ValueError(f"Payload/point-count verification failed for {name}")
                if any(len(point.vector) != DIMENSION for point in points):
                    raise ValueError(f"Stored vector dimension verification failed for {name}")
                verification[name] = {"points": len(points), "dimension": DIMENSION, "distance": "Cosine"}
            for name, baseline in before.items():
                if name not in names:
                    info = client.get_collection(name)
                    config = info.config.params.vectors
                    current = {
                        "points": client.count(name, exact=True).count,
                        "vectors": config.model_dump(mode="json") if not isinstance(config, dict) else config,
                    }
                    if current != baseline:
                        raise RuntimeError(f"Unrelated collection changed: {name}")
        except Exception:
            for name in names:
                client.delete_collection(name)
                config = before[name]["vectors"]
                client.create_collection(name, vectors_config=models.VectorParams(**config))
                points = [models.PointStruct(id=point.id, payload=point.payload, vector=point.vector)
                          for point in originals[name]]
                for start in range(0, len(points), 64):
                    client.upsert(name, points=points[start:start + 64], wait=True)
            raise
        result = {
            "verification": verification, "chunks_embedded": len(chunks), "omitted": len(omitted),
            "orphan_omitted": APPROVED_ORPHAN in omitted, "embedding_failures": 0,
            "all_vectors_384": True, "other_collections_unchanged": True,
            "source_catalog_unchanged": hashlib.sha256(catalog_path.read_bytes()).hexdigest() == catalog_hash,
        }
        (backup / "result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(json.dumps(result), flush=True)
    finally:
        client.close()


if __name__ == "__main__":
    main()
