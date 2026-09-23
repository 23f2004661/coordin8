# Coordin8 — Multimodal Hierarchical RAG

Coordin8 is a multimodal knowledge and retrieval system that ingests heterogeneous files—meeting transcripts, PDFs, images, Excel workbooks, Word documents, and PowerPoint presentations—and makes the information available to a high-quality, provenance-preserving Retrieval-Augmented Generation (RAG) system.

The long-term goal is to build a reusable knowledge backend that can be exposed to agent systems such as OpenWorker through the Model Context Protocol (MCP).

---

## Architectural Principle

> **Summaries are retrieval aids, not substitutes for source evidence.**  
> The original document and its normalized canonical representation remain the source of truth.

---

## Repository Structure

```text
coordin8/
├── ProjectDetails.md          # Architectural contract and detailed specification
├── README.md                  # Project overview and quickstart
├── docs/                      # Extensive integration guides & documentation
│   └── openworker_integration.md # Complete OpenWorker SDK & MCP manual
├── .gitignore                 # Environment and build ignores
├── .env.example               # Configuration template
├── docker-compose.yml         # Qdrant vector store and PostgreSQL
│
├── backend/                   # FastAPI Python backend
│   ├── app/                   # Core application modules
│   │   ├── api/               # REST API endpoints
│   │   ├── core/              # Config, logging, security
│   │   ├── domain/            # Canonical Document, Section, Chunk, Asset models
│   │   ├── db/                # Database models and session management
│   │   ├── ingestion/         # File registration, hashing, pipeline orchestration
│   │   ├── preprocessing/     # Format adapters (PDF, DOCX, PPTX, XLSX, Image, Transcript)
│   │   ├── ocr/               # Unlimited-OCR client & provider adapters
│   │   ├── enrichment/        # Summaries, entity, and topic generators
│   │   ├── chunking/          # Hierarchical and semantic chunkers
│   │   ├── indexing/          # Dense/sparse vector indexing & Qdrant integration
│   │   ├── retrieval/         # Hierarchical retrieval, RRF fusion, reranker, context assembly
│   │   ├── routing/           # Query intent and modality router
│   │   ├── spreadsheets/      # Safe Excel computation engine
│   │   ├── llm/               # OpenAI/LM Studio compatible generation
│   │   ├── storage/           # Artifact filesystem manager
│   │   ├── mcp/               # Model Context Protocol server & tool definitions
│   │   └── utils/             # Hashing, tokenization, provenance formatters
│   ├── tests/                 # Unit, integration, and retrieval tests
│   ├── evals/                 # Benchmark questions and eval runner
│   ├── scripts/               # Ingest, reindex, and evaluate CLI scripts
│   └── data/                  # Raw, derived, and rendered artifacts
│
├── services/
│   └── unlimited_ocr/         # Isolated Baidu Unlimited-OCR microservice (GPU-optimized)
│
└── frontend/                  # Web interface dashboard & developer provenance inspector
```

---

## OpenWorker & Agent Integration (Custom Class & MCP)

Coordin8 can be used either as an in-process Python class library or as a standalone Model Context Protocol (MCP) tool server for agentic harnesses like **OpenWorker**:

### Option 1: In-Process Python SDK (`KnowledgeBase` Custom Class)
OpenWorker agents can dynamically instantiate isolated vector stores and knowledge repositories:

```python
from app import KnowledgeBase

# 1. Dynamically create an isolated knowledge base
kb = KnowledgeBase(
    kb_id="research_agent_01",
    storage_dir="./data/agent_kbs/agent_01",
)

# 2. Ingest documents (PDF, Word, Excel, Markdown, PPTX, Images)
kb.ingest_file("./docs/system_spec.pdf", title="System Architecture")

# 3. Perform hierarchical hybrid search
results = kb.search("What is the failover latency?")

# 4. Assemble citation-grounded prompt context ready for LLMs
context = kb.query_context("failover latency SLA", limit=3)
print(context["formatted_context"])

# 5. Export tool calling schemas directly for OpenWorker
tools = kb.as_tools()
tool_result = kb.execute_tool("search_knowledge", {"query": "failover latency", "limit": 2})

# 6. Clean up resources
kb.close()
```

