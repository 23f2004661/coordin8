"""SQLAlchemy ORM models for metadata, jobs, chunks, and assets."""

from datetime import datetime, timezone
import json
from typing import Any
import uuid
from sqlalchemy import Boolean, Column, Date, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from app.db.session import Base


class DocumentRecord(Base):
    """Stores registered documents and high-level processing status."""
    __tablename__ = "documents"

    document_id = Column(String(64), primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    file_type = Column(String(32), nullable=False)
    file_size_bytes = Column(Integer, default=0)
    source_hash = Column(String(64), unique=True, index=True, nullable=False)
    status = Column(String(32), default="REGISTERED", index=True)
    summary = Column(Text, nullable=True)
    source_path = Column(String(512), nullable=False)
    normalized_markdown_path = Column(String(512), nullable=True)
    extra_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def get_extra(self) -> dict[str, Any]:
        return json.loads(self.extra_json) if self.extra_json else {}

    def set_extra(self, data: dict[str, Any]) -> None:
        self.extra_json = json.dumps(data)


class JobRecord(Base):
    """Tracks processing job pipeline states matching Section 16 of ProjectDetails.md."""
    __tablename__ = "jobs"

    job_id = Column(String(64), primary_key=True, index=True)
    document_id = Column(String(64), index=True, nullable=False)
    status = Column(String(32), default="REGISTERED", index=True)
    stage = Column(String(32), default="REGISTERED")
    progress = Column(Float, default=0.0)  # 0.0 to 1.0
    error_message = Column(Text, nullable=True)
    processing_duration = Column(Float, default=0.0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class ChunkRecord(Base):
    """Relational catalog of document chunks and structural locations."""
    __tablename__ = "chunks"

    chunk_id = Column(String(64), primary_key=True, index=True)
    document_id = Column(String(64), index=True, nullable=False)
    parent_id = Column(String(64), nullable=True)
    section_id = Column(String(64), nullable=True)
    content_type = Column(String(32), default="text")
    content = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    token_count = Column(Integer, default=0)
    page_number = Column(Integer, nullable=True)
    slide_number = Column(Integer, nullable=True)
    sheet_name = Column(String(128), nullable=True)
    source_range = Column(String(64), nullable=True)
    metadata_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class AssetRecord(Base):
    """Metadata catalog of visual and tabular extracted assets."""
    __tablename__ = "assets"

    asset_id = Column(String(64), primary_key=True, index=True)
    document_id = Column(String(64), index=True, nullable=False)
    asset_type = Column(String(32), nullable=False)
    file_path = Column(String(512), nullable=False)
    caption = Column(Text, nullable=True)
    visual_description = Column(Text, nullable=True)
    retrieval_description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    status = Column(String(32), nullable=False, default="ACTIVE")
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(320), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(32), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))


class Project(Base):
    __tablename__ = "projects"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    client = Column(String(255), nullable=True)
    status = Column(String(32), nullable=False, default="ACTIVE")
    kb_id = Column(String(36), nullable=False, unique=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))


class ProjectMember(Base):
    __tablename__ = "project_members"
    __table_args__ = (UniqueConstraint("project_id", "user_id", name="uq_project_member"),)

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    project_role = Column(String(32), nullable=False, default="MEMBER")
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))


class Task(Base):
    __tablename__ = "tasks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    owner_id = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)
    due_date = Column(Date, nullable=True)
    status = Column(String(32), nullable=False, default="BACKLOG")
    risk = Column(Boolean, nullable=False, default=False)
    risk_reason = Column(String(500), nullable=True)
    source_document_id = Column(String(64), nullable=True)
    source_chunk_id = Column(String(64), nullable=True)
    source_meeting_id = Column(String(36), nullable=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class Meeting(Base):
    __tablename__ = "meetings"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    transcript_text = Column(Text, nullable=False)
    transcript_document_id = Column(String(64), nullable=True)
    summary = Column(Text, nullable=True)
    decisions_json = Column(Text, nullable=True)
    created_by = Column(String(36), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))


class ActionItem(Base):
    __tablename__ = "action_items"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    meeting_id = Column(String(36), ForeignKey("meetings.id"), nullable=False, index=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False, index=True)
    text = Column(Text, nullable=False)
    owner_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    owner_label = Column(String(255), nullable=True)
    due_date = Column(Date, nullable=True)
    task_id = Column(String(36), ForeignKey("tasks.id"), nullable=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
