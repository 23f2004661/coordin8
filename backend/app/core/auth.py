"""Authentication and project authorization helpers."""

import base64
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.models import Project, ProjectMember, Tenant, User
from app.db.session import get_db

bearer_scheme = HTTPBearer(auto_error=False)
VALID_ROLES = {"SUPER_ADMIN", "ADMIN", "MANAGER", "TEAM_MEMBER"}


def hash_password(password: str) -> str:
    """Hash a password with scrypt and a cryptographically random salt."""
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode("utf-8"), salt=salt, n=2**14, r=8, p=1)
    encode = lambda value: base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")
    return f"scrypt$16384$8$1${encode(salt)}${encode(digest)}"


def verify_password(password: str, encoded_hash: str) -> bool:
    try:
        algorithm, n, r, p, salt_text, digest_text = encoded_hash.split("$")
        if algorithm != "scrypt":
            return False
        decode = lambda value: base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))
        salt = decode(salt_text)
        expected = decode(digest_text)
        actual = hashlib.scrypt(
            password.encode("utf-8"), salt=salt, n=int(n), r=int(r), p=int(p), dklen=len(expected)
        )
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False


def create_access_token(user: User) -> str:
    settings = get_settings()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    return jwt.encode(
        {
            "user_id": user.id,
            "tenant_id": user.tenant_id,
            "role": user.role,
            "exp": expires_at,
        },
        settings.secret_key,
        algorithm="HS256",
    )


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Authentication required", headers={"WWW-Authenticate": "Bearer"})
    try:
        claims = jwt.decode(credentials.credentials, get_settings().secret_key, algorithms=["HS256"])
        user_id = claims.get("user_id")
        tenant_id = claims.get("tenant_id")
        role = claims.get("role")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token", headers={"WWW-Authenticate": "Bearer"}) from None

    user = db.query(User).filter(User.id == user_id).first()
    if (
        not user
        or not user.is_active
        or user.tenant_id != tenant_id
        or user.role != role
        or user.role not in VALID_ROLES
    ):
        raise HTTPException(status_code=401, detail="Invalid or inactive account", headers={"WWW-Authenticate": "Bearer"})
    tenant = db.query(Tenant).filter(Tenant.id == user.tenant_id).first()
    if not tenant or tenant.status != "ACTIVE":
        raise HTTPException(status_code=401, detail="Inactive tenant", headers={"WWW-Authenticate": "Bearer"})
    return user


def require_roles(*roles: str):
    def dependency(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user

    return dependency


def deny_unscoped_knowledge_access(user: User = Depends(get_current_user)) -> None:
    raise HTTPException(status_code=403, detail="Use an authorized project-scoped knowledge endpoint")


def require_project_access(db: Session, user: User, project_id: str) -> Project:
    """Return an accessible project or fail before any project-scoped operation."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project or project.tenant_id != user.tenant_id:
        raise HTTPException(status_code=403, detail="Project access denied")
    if user.role not in VALID_ROLES:
        raise HTTPException(status_code=403, detail="Project access denied")
    if user.role not in {"SUPER_ADMIN", "ADMIN"}:
        membership = (
            db.query(ProjectMember)
            .filter(ProjectMember.project_id == project.id, ProjectMember.user_id == user.id)
            .first()
        )
        if not membership:
            raise HTTPException(status_code=403, detail="Project access denied")
    return project