"""Tenant-scoped projects and project-isolated knowledge operations."""

from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.auth import get_current_user, require_project_access, require_roles
from app.db.models import ChunkRecord, DocumentRecord, Project, ProjectMember, User
from app.db.session import get_db
from app.knowledge_base import KnowledgeBaseManager
from app.llm.client import LLMClient

router = APIRouter(prefix="/projects", tags=["projects"])
kb_manager = KnowledgeBaseManager()
llm_client = LLMClient()


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    client: str | None = None


class ProjectPatch(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    client: str | None = None
    status: str | None = None


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=10000)


class SearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=10000)
    limit: int = Field(default=5, ge=1, le=50)


def project_payload(project: Project) -> dict:
    return {
        "id": project.id,
        "tenant_id": project.tenant_id,
        "name": project.name,
        "client": project.client,
        "status": project.status,
        "kb_id": project.kb_id,
        "created_at": project.created_at.isoformat() if project.created_at else None,
    }


@router.get("")
def list_projects(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    projects = db.query(Project).filter(Project.tenant_id == user.tenant_id)
    if user.role not in {"SUPER_ADMIN", "ADMIN"}:
        projects = projects.join(ProjectMember).filter(ProjectMember.user_id == user.id)
    return [project_payload(project) for project in projects.order_by(Project.name).all()]


@router.post("", status_code=201)
def create_project(
    request: ProjectCreate,
    user: User = Depends(require_roles("ADMIN")),
    db: Session = Depends(get_db),
):
    project_id = str(uuid4())
    project = Project(
        id=project_id,
        tenant_id=user.tenant_id,
        name=request.name.strip(),
        client=request.client,
        status="ACTIVE",
        kb_id=project_id,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    kb_manager.get_or_create(project.kb_id)
    return project_payload(project)


@router.get("/{project_id}")
def get_project(
    project_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return project_payload(require_project_access(db, user, project_id))


@router.patch("/{project_id}")
def update_project(
    project_id: str,
    request: ProjectPatch,
    user: User = Depends(require_roles("ADMIN")),
    db: Session = Depends(get_db),
):
    project = require_project_access(db, user, project_id)
    for field, value in request.model_dump(exclude_unset=True).items():
        setattr(project, field, value.strip() if field == "name" and value else value)
    db.commit()
    db.refresh(project)
    return project_payload(project)


@router.get("/{project_id}/documents")
def list_project_documents(
    project_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = require_project_access(db, user, project_id)
    return kb_manager.get_or_create(project.kb_id).list_documents()


@router.get("/{project_id}/documents/{document_id}/hierarchy")
def project_document_hierarchy(
    project_id: str,
    document_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = require_project_access(db, user, project_id)
    kb = kb_manager.get_or_create(project.kb_id)
    with kb.session() as kb_db:
        document = kb_db.query(DocumentRecord).filter(DocumentRecord.document_id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        chunks = kb_db.query(ChunkRecord).filter(ChunkRecord.document_id == document_id).all()
    sections_map: dict[str, list[dict]] = {}
    for chunk in chunks:
        section_id = chunk.section_id or "sec_main"
        sections_map.setdefault(section_id, []).append(
            {
                "chunk_id": chunk.chunk_id,
                "content": chunk.content,
                "content_type": chunk.content_type,
                "token_count": chunk.token_count,
                "page": chunk.page_number,
                "slide": chunk.slide_number,
                "sheet": chunk.sheet_name,
                "summary": chunk.summary,
            }
        )
    return {
        "document_id": document.document_id,
        "title": document.title,
        "file_type": document.file_type,
        "status": document.status,
        "summary": document.summary,
        "total_chunks": len(chunks),
        "sections": [
            {"section_id": section_id, "chunks_count": len(section_chunks), "chunks": section_chunks}
            for section_id, section_chunks in sections_map.items()
        ],
    }


@router.post("/{project_id}/documents", status_code=201)
async def upload_project_document(
    project_id: str,
    file: UploadFile = File(...),
    user: User = Depends(require_roles("ADMIN", "MANAGER")),
    db: Session = Depends(get_db),
):
    project = require_project_access(db, user, project_id)
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")
    try:
        return kb_manager.get_or_create(project.kb_id).ingest_bytes(
            content=content,
            filename=file.filename or "upload",
        )
    except (ValueError, OSError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/{project_id}/chat")
def project_chat(
    project_id: str,
    request: ChatRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = require_project_access(db, user, project_id)
    kb = kb_manager.get_or_create(project.kb_id)
    context = kb.query_context(request.message)
    if not context["formatted_context"].strip():
        return {
            "answer": "I couldn't find enough relevant information in this project's knowledge base to answer that question.",
            "citations": [],
            "sources": [],
            "grounded": False,
        }
    try:
        answer = llm_client.generate_answer(request.message, context["formatted_context"])
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    evidence_units = context.get("evidence_units", [])
    citations = [unit["citation"] for unit in evidence_units if unit.get("citation")]
    document_titles = {}
    sources = []
    for unit in evidence_units:
        citation = unit.get("citation")
        document_id = unit.get("document_id")
        if not citation or not document_id:
            continue
        if document_id not in document_titles:
            document = kb.get_document(document_id)
            document_titles[document_id] = document.get("title") if document else None
        sources.append(
            {
                "document_id": document_id,
                "document_title": document_titles[document_id],
                "citation": citation,
            }
        )
    return {"answer": answer, "citations": citations, "sources": sources, "grounded": bool(sources)}


@router.post("/{project_id}/search")
def project_search(
    project_id: str,
    request: SearchRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = require_project_access(db, user, project_id)
    return kb_manager.get_or_create(project.kb_id).search(request.query, limit=request.limit)