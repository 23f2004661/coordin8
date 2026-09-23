"""Tool implementations conforming to Milestone 9 of ProjectDetails.md.

Exposes Coordin8 RAG capabilities as clean, callable tools for agentic systems
like OpenWorker, either over MCP or in-process.
"""

from pathlib import Path
from typing import Any

from app.core.logging import logger
from app.knowledge_base import KnowledgeBase, KnowledgeBaseManager

_default_manager: KnowledgeBaseManager | None = None


def get_default_kb_manager() -> KnowledgeBaseManager:
    """Obtain or initialize the global KnowledgeBaseManager."""
    global _default_manager
    if _default_manager is None:
        _default_manager = KnowledgeBaseManager()
    return _default_manager


class Coordin8Tools:
    """Tool declarations and live execution for agent harnesses (OpenWorker, Claude, etc)."""

    def __init__(self, manager: KnowledgeBaseManager | None = None) -> None:
        self.manager = manager or get_default_kb_manager()

    def _get_kb(self, kb_id: str = "default") -> KnowledgeBase:
        return self.manager.get_or_create(kb_id)

    def create_knowledge_base(self, kb_id: str) -> dict[str, Any]:
        """Create a new isolated knowledge base / vector database."""
        kb = self.manager.get_or_create(kb_id)
        return {
            "success": True,
            "kb_id": kb.kb_id,
            "storage_dir": str(kb.storage_dir),
            "collection_prefix": kb.collection_prefix,
        }

    def list_knowledge_bases(self) -> dict[str, Any]:
        """List all active or registered knowledge bases."""
        kbs = self.manager.list_kbs()
        return {"knowledge_bases": kbs}

    def ingest_document(
        self,
        file_path: str,
        kb_id: str = "default",
        title: str | None = None,
    ) -> dict[str, Any]:
        """Ingest and index a document into the specified knowledge base."""
        kb = self._get_kb(kb_id)
        return kb.ingest_file(file_path=file_path, title=title)

    def search_knowledge(
        self,
        query: str,
        kb_id: str = "default",
        limit: int = 5,
        document_id: str | None = None,
    ) -> dict[str, Any]:
        """Search the canonical knowledge base using hybrid hierarchical retrieval."""
        kb = self._get_kb(kb_id)
        return kb.search(query=query, limit=limit, document_id=document_id)

    def query_context(
        self,
        query: str,
        kb_id: str = "default",
        limit: int = 5,
    ) -> dict[str, Any]:
        """Retrieve citation-grounded prompt context ready for LLM synthesis."""
        kb = self._get_kb(kb_id)
        return kb.query_context(query=query, limit=limit)

    def find_documents(
        self,
        query: str,
        kb_id: str = "default",
        modalities: list[str] | None = None,
    ) -> dict[str, Any]:
        """Discover candidate documents matching topic or metadata."""
        kb = self._get_kb(kb_id)
        parsed = kb.query_parser.parse(query)
        if modalities:
            parsed.modalities = modalities
        with kb.session() as db:
            candidates = kb.doc_retriever.retrieve_candidates(db, parsed, limit=10)
            return {
                "kb_id": kb_id,
                "query": query,
                "documents": [
                    {
                        "document_id": c.document_id,
                        "title": c.title,
                        "summary": c.summary,
                        "score": round(c.score, 4),
                    }
                    for c in candidates
                ],
            }

    def read_document(self, document_id: str, kb_id: str = "default") -> dict[str, Any]:
        """Retrieve the canonical normalized markdown representation of a document."""
        kb = self._get_kb(kb_id)
        content = kb.read_document(document_id)
        return {
            "kb_id": kb_id,
            "document_id": document_id,
            "content": content or "",
            "found": content is not None,
        }

    def read_section(
        self,
        document_id: str,
        section_id: str,
        kb_id: str = "default",
    ) -> dict[str, Any]:
        """Retrieve detailed blocks and provenance for a specific section."""
        kb = self._get_kb(kb_id)
        with kb.session() as db:
            from app.db.models import ChunkRecord
            chunks = (
                db.query(ChunkRecord)
                .filter(
                    ChunkRecord.document_id == document_id,
                    ChunkRecord.section_id == section_id,
                )
                .all()
            )
            return {
                "kb_id": kb_id,
                "document_id": document_id,
                "section_id": section_id,
                "chunks": [
                    {
                        "chunk_id": c.chunk_id,
                        "content": c.content,
                        "page": c.page_number,
                        "slide": c.slide_number,
                        "sheet": c.sheet_name,
                    }
                    for c in chunks
                ],
            }

    def analyze_spreadsheet(
        self,
        document_id: str,
        sheet_name: str,
        operation: str,
        column: str,
        kb_id: str = "default",
    ) -> dict[str, Any]:
        """Execute a safe mathematical or aggregation operation on tabular data."""
        kb = self._get_kb(kb_id)
        return kb.analyze_spreadsheet(
            document_id=document_id,
            sheet_name=sheet_name,
            operation=operation,
            column=column,
        )
