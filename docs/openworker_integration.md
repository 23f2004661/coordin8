# OpenWorker Integration Guide & KnowledgeBase API Reference

Coordin8 provides a multimodal, hierarchical Retrieval-Augmented Generation (RAG) engine designed to serve as a high-performance knowledge backend for external agent harnesses like **OpenWorker**.

This guide details the two integration patterns:
1. **In-Process Python SDK**: OpenWorker directly instantiates `KnowledgeBase` objects like a custom class, dynamically creating isolated vector databases and knowledge stores per agent, session, or project.
2. **Out-of-Process MCP Server**: OpenWorker communicates with Coordin8 via the standardized **Model Context Protocol (MCP)** over `stdio` or HTTP/SSE, keeping the agent harness lightweight and language-agnostic.

---

## 1. High-Level Architecture

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                             OpenWorker Agent                                │
│                                                                             │
│   ┌───────────────────────────┐         ┌──────────────────────────────┐    │
│   │   ReAct / Agent Harness   │         │     Tool Call Dispatcher     │    │
│   └─────────────┬─────────────┘         └──────────────┬───────────────┘    │
└─────────────────┼──────────────────────────────────────┼────────────────────┘
                  │                                      │
                  ▼                                      ▼
     [Pattern A: In-Process SDK]             [Pattern B: Out-of-Process MCP]
     from app import KnowledgeBase           python -m app.mcp.server (stdio)
                  │                                      │
                  └───────────────────┬──────────────────┘
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                       Coordin8 Knowledge Engine                             │
│                                                                             │
│  KnowledgeBase("research_agent_01")      KnowledgeBase("finance_agent_02")  │
│  ├── Qdrant prefix: kb_research_*        ├── Qdrant prefix: kb_finance_*    │
│  ├── SQLite: metadata.db (scoped)        ├── SQLite: metadata.db (scoped)   │
│  ├── Storage: ./artifacts/ (scoped)      ├── Storage: ./artifacts/ (scoped) │
│  ├── Hierarchical Ingestion Pipeline     ├── Hierarchical Ingestion Pipeline│
│  └── Hybrid Hierarchical Retriever       └── Hybrid Hierarchical Retriever  │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Key Architectural Guarantees
- **Strict Multi-Tenancy**: Every `KnowledgeBase` instance maintains its own vector collection namespace, relational SQLite database, and raw/derived artifact folders. Searches in one knowledge base never leak data into another.
- **Hierarchical Provenance**: Chunks maintain traceable lineage back to parent sections, document summaries, page numbers, slides, and spreadsheet sheets (`Document → Section → Chunk`).
- **Separation of Evidence and Discovery**: Summaries are used for coarse discovery; raw canonical chunks are used as prompt evidence.

---

## 2. Integration Pattern A: In-Process Python SDK

### 2.1 Importing Core Classes

```python
from app import KnowledgeBase, KnowledgeBaseManager
```

### 2.2 Instantiating a `KnowledgeBase`

External agents can instantiate `KnowledgeBase` like a standard Python class:

```python
from pathlib import Path
from app import KnowledgeBase

kb = KnowledgeBase(
    kb_id="project_alpha",                         # Unique namespace identifier
    storage_dir=Path("./data/agent_kbs/alpha"),    # Local folder for DB and artifacts
    qdrant_url=None,                               # Optional custom Qdrant URL (defaults to env)
    collection_prefix=None,                        # Defaults to "kb_{kb_id}"
    db_url=None,                                   # Defaults to sqlite:///{storage_dir}/metadata.db
)
```

#### Constructor Parameters

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `kb_id` | `str` | *Required* | Unique identifier used for namespacing and collection prefixes. |
| `storage_dir` | `str \| Path \| None` | `./data/knowledge_bases/{kb_id}` | Directory where SQLite metadata and file artifacts reside. |
| `db_url` | `str \| None` | `sqlite:///{storage_dir}/metadata.db` | SQLAlchemy database URL. Pass `sqlite:///:memory:` for ephemeral memory. |
| `qdrant_url` | `str \| None` | Read from `.env` (`QDRANT_URL`) | URL to Qdrant cluster. Falls back to mock/local if unavailable. |
| `collection_prefix` | `str \| None` | `kb_{kb_id}` | Namespace prefix applied to all Qdrant vector collections. |
| `embedding_provider`| `EmbeddingProvider \| None` | Default BGE-M3 provider | Custom embedding adapter if overriding default models. |

---

### 2.3 Ingesting Documents

