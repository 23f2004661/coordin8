from zipfile import ZipFile, ZIP_DEFLATED
from datetime import datetime, timezone
from xml.sax.saxutils import escape
from pathlib import Path

root = Path(r"c:\Users\16301\OneDrive - Compunnel\Desktop\IIT-M\GenAIProject\coordin8")
out_dir = root / "report_lily"
out_dir.mkdir(exist_ok=True)
out_file = out_dir / "coordin8_project_report.docx"

report_text = [
    "Coordin8 Project Report",
    "Generated from the current repository code and project documentation.",
    "",
    "1. Executive Summary",
    "Coordin8 is a multimodal knowledge and retrieval system designed to ingest heterogeneous document types, normalize them into a canonical structure, index the content for retrieval, and answer user queries with provenance-preserving evidence. The codebase is organized around a FastAPI backend, Qdrant-backed vector indexing, a SQL metadata layer, and a frontend dashboard for document management and retrieval inspection.",
    "",
    "The repository clearly documents a design principle: summaries are retrieval aids, not substitutes for source evidence. In practice, the system separates document-level summaries, section summaries, and raw chunk content so that retrieval can be coarse-to-fine while generated answers remain grounded in original content.",
    "",
    "2. Project Purpose and Vision",
    "The README and ProjectDetails.md describe Coordin8 as more than a simple chatbot over uploaded files. The intention is to build a reusable knowledge backend that can later be exposed to autonomous agents and tools in systems such as OpenWorker through Model Context Protocol (MCP).",
    "The system is meant to work with PDFs, DOCX files, spreadsheets, PPTX files, images, transcripts, and other structured or semi-structured content. It normalizes them into a common internal document model and preserves provenance such as page number, sheet name, slide number, section association, and chunk lineage.",
    "",
    "3. Repository Structure and Key Components",
    "The project is divided into a Python backend, a static frontend, infrastructure config, and support services. The backend includes the application runtime, API routes, ingestors, preprocessing adapters, OCR connectors, enrichment modules, indexing, retrieval, routing, spreadsheet evaluation, and MCP integration.",
    "Core runtime entry points include backend/main.py and backend/app/main.py. The latter creates a FastAPI application with startup lifecycle hooks that initialize the database schema and ensure required Qdrant collections exist before serving requests.",
    "The app/api package registers multiple route groups under /api including documents, jobs, search, answers, and spreadsheets. The frontend app.js file calls these APIs and provides a dashboard for search, upload, and provenance inspection.",
    "",
    "4. Startup and Runtime Architecture",
    "The system startup is configured through backend/app/core/config.py. This file centralizes settings such as API host/port, database URL, Qdrant endpoint, LLM endpoint, embedding model, reranker model, OCR provider, and artifact paths. The default deployment targets localhost services: FastAPI at port 8000, Qdrant at 6333, and PostgreSQL at 5432 as configured in the Docker Compose setup.",
    "The application startup in backend/app/main.py calls init_db() to create ORM tables and calls QdrantManager.ensure_collections() to ensure dense vector collections such as document summaries, section summaries, chunks, and assets exist. If infrastructure is not yet running, the code logs warnings rather than crashing the whole service, allowing startup to remain resilient.",
    "",
    "5. Data and Storage Model",
    "The backend uses SQLAlchemy for relational metadata management and Qdrant for vector storage. The database session layer supports both SQLite and PostgreSQL, and the project is designed to work with a local development database while also supporting a production-ready relational store when configured.",
    "The document model imposes a canonical hierarchy: Document -> Sections -> Chunks -> Assets. This is a major design commitment because it prevents modality-specific logic from spreading across retrieval and answer generation. Provenance information such as page, slide, sheet, and block lineage is retained to support citation quality and traceability.",
    "The Qdrant manager creates collections named using a prefix, including document summary, section summary, chunk, and asset collections, each configured with vector parameters and cosine distance search. This matches the project design for hierarchical retrieval over dense embeddings.",
    "",
    "6. Knowledge Base and Agent Integration",
    "The custom KnowledgeBase class in backend/app/knowledge_base.py is one of the most important engineering features in the repo. It creates an isolated knowledge base instance with its own storage directory, database, artifact storage, and Qdrant collection prefix. This makes it suitable for multi-tenant or per-agent storage use cases.",
    "The KnowledgeBase class orchestrates ingestion, indexing, retrieval, and context assembly. It registers documents, creates ingestion jobs, runs the ingestion pipeline, performs hierarchical search, fuses retrieval scores, reranks the final candidates, and returns a result payload with metadata, provenance, and score information. This class is meant to be used by agents or tool orchestrators instead of only by a single application instance.",
    "The project also exposes a Model Context Protocol server in backend/app/mcp/server.py. It defines standard tool names such as create_knowledge_base, ingest_document, search_knowledge, query_context, read_document, read_section, and analyze_spreadsheet. This means the knowledge backend can be used as an external tool provider for frameworks like OpenWorker.",
    "",
    "7. Ingestion Pipeline",
    "The ingestion pipeline is implemented through the document registry, job manager, and preprocessing components. The documents API reads uploaded bytes, detects file type, registers a document record, creates a job record, and triggers the pipeline. The process stores the original artifact, canonical representation, and metadata for later search and retrieval.",
    "The project explicitly supports diverse file types including PDF, DOCX, PPTX, XLSX, images, transcripts, and CSV-like sources. The preprocessing modules under backend/app/preprocessing implement adapters for each format, while OCR support is separated into backend/app/ocr with provider-level abstractions and a dedicated unlimited OCR microservice under services/unlimited_ocr.",
    "This design is intentional: the pipeline handles extraction, normalization, and enrichment before indexing, reducing the complexity of retrieval itself.",
    "",
    "8. Retrieval and Ranking Strategy",
    "The retrieval stack is hierarchical and hybrid. The search endpoints in backend/app/api/search.py perform a sequence of retrieval stages: document retrieval, section retrieval, chunk retrieval, hybrid fusion, and reranking. Query parsing identifies intent and modalities, allowing the system to include modality-aware search behavior.",
    "The retrieval design is consistent with the project specification: document summaries are used to narrow the search space, section summaries then select candidate sections, and raw chunks provide the final evidence. This reduces the amount of irrelevant content sent to the LLM while preserving grounded citations based on source material.",
    "The fusion layer combines retrieval signals, and the reranker improves precision on the strongest candidates before context assembly. The design is well aligned with modern RAG practices, especially where evidence quality and provenance matter more than raw retrieval recall alone.",
    "",
    "9. API Surface and User Experience",
    "The API layer aggregates routers under backend/app/api/__init__.py. The document routes support upload, list, summary retrieval, hierarchy exploration, processing trigger, and deletion. The search routes support hierarchical and per-document retrieval. The answer route is likely designed to combine retrieval and context assembly into grounded responses.",
    "The frontend in frontend/js/app.js implements a dashboard with document listing, upload flow, search and answer chat, and a developer inspector view for provenance tracing. This gives the project a complete UI for both end-user queries and technical debugging of retrieval lineage.",
    "The root application also exposes /health and /api/health endpoints, and the FastAPI app includes Swagger docs at /docs and /redoc, which makes it easy to validate API behavior during development.",
    "",
    "10. Infrastructure Dependencies",
    "The project depends on Docker-based infrastructure for Qdrant and PostgreSQL, a Python backend, and optional OCR services. The README states the recommended workflow is to start Docker, then the backend server, then the frontend static web server. This is a coherent development environment for a vector-search plus document-processing system.",
    "The configuration also includes support for local LM Studio endpoints and OpenAI-compatible LLM providers, which makes the system adaptable to local experimentation and external hosted models. The OCR layer similarly supports a local unlimited OCR microservice or Mistral OCR backend.",
    "",
    "11. Key Strengths",
    "The codebase is well-structured for a research and production prototype. It cleanly separates concerns across ingestion, preprocessing, enrichment, indexing, retrieval, API, and MCP integration. The design uses a canonical document model and hierarchical retrieval, which are strong choices for multimodal knowledge systems.",
    "The inclusion of provenance-aware retrieval and agent-facing MCP tools is especially notable because it reflects a long-term vision beyond a simple chat interface. The project is clearly built to evolve into a reusable backend for agents, not just a single app.",
    "",
    "12. Notable Observations and Risks",
    "The architecture is ambitious and the repo is feature-rich, but it is also broad in scope. Several subsystems are present at once: OCR, embeddings, reranking, spreadsheet execution, MCP server, and frontend inspection. This means the project requires careful operational management and verification of dependencies and environment variables.",
    "Because the code includes graceful fallback paths for missing services, the backend can boot even when some infrastructure is absent. This is helpful for resilience, but it also means that application correctness depends heavily on having the proper local services available during full end-to-end testing.",
    "For production maturity, the project would benefit from stronger validation around end-to-end ingestion, consistent test coverage, and operational monitoring for indexing and retrieval quality.",
    "",
    "13. Conclusion",
    "From the current repository code, Coordin8 is a research-grade multimodal knowledge platform with a clear architecture, a structured ingestion pipeline, a layered retrieval stack, and agent-ready MCP tooling. It is designed to transform heterogeneous enterprise documents into a searchable, evidence-grounded knowledge layer that can support both human interfaces and autonomous agents.",
    "The repository demonstrates a serious engineering plan around hierarchical RAG, provenance preservation, and system extensibility. The code and documentation align well, and the implementation is consistent with the project mission of building a reusable knowledge backend rather than a narrow document chatbot.",
    "End of report.",
]

