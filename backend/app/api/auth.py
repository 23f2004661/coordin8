"""Login and authenticated-user endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.auth import create_access_token, get_current_user, verify_password
from app.db.models import Project, ProjectMember, Tenant, User
from app.db.session import get_db

router = APIRouter(prefix="/auth", tags=["authentication"])


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    email = request.email.strip().lower()
    user = db.query(User).filter(func.lower(User.email) == email).first()
    if not user or not user.is_active or not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    tenant = db.query(Tenant).filter(Tenant.id == user.tenant_id, Tenant.status == "ACTIVE").first()
    if not tenant:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return {"access_token": create_access_token(user), "token_type": "bearer"}


@router.get("/me")
def current_user(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tenant = db.query(Tenant).filter(Tenant.id == user.tenant_id).first()
    projects_query = db.query(Project).filter(Project.tenant_id == user.tenant_id)
    if user.role not in {"SUPER_ADMIN", "ADMIN"}:
        projects_query = projects_query.join(ProjectMember).filter(ProjectMember.user_id == user.id)
    projects = projects_query.order_by(Project.name).all()
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "tenant": {"id": tenant.id, "name": tenant.name} if tenant else None,
        "projects": [
            {"id": project.id, "name": project.name, "status": project.status}
            for project in projects
        ],
    }