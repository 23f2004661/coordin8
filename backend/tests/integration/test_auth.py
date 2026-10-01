"""Authentication endpoint tests."""

from fastapi.testclient import TestClient

from app.core.auth import hash_password
from app.db.models import Tenant, User
from app.db.session import SessionLocal
from app.main import app


def create_user(email: str = "member@example.com", active: bool = True) -> User:
    db = SessionLocal()
    tenant = Tenant(name="Test tenant")
    db.add(tenant)
    db.flush()
    user = User(
        tenant_id=tenant.id,
        name="Test User",
        email=email,
        password_hash=hash_password("correct horse battery staple"),
        role="TEAM_MEMBER",
        is_active=active,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return user


def test_login_and_current_user():
    user = create_user()
    client = TestClient(app)

    response = client.post(
        "/api/auth/login",
        json={"email": "MEMBER@example.com", "password": "correct horse battery staple"},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]

    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["id"] == user.id
    assert me.json()["role"] == "TEAM_MEMBER"
    assert me.json()["projects"] == []


def test_inactive_user_cannot_login_or_use_api():
    user = create_user(email="inactive@example.com")
    client = TestClient(app)
    token = client.post(
        "/api/auth/login",
        json={"email": "inactive@example.com", "password": "correct horse battery staple"},
    ).json()["access_token"]

    db = SessionLocal()
    db_user = db.query(User).filter(User.id == user.id).first()
    db_user.is_active = False
    db.commit()
    db.close()

    login = client.post(
        "/api/auth/login",
        json={"email": "inactive@example.com", "password": "correct horse battery staple"},
    )
    assert login.status_code == 401
    headers = {"Authorization": f"Bearer {token}"}
    assert client.get("/api/auth/me", headers=headers).status_code == 401
    assert client.get("/api/projects", headers=headers).status_code == 401