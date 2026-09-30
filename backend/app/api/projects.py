"""API endpoints for project workspaces, deliverables intelligence, and dedicated KnowledgeBases."""

from datetime import datetime
from typing import Any, Optional
from fastapi import APIRouter, HTTPException, Query, File, Form, UploadFile
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
    project_type: str = Field("internal", description="'internal' or 'client'")
    client_name: str = Field("", description="Client name if external/client project")
    client_email: str = Field("", description="Client contact email")
    problem_statement: str = Field("", description="Main problem statement and background context")
    overall_context: str = Field("", description="Extended context and scope description")


class UpdateProjectRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    category: str | None = None
    color: str | None = None
    code: str | None = None
    project_type: str | None = None
    client_name: str | None = None
    client_email: str | None = None
    problem_statement: str | None = None
    overall_context: str | None = None
    progress: int | None = None


class MeetingPayload(BaseModel):
    id: str | None = None
    title: str
    startTime: str
    endTime: str | None = None
    duration: str = "30 min"
    platform: str = "Google Meet"
    meetUrl: str | None = None
    attendees: list[str] = []
    agenda: str = ""
    prepDoc: str = ""
    status: str = "confirmed"
    isGcal: bool = False
    gcalId: str | None = None
    htmlLink: str | None = None
    projectId: str | None = None
    projectName: str | None = None
    projectColor: str | None = None

    class Config:
        extra = "allow"


class DeliverablePayload(BaseModel):
    title: str
    dueDate: str
    status: str = "in_progress"
    priority: str = "medium"
    progress: int = 0
    owner: str = "Team"
    description: str = ""
    source: str = "manual"
    sourceEvidence: str = ""
    evidenceFiles: list[str] = []


class OpenFileRequest(BaseModel):
    file_path: str | None = None
    project_id: str | None = None
    file_name: str | None = None


# -------------------------------------------------------------------------
# Static endpoints (MUST be defined before parameterized /{project_id})
# -------------------------------------------------------------------------

@router.post("/open-file")
def open_file_endpoint(req: OpenFileRequest):
    """Open any file (Excel, Word, PDF, text, markdown) in its native OS application."""
    mgr = ProjectManager.get_instance()
    try:
        res = mgr.open_file_in_os(
            file_path=req.file_path,
            project_id=req.project_id,
            file_name=req.file_name,
        )
        return res
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to open file in native application: {exc}")


@router.get("/home_folder")
def get_home_folder():
    """Return configured Home Folder path and list of existing subdirectories."""
    mgr = ProjectManager.get_instance()
    return mgr.get_home_folder_info()


@router.get("")
def list_projects():
    """List all registered projects with live file trees and stats, plus unassigned meetings."""
    mgr = ProjectManager.get_instance()
    return {
        "projects": mgr.list_projects(),
        "unassigned_meetings": mgr.get_unassigned_meetings(),
    }


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
            project_type=req.project_type,
            client_name=req.client_name,
            client_email=req.client_email,
            problem_statement=req.problem_statement or req.description,
            overall_context=req.overall_context,
        )
        return proj
    except FileNotFoundError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to create project: {exc}")


@router.get("/gcal_account")
def get_gcal_account():
    """Retrieve connected Google Account metadata."""
    mgr = ProjectManager.get_instance()
    return {"account": mgr.get_google_account()}


@router.post("/gcal_account")
def set_gcal_account(payload: dict[str, Any]):
    """Persist connected Google Account metadata."""
    mgr = ProjectManager.get_instance()
    account = mgr.set_google_account(payload)
    return {"account": account}


@router.delete("/gcal_account")
def clear_gcal_account():
    """Clear connected Google Account metadata."""
    mgr = ProjectManager.get_instance()
    mgr.clear_google_account()
    return {"status": "ok"}


@router.get("/meetings/unassigned")
def get_unassigned_meetings():
    """Return all unassigned meetings."""
    mgr = ProjectManager.get_instance()
    return {"meetings": mgr.get_unassigned_meetings()}


@router.post("/meetings/unassigned", status_code=201)
def add_unassigned_meeting(meeting: MeetingPayload):
    """Add or update an unassigned meeting."""
    mgr = ProjectManager.get_instance()
    data = meeting.dict()
    if not data.get("id"):
        data["id"] = f"m_{int(datetime.now().timestamp() * 1000)}"
    return mgr.add_meeting(None, data)


