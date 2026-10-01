"""Project authorization must run before project data or retrieval is accessed."""

from datetime import date, timedelta
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.core.auth import create_access_token, hash_password
from app.db.models import ActionItem, Meeting, Project, ProjectMember, Task, Tenant, User
from app.db.session import SessionLocal
from app.main import app


def create_identity(
    role: str = "TEAM_MEMBER",
    tenant_name: str = "Tenant A",
    tenant_id: str | None = None,
) -> tuple[str, str, str]:
    db = SessionLocal()
    tenant = db.get(Tenant, tenant_id) if tenant_id else Tenant(name=tenant_name)
    if not tenant_id:
        db.add(tenant)
        db.flush()
    user = User(
        tenant_id=tenant.id,
        name="Project User",
        email=f"{uuid4()}@example.com",
        password_hash=hash_password("project-test-password"),
        role=role,
        is_active=True,
    )
    db.add(user)
    db.commit()
    token = create_access_token(user)
    user_id = user.id
    tenant_id = tenant.id
    db.close()
    return user_id, tenant_id, token


def create_project(tenant_id: str, member_id: str | None = None) -> str:
    db = SessionLocal()
    project_id = str(uuid4())
    db.add(
        Project(
            id=project_id,
            tenant_id=tenant_id,
            name="Confidential project",
            status="ACTIVE",
            kb_id=project_id,
        )
    )
    if member_id:
        db.add(ProjectMember(project_id=project_id, user_id=member_id, project_role="MEMBER"))
    db.commit()
    db.close()
    return project_id


def create_tenant(name: str) -> str:
    db = SessionLocal()
    tenant = Tenant(name=name)
    db.add(tenant)
    db.commit()
    tenant_id = tenant.id
    db.close()
    return tenant_id


def test_projects_require_authentication():
    assert TestClient(app).get("/api/projects").status_code == 401


def test_member_cannot_read_unassigned_project_or_trigger_chat(monkeypatch):
    _, tenant_id, token = create_identity()
    other_user_id, _, _ = create_identity(tenant_id=tenant_id)
    project_id = create_project(tenant_id=tenant_id, member_id=other_user_id)
    from app.api import projects as project_api

    def retrieval_must_not_run(*args, **kwargs):
        pytest.fail("Unauthorized request reached the KnowledgeBase")

    monkeypatch.setattr(project_api.kb_manager, "get_or_create", retrieval_must_not_run)
    client = TestClient(app)
    headers = {"Authorization": f"Bearer {token}"}

    assert client.get(f"/api/projects/{project_id}/documents", headers=headers).status_code == 403
    chat = client.post(
        f"/api/projects/{project_id}/chat",
        json={"message": "What is confidential?"},
        headers=headers,
    )
    assert chat.status_code == 403


