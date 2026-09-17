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

## Quickstart

### 1. Launch Infrastructure
```powershell
docker-compose up -d
```

### 2. Backend Setup
```powershell
cd backend
# Create or activate virtual environment
.\venv\Scripts\Activate.ps1

# Install requirements
pip install -r requirements.txt

# Copy configuration
cp ../.env.example .env

# Run development server
python main.py
```
The backend API documentation will be available at `http://localhost:8000/docs`.

### 3. Isolated OCR Service (Optional for Scanned Documents)
```powershell
cd services/unlimited_ocr
python server.py
```

### 4. Frontend
Open `frontend/index.html` in any modern web browser or serve with a lightweight local server:
```powershell
cd frontend
python -m http.server 3000
```
Visit `http://localhost:3000` to access the dashboard and provenance inspector.