Coordin8 automatically detects document types and runs them through modality preprocessors, canonical JSON normalization, markdown conversion, summary generation, hierarchical chunking, and dense/sparse indexing.

#### Ingesting from File Path:
```python
result = kb.ingest_file(
    file_path="./documents/q3_earnings.pdf",
    title="Q3 2026 Financial Results",
)

print(result)
# Output:
# {
#   "kb_id": "project_alpha",
#   "document_id": "doc_a1b2c3d4e5f6",
#   "job_id": "job_9876543210ab",
#   "title": "Q3 2026 Financial Results",
#   "file_type": "pdf",
#   "status": "READY",
#   "summary": "Financial results for Q3 2026 showing 18% YoY growth...",
#   "is_new": True,
#   "success": True
# }
```

#### Ingesting from In-Memory Bytes:
```python
raw_bytes = b"# System SLA\nProduction API uptime must meet 99.99% availability."

result = kb.ingest_bytes(
    content=raw_bytes,
    filename="sla_policy.md",
    title="Production SLA Policy",
)
```

#### Supported File Types
- **PDF** (`.pdf`) — Layout-aware extraction, table bounding, OCR fallback.
- **Word** (`.docx`, `.doc`) — Heading hierarchies, table parsing.
- **PowerPoint** (`.pptx`, `.ppt`) — Slide text, speaker notes, embedded images.
- **Excel** (`.xlsx`, `.xls`, `.csv`) — Multi-sheet structural ingestion and safe math.
- **Images** (`.png`, `.jpg`, `.jpeg`, `.webp`, `.tiff`) — Multimodal OCR processing.
- **Transcripts** (`.vtt`, `.srt`, `.txt`) — Turn-by-turn speaker segmentation.
- **Markdown / Text** (`.md`, `.txt`) — Markdown heading preservation.

---

### 2.4 Hierarchical Search & Retrieval

#### Full Hierarchical Hybrid Search (`kb.search`):
Searches across document summaries, candidate sections, and granular chunks using hybrid dense + sparse BM25 fusion and cross-encoder reranking.

```python
search_response = kb.search(
    query="What were the reasons for moving the migration to Q4?",
    limit=5,
    document_id=None,  # Optional filter by specific document_id
)

for item in search_response["results"]:
    print(f"[{item['fusion_rank']}] {item['document_title']} ({item['provenance']})")
    print(f"    Lineage: {item['lineage']}")
    print(f"    Score: {item['score']} (Dense: {item['dense_score']}, Sparse: {item['sparse_score']})")
    print(f"    Content: {item['content'][:120]}...\n")
```

#### Response Structure:
```json
{
  "kb_id": "project_alpha",
  "query": "What were the reasons for moving the migration to Q4?",
  "intent": "fact_lookup",
  "modalities": ["pdf", "pptx"],
  "candidate_documents": 2,
  "total_results": 3,
  "results": [
    {
      "chunk_id": "chk_12345678",
      "document_id": "doc_abcdef12",
      "document_title": "Architecture Review",
      "file_type": "pdf",
      "section_id": "sec_02_migration",
      "lineage": "Architecture Review → sec_02_migration → chk_12345678",
      "content": "The API gateway migration was postponed to Q4 due to Kubernetes v1.30 dependencies...",
      "page": 4,
      "slide": null,
      "sheet": null,
      "score": 0.942,
      "dense_score": 0.885,
      "sparse_score": 0.720,
      "retriever_type": "Dense (Qdrant BGE-M3)",
      "fusion_rank": 1,
      "reranker_score": 0.942,
      "provenance": "Architecture Review — Page 4"
    }
  ]
}
```

---

### 2.5 LLM Prompt Context Assembly (`kb.query_context`)

Retrieves the top evidence blocks, sanitizes untrusted input, and formats prompt-ready context with grounded citations conforming to Section 19 & 20 of `ProjectDetails.md`.

```python
ctx = kb.query_context(query="Kubernetes version requirement for gateway", limit=3)

# Pass this directly into your OpenWorker LLM system prompt:
prompt = f"""Use the following evidence to answer the user request:

{ctx['formatted_context']}

Question: What version of Kubernetes is required?
"""
```

**`ctx['formatted_context']` format:**
```text
--- EVIDENCE ITEM [1] ---
Source: Doc doc_abcdef12 (Page 4, Section sec_02_migration)
Content:
The API gateway migration was postponed to Q4 due to Kubernetes v1.30 dependencies.

--- EVIDENCE ITEM [2] ---
Source: Doc doc_789abcde (General)
Content:
Upstream ingress controllers require cluster compatibility >= 1.30.
```

