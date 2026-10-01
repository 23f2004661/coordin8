"""Seed a local Coordin8 demo tenant and isolated projects."""

import sys
from datetime import date, timedelta
from pathlib import Path
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.auth import hash_password
from app.db.models import ActionItem, Meeting, Project, ProjectMember, Task, Tenant, User
from app.db.session import SessionLocal, init_db


DEMO_USERS = [
    ("Coordin8 Admin", "admin@coordin8.local", "AdminDev!2026", "ADMIN"),
    ("Anjali Gupta", "manager@coordin8.local", "ManagerDev!2026", "MANAGER"),
    ("Tarang Jhaveri", "analyst@coordin8.local", "AnalystDev!2026", "TEAM_MEMBER"),
]


def main() -> None:
    init_db()
    db = SessionLocal()
    try:
        tenant = db.query(Tenant).filter(Tenant.name == "Acme Consulting").first()
        if not tenant:
            tenant = Tenant(name="Acme Consulting", status="ACTIVE")
            db.add(tenant)
            db.flush()

        users: dict[str, User] = {}
        for name, email, password, role in DEMO_USERS:
            user = db.query(User).filter(User.email == email).first()
            if not user:
                user = User(
                    id=str(uuid4()),
                    tenant_id=tenant.id,
                    name=name,
                    email=email,
                    password_hash=hash_password(password),
                    role=role,
                    is_active=True,
                )
                db.add(user)
                db.flush()
            users[email] = user

        projects: dict[str, Project] = {}
        for name, client in (
            ("Q3 Onboarding", "Acme Consulting"),
            ("ACME Client Transformation", "ACME"),
        ):
            project = (
                db.query(Project)
                .filter(Project.tenant_id == tenant.id, Project.name == name)
                .first()
            )
            if not project:
                project_id = str(uuid4())
                project = Project(
                    id=project_id,
                    tenant_id=tenant.id,
                    name=name,
                    client=client,
                    status="ACTIVE",
                    kb_id=project_id,
                )
                db.add(project)
                db.flush()
            projects[name] = project

        q3 = projects["Q3 Onboarding"]
        for email in ("manager@coordin8.local", "analyst@coordin8.local"):
            user = users[email]
            member = db.query(ProjectMember).filter_by(project_id=q3.id, user_id=user.id).first()
            if not member:
                db.add(ProjectMember(project_id=q3.id, user_id=user.id, project_role=user.role))

        onboarding_tasks = (
            ("Complete onboarding tracker", users["analyst@coordin8.local"], date.today() - timedelta(days=1), "IN_PROGRESS"),
            ("Validate client access list", users["manager@coordin8.local"], date.today() + timedelta(days=1), "BACKLOG"),
            ("Prepare kickoff summary", users["analyst@coordin8.local"], date.today() + timedelta(days=8), "REVIEW"),
            ("Confirm training schedule", users["manager@coordin8.local"], None, "DONE"),
        )
        for title, owner, due_date, status in onboarding_tasks:
            if not db.query(Task).filter_by(project_id=q3.id, title=title).first():
                db.add(
                    Task(
                        id=str(uuid4()),
                        project_id=q3.id,
                        title=title,
                        owner_id=owner.id,
                        due_date=due_date,
                        status=status,
                    )
                )
        client_project = projects["ACME Client Transformation"]
        if not db.query(Task).filter_by(project_id=client_project.id).first():
            db.add(
                Task(
                    id=str(uuid4()),
                    project_id=client_project.id,
                    title="Draft transformation roadmap",
                    owner_id=None,
                    due_date=date.today() + timedelta(days=14),
                    status="BACKLOG",
                )
            )

        meeting = (
            db.query(Meeting)
            .filter_by(project_id=q3.id, title="Q3 Onboarding Kickoff")
            .first()
        )
        if not meeting:
            meeting = Meeting(
                id=str(uuid4()),
                project_id=q3.id,
                title="Q3 Onboarding Kickoff",
                transcript_text="Anjali: We will complete the client tracker this week. Tarang: I will validate the onboarding checklist by Friday.",
                summary="The team reviewed onboarding milestones and owners.",
                decisions_json='["Use the shared tracker as the source of truth"]',
                created_by=users["manager@coordin8.local"].id,
            )
            db.add(meeting)
            db.flush()
            db.add(
                ActionItem(
                    id=str(uuid4()),
                    meeting_id=meeting.id,
                    project_id=q3.id,
                    text="Validate the onboarding checklist",
                    owner_id=users["analyst@coordin8.local"].id,
                    owner_label="Tarang Jhaveri",
                    due_date=date.today() + timedelta(days=4),
                )
            )

        db.commit()
        print("Seeded Acme Consulting demo data.")
        for _, email, password, _ in DEMO_USERS:
            print(f"{email} / {password}")
        print("manager@coordin8.local is assigned only to Q3 Onboarding.")
    finally:
        db.close()


if __name__ == "__main__":
    main()