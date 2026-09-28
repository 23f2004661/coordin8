"""Coordin8 KnowledgeBase Custom Class and Multi-KB Manager for Agent Integration.

Provides an instantiable, autonomous knowledge base class for external agent harnesses
like OpenWorker, allowing agents to dynamically create, ingest into, and query
isolated vector databases and knowledge repositories.
"""

from contextlib import contextmanager
from dataclasses import asdict
from pathlib import Path
import shutil
from typing import Any, Generator
import uuid

from sqlalchemy.orm import Session

from app.core.logging import logger
from app.db.models import ChunkRecord, DocumentRecord, JobRecord
from app.db.session import create_db_engine, create_session_factory, init_db
from app.domain.document import DocumentType
from app.indexing.embeddings import EmbeddingProvider, get_embedding_provider
from app.indexing.index_pipeline import IndexPipeline
from app.indexing.qdrant import QdrantManager
from app.indexing.sparse import SparseVectorProvider
from app.ingestion.detector import detect_file_type
from app.ingestion.jobs import JobManager
from app.ingestion.pipeline import IngestionPipeline
from app.ingestion.registry import DocumentRegistry
from app.retrieval.chunk_retriever import ChunkRetriever
from app.retrieval.context import ContextAssembler
from app.retrieval.document_retriever import DocumentRetriever
from app.retrieval.hybrid import HybridFusion
from app.retrieval.query_parser import QueryParser
from app.retrieval.reranker import get_reranker
from app.retrieval.section_retriever import SectionRetriever
from app.spreadsheets.executor import SpreadsheetExecutor
from app.spreadsheets.operations import OperationType, SpreadsheetOperation
from app.storage.artifacts import ArtifactStorage