---

### 2.6 Document & Artifact Management

```python
# Read canonical normalized markdown of any ingested document
markdown_text = kb.read_document(document_id="doc_abcdef12")

# Get metadata and summary
metadata = kb.get_document(document_id="doc_abcdef12")

# List all documents in this knowledge base
all_docs = kb.list_documents()

# Delete document, chunks, and disk artifacts
kb.delete_document(document_id="doc_abcdef12")

# Clean up resources (closes SQLite engine locks on Windows)
kb.close()
```

---

### 2.7 Safe Spreadsheet Calculations (`kb.analyze_spreadsheet`)

Executes deterministic aggregations over tabular data without LLM hallucination:

```python
calc = kb.analyze_spreadsheet(
    document_id="doc_financials",
    sheet_name="Expenses",
    operation="sum",          # "sum", "average", "count", "min", "max"
    column="TotalCost",
)
print(calc["value"], calc["provenance_citation"])
```

---

### 2.8 Native OpenWorker Tool Calling Integration

The `KnowledgeBase` instance provides built-in tool binding for LLM tool loops:

```python
# 1. Export standard function calling schemas (OpenAI / OpenWorker format)
tools = kb.as_tools()

# 2. When OpenWorker's agent model emits a tool call:
# {"name": "search_knowledge", "arguments": {"query": "latency budget", "limit": 3}}
tool_name = "search_knowledge"
arguments = {"query": "latency budget", "limit": 3}

# 3. Execute directly on the instance:
tool_output = kb.execute_tool(tool_name, arguments)
```

#### Available Built-in Tools:
- `search_knowledge`: Hierarchical hybrid retrieval across the knowledge base.
- `query_context`: Formatted prompt context with citations ready for LLM generation.
- `read_document`: Retrieve full normalized markdown for a document.
- `list_documents`: List all registered documents.
- `ingest_file`: Ingest and index a local file.
- `analyze_spreadsheet`: Perform safe mathematical calculations on tabular data.

---

### 2.9 Multi-Tenant Management via `KnowledgeBaseManager`

When OpenWorker runs multiple concurrent agents or needs dynamically provisioned workspaces:

```python
from app import KnowledgeBaseManager

manager = KnowledgeBaseManager(base_storage_dir="./data/knowledge_bases")

# Get or create isolated knowledge bases for different agents
agent1_kb = manager.get_or_create("agent_researcher_01")
agent2_kb = manager.get_or_create("agent_finance_02")

# List all active/on-disk knowledge bases
all_kbs = manager.list_kbs()  # ['agent_finance_02', 'agent_researcher_01']

# Delete a knowledge base and all its on-disk data
manager.delete_kb("agent_researcher_01")

# Clean shutdown
manager.close_all()
```

---

## 3. Integration Pattern B: Out-of-Process MCP Server

If OpenWorker runs in a separate process, container, or non-Python environment, use the **Model Context Protocol (MCP)** server.

### 3.1 Starting the MCP Server

```bash
# From coordin8/backend/ with virtual environment activated:
python -m app.mcp.server
```

The server listens on `stdin` and writes JSON-RPC 2.0 messages to `stdout`.

### 3.2 Configuring OpenWorker MCP Client

In your OpenWorker agent configuration (or `mcp_config.json`):

```json
{
  "mcpServers": {
    "coordin8": {
      "command": "python",
      "args": ["-m", "app.mcp.server"],
      "cwd": "C:/Users/ssrin/Desktop/1. Projects/Coordin8/coordin8/backend",
      "env": {
        "PYTHONPATH": "."
      }
    }
  }
}
```

### 3.3 Available MCP Tools

| MCP Tool Name | Description | Required Arguments |
| :--- | :--- | :--- |
| `create_knowledge_base` | Creates a new isolated knowledge base. | `kb_id` (string) |
| `list_knowledge_bases` | Lists all knowledge base namespaces. | *None* |
| `ingest_document` | Ingests and indexes a local file into a KB. | `file_path` (string), `kb_id` (optional, default: "default") |
| `search_knowledge` | Hierarchical search with provenance. | `query` (string), `kb_id` (optional), `limit` (optional) |
| `query_context` | Formatted prompt context with citations. | `query` (string), `kb_id` (optional), `limit` (optional) |
| `find_documents` | Find candidate documents by summary. | `query` (string), `kb_id` (optional) |
| `read_document` | Returns normalized markdown. | `document_id` (string), `kb_id` (optional) |
| `read_section` | Returns chunks for a specific section. | `document_id`, `section_id`, `kb_id` (optional) |
| `analyze_spreadsheet` | Executes safe mathematical operations. | `document_id`, `sheet_name`, `operation`, `column` |

