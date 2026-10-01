"""Project task endpoints and deterministic risk evaluation."""

from datetime import date, timedelta
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.auth import get_current_user, require_project_access, require_roles
from app.db.models import ProjectMember, Task, User
from app.db.session import get_db

router = APIRouter(tags=["tasks"])
TASK_STATUSES = {"BACKLOG", "IN_PROGRESS", "REVIEW", "DONE"}


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    owner_id: str | None = None
    due_date: date | None = None
    status: str = "BACKLOG"
    source_document_id: str | None = None
    source_chunk_id: str | None = None
    source_meeting_id: str | None = None


class TaskPatch(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=500)
    owner_id: str | None = None
    due_date: date | None = None
    status: str | None = None


def task_risk(status: str, due_date: date | None) -> tuple[bool, str | None]:
    if status == "DONE":
        return False, None
    if status == "BLOCKED":
        return True, "Task is blocked"
    if due_date and due_date < date.today():
        return True, "Task is overdue"
    if due_date and due_date <= date.today() + timedelta(days=2):
        return True, "Deadline is approaching"
    return False, None


def task_payload(task: Task, db: Session) -> dict:
    risk, reason = task_risk(task.status, task.due_date)
    owner = db.query(User).filter(User.id == task.owner_id).first() if task.owner_id else None
    return {
        "id": task.id,
        "project_id": task.project_id,
        "title": task.title,
        "owner_id": task.owner_id,
        "owner_name": owner.name if owner else None,
        "due_date": task.due_date.isoformat() if task.due_date else None,
        "status": task.status,
        "risk": risk,
        "risk_reason": reason,
        "source_document_id": task.source_document_id,
        "source_chunk_id": task.source_chunk_id,
        "source_meeting_id": task.source_meeting_id,
        "created_at": task.created_at.isoformat() if task.created_at else None,
        "updated_at": task.updated_at.isoformat() if task.updated_at else None,
    }


def validate_task_status(status: str) -> None:
    if status not in TASK_STATUSES:
        raise HTTPException(status_code=422, detail="Invalid task status")


def validate_owner(db: Session, project_id: str, owner_id: str | None) -> None:
    if owner_id is None:
        return
    member = (
        db.query(ProjectMember)
        .join(User, User.id == ProjectMember.user_id)
        .filter(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == owner_id,
            User.is_active.is_(True),
        )
        .first()
    )
    if not member:
        raise HTTPException(status_code=422, detail="Task owner must be an active project member")


@router.get("/projects/{project_id}/tasks")
def list_tasks(
    project_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_project_access(db, user, project_id)
    tasks = db.query(Task).filter(Task.project_id == project_id).order_by(Task.due_date, Task.created_at).all()
    if user.role == "TEAM_MEMBER":
        tasks = [task for task in tasks if task.owner_id in {None, user.id}]
    return [task_payload(task, db) for task in tasks]


@router.post("/projects/{project_id}/tasks", status_code=201)
def create_task(
    project_id: str,
    request: TaskCreate,
    user: User = Depends(require_roles("ADMIN", "MANAGER")),
    db: Session = Depends(get_db),
):
    require_project_access(db, user, project_id)
    validate_task_status(request.status)
    validate_owner(db, project_id, request.owner_id)
    task = Task(id=str(uuid4()), project_id=project_id, **request.model_dump())
    task.risk, task.risk_reason = task_risk(task.status, task.due_date)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task_payload(task, db)


@router.patch("/tasks/{task_id}")
def update_task(
    task_id: str,
    request: TaskPatch,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    require_project_access(db, user, task.project_id)
    updates = request.model_dump(exclude_unset=True)
    if updates.get("title") is None and "title" in updates:
        raise HTTPException(status_code=422, detail="Task title cannot be null")
    if updates.get("status") is None and "status" in updates:
        raise HTTPException(status_code=422, detail="Task status cannot be null")
    if user.role == "TEAM_MEMBER":
        if task.owner_id != user.id or set(updates) - {"status"}:
            raise HTTPException(status_code=403, detail="Members may update status on their own tasks only")
    if "status" in updates and updates["status"] is not None:
        validate_task_status(updates["status"])
    if "owner_id" in updates:
        validate_owner(db, task.project_id, updates["owner_id"])
    for field, value in updates.items():
        setattr(task, field, value.strip() if field == "title" and value else value)
    task.risk, task.risk_reason = task_risk(task.status, task.due_date)
    db.commit()
    db.refresh(task)
    return task_payload(task, db)