paragraphs = []
for text in report_text:
    if not text.strip():
        paragraphs.append("<w:p/>")
    else:
        paragraphs.append("<w:p><w:r><w:t xml:space=\"preserve\">" + escape(text) + "</w:t></w:r></w:p>")

body_xml = "\n".join(paragraphs)
doc_xml = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:wpc="http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas" xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:wp14="http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing" xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" xmlns:w10="urn:schemas-microsoft-com:office:word" xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:w14="http://schemas.microsoft.com/office/word/2010/wordml" xmlns:w15="http://schemas.microsoft.com/office/word/2012/wordml" xmlns:wpg="http://schemas.microsoft.com/office/word/2010/wordprocessingGroup" xmlns:wpi="http://schemas.microsoft.com/office/word/2010/wordprocessingInk" xmlns:wne="http://schemas.microsoft.com/office/word/2006/wordml" xmlns:wps="http://schemas.microsoft.com/office/word/2010/wordprocessingShape" mc:Ignorable="w14 w15 wp14">
  <w:body>
    {body_xml}
    <w:sectPr>
      <w:pgSz w:w="12240" w:h="15840"/>
      <w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" w:header="720" w:footer="720" w:gutter="0"/>
    </w:sectPr>
  </w:body>
</w:document>
'''

styles_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/></w:style>
</w:styles>
'''

content_types = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
</Types>
'''

rels_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>
'''

created = datetime.now(timezone.utc).isoformat()
core_xml = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:dcmitype="http://purl.org/dc/dcmitype/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:title>Coordin8 Project Report</dc:title>
  <dc:creator>GitHub Copilot</dc:creator>
  <cp:lastModifiedBy>GitHub Copilot</cp:lastModifiedBy>
  <dcterms:created xsi:type="dcterms:W3CDTF">{created}</dcterms:created>
  <dcterms:modified xsi:type="dcterms:W3CDTF">{created}</dcterms:modified>
</cp:coreProperties>
'''

app_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
  <Application>Microsoft Word</Application>
</Properties>
'''

with ZipFile(out_file, "w", ZIP_DEFLATED) as zf:
    zf.writestr("[Content_Types].xml", content_types)
    zf.writestr("_rels/.rels", rels_xml)
    zf.writestr("docProps/core.xml", core_xml)
    zf.writestr("docProps/app.xml", app_xml)
    zf.writestr("word/document.xml", doc_xml)
    zf.writestr("word/styles.xml", styles_xml)

print(f"Created docx: {out_file}")
print(f"File exists: {out_file.exists()}")