def test_manager_cannot_access_another_tenants_project():
    _, _, token = create_identity(role="MANAGER", tenant_name="Tenant A")
    other_tenant = create_tenant("Tenant B")
    project_id = create_project(other_tenant)

    response = TestClient(app).get(
        f"/api/projects/{project_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403


def test_admin_cannot_access_another_tenants_project():
    _, _, token = create_identity(role="ADMIN", tenant_name="Tenant A")
    other_tenant = create_tenant("Tenant B")
    project_id = create_project(other_tenant)

    response = TestClient(app).get(
        f"/api/projects/{project_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403


def test_system_admin_must_use_project_scoped_rag():
    _, _, token = create_identity(role="SUPER_ADMIN")
    response = TestClient(app).post(
        "/api/answer",
        json={"query": "What is in the knowledge base?"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403


def test_rag_chat_isolated_to_authorized_project(monkeypatch, tmp_path):
    user_id, tenant_id, token = create_identity()
    project_a = create_project(tenant_id)
    project_b = create_project(tenant_id)
    db = SessionLocal()
    db.add(ProjectMember(project_id=project_a, user_id=user_id, project_role="MEMBER"))
    db.commit()
    db.close()

    from app.api import projects as project_api
    from app.knowledge_base import KnowledgeBaseManager

    isolated_manager = KnowledgeBaseManager(base_storage_dir=tmp_path)
    kb_a = isolated_manager.get_or_create(project_a)
    kb_b = isolated_manager.get_or_create(project_b)
    kb_a.ingest_bytes(
        b"Project A confidential information: Alpha",
        filename="project-a.txt",
        title="Project A",
    )
    kb_b.ingest_bytes(
        b"Project B confidential information: Beta",
        filename="project-b.txt",
        title="Project B",
    )
    accessed_kbs = []
    original_get_or_create = isolated_manager.get_or_create

    def get_kb(kb_id):
        accessed_kbs.append(kb_id)
        return original_get_or_create(kb_id)

    monkeypatch.setattr(project_api.kb_manager, "get_or_create", get_kb)
    monkeypatch.setattr(project_api.llm_client, "generate_answer", lambda _query, context: context)
    try:
        client = TestClient(app)
        headers = {"Authorization": f"Bearer {token}"}
        answer = client.post(
            f"/api/projects/{project_a}/chat",
            json={"message": "What confidential information is available?"},
            headers=headers,
        )
        assert answer.status_code == 200
        assert "Alpha" in answer.json()["answer"]
        assert "Beta" not in answer.json()["answer"]

        denied = client.post(
            f"/api/projects/{project_b}/chat",
            json={"message": "What confidential information is available?"},
            headers=headers,
        )
        assert denied.status_code == 403
        assert accessed_kbs == [project_a]
    finally:
        isolated_manager.close_all()


def test_chat_surfaces_llm_unavailable_instead_of_fallback(monkeypatch):
    manager_id, tenant_id, token = create_identity(role="MANAGER")
    project_id = create_project(tenant_id, member_id=manager_id)
    from app.api import projects as project_api

    class EmptyContextKB:
        def query_context(self, _query):
            return {"formatted_context": "evidence", "evidence_units": []}

    monkeypatch.setattr(project_api.kb_manager, "get_or_create", lambda _kb_id: EmptyContextKB())
    monkeypatch.setattr(
        project_api.llm_client,
        "generate_answer",
        lambda *_args: (_ for _ in ()).throw(RuntimeError("AI service is currently unavailable. Please try again.")),
    )
    response = TestClient(app).post(
        f"/api/projects/{project_id}/chat",
        json={"message": "What is blocking this project?"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 502
    assert response.json()["detail"] == "AI service is currently unavailable. Please try again."


def test_mom_surfaces_llm_unavailable(monkeypatch):
    manager_id, tenant_id, token = create_identity(role="MANAGER")
    project_id = create_project(tenant_id, member_id=manager_id)
    db = SessionLocal()
    meeting = Meeting(
        id=str(uuid4()),
        project_id=project_id,
        title="Weekly sync",
        transcript_text="John will complete the tracker.",
        created_by=manager_id,
    )
    db.add(meeting)
    db.commit()
    meeting_id = meeting.id
    db.close()

    from app.api import meetings as meeting_api

    monkeypatch.setattr(
        meeting_api.llm_client,
        "generate_completion",
        lambda *_args: (_ for _ in ()).throw(RuntimeError("AI service is currently unavailable. Please try again.")),
    )
    response = TestClient(app).post(
        f"/api/meetings/{meeting_id}/generate-mom",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 502
    assert response.json()["detail"] == "AI service is currently unavailable. Please try again."


def test_team_member_cannot_create_employee_or_task():
    _, tenant_id, token = create_identity()
    project_id = create_project(tenant_id)
    headers = {"Authorization": f"Bearer {token}"}
    client = TestClient(app)

    employee = client.post(
        "/api/employees",
        json={
            "name": "New Employee",
            "email": "new@example.com",
            "temporary_password": "temporary-password",
            "role": "TEAM_MEMBER",
        },
        headers=headers,
    )
    task = client.post(
        f"/api/projects/{project_id}/tasks",
        json={"title": "Unauthorized task"},
        headers=headers,
    )
    upload = client.post(
        f"/api/projects/{project_id}/documents",
        files={"file": ("notes.txt", b"project notes")},
        headers=headers,
    )
    global_documents = client.get("/api/documents", headers=headers)
    global_answer = client.post("/api/answer", json={"query": "anything"}, headers=headers)
    assert employee.status_code == 403
    assert task.status_code == 403
    assert upload.status_code == 403
    assert global_documents.status_code == 403
    assert global_answer.status_code == 403


def test_admin_can_create_employee_without_exposing_password_hash():
    _, _, token = create_identity(role="ADMIN")
    response = TestClient(app).post(
        "/api/employees",
        json={
            "name": "Anjali Gupta",
            "email": "anjali@example.com",
            "temporary_password": "temporary-password",
            "role": "MANAGER",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    assert response.json()["role"] == "MANAGER"
    assert "password_hash" not in response.json()


def test_manager_task_risk_and_member_update_permissions():
    manager_id, tenant_id, _ = create_identity(role="MANAGER")
    member_id, _, member_token = create_identity(tenant_id=tenant_id)
    project_id = create_project(tenant_id, member_id=manager_id)
    db = SessionLocal()
    db.add(ProjectMember(project_id=project_id, user_id=member_id, project_role="MEMBER"))
    task = Task(
        id=str(uuid4()),
        project_id=project_id,
        title="Reconcile the tracker",
        owner_id=member_id,
        due_date=date.today() - timedelta(days=1),
        status="BACKLOG",
    )
    db.add(task)
    db.commit()
    task_id = task.id
    db.close()

    client = TestClient(app)
    member_headers = {"Authorization": f"Bearer {member_token}"}
    tasks = client.get(f"/api/projects/{project_id}/tasks", headers=member_headers)
    assert tasks.status_code == 200
    assert tasks.json()[0]["risk"] is True
    assert tasks.json()[0]["risk_reason"] == "Task is overdue"

    status_update = client.patch(
        f"/api/tasks/{task_id}",
        json={"status": "IN_PROGRESS"},
        headers=member_headers,
    )
    assert status_update.status_code == 200
    denied_update = client.patch(
        f"/api/tasks/{task_id}",
        json={"title": "Changed by member"},
        headers=member_headers,
    )
    assert denied_update.status_code == 403
    assert client.post(
        f"/api/projects/{project_id}/tasks",
        json={"title": "Manager task"},
        headers=member_headers,
    ).status_code == 403


def test_meeting_mom_action_item_conversion_keeps_provenance(monkeypatch):
    manager_id, tenant_id, token = create_identity(role="MANAGER")
    project_id = create_project(tenant_id, member_id=manager_id)
    db = SessionLocal()
    meeting = Meeting(
        id=str(uuid4()),
        project_id=project_id,
        title="Weekly sync",
        transcript_text="Project User will finish the tracker by 2026-10-05.",
        transcript_document_id="doc-transcript-1",
        created_by=manager_id,
    )
    db.add(meeting)
    db.commit()
    meeting_id = meeting.id
    db.close()

    from app.api import meetings as meeting_api

    generated = {
        "summary": "The tracker is the next priority.",
        "decisions": ["Use the shared tracker"],
        "action_items": [
            {"text": "Finish the tracker", "owner": "Project User", "due_date": "2026-10-05"}
        ],
    }
    monkeypatch.setattr(meeting_api.llm_client, "generate_completion", lambda *_args: __import__("json").dumps(generated))
    client = TestClient(app)
    headers = {"Authorization": f"Bearer {token}"}
    mom = client.post(f"/api/meetings/{meeting_id}/generate-mom", headers=headers)
    assert mom.status_code == 200
    assert mom.json()["action_items"][0]["owner_id"] == manager_id
    action_id = mom.json()["action_items"][0]["id"]

    converted = client.post(f"/api/action-items/{action_id}/tasks", headers=headers)
    assert converted.status_code == 201
    assert converted.json()["source_meeting_id"] == meeting_id
    assert converted.json()["source_document_id"] == "doc-transcript-1"

    regenerated = client.post(f"/api/meetings/{meeting_id}/generate-mom", headers=headers)
    assert regenerated.status_code == 200
    assert regenerated.json()["action_items"][0]["task_id"] == converted.json()["id"]
