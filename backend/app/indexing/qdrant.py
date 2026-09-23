"""Qdrant vector and sparse collection manager for Coordin8.

Manages logical indexes conforming to Section 10 of ProjectDetails.md:
- DocumentSummaryIndex
- SectionSummaryIndex
- ChunkIndex
- AssetIndex
"""

from typing import Any
from app.core.config import get_settings
from app.core.logging import logger


class QdrantManager:
    """Manages Qdrant collections and points upsert."""

    def __init__(
        self,
        url: str | None = None,
        api_key: str | None = None,
        collection_prefix: str | None = None,
    ) -> None:
        settings = get_settings()
        self.url = url or settings.qdrant_url
        self.api_key = api_key or settings.qdrant_api_key
        self.prefix = collection_prefix or settings.qdrant_collection_prefix
        self.client = None
        self._init_client()

    def _init_client(self) -> None:
        try:
            from qdrant_client import QdrantClient
            self.client = QdrantClient(url=self.url, api_key=self.api_key, timeout=5.0)
        except Exception as exc:
            logger.warning("Qdrant client unavailable or not running: %s", exc)
            self.client = None

    def ensure_collections(self) -> None:
        """Create required collections if not already present."""
        if not self.client:
            return
        collections = [
            f"{self.prefix}_document_summaries",
            f"{self.prefix}_section_summaries",
            f"{self.prefix}_chunks",
            f"{self.prefix}_assets",
        ]
        try:
            existing = [c.name for c in self.client.get_collections().collections]
            for col in collections:
                if col not in existing:
                    # Create standard dense vector collection
                    from qdrant_client.http import models as rest
                    self.client.create_collection(
                        collection_name=col,
                        vectors_config=rest.VectorParams(
                            size=1024,
                            distance=rest.Distance.COSINE,
                        ),
                    )
                    logger.info("Created Qdrant collection: %s", col)
        except Exception as exc:
            logger.warning("Failed to initialize Qdrant collections: %s", exc)

    def upsert_points(self, collection_name: str, points: list[dict[str, Any]]) -> bool:
        """Upsert points into specified collection."""
        if not self.client:
            logger.info("Mock Qdrant upsert: %d points into %s", len(points), collection_name)
            return True
        try:
            from qdrant_client.http import models as rest
            qpoints = []
            for p in points:
                qpoints.append(
                    rest.PointStruct(
                        id=p["id"],
                        vector=p["vector"],
                        payload=p["payload"],
                    )
                )
            self.client.upsert(collection_name=collection_name, points=qpoints)
            return True
        except Exception as exc:
            logger.error("Failed to upsert points into %s: %s", collection_name, exc)
            return False

    def search_points(
        self, collection_name: str, query_vector: list[float], limit: int = 10
    ) -> list[dict[str, Any]]:
        """Search points by dense vector similarity."""
        if not self.client:
            return []
        try:
            if hasattr(self.client, "query_points"):
                response = self.client.query_points(
                    collection_name=collection_name,
                    query=query_vector,
                    limit=limit,
                )
                results = response.points
            else:
                results = self.client.search(
                    collection_name=collection_name,
                    query_vector=query_vector,
                    limit=limit,
                )
            return [
                {
                    "id": hit.id,
                    "score": hit.score,
                    "payload": hit.payload or {},
                }
                for hit in results
            ]
        except Exception as exc:
            logger.warning("Qdrant search in %s failed: %s", collection_name, exc)
            return []
