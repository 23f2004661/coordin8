"""Project meetings, minutes of meeting, and action items."""

import json
from datetime import date
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.auth import get_current_user, require_project_access, require_roles
from app.db.models import ActionItem, Meeting, Project, ProjectMember, Task, User
from app.db.session import get_db
from app.knowledge_base import KnowledgeBaseManager
from app.llm.client import LLMClient
from app.api.tasks import task_payload, task_risk

router = APIRouter(tags=["meetings"])
kb_manager = KnowledgeBaseManager()
llm_client = LLMClient()


def meeting_payload(db: Session, meeting: Meeting) -> dict:
    actions = db.query(ActionItem).filter(ActionItem.meeting_id == meeting.id).order_by(ActionItem.created_at).all()
    return {
        "id": meeting.id,
        "project_id": meeting.project_id,
        "title": meeting.title,
        "transcript_document_id": meeting.transcript_document_id,
        "summary": meeting.summary,
        "decisions": json.loads(meeting.decisions_json or "[]"),
        "action_items": [
            {
                "id": action.id,
                "text": action.text,
                "owner_id": action.owner_id,
                "owner_label": action.owner_label,
                "due_date": action.due_date.isoformat() if action.due_date else None,
                "task_id": action.task_id,
            }
            for action in actions
        ],
        "created_at": meeting.created_at.isoformat() if meeting.created_at else None,
    }


@router.post("/projects/{project_id}/meetings", status_code=201)
async def upload_meeting(
    project_id: str,
    file: UploadFile = File(...),
    title: str | None = Form(default=None),
    user: User = Depends(require_roles("ADMIN", "MANAGER")),
    db: Session = Depends(get_db),
):
    project = require_project_access(db, user, project_id)
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Transcript is empty")
    try:
        transcript = content.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise HTTPException(status_code=400, detail="Transcript must be UTF-8 text") from exc

    filename = file.filename or "meeting-transcript.txt"
    try:
        ingested = kb_manager.get_or_create(project.kb_id).ingest_bytes(
            content=content,
            filename=filename,
            title=title or filename.rsplit(".", 1)[0],
        )
    except (ValueError, OSError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    meeting = Meeting(
        id=str(uuid4()),
        project_id=project.id,
        title=(title or filename.rsplit(".", 1)[0]).strip(),
        transcript_text=transcript,
        transcript_document_id=ingested["document_id"],
        created_by=user.id,
    )
    db.add(meeting)
    db.commit()
    db.refresh(meeting)
    return meeting_payload(db, meeting)


@router.get("/projects/{project_id}/meetings")
def list_meetings(
    project_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_project_access(db, user, project_id)
    meetings = (
        db.query(Meeting)
        .filter(Meeting.project_id == project_id)
        .order_by(Meeting.created_at.desc())
        .all()
    )
    return [meeting_payload(db, meeting) for meeting in meetings]


@router.post("/meetings/{meeting_id}/generate-mom")
def generate_mom(
    meeting_id: str,
    user: User = Depends(require_roles("ADMIN", "MANAGER")),
    db: Session = Depends(get_db),
):
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    project = require_project_access(db, user, meeting.project_id)
    system_prompt = (
        "Extract minutes from the supplied meeting transcript. Return only valid JSON. "
        "Do not invent names, dates, decisions, or tasks. Use null for unknown owners or dates."
    )
    user_prompt = (
        'Return keys "summary" (string), "decisions" (array of strings), and "action_items" '
        '(array of objects with "text", "owner", and "due_date" as YYYY-MM-DD or null).\n\n'
        f"Meeting transcript:\n{meeting.transcript_text}"
    )
    try:
        generated = llm_client.generate_completion(system_prompt, user_prompt)
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail="AI service is currently unavailable. Please try again.") from exc
    try:
        parsed = json.loads(generated.strip().removeprefix("```json").removesuffix("```").strip())
        if not isinstance(parsed.get("summary"), str) or not isinstance(parsed.get("action_items", []), list):
            raise ValueError("Invalid MoM structure")
    except (json.JSONDecodeError, AttributeError, TypeError, ValueError) as exc:
        raise HTTPException(status_code=502, detail="LLM returned invalid MoM JSON") from exc

    meeting.summary = parsed["summary"]
    meeting.decisions_json = json.dumps(parsed.get("decisions", []))
    converted_actions = (
        db.query(ActionItem)
        .filter(ActionItem.meeting_id == meeting.id, ActionItem.task_id.is_not(None))
        .all()
    )
    converted_texts = {action.text.strip().casefold() for action in converted_actions}
    db.query(ActionItem).filter(
        ActionItem.meeting_id == meeting.id,
        ActionItem.task_id.is_(None),
    ).delete()
    for raw in parsed.get("action_items", []):
        if not isinstance(raw, dict) or not isinstance(raw.get("text"), str) or not raw["text"].strip():
            continue
        action_text = raw["text"].strip()
        if action_text.casefold() in converted_texts:
            continue
        owner_label = raw.get("owner") if isinstance(raw.get("owner"), str) else None
        owner = None
        if owner_label:
            owner = (
                db.query(User)
                .join(ProjectMember, ProjectMember.user_id == User.id)
                .filter(
                    ProjectMember.project_id == project.id,
                    User.is_active.is_(True),
                    User.name.ilike(owner_label.strip()),
                )
                .first()
            )
        due_date = None
        if raw.get("due_date"):
            try:
                due_date = date.fromisoformat(raw["due_date"])
            except (TypeError, ValueError):
                due_date = None
        db.add(
            ActionItem(
                id=str(uuid4()),
                meeting_id=meeting.id,
                project_id=meeting.project_id,
                text=action_text,
                owner_id=owner.id if owner else None,
                owner_label=owner_label,
                due_date=due_date,
            )
        )
    db.commit()
    db.refresh(meeting)
    return meeting_payload(db, meeting)


@router.post("/action-items/{action_item_id}/tasks", status_code=201)
def convert_action_item_to_task(
    action_item_id: str,
    user: User = Depends(require_roles("ADMIN", "MANAGER")),
    db: Session = Depends(get_db),
):
    action = db.query(ActionItem).filter(ActionItem.id == action_item_id).first()
    if not action:
        raise HTTPException(status_code=404, detail="Action item not found")
    project: Project = require_project_access(db, user, action.project_id)
    if action.task_id:
        task = db.query(Task).filter(Task.id == action.task_id).first()
        if task:
            return task_payload(task, db)
    task = Task(
        id=str(uuid4()),
        project_id=project.id,
        title=action.text,
        owner_id=action.owner_id,
        due_date=action.due_date,
        status="BACKLOG",
        source_document_id=(
            db.query(Meeting.transcript_document_id).filter(Meeting.id == action.meeting_id).scalar()
        ),
        source_meeting_id=action.meeting_id,
    )
    task.risk, task.risk_reason = task_risk(task.status, task.due_date)
    db.add(task)
    db.flush()
    action.task_id = task.id
    db.commit()
    db.refresh(task)
    return task_payload(task, db)