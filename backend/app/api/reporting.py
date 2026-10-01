"""Project dashboards and deterministic reporting endpoints."""

from datetime import date, datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.tasks import task_risk
from app.core.auth import get_current_user, require_project_access
from app.db.models import Meeting, Project, ProjectMember, Task, Tenant, User
from app.db.session import get_db

router = APIRouter(tags=["reporting"])


def get_user_projects(db: Session, user: User) -> list[Project]:
    query = db.query(Project).filter(Project.tenant_id == user.tenant_id)
    if user.role not in {"SUPER_ADMIN", "ADMIN"}:
        query = query.join(ProjectMember).filter(ProjectMember.user_id == user.id)
    return query.order_by(Project.name).all()


def task_totals(tasks: list[Task]) -> dict:
    counts = {status.lower(): sum(task.status == status for task in tasks) for status in ("BACKLOG", "IN_PROGRESS", "REVIEW", "DONE")}
    counts["total"] = len(tasks)
    counts["at_risk"] = sum(task_risk(task.status, task.due_date)[0] for task in tasks)
    counts["completion_percentage"] = round(counts["done"] / len(tasks) * 100) if tasks else 0
    return counts


def task_summary(task: Task) -> dict:
    risk, reason = task_risk(task.status, task.due_date)
    return {
        "id": task.id,
        "project_id": task.project_id,
        "title": task.title,
        "owner_id": task.owner_id,
        "due_date": task.due_date.isoformat() if task.due_date else None,
        "status": task.status,
        "risk": risk,
        "risk_reason": reason,
    }


@router.get("/dashboard")
def role_dashboard(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    projects = get_user_projects(db, user)
    project_ids = [project.id for project in projects]
    task_query = db.query(Task).filter(Task.project_id.in_(project_ids)) if project_ids else db.query(Task).filter(False)
    tasks = task_query.all()
    if user.role == "ADMIN":
        tenant_employees = db.query(User).filter(User.tenant_id == user.tenant_id).count()
        return {
            "role": user.role,
            "employee_count": tenant_employees,
            "project_count": len(projects),
            "active_projects": sum(project.status == "ACTIVE" for project in projects),
            "tasks": task_totals(tasks),
            "at_risk_projects": [
                {"project_id": project.id, "name": project.name}
                for project in projects
                if any(
                    task_risk(task.status, task.due_date)[0]
                    for task in tasks
                    if task.project_id == project.id
                )
            ],
        }

    if user.role == "TEAM_MEMBER":
        tasks = [task for task in tasks if task.owner_id == user.id]
    project_progress = []
    for project in projects:
        project_tasks = [task for task in tasks if task.project_id == project.id]
        project_progress.append({"project_id": project.id, "name": project.name, **task_totals(project_tasks)})
    return {
        "role": user.role,
        "projects": project_progress,
        "tasks": task_totals(tasks),
        "my_tasks": [task_summary(task) for task in tasks if task.owner_id == user.id],
        "due_soon": [
            task_summary(task)
            for task in tasks
            if task.due_date and date.today() <= task.due_date <= date.today() + timedelta(days=7)
            and task.status != "DONE"
        ],
        "overdue": [
            task_summary(task)
            for task in tasks
            if task.due_date and task.due_date < date.today() and task.status != "DONE"
        ],
        "recent_meetings": [
            {"id": meeting.id, "project_id": meeting.project_id, "title": meeting.title, "created_at": meeting.created_at.isoformat()}
            for meeting in db.query(Meeting)
            .filter(Meeting.project_id.in_(project_ids))
            .order_by(Meeting.created_at.desc())
            .limit(5)
            .all()
        ] if project_ids else [],
    }


@router.get("/projects/{project_id}/dashboard")
def project_dashboard(
    project_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_project_access(db, user, project_id)
    tasks = db.query(Task).filter(Task.project_id == project_id).all()
    today = date.today()
    upcoming = [task_summary(task) for task in tasks if task.due_date and today <= task.due_date <= today + timedelta(days=7) and task.status != "DONE"]
    meetings = db.query(Meeting).filter(Meeting.project_id == project_id).order_by(Meeting.created_at.desc()).limit(5).all()
    activity = [
        {"type": "task", "id": task.id, "title": task.title, "created_at": task.created_at.isoformat()}
        for task in tasks
    ] + [
        {"type": "meeting", "id": meeting.id, "title": meeting.title, "created_at": meeting.created_at.isoformat()}
        for meeting in meetings
    ]
    activity.sort(key=lambda item: item["created_at"], reverse=True)
    return {
        "project_id": project_id,
        "tasks": task_totals(tasks),
        "upcoming_tasks": upcoming,
        "meetings": [
            {"id": meeting.id, "title": meeting.title, "created_at": meeting.created_at.isoformat()}
            for meeting in meetings
        ],
        "recent_activity": activity[:10],
    }


@router.get("/projects/{project_id}/reports/weekly")
def weekly_report(
    project_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_project_access(db, user, project_id)
    tasks = db.query(Task).filter(Task.project_id == project_id).all()
    counts = task_totals(tasks)
    risks = [task_summary(task) for task in tasks if task_risk(task.status, task.due_date)[0]]
    next_steps = [task_summary(task) for task in tasks if task.status != "DONE"]
    next_steps.sort(key=lambda task: task["due_date"] or "9999-12-31")
    recent_meetings = (
        db.query(Meeting)
        .filter(Meeting.project_id == project_id, Meeting.created_at >= datetime.now(timezone.utc) - timedelta(days=7))
        .count()
    )
    return {
        "project_id": project_id,
        "period_days": 7,
        "progress": {"completed": counts["done"], "total": counts["total"], "completion_percentage": counts["completion_percentage"]},
        "risks": risks,
        "next_steps": next_steps[:5],
        "meetings_this_week": recent_meetings,
    }


@router.get("/projects/{project_id}/jira-metrics")
def mock_jira_metrics(
    project_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_project_access(db, user, project_id)
    return {"provider": "mock", "open": 12, "in_sprint": 8, "overdue": 2, "sprint_progress": 62}