@router.post("/meetings/unassigned/batch", status_code=201)
def add_unassigned_meetings_batch(meetings: list[MeetingPayload]):
    """Batch upsert unassigned meetings."""
    mgr = ProjectManager.get_instance()
    added = []
    for m in meetings:
        data = m.dict()
        if not data.get("id"):
            data["id"] = f"m_{int(datetime.now().timestamp() * 1000)}"
        mgr.add_meeting(None, data)
        added.append(data)
    return {"synced_count": len(added), "meetings": added}


@router.delete("/meetings/unassigned/{meeting_id}")
def delete_unassigned_meeting(meeting_id: str):
    """Delete a meeting from the unassigned list."""
    mgr = ProjectManager.get_instance()
    removed = mgr.delete_unassigned_meeting(meeting_id)
    return {"success": removed, "meeting_id": meeting_id}


@router.post("/meetings/{meeting_id}/transcript", status_code=200)
async def upload_meeting_transcript(
    meeting_id: str,
    file: UploadFile = File(...),
    project_id: Optional[str] = Form(None),
):
    """Upload and index a meeting transcript into the project KB or general workspace KB."""
    mgr = ProjectManager.get_instance()
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Transcript file is empty")

    try:
        result = mgr.upload_meeting_transcript(
            meeting_id=meeting_id,
            filename=file.filename or "transcript.txt",
            content=content,
            target_project_id=project_id,
        )
        return result
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to index transcript: {exc}")


@router.get("/emails")
def get_synced_emails():
    """Retrieve all synchronized Gmail messages."""
    mgr = ProjectManager.get_instance()
    return {"emails": mgr.get_synced_emails()}


@router.post("/emails/sync")
def sync_emails(payload: dict[str, Any]):
    """Save or merge newly synchronized Gmail messages."""
    mgr = ProjectManager.get_instance()
    emails = payload.get("emails", [])
    synced = mgr.save_synced_emails(emails)
    return {"status": "ok", "count": len(synced), "emails": synced}


@router.post("/emails/{email_id}/assign")
def assign_email(email_id: str, payload: dict[str, Any]):
    """Assign or unassign an email to a project and run AI archetype classification."""
    mgr = ProjectManager.get_instance()
    project_id = payload.get("projectId")
    try:
        updated = mgr.assign_email_to_project(email_id, project_id)
        return {"status": "ok", "email": updated}
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to assign email: {exc}")


# -------------------------------------------------------------------------
# Dynamic /{project_id} endpoints
# -------------------------------------------------------------------------