### 3.4 MCP JSON-RPC Protocol Examples

#### Listing Available Tools:
```json
--> {"jsonrpc": "2.0", "id": 1, "method": "tools/list"}
<-- {"jsonrpc": "2.0", "id": 1, "result": {"tools": [{"name": "search_knowledge", ...}]}}
```

#### Calling a Tool (`search_knowledge`):
```json
--> {
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "search_knowledge",
    "arguments": {
      "kb_id": "research_kb",
      "query": "What is the failover timeout?",
      "limit": 3
    }
  }
}
<-- {
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\"kb_id\": \"research_kb\", \"results\": [...]}"
      }
    ]
  }
}
```

---

## 4. End-to-End OpenWorker Harness Example

Here is a complete, runnable agent harness pattern showing how an OpenWorker worker thread creates a vector store, ingests files, queries context, and synthesizes answers:

```python
from pathlib import Path
from app import KnowledgeBase

class OpenWorkerResearchAgent:
    def __init__(self, agent_id: str, workspace_dir: str):
        self.agent_id = agent_id
        # 1. Instantiate dedicated KnowledgeBase for this agent
        self.kb = KnowledgeBase(
            kb_id=agent_id,
            storage_dir=Path(workspace_dir) / agent_id,
        )

    def load_materials(self, file_paths: list[str]):
        """Agent ingests study materials into its private vector DB."""
        for path in file_paths:
            print(f"[{self.agent_id}] Ingesting {path}...")
            res = self.kb.ingest_file(path)
            print(f"[{self.agent_id}] Ready: {res['title']} ({res['document_id']})")

    def answer_question(self, question: str) -> str:
        """Agent retrieves grounded evidence and builds answer."""
        # 2. Retrieve assembled evidence
        evidence = self.kb.query_context(question, limit=3)
        
        # 3. Synthesize answer with grounding
        prompt = (
            f"You are an OpenWorker assistant. Answer using the evidence below:\n\n"
            f"{evidence['formatted_context']}\n\n"
            f"Question: {question}\n"
            f"Answer:"
        )
        return prompt

    def shutdown(self):
        """Clean up SQLite database locks."""
        self.kb.close()

# Example usage:
if __name__ == "__main__":
    agent = OpenWorkerResearchAgent("worker_42", "./data/workspaces")
    # Ingest document
    agent.kb.ingest_bytes(
        content=b"# Deployment Guide\nStaging deployments require approval from QA lead.",
        filename="guide.md",
        title="Deployment Guide"
    )
    # Query
    print(agent.answer_question("Who must approve staging deployments?"))
    agent.shutdown()
```

---

## 5. Storage Layout Reference

When `KnowledgeBase(kb_id="alpha", storage_dir="./data/kbs/alpha")` runs, it establishes this filesystem structure:

```text
./data/kbs/alpha/
├── metadata.db                     # Isolated SQLite database (documents, chunks, jobs)
└── artifacts/
    ├── raw/                        # Original source files (Section 14.1)
    │   └── doc_abcdef12/
    │       └── original_file.pdf
    ├── derived/                    # Derived canonical representations (Section 14.2)
    │   └── doc_abcdef12/
    │       ├── normalized.md       # Clean Markdown representation
    │       └── canonical.json      # Structured Canonical Document AST
    └── renders/                    # Page images, chart renders, cropped visual blocks
```

In Qdrant, collections are namespaced:
- `kb_alpha_document_summaries`
- `kb_alpha_section_summaries`
- `kb_alpha_chunks`
- `kb_alpha_assets`

---

## 6. Troubleshooting & Best Practices

1. **Windows SQLite File Locking**:
   - Always call `kb.close()` or `manager.close_all()` when tearing down an agent or unit test. SQLite on Windows holds file handles until the SQLAlchemy connection pool is explicitly disposed.
2. **Qdrant Connection**:
   - If Qdrant is offline or not installed, Coordin8 automatically logs a warning and falls back to relational/sparse search gracefully without crashing.
3. **Empty File Handling**:
   - `ingest_bytes` and `ingest_file` validate content size and raise clear `ValueError` or `FileNotFoundError` exceptions before pipeline execution.
4. **Idempotency**:
   - If the same file (identical SHA-256 hash) is uploaded multiple times, Coordin8 detects the duplicate, returns `is_new: False`, and reuses the existing document and vector points without redundant processing.