class KnowledgeBase:
    """An autonomous, isolated Knowledge Base instance.

    Encapsulates its own vector collection namespace, relational metadata catalog,
    artifact storage directory, and hierarchical retrieval engine.
    """

    def __init__(
        self,
        kb_id: str,
        storage_dir: str | Path | None = None,
        db_url: str | None = None,
        qdrant_url: str | None = None,
        collection_prefix: str | None = None,
        embedding_provider: EmbeddingProvider | None = None,
    ) -> None:
        self.kb_id = kb_id

        # 1. Scoped Storage Directory
        if storage_dir:
            self.storage_dir = Path(storage_dir)
        else:
            self.storage_dir = Path("./data/knowledge_bases") / kb_id
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        # 2. Scoped Database
        if db_url:
            self.db_url = db_url
        else:
            db_path = (self.storage_dir / "metadata.db").resolve()
            self.db_url = f"sqlite:///{db_path}"

        self.db_engine = create_db_engine(self.db_url)
        self.session_factory = create_session_factory(self.db_engine)
        init_db(self.db_engine)

        # 3. Scoped Artifact Storage
        self.storage = ArtifactStorage(root_dir=self.storage_dir / "artifacts")

        # 4. Scoped Vector Store
        self.collection_prefix = collection_prefix or f"kb_{kb_id}"
        self.qdrant = QdrantManager(url=qdrant_url, collection_prefix=self.collection_prefix)
        self.qdrant.ensure_collections()

        # 5. Core Pipelines
        self.embeddings = embedding_provider or get_embedding_provider()
        self.sparse = SparseVectorProvider()
        self.index_pipeline = IndexPipeline(
            embeddings=self.embeddings,
            sparse=self.sparse,
            qdrant=self.qdrant,
        )
        self.ingestion_pipeline = IngestionPipeline(
            storage=self.storage,
            indexer=self.index_pipeline,
        )
        self.registry = DocumentRegistry(storage=self.storage)

        # 6. Retrieval & Context Components
        self.query_parser = QueryParser()
        self.doc_retriever = DocumentRetriever(embeddings=self.embeddings)
        self.sec_retriever = SectionRetriever()
        self.chk_retriever = ChunkRetriever(qdrant=self.qdrant, embeddings=self.embeddings)
        self.fusion = HybridFusion()
        self.reranker = get_reranker()
        self.context_assembler = ContextAssembler()
        self.spreadsheet_executor = SpreadsheetExecutor()

    @contextmanager
    def session(self) -> Generator[Session, None, None]:
        """Context manager providing an active database session for this KB."""
        db: Session = self.session_factory()
        try:
            yield db
        finally:
            db.close()

    def ingest_bytes(
        self,
        content: bytes,
        filename: str,
        title: str | None = None,
    ) -> dict[str, Any]:
        """Ingest raw byte content into the knowledge base."""
        if not content:
            raise ValueError("Document content cannot be empty.")

        file_type = detect_file_type(filename, content[:1024])

        with self.session() as db:
            record, is_new = self.registry.register_document(
                db=db,
                filename=filename,
                content=content,
                file_type=file_type,
            )
            if title:
                record.title = title
                db.commit()

            job = JobManager.create_job(db, record.document_id)
            success = self.ingestion_pipeline.run_pipeline(db, record.document_id, job.job_id)

            db.refresh(record)
            db.refresh(job)

            return {
                "kb_id": self.kb_id,
                "document_id": record.document_id,
                "job_id": job.job_id,
                "title": record.title,
                "file_type": record.file_type,
                "status": record.status,
                "summary": record.summary,
                "is_new": is_new,
                "success": success,
            }

    def ingest_file(
        self,
        file_path: str | Path,
        title: str | None = None,
    ) -> dict[str, Any]:
        """Ingest a file from disk into the knowledge base."""
        path = Path(file_path)
        if not path.is_file():
            raise FileNotFoundError(f"File not found: {path}")

        content = path.read_bytes()
        filename = path.name
        doc_title = title or path.stem
        return self.ingest_bytes(content=content, filename=filename, title=doc_title)

    def search(
        self,
        query: str,
        limit: int = 5,
        document_id: str | None = None,
    ) -> dict[str, Any]:
        """Perform hierarchical hybrid retrieval across this knowledge base."""
        parsed = self.query_parser.parse(query)

        with self.session() as db:
            if document_id:
                candidate_docs = [
                    d for d in self.doc_retriever.retrieve_candidates(db, parsed, limit=limit)
                    if d.document_id == document_id
                ]
            else:
                candidate_docs = self.doc_retriever.retrieve_candidates(db, parsed, limit=limit)

            candidate_secs = self.sec_retriever.retrieve_sections(
                candidate_docs, parsed, limit=limit * 2
            )
            chunks = self.chk_retriever.retrieve_chunks(
                db, candidate_secs, parsed, limit=limit * 3
            )

            # Filter by document_id if requested
            if document_id:
                chunks = [c for c in chunks if c.document_id == document_id]

            fused = self.fusion.fuse_ranks(chunks, [], top_k=limit)
            final = self.reranker.rerank(query, fused, top_n=limit)

            results = []
            for rank, c in enumerate(final, start=1):
                doc_record = db.query(DocumentRecord).filter(DocumentRecord.document_id == c.document_id).first()
                doc_title = doc_record.title if doc_record else c.document_id
                file_type = doc_record.file_type if doc_record else "unknown"

                prov_loc = c.provenance or "Main Content"
                prov_str = f"{doc_title} — {prov_loc}"

                results.append({
                    "chunk_id": c.chunk_id,
                    "document_id": c.document_id,
                    "document_title": doc_title,
                    "file_type": file_type,
                    "section_id": c.section_id or f"sec_{c.document_id}",
                    "lineage": f"{doc_title} → {c.section_id or 'section'} → {c.chunk_id}",
                    "content": c.content,
                    "page": c.page,
                    "slide": c.slide,
                    "sheet": c.sheet,
                    "score": round(c.score, 4),
                    "dense_score": round(c.dense_score, 4),
                    "sparse_score": round(c.sparse_score, 4),
                    "retriever_type": c.retriever_type,
                    "fusion_rank": c.fusion_rank or rank,
                    "reranker_score": round(c.reranker_score or c.score, 4),
                    "provenance": prov_str,
                })

            return {
                "kb_id": self.kb_id,
                "query": query,
                "intent": parsed.intent,
                "modalities": parsed.modalities,
                "candidate_documents": len(candidate_docs),
                "total_results": len(results),
                "results": results,
            }

    def query_context(self, query: str, limit: int = 5) -> dict[str, Any]:
        """Retrieve and assemble citation-grounded prompt context ready for LLMs."""
        parsed = self.query_parser.parse(query)

        with self.session() as db:
            candidate_docs = self.doc_retriever.retrieve_candidates(db, parsed, limit=limit)
            candidate_secs = self.sec_retriever.retrieve_sections(candidate_docs, parsed, limit=limit * 2)
            chunks = self.chk_retriever.retrieve_chunks(db, candidate_secs, parsed, limit=limit * 2)

            fused = self.fusion.fuse_ranks(chunks, [], top_k=limit)
            final = self.reranker.rerank(query, fused, top_n=limit)
            assembled = self.context_assembler.assemble(final)

            return {
                "kb_id": self.kb_id,
                "query": query,
                "formatted_context": assembled.formatted_prompt_context,
                "evidence_units": [asdict(u) for u in assembled.evidence_units],
                "estimated_tokens": assembled.total_estimated_tokens,
            }

    def read_document(self, document_id: str) -> str | None:
        """Fetch canonical normalized markdown for a document."""
        return self.storage.get_normalized_markdown(document_id)

    def get_document(self, document_id: str) -> dict[str, Any] | None:
        """Fetch metadata and summary for a single document."""
        with self.session() as db:
            doc = db.query(DocumentRecord).filter(DocumentRecord.document_id == document_id).first()
            if not doc:
                return None
            return {
                "document_id": doc.document_id,
                "title": doc.title,
                "file_type": doc.file_type,
                "file_size_bytes": doc.file_size_bytes,
                "source_hash": doc.source_hash,
                "status": doc.status,
                "summary": doc.summary,
                "created_at": doc.created_at.isoformat() if doc.created_at else None,
                "updated_at": doc.updated_at.isoformat() if doc.updated_at else None,
            }

    def list_documents(self) -> list[dict[str, Any]]:
        """List all registered documents in this knowledge base."""
        with self.session() as db:
            docs = db.query(DocumentRecord).order_by(DocumentRecord.created_at.desc()).all()
            return [
                {
                    "document_id": d.document_id,
                    "title": d.title,
                    "file_type": d.file_type,
                    "file_size_bytes": d.file_size_bytes,
                    "status": d.status,
                    "summary": d.summary,
                    "created_at": d.created_at.isoformat() if d.created_at else None,
                }
                for d in docs
            ]

    def delete_document(self, document_id: str) -> bool:
        """Delete a document, its chunks, its artifacts, and its vector points."""
        with self.session() as db:
            doc = db.query(DocumentRecord).filter(DocumentRecord.document_id == document_id).first()
            if not doc:
                return False

            # Delete chunks
            db.query(ChunkRecord).filter(ChunkRecord.document_id == document_id).delete()
            # Delete jobs
            db.query(JobRecord).filter(JobRecord.document_id == document_id).delete()
            # Delete doc record
            db.delete(doc)
            db.commit()

        # Delete filesystem artifacts
        self.storage.delete_document_artifacts(document_id)
        return True

    def analyze_spreadsheet(
        self,
        document_id: str,
        sheet_name: str,
        operation: str,
        column: str,
        filter_column: str | None = None,
        filter_value: str | None = None,
    ) -> dict[str, Any]:
        """Perform a sandboxed numerical operation on a spreadsheet."""
        try:
            op_enum = OperationType(operation.lower())
        except ValueError:
            op_enum = OperationType.SUM

        op = SpreadsheetOperation(
            workbook_id=document_id,
            sheet_name=sheet_name,
            operation=op_enum,
            target_column=column,
            filter_column=filter_column,
            filter_value=filter_value,
        )
        result = self.spreadsheet_executor.execute(op)
        return asdict(result)

    def as_tools(self) -> list[dict[str, Any]]:
        """Export standardized tool declarations bound to this KnowledgeBase instance."""
        return [
            {
                "name": "search_knowledge",
                "description": f"Search knowledge base '{self.kb_id}' using hierarchical hybrid retrieval.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "The search question or topic"},
                        "limit": {"type": "integer", "description": "Max results to return", "default": 5},
                        "document_id": {"type": "string", "description": "Optional specific document filter"},
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "query_context",
                "description": f"Retrieve citation-grounded prompt context from '{self.kb_id}' for answer synthesis.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "The question to retrieve evidence for"},
                        "limit": {"type": "integer", "description": "Max evidence blocks", "default": 5},
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "read_document",
                "description": f"Retrieve full normalized markdown text for a document in '{self.kb_id}'.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "document_id": {"type": "string", "description": "The document identifier"},
                    },
                    "required": ["document_id"],
                },
            },
            {
                "name": "list_documents",
                "description": f"List all documents registered in knowledge base '{self.kb_id}'.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                },
            },
            {
                "name": "ingest_file",
                "description": f"Ingest and index a local file into knowledge base '{self.kb_id}'.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_path": {"type": "string", "description": "Absolute or relative path to file"},
                        "title": {"type": "string", "description": "Optional title for document"},
                    },
                    "required": ["file_path"],
                },
            },
            {
                "name": "analyze_spreadsheet",
                "description": f"Perform a safe numerical calculation on a spreadsheet in '{self.kb_id}'.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "document_id": {"type": "string"},
                        "sheet_name": {"type": "string"},
                        "operation": {"type": "string", "enum": ["sum", "average", "count", "min", "max", "filter"]},
                        "column": {"type": "string"},
                    },
                    "required": ["document_id", "sheet_name", "operation", "column"],
                },
            },
        ]

    def execute_tool(self, tool_name: str, arguments: dict[str, Any]) -> Any:
        """Execute a tool call against this KnowledgeBase instance."""
        if tool_name == "search_knowledge":
            return self.search(
                query=arguments["query"],
                limit=arguments.get("limit", 5),
                document_id=arguments.get("document_id"),
            )
        elif tool_name == "query_context":
            return self.query_context(
                query=arguments["query"],
                limit=arguments.get("limit", 5),
            )
        elif tool_name == "read_document":
            content = self.read_document(arguments["document_id"])
            return {"document_id": arguments["document_id"], "content": content or ""}
        elif tool_name == "list_documents":
            return {"kb_id": self.kb_id, "documents": self.list_documents()}
        elif tool_name == "ingest_file":
            return self.ingest_file(
                file_path=arguments["file_path"],
                title=arguments.get("title"),
            )
        elif tool_name == "analyze_spreadsheet":
            return self.analyze_spreadsheet(
                document_id=arguments["document_id"],
                sheet_name=arguments["sheet_name"],
                operation=arguments["operation"],
                column=arguments["column"],
            )
        else:
            raise ValueError(f"Unknown tool name: '{tool_name}' for KnowledgeBase '{self.kb_id}'")

    def close(self) -> None:
        """Dispose database engine connections."""
        try:
            self.db_engine.dispose()
        except Exception as exc:
            logger.warning("Error closing db engine for %s: %s", self.kb_id, exc)