@router.get("/{project_id}")
def get_project(project_id: str):
    """Get project details, physical folders, live document inventory, and emails."""
    mgr = ProjectManager.get_instance()
    try:
        return mgr.get_project_details(project_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Project not found")


@router.patch("/{project_id}")
def update_project_details(project_id: str, req: UpdateProjectRequest):
    """Update project details like problem statement, background context, client info."""
    mgr = ProjectManager.get_instance()
    updates = {k: v for k, v in req.dict().items() if v is not None}
    try:
        return mgr.update_project(project_id, updates)
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


@router.post("/{project_id}/meetings", status_code=201)
def add_project_meeting(project_id: str, meeting: MeetingPayload):
    """Add a scheduled or Google Calendar-synced meeting to the project."""
    mgr = ProjectManager.get_instance()
    try:
        data = meeting.dict()
        if not data.get("id"):
            data["id"] = f"m_{int(datetime.now().timestamp() * 1000)}"
        return mgr.add_meeting(project_id, data)
    except KeyError:
        raise HTTPException(status_code=404, detail="Project not found")


@router.post("/{project_id}/meetings/batch", status_code=201)
def add_project_meetings_batch(project_id: str, meetings: list[MeetingPayload]):
    """Add a batch of Google Calendar-synced meetings to the project."""
    mgr = ProjectManager.get_instance()
    try:
        added = []
        for m in meetings:
            data = m.dict()
            if not data.get("id"):
                data["id"] = f"m_{int(datetime.now().timestamp() * 1000)}"
            mgr.add_meeting(project_id, data)
            added.append(data)
        return {"project_id": project_id, "synced_count": len(added), "meetings": added}
    except KeyError:
        raise HTTPException(status_code=404, detail="Project not found")


@router.delete("/{project_id}/meetings/{meeting_id}")
def delete_project_meeting(project_id: str, meeting_id: str):
    """Delete a meeting from a project."""
    mgr = ProjectManager.get_instance()
    try:
        removed = mgr.delete_meeting(project_id, meeting_id)
        return {"success": removed, "project_id": project_id, "meeting_id": meeting_id}
    except KeyError:
        raise HTTPException(status_code=404, detail="Project not found")


# -------------------------------------------------------------------------
# Deliverables & AI Intelligence Endpoints
# -------------------------------------------------------------------------

@router.post("/{project_id}/deliverables", status_code=201)
def add_project_deliverable(project_id: str, payload: dict[str, Any]):
    """Add a milestone deliverable to a project."""
    mgr = ProjectManager.get_instance()
    try:
        data = payload.copy()
        if not data.get("id"):
            data["id"] = f"del_{int(datetime.now().timestamp() * 1000)}"
        return mgr.add_deliverable(project_id, data)
    except KeyError:
        raise HTTPException(status_code=404, detail="Project not found")


@router.patch("/{project_id}/deliverables/{deliverable_id}")
def update_project_deliverable(project_id: str, deliverable_id: str, updates: dict[str, Any]):
    """Update a deliverable's status, progress, or attributes."""
    mgr = ProjectManager.get_instance()
    try:
        return mgr.update_deliverable(project_id, deliverable_id, updates)
    except KeyError:
        raise HTTPException(status_code=404, detail="Deliverable or project not found")


@router.delete("/{project_id}/deliverables/{deliverable_id}")
def delete_project_deliverable(project_id: str, deliverable_id: str):
    """Delete a deliverable from a project."""
    mgr = ProjectManager.get_instance()
    try:
        removed = mgr.delete_deliverable(project_id, deliverable_id)
        return {"success": removed, "deliverable_id": deliverable_id}
    except KeyError:
        raise HTTPException(status_code=404, detail="Deliverable or project not found")


@router.post("/{project_id}/deliverables/{deliverable_id}/breakdown")
def breakdown_project_deliverable(project_id: str, deliverable_id: str):
    """Decompose a deliverable into granular execution tasks via AI."""
    mgr = ProjectManager.get_instance()
    try:
        tasks = mgr.breakdown_deliverable(project_id, deliverable_id)
        return {"project_id": project_id, "deliverable_id": deliverable_id, "tasks": tasks}
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Deliverable breakdown failed: {exc}")


@router.get("/{project_id}/tasks")
def get_project_tasks_endpoint(project_id: str):
    """Retrieve all decomposed execution tasks for a project."""
    mgr = ProjectManager.get_instance()
    try:
        tasks = mgr.get_project_tasks(project_id)
        return {"project_id": project_id, "tasks": tasks, "total_tasks": len(tasks)}
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.patch("/{project_id}/deliverables/{deliverable_id}/tasks/{task_id}")
def update_project_task_endpoint(project_id: str, deliverable_id: str, task_id: str, updates: dict[str, Any]):
    """Update execution task status, stage, or attributes."""
    mgr = ProjectManager.get_instance()
    try:
        updated = mgr.update_task(project_id, deliverable_id, task_id, updates)
        return {"status": "ok", "task": updated}
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/{project_id}/analyze-deliverables")
def analyze_project_deliverables(project_id: str):
    """Trigger AI progress audit and candidate deliverable extraction across documents, meetings, and emails."""
    mgr = ProjectManager.get_instance()
    try:
        result = mgr.run_project_ai_audit(project_id)
        return result
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Deliverable analysis failed: {exc}")


@router.post("/{project_id}/deliverables/accept-discovered")
def accept_discovered_deliverable_endpoint(project_id: str, payload: dict[str, Any]):
    """Accept an AI-discovered candidate deliverable into the active project timeline."""
    mgr = ProjectManager.get_instance()
    try:
        deliv = mgr.accept_discovered_deliverable(project_id, payload)
        return {"status": "ok", "deliverable": deliv}
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to accept deliverable: {exc}")


@router.post("/{project_id}/deliverables/dismiss-discovered")
def dismiss_discovered_deliverable_endpoint(project_id: str, payload: dict[str, Any]):
    """Dismiss an AI-discovered deliverable recommendation."""
    mgr = ProjectManager.get_instance()
    title = payload.get("title", "")
    try:
        mgr.dismiss_discovered_deliverable(project_id, title)
        return {"status": "ok", "title": title}
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/{project_id}/open-folder")
def open_project_folder_endpoint(project_id: str):
    """Open the physical project folder in Windows File Explorer."""
    mgr = ProjectManager.get_instance()
    try:
        return mgr.open_project_folder_in_os(project_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to open project folder: {exc}")

