"""Tenant administrator employee and project membership endpoints."""

from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.auth import hash_password, require_project_access, require_roles
from app.db.models import Project, ProjectMember, Task, User
from app.db.session import get_db

router = APIRouter(tags=["administration"])
ADMIN_ROLES = ("ADMIN", "SUPER_ADMIN")
EMPLOYEE_ROLES = {"MANAGER", "TEAM_MEMBER", "ADMIN"}


class EmployeeCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    email: str = Field(min_length=3, max_length=320)
    temporary_password: str = Field(min_length=8, max_length=256)
    role: str
    project_ids: list[str] = []


class EmployeePatch(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    role: str | None = None
    is_active: bool | None = None
    project_ids: list[str] | None = None


class MemberAdd(BaseModel):
    user_id: str
    project_role: str = "MEMBER"


def validate_employee_role(role: str, admin_role: str) -> None:
    if role not in EMPLOYEE_ROLES or (role == "ADMIN" and admin_role != "SUPER_ADMIN"):
        raise HTTPException(status_code=403, detail="Not permitted to assign this role")


def set_projects(db: Session, admin: User, employee: User, project_ids: list[str]) -> None:
    requested = set(project_ids)
    projects = (
        db.query(Project)
        .filter(Project.id.in_(requested), Project.tenant_id == admin.tenant_id)
        .all()
        if requested
        else []
    )
    if len(projects) != len(requested):
        raise HTTPException(status_code=403, detail="Project assignment denied")
    existing = {
        member.project_id: member
        for member in db.query(ProjectMember).filter(ProjectMember.user_id == employee.id).all()
    }
    for project_id, membership in existing.items():
        if project_id not in requested:
            db.delete(membership)
    for project_id in requested - existing.keys():
        db.add(ProjectMember(project_id=project_id, user_id=employee.id, project_role=employee.role))


def employee_payload(db: Session, employee: User) -> dict:
    project_ids = [
        row[0]
        for row in db.query(ProjectMember.project_id)
        .join(Project, Project.id == ProjectMember.project_id)
        .filter(ProjectMember.user_id == employee.id)
        .order_by(Project.name)
        .all()
    ]
    return {
        "id": employee.id,
        "tenant_id": employee.tenant_id,
        "name": employee.name,
        "email": employee.email,
        "role": employee.role,
        "is_active": employee.is_active,
        "project_ids": project_ids,
        "created_at": employee.created_at.isoformat() if employee.created_at else None,
    }


@router.get("/employees")
def list_employees(
    admin: User = Depends(require_roles(*ADMIN_ROLES)),
    db: Session = Depends(get_db),
):
    employees = (
        db.query(User)
        .filter(User.tenant_id == admin.tenant_id)
        .order_by(User.name)
        .all()
    )
    return [employee_payload(db, employee) for employee in employees]


@router.post("/employees", status_code=201)
def create_employee(
    request: EmployeeCreate,
    admin: User = Depends(require_roles(*ADMIN_ROLES)),
    db: Session = Depends(get_db),
):
    validate_employee_role(request.role, admin.role)
    email = request.email.strip().lower()
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=409, detail="Email is already registered")
    employee = User(
        id=str(uuid4()),
        tenant_id=admin.tenant_id,
        name=request.name.strip(),
        email=email,
        password_hash=hash_password(request.temporary_password),
        role=request.role,
        is_active=True,
    )
    db.add(employee)
    db.flush()
    set_projects(db, admin, employee, request.project_ids)
    db.commit()
    db.refresh(employee)
    return employee_payload(db, employee)


@router.patch("/employees/{employee_id}")
def update_employee(
    employee_id: str,
    request: EmployeePatch,
    admin: User = Depends(require_roles(*ADMIN_ROLES)),
    db: Session = Depends(get_db),
):
    employee = (
        db.query(User)
        .filter(User.id == employee_id, User.tenant_id == admin.tenant_id)
        .first()
    )
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    updates = request.model_dump(exclude_unset=True)
    if "role" in updates:
        validate_employee_role(updates["role"], admin.role)
    if "name" in updates and updates["name"] is not None:
        employee.name = updates["name"].strip()
    if "role" in updates and updates["role"] is not None:
        employee.role = updates["role"]
        db.query(ProjectMember).filter(ProjectMember.user_id == employee.id).update(
            {ProjectMember.project_role: employee.role}
        )
    if "is_active" in updates and updates["is_active"] is not None:
        employee.is_active = updates["is_active"]
    if updates.get("project_ids") is not None:
        set_projects(db, admin, employee, updates["project_ids"])
    db.commit()
    db.refresh(employee)
    return employee_payload(db, employee)


@router.get("/projects/{project_id}/members")
def list_project_members(
    project_id: str,
    user: User = Depends(require_roles("ADMIN", "MANAGER", "TEAM_MEMBER", "SUPER_ADMIN")),
    db: Session = Depends(get_db),
):
    require_project_access(db, user, project_id)
    members = (
        db.query(ProjectMember, User)
        .join(User, User.id == ProjectMember.user_id)
        .filter(ProjectMember.project_id == project_id, User.is_active.is_(True))
        .order_by(User.name)
        .all()
    )
    return [
        {
            "user_id": member.user_id,
            "name": employee.name,
            "email": employee.email,
            "role": employee.role,
            "project_role": member.project_role,
            "active_tasks": (
                db.query(Task)
                .filter(
                    Task.project_id == project_id,
                    Task.owner_id == member.user_id,
                    Task.status != "DONE",
                )
                .count()
            ),
        }
        for member, employee in members
    ]


@router.post("/projects/{project_id}/members", status_code=201)
def add_project_member(
    project_id: str,
    request: MemberAdd,
    admin: User = Depends(require_roles(*ADMIN_ROLES)),
    db: Session = Depends(get_db),
):
    project = require_project_access(db, admin, project_id)
    employee = (
        db.query(User)
        .filter(User.id == request.user_id, User.tenant_id == project.tenant_id, User.is_active.is_(True))
        .first()
    )
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    if db.query(ProjectMember).filter_by(project_id=project_id, user_id=employee.id).first():
        raise HTTPException(status_code=409, detail="Employee is already a project member")
    member = ProjectMember(project_id=project_id, user_id=employee.id, project_role=request.project_role)
    db.add(member)
    db.commit()
    return {"user_id": employee.id, "project_id": project_id, "project_role": member.project_role}


@router.delete("/projects/{project_id}/members/{user_id}", status_code=204)
def remove_project_member(
    project_id: str,
    user_id: str,
    admin: User = Depends(require_roles(*ADMIN_ROLES)),
    db: Session = Depends(get_db),
):
    require_project_access(db, admin, project_id)
    member = db.query(ProjectMember).filter_by(project_id=project_id, user_id=user_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Project member not found")
    db.delete(member)
    db.commit()