class KnowledgeBaseManager:
    """Manages creation, lifecycle, and discovery of multiple KnowledgeBase instances."""

    def __init__(self, base_storage_dir: str | Path | None = None) -> None:
        self.base_dir = Path(base_storage_dir or "./data/knowledge_bases")
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self._instances: dict[str, KnowledgeBase] = {}

    def get_or_create(self, kb_id: str, **kwargs: Any) -> KnowledgeBase:
        """Retrieve existing KnowledgeBase or create a new one."""
        if kb_id in self._instances:
            return self._instances[kb_id]

        storage_dir = kwargs.pop("storage_dir", self.base_dir / kb_id)
        kb = KnowledgeBase(kb_id=kb_id, storage_dir=storage_dir, **kwargs)
        self._instances[kb_id] = kb
        return kb

    def get(self, kb_id: str) -> KnowledgeBase | None:
        """Get an existing in-memory instance."""
        return self._instances.get(kb_id)

    def list_kbs(self) -> list[str]:
        """List all active or on-disk knowledge bases."""
        found = set(self._instances.keys())
        if self.base_dir.exists():
            for child in self.base_dir.iterdir():
                if child.is_dir():
                    found.add(child.name)
        return sorted(list(found))

    def close_all(self) -> None:
        """Dispose all open KnowledgeBase database engines."""
        for kb in list(self._instances.values()):
            kb.close()
        self._instances.clear()

    def delete_kb(self, kb_id: str) -> bool:
        """Remove a knowledge base and all its on-disk files."""
        if kb_id in self._instances:
            self._instances[kb_id].close()
            del self._instances[kb_id]

        kb_path = self.base_dir / kb_id
        if kb_path.exists():
            shutil.rmtree(kb_path, ignore_errors=True)
            return True
        return False