### Option 2: Model Context Protocol (MCP) Server (Milestone 9)
Run Coordin8 as an out-of-process tool provider over stdio JSON-RPC:
```powershell
cd backend
python -m app.mcp.server
```

OpenWorker connects via standard MCP and gains access to tools: `create_knowledge_base`, `ingest_document`, `search_knowledge`, `query_context`, `read_document`, `read_section`, `analyze_spreadsheet`.

> 📖 **Full Manual**: See [docs/openworker_integration.md](docs/openworker_integration.md) for complete API reference, parameters, and multi-tenant management.  
> 🚀 **Runnable Demo**: Run `python backend/scripts/openworker_sdk_example.py` for a live demonstration.

---

## Starting the System (Step-by-Step)

Whenever you start working on Coordin8, follow these 3 steps across separate terminal windows:

### Step 1: Start Infrastructure (Docker)
In your root project directory (`coordin8/`), spin up the Qdrant vector database and PostgreSQL:
```powershell
docker compose up -d
```
> *(Or `docker-compose up -d` on older Docker installations)*

To verify that the containers are healthy and running:
```powershell
docker compose ps
```

---

### Step 2: Start Backend Server (FastAPI)
In a new terminal window, activate your virtual environment and start the API server:

**Windows (PowerShell):**
```powershell
cd backend
.\venv\Scripts\Activate.ps1
python main.py
```

**Linux / macOS:**
```bash
cd backend
source venv/bin/activate
python main.py
```

- API Server: `http://localhost:8000`
- Interactive Swagger UI: `http://localhost:8000/docs`
- ReDoc UI: `http://localhost:8000/redoc`

---

### Step 3: Start Frontend Dashboard
In another terminal window, serve the static web dashboard:

```powershell
cd frontend
python -m http.server 3000
```

- Dashboard UI: `http://localhost:3000`
- The frontend automatically communicates with the backend at `http://localhost:8000`.

---

### Step 4 (Optional): Start Isolated OCR Service
If processing scanned documents or high-volume OCR with the isolated Baidu Unlimited-OCR microservice:

```powershell
cd services/unlimited_ocr
python server.py
```

---

## Service Summary & Ports

| Service | Address | Purpose |
| :--- | :--- | :--- |
| **Frontend Web Dashboard** | `http://localhost:3000` | UI, search, upload & provenance inspector |
| **Backend REST API** | `http://localhost:8000` | Core API & business logic |
| **API Documentation** | `http://localhost:8000/docs` | Swagger OpenAPI interactive docs |
| **Qdrant Vector DB** | `http://localhost:6333` | REST vector search (`/dashboard` for web UI) |
| **Qdrant gRPC** | `localhost:6334` | High-throughput vector indexing |
| **PostgreSQL Database** | `localhost:5432` | Relational document metadata & states |
| **Unlimited OCR (Opt.)**| `http://localhost:8001` | Isolated GPU-optimized OCR service |

---

## Stopping the System

When you are done working:
1. Press `Ctrl + C` in both the Backend and Frontend terminal windows.
2. Stop the Docker containers from the `coordin8/` directory:
   ```powershell
   docker compose down
   ```

---

## First-Time Installation & Setup

If you are setting up the project for the very first time on a new machine:

1. **Clone and enter repository**:
   ```powershell
   git clone <repo_url>
   cd coordin8
   ```

2. **Configure environment variables**:
   ```powershell
   cp .env.example .env
   cp .env.example backend/.env
   ```
   *Edit `.env` or `backend/.env` to configure your LLM provider (`OPENAI_API_KEY` or local LM Studio endpoint).*

3. **Set up backend virtual environment**:
   ```powershell
   cd backend
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Launch containers and run**:
   Follow the [Starting the System](#starting-the-system-step-by-step) steps above.