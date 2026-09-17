"""Index pipeline orchestrator."""

from app.core.logging import logger
from app.domain.document import Document
from app.indexing.embeddings import EmbeddingProvider, get_embedding_provider
from app.indexing.qdrant import QdrantManager
from app.indexing.sparse import SparseVectorProvider


class IndexPipeline:
    """Coordinates dense, sparse, and hierarchical indexing."""

    def __init__(
        self,
        embeddings: EmbeddingProvider | None = None,
        sparse: SparseVectorProvider | None = None,
        qdrant: QdrantManager | None = None,
    ) -> None:
        self.embeddings = embeddings or get_embedding_provider()
        self.sparse = sparse or SparseVectorProvider()
        self.qdrant = qdrant or QdrantManager()

    def index_document(self, document: Document) -> bool:
        """Index document summary, section summaries, chunks, and assets."""
        logger.info("Indexing document: %s", document.document_id)

        # 1. Index document summary if present
        if document.summary:
            summary_vec = self.embeddings.embed_text(document.summary.summary)
            self.qdrant.upsert_points(
                collection_name=f"{self.qdrant.prefix}_document_summaries",
                points=[
                    {
                        "id": abs(hash(document.document_id)) % (2**63 - 1),
                        "vector": summary_vec,
                        "payload": {
                            "document_id": document.document_id,
                            "title": document.metadata.title,
                            "summary": document.summary.summary,
                            "topics": document.summary.main_topics,
                        },
                    }
                ],
            )

        # 2. Index chunks
        chunk_points = []
        for chunk in document.chunks:
            chunk_vec = self.embeddings.embed_text(chunk.content)
            chunk_points.append(
                {
                    "id": abs(hash(chunk.chunk_id)) % (2**63 - 1),
                    "vector": chunk_vec,
                    "payload": chunk.metadata.to_dict(),
                }
            )

        if chunk_points:
            self.qdrant.upsert_points(
                collection_name=f"{self.qdrant.prefix}_chunks",
                points=chunk_points,
            )

        return True
