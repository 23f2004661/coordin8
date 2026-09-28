"""API endpoints for project workspaces and dedicated KnowledgeBases."""

from typing import Any
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.projects.manager import ProjectManager

router = APIRouter(prefix="/projects", tags=["projects"])


class CreateProjectRequest(BaseModel):
    name: str = Field(..., description="Project name")
    description: str = Field("", description="Project description")
    category: str = Field("General", description="Project category")
    color: str = Field("#6366f1", description="Project accent color hex")
    code: str | None = Field(None, description="Short project code, e.g. RAG-CORE")
    creation_mode: str = Field("scratch", description="'scratch' or 'existing_folder'")
    folder_path: str | None = Field(None, description="Path to folder if creating from existing")


class MeetingPayload(BaseModel):
    title: str
    startTime: str
    endTime: str | None = None
    platform: str = "Google Meet"
    meetUrl: str | None = None
    attendees: list[str] = []
    agenda: str = ""
    prepDoc: str = ""


class DeliverablePayload(BaseModel):
    title: str
    dueDate: str
    status: str = "in_progress"
    priority: str = "medium"
    progress: int = 0
    owner: str = "Team"
    description: str = ""


@router.get("/home_folder")
def get_home_folder():
    """Return configured Home Folder path and list of existing subdirectories."""
    mgr = ProjectManager.get_instance()
    return mgr.get_home_folder_info()


@router.get("")
def list_projects():
    """List all registered projects with live file trees and stats."""
    mgr = ProjectManager.get_instance()
    return {"projects": mgr.list_projects()}


@router.post("", status_code=201)
def create_project(req: CreateProjectRequest):
    """Create a project workspace from scratch or from an existing directory."""
    mgr = ProjectManager.get_instance()
    try:
        proj = mgr.create_project(
            name=req.name,
            description=req.description,
            category=req.category,
            color=req.color,
            code=req.code,
            creation_mode=req.creation_mode,
            folder_path=req.folder_path,
        )
        return proj
    except FileNotFoundError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to create project: {exc}")


@router.get("/{project_id}")
def get_project(project_id: str):
    """Get project details, physical folders, and live document inventory."""
    mgr = ProjectManager.get_instance()
    try:
        return mgr.get_project_details(project_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Project not found")


@router.post("/{project_id}/rescan")
def rescan_project(project_id: str):
    """Manually trigger immediate rescan and ingestion of project folder files."""
    mgr = ProjectManager.get_instance()
    try:
        count = mgr.scan_and_ingest_project_files(project_id)
        return {"project_id": project_id, "ingested_count": count, "success": True}
    except KeyError:
        raise HTTPException(status_code=404, detail="Project not found")


@router.get("/{project_id}/search")
def search_project_knowledge(
    project_id: str,
    query: str = Query(..., description="Semantic search query"),
    limit: int = Query(5, ge=1, le=20),
):
    """Perform hybrid hierarchical retrieval across this project's dedicated KnowledgeBase."""
    mgr = ProjectManager.get_instance()
    try:
        kb = mgr.get_project_kb(project_id)
        results = kb.search(query=query, limit=limit)
        return results
    except KeyError:
        raise HTTPException(status_code=404, detail="Project not found")


@router.delete("/{project_id}")
def delete_project(project_id: str, delete_folder: bool = False):
    """Unregister project and optionally delete on-disk files."""
    mgr = ProjectManager.get_instance()
    success = mgr.delete_project(project_id, delete_folder=delete_folder)
    if not success:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"success": True, "project_id": project_id}
