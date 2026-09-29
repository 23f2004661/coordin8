"""Project workspace and multi-knowledge base manager for Coordin8."""

from datetime import datetime
import json
import os
from pathlib import Path
import re
import shutil
from typing import Any

from app.core.config import get_settings
from app.core.logging import logger
from app.db.models import IntegrationRecord
from app.db.session import SessionLocal
from app.knowledge_base import KnowledgeBase, KnowledgeBaseManager
from app.projects.watcher import SUPPORTED_EXTENSIONS, IGNORED_PATTERNS, ProjectWatcherManager

DEFAULT_HOME_FOLDER = Path(r"C:\Users\ssrin\Desktop\Coordin8 Home")


def slugify(text: str) -> str:
    s = text.lower().strip()
    s = re.sub(r"[^\w\s-]", "", s)
    return re.sub(r"[-\s]+", "_", s)


class ProjectManager:
    """Manages physical project folders, auto-ingestion, and dedicated KnowledgeBases."""

    _instance: "ProjectManager | None" = None

    def __init__(self, home_folder: Path | None = None) -> None:
        self.home_folder = Path(home_folder or DEFAULT_HOME_FOLDER).resolve()
        self.home_folder.mkdir(parents=True, exist_ok=True)

        self.storage_root = Path("./data").resolve()
        self.storage_root.mkdir(parents=True, exist_ok=True)

        self.registry_file = self.storage_root / "projects_registry.json"
        self.kb_manager = KnowledgeBaseManager(base_storage_dir=self.storage_root / "projects_kbs")

        # Watcher
        self.watcher = ProjectWatcherManager(on_file_detected=self._on_watched_file_detected)

        self._projects: dict[str, dict[str, Any]] = {}
        self._unassigned_meetings: list[dict[str, Any]] = []
        self._google_account: dict[str, Any] | None = None
        self._synced_emails: list[dict[str, Any]] = []
        self._load_registry()

    @classmethod
    def get_instance(cls) -> "ProjectManager":
        if cls._instance is None:
            cls._instance = ProjectManager()
        return cls._instance

    def _load_registry(self) -> None:
        if self.registry_file.exists():
            try:
                data = json.loads(self.registry_file.read_text(encoding="utf-8"))
                self._projects = data.get("projects", {})
                self._unassigned_meetings = data.get("unassigned_meetings", [])
                self._google_account = data.get("google_account", None)
                self._synced_emails = data.get("synced_emails", [])
                # Filter out any simulated/demo meetings automatically
                for pid, proj in self._projects.items():
                    if "meetings" in proj and isinstance(proj["meetings"], list):
                        proj["meetings"] = [
                            m for m in proj["meetings"]
                            if not (str(m.get("id", "")).startswith(("sim_", "gcal_sim_")) or
                                    str(m.get("gcalId", "")).startswith(("sim_", "gcal_sim_")))
                        ]
                self._unassigned_meetings = [
                    m for m in self._unassigned_meetings
                    if not (str(m.get("id", "")).startswith(("sim_", "gcal_sim_")) or
                            str(m.get("gcalId", "")).startswith(("sim_", "gcal_sim_")))
                ]
            except Exception as exc:
                logger.error("Error loading project registry: %s", exc)
                self._projects = {}
                self._unassigned_meetings = []
                self._google_account = None
                self._synced_emails = []
        else:
            self._projects = {}
            self._unassigned_meetings = []
            self._google_account = None
            self._synced_emails = []

        # Global deduplication across all projects and unassigned meetings
        seen_keys: set[str] = set()
        for pid, proj in self._projects.items():
            unique_meetings = []
            for m in proj.get("meetings", []):
                key = m.get("gcalId") or m.get("id") or f"{m.get('title')}_{m.get('startTime')}"
                if key and key not in seen_keys:
                    seen_keys.add(key)
                    unique_meetings.append(m)
            proj["meetings"] = unique_meetings

        # Also deduplicate unassigned meetings against projects
        unique_unassigned = []
        for m in self._unassigned_meetings:
            key = m.get("gcalId") or m.get("id") or f"{m.get('title')}_{m.get('startTime')}"
            if key and key not in seen_keys:
                seen_keys.add(key)
                unique_unassigned.append(m)
        self._unassigned_meetings = unique_unassigned

        # 1. Primary source: check SQLite database integrations table
        try:
            with SessionLocal() as db:
                rec = db.query(IntegrationRecord).filter_by(provider="google_calendar").first()
                if rec and rec.is_connected and rec.account_email:
                    extra = rec.get_extra()
                    self._google_account = {
                        "connected": True,
                        "email": rec.account_email,
                        "name": rec.account_name or rec.account_email.split("@")[0],
                        "picture": rec.picture_url or "",
                        "mode": extra.get("mode", "real"),
                        "lastSync": extra.get("lastSync", datetime.now().isoformat()),
                        "syncedCount": extra.get("syncedCount", 0),
                    }
        except Exception as db_exc:
            logger.warning("Could not read integration from db on startup: %s", db_exc)

    def _save_registry(self) -> None:
        try:
            payload = {
                "home_folder": str(self.home_folder),
                "updated_at": datetime.now().isoformat(),
                "projects": self._projects,
                "unassigned_meetings": self._unassigned_meetings,
                "google_account": self._google_account,
                "synced_emails": self._synced_emails,
            }
            self.registry_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        except Exception as exc:
            logger.error("Error saving project registry: %s", exc)

    def get_google_account(self) -> dict[str, Any] | None:
        """Return connected Google account metadata from DB or cache."""
        try:
            with SessionLocal() as db:
                rec = db.query(IntegrationRecord).filter_by(provider="google_calendar").first()
                if rec:
                    if not rec.is_connected:
                        return None
                    extra = rec.get_extra()
                    return {
                        "connected": True,
                        "email": rec.account_email,
                        "name": rec.account_name or (rec.account_email.split("@")[0] if rec.account_email else ""),
                        "picture": rec.picture_url or "",
                        "mode": extra.get("mode", "real"),
                        "lastSync": extra.get("lastSync", datetime.now().isoformat()),
                        "syncedCount": extra.get("syncedCount", 0),
                    }
        except Exception as exc:
            logger.warning("Could not read integration from db: %s", exc)

        return self._google_account

    def set_google_account(self, account_data: dict[str, Any]) -> dict[str, Any]:
        """Save connected Google account metadata to both SQLite database and registry."""
        self._google_account = account_data
        self._save_registry()

        try:
            with SessionLocal() as db:
                rec = db.query(IntegrationRecord).filter_by(provider="google_calendar").first()
                if not rec:
                    rec = IntegrationRecord(provider="google_calendar")
                    db.add(rec)
                rec.account_email = account_data.get("email")
                rec.account_name = account_data.get("name")
                rec.picture_url = account_data.get("picture", "")
                rec.is_connected = 1 if account_data.get("connected", True) else 0
                rec.set_extra({
                    "mode": account_data.get("mode", "real"),
                    "lastSync": account_data.get("lastSync", datetime.now().isoformat()),
                    "syncedCount": account_data.get("syncedCount", 0),
                })
                db.commit()
        except Exception as exc:
            logger.warning("Could not persist integration to db: %s", exc)

        return self._google_account

    def clear_google_account(self) -> None:
        """Clear connected Google account metadata in SQLite database and registry."""
        self._google_account = None
        self._save_registry()

        try:
            with SessionLocal() as db:
                rec = db.query(IntegrationRecord).filter_by(provider="google_calendar").first()
                if rec:
                    rec.is_connected = 0
                    rec.account_email = None
                    db.commit()
        except Exception as exc:
            logger.warning("Could not clear integration from db: %s", exc)

    def start_service(self) -> None:
        """Start the watchdog observer and watch all registered project folders."""
        self.watcher.start()
        for project_id, proj in self._projects.items():
            folder = proj.get("folder_path")
            if folder and os.path.exists(folder):
                self.watcher.watch_project(project_id, folder)
        logger.info(
            "ProjectManager service initialized. Monitoring %d projects in home: %s",
            len(self._projects),
            self.home_folder,
        )

    def stop_service(self) -> None:
        """Stop watcher observer."""
        self.watcher.stop()

    def get_home_folder_info(self) -> dict[str, Any]:
        """Return information about the Home Folder and existing folders inside it."""
        self.home_folder.mkdir(parents=True, exist_ok=True)
        subdirs = []
        try:
            for item in self.home_folder.iterdir():
                if item.is_dir() and item.name not in IGNORED_PATTERNS and not item.name.startswith("."):
                    subdirs.append({
                        "name": item.name,
                        "path": str(item.resolve()),
                    })
        except Exception as exc:
            logger.warning("Error reading home folder subdirs: %s", exc)

        return {
            "home_folder": str(self.home_folder),
            "exists": self.home_folder.exists(),
            "existing_folders": subdirs,
        }

    def get_project_kb(self, project_id: str) -> KnowledgeBase:
        """Retrieve or instantiate the dedicated KnowledgeBase for a project."""
        proj = self._projects.get(project_id)
        if not proj:
            raise KeyError(f"Project '{project_id}' not found")

        kb_id = proj["kb_id"]
        kb_storage = self.storage_root / "projects_kbs" / project_id
        return self.kb_manager.get_or_create(
            kb_id=kb_id,
            storage_dir=kb_storage,
            collection_prefix=f"kb_{project_id.replace('-', '_')}",
        )

    def get_general_kb(self) -> KnowledgeBase:
        """Retrieve or instantiate the global / general KnowledgeBase for unassigned or cross-project artifacts."""
        kb_storage = self.storage_root / "projects_kbs" / "general"
        return self.kb_manager.get_or_create(
            kb_id="general",
            storage_dir=kb_storage,
            collection_prefix="kb_general",
        )

    def create_project(
        self,
        name: str,
        description: str = "",
        category: str = "General",
        color: str = "#6366f1",
        code: str | None = None,
        creation_mode: str = "scratch",
        folder_path: str | None = None,
    ) -> dict[str, Any]:
        """Create a new project workspace either from scratch or from an existing directory."""
        slug = slugify(name)
        project_id = f"proj_{slug}"

        # Determine target folder path
        if creation_mode == "scratch":
            target_path = (self.home_folder / name).resolve()
            target_path.mkdir(parents=True, exist_ok=True)
        else:
            if not folder_path:
                raise ValueError("folder_path is required when creating from an existing folder")
            target_path = Path(folder_path).resolve()
            if not target_path.exists():
                raise FileNotFoundError(f"Existing folder path does not exist: {target_path}")

        # Derive project code
        project_code = (code or "".join([w[0] for w in name.split()[:3]])).upper()

        proj_record = {
            "project_id": project_id,
            "name": name,
            "code": project_code,
            "description": description,
            "category": category,
            "color": color,
            "folder_path": str(target_path),
            "kb_id": f"kb_{slug}",
            "creation_mode": creation_mode,
            "created_at": datetime.now().isoformat(),
            "progress": 0,
            "meetings": [],
            "deliverables": [],
        }

        self._projects[project_id] = proj_record
        self._save_registry()

        # Instantiate dedicated KnowledgeBase
        kb = self.get_project_kb(project_id)

        # Automatically watch folder
        self.watcher.watch_project(project_id, target_path)

        # Automatically scan and index existing files in folder
        ingested_count = self.scan_and_ingest_project_files(project_id)
        proj_record["ingested_count"] = ingested_count

        logger.info(
            "Created project '%s' (mode: %s) at '%s' with %d initial files indexed",
            name,
            creation_mode,
            target_path,
            ingested_count,
        )

        return self.get_project_details(project_id)

    def scan_and_ingest_project_files(self, project_id: str) -> int:
        """Scan physical project folder and ingest all supported files into its KB."""
        proj = self._projects.get(project_id)
        if not proj:
            return 0

        target_path = Path(proj["folder_path"])
        if not target_path.exists():
            return 0

        kb = self.get_project_kb(project_id)
        ingested = 0

        for root, dirs, files in os.walk(target_path):
            # Prune ignored directories in-place
            dirs[:] = [d for d in dirs if d not in IGNORED_PATTERNS and not d.startswith(".")]

            for filename in files:
                if filename.startswith("~$") or filename.startswith("."):
                    continue
                file_path = Path(root) / filename
                if file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
                    try:
                        logger.info("Ingesting initial file '%s' into %s", filename, project_id)
                        kb.ingest_file(file_path, title=file_path.stem)
                        ingested += 1
                    except Exception as exc:
                        logger.warning("Failed to ingest file '%s': %s", file_path, exc)

        return ingested

    def _on_watched_file_detected(self, project_id: str, file_path: Path) -> None:
        """Callback from Watchdog when a new/modified file is detected in a project folder."""
        try:
            kb = self.get_project_kb(project_id)
            logger.info("[Auto-Ingest] Indexing detected file: %s", file_path)
            res = kb.ingest_file(file_path, title=file_path.stem)
            logger.info("[Auto-Ingest] Ingestion complete: %s (status=%s)", file_path.name, res.get("status"))
        except Exception as exc:
            logger.error("[Auto-Ingest] Failed indexing '%s': %s", file_path, exc)

    def get_project_details(self, project_id: str) -> dict[str, Any]:
        """Return project metadata along with real-time physical files and subfolders."""
        proj = self._projects.get(project_id)
        if not proj:
            raise KeyError(f"Project '{project_id}' not found")

        folder_path = Path(proj["folder_path"])
        kb = self.get_project_kb(project_id)

        # Retrieve documents from dedicated KB database
        kb_docs_map = {}
        try:
            for doc in kb.list_documents():
                kb_docs_map[doc["filename"]] = doc
        except Exception:
            pass

        # Scan physical directory structure
        folders_tree = []
        root_files = []

        if folder_path.exists():
            # First, check root files
            try:
                for item in folder_path.iterdir():
                    if item.is_file() and not item.name.startswith((".", "~$")):
                        ext = item.suffix.lower()
                        kb_meta = kb_docs_map.get(item.name, {})
                        size_kb = f"{(item.stat().st_size / 1024):.1f} KB" if item.exists() else "0 KB"
                        mtime = datetime.fromtimestamp(item.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
                        root_files.append({
                            "id": kb_meta.get("document_id") or f"file_{item.name}",
                            "name": item.name,
                            "type": ext.replace(".", "") or "file",
                            "size": size_kb,
                            "status": kb_meta.get("status") or ("INDEXED" if ext in SUPPORTED_EXTENSIONS else "READY"),
                            "updatedAt": mtime,
                            "summary": kb_meta.get("summary") or "Indexed in project knowledge base.",
                        })
            except Exception as exc:
                logger.warning("Error reading root files in %s: %s", folder_path, exc)

            folders_tree.append({
                "id": "f_root",
                "name": "General Documents",
                "path": str(folder_path),
                "files": root_files,
            })

            # Then check subdirectories
            try:
                for sub_item in folder_path.iterdir():
                    if sub_item.is_dir() and sub_item.name not in IGNORED_PATTERNS and not sub_item.name.startswith("."):
                        sub_files = []
                        for sub_f in sub_item.rglob("*"):
                            if sub_f.is_file() and not sub_f.name.startswith((".", "~$")):
                                ext = sub_f.suffix.lower()
                                kb_meta = kb_docs_map.get(sub_f.name, {})
                                size_kb = f"{(sub_f.stat().st_size / 1024):.1f} KB" if sub_f.exists() else "0 KB"
                                mtime = datetime.fromtimestamp(sub_f.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
                                sub_files.append({
                                    "id": kb_meta.get("document_id") or f"file_{sub_f.name}",
                                    "name": sub_f.name,
                                    "type": ext.replace(".", "") or "file",
                                    "size": size_kb,
                                    "status": kb_meta.get("status") or ("INDEXED" if ext in SUPPORTED_EXTENSIONS else "READY"),
                                    "updatedAt": mtime,
                                    "summary": kb_meta.get("summary") or "Indexed in project knowledge base.",
                                })
                        folders_tree.append({
                            "id": f"f_{sub_item.name}",
                            "name": sub_item.name,
                            "path": str(sub_item),
                            "files": sub_files,
                        })
            except Exception as exc:
                logger.warning("Error reading subdirectories in %s: %s", folder_path, exc)

        total_files = sum(len(f["files"]) for f in folders_tree)

        return {
            **proj,
            "total_files": total_files,
            "folders": folders_tree,
        }

    def list_projects(self) -> list[dict[str, Any]]:
        """Return summary of all registered projects with live file counts."""
        self._load_registry()
        result = []
        for project_id in self._projects:
            try:
                details = self.get_project_details(project_id)
                result.append(details)
            except Exception as exc:
                logger.warning("Error generating details for project %s: %s", project_id, exc)
                proj = self._projects[project_id]
                result.append({**proj, "folders": [], "total_files": 0})
        return result

    def delete_project(self, project_id: str, delete_folder: bool = False) -> bool:
        """Remove a project from the registry and optionally delete its physical directory."""
        proj = self._projects.get(project_id)
        if not proj:
            return False

        # Close and delete KB
        try:
            self.kb_manager.delete_kb(proj["kb_id"])
        except Exception:
            pass

        if delete_folder and os.path.exists(proj["folder_path"]):
            shutil.rmtree(proj["folder_path"], ignore_errors=True)

        del self._projects[project_id]
        self._save_registry()
        return True

    def get_unassigned_meetings(self) -> list[dict[str, Any]]:
        """Return all meetings not assigned to any specific project."""
        return self._unassigned_meetings

    def delete_unassigned_meeting(self, meeting_id: str) -> bool:
        """Remove a meeting from the unassigned list."""
        before_count = len(self._unassigned_meetings)
        self._unassigned_meetings = [
            m for m in self._unassigned_meetings
            if m.get("id") != meeting_id and m.get("gcalId") != meeting_id
        ]
        if len(self._unassigned_meetings) < before_count:
            self._save_registry()
            return True
        return False

    def batch_add_unassigned_meetings(self, meetings: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Batch upsert unassigned meetings, removing duplicates across projects."""
        added = []
        for m in meetings:
            res = self.add_meeting(None, m)
            added.append(res)
        return added

    def add_meeting(self, project_id: str | None, meeting_data: dict[str, Any]) -> dict[str, Any]:
        """Add or update a scheduled meeting in a project or unassigned list, removing from any other project."""
        # Ignore any simulated meetings
        m_id = str(meeting_data.get("id", ""))
        g_id = str(meeting_data.get("gcalId", ""))
        if m_id.startswith(("sim_", "gcal_sim_")) or g_id.startswith(("sim_", "gcal_sim_")):
            return meeting_data

        meeting_id = meeting_data.get("id")
        gcal_id = meeting_data.get("gcalId")
        title = meeting_data.get("title")
        start_time = meeting_data.get("startTime")

        def is_match(m):
            if gcal_id and m.get("gcalId") == gcal_id:
                return True
            if meeting_id and m.get("id") == meeting_id:
                return True
            if title and start_time and m.get("title") == title and m.get("startTime") == start_time:
                return True
            return False

        # If project_id is empty or "unassigned", target is unassigned_meetings
        is_unassigned = not project_id or str(project_id).lower() in ("unassigned", "null", "none", "")

        if is_unassigned:
            # Remove from all projects to prevent duplicates
            for pid, p in self._projects.items():
                if "meetings" in p and isinstance(p["meetings"], list):
                    p["meetings"] = [m for m in p["meetings"] if not is_match(m)]

            # Upsert into unassigned_meetings
            meeting_copy = {
                **meeting_data,
                "projectId": None,
                "projectName": None,
                "projectColor": "#94a3b8",
            }
            existing_idx = next((i for i, m in enumerate(self._unassigned_meetings) if is_match(m)), None)
            if existing_idx is not None:
                self._unassigned_meetings[existing_idx] = {**self._unassigned_meetings[existing_idx], **meeting_copy}
            else:
                self._unassigned_meetings.insert(0, meeting_copy)

            self._save_registry()
            return meeting_copy

        target_proj = self._projects.get(project_id)
        if not target_proj:
            raise KeyError(f"Project '{project_id}' not found")

        # Remove from unassigned_meetings
        self._unassigned_meetings = [m for m in self._unassigned_meetings if not is_match(m)]

        # Remove from any other project to prevent cross-project duplicates
        for pid, p in self._projects.items():
            if pid != project_id and "meetings" in p and isinstance(p["meetings"], list):
                p["meetings"] = [m for m in p["meetings"] if not is_match(m)]

        if "meetings" not in target_proj or not isinstance(target_proj["meetings"], list):
            target_proj["meetings"] = []

        # Find existing meeting in target project
        existing_idx = next((i for i, m in enumerate(target_proj["meetings"]) if is_match(m)), None)
        if existing_idx is not None:
            # Update existing meeting in-place
            target_proj["meetings"][existing_idx] = {**target_proj["meetings"][existing_idx], **meeting_data}
        else:
            # Insert at beginning
            target_proj["meetings"].insert(0, meeting_data)

        self._save_registry()
        return meeting_data

    def delete_meeting(self, project_id: str | None, meeting_id: str) -> bool:
        """Remove a meeting from a project or unassigned list by meeting ID or gcalId."""
        if not project_id or str(project_id).lower() in ("unassigned", "null", "none", ""):
            return self.delete_unassigned_meeting(meeting_id)

        proj = self._projects.get(project_id)
        if not proj:
            # If project not found, try unassigned
            return self.delete_unassigned_meeting(meeting_id)

        meetings = proj.get("meetings", [])
        before_count = len(meetings)
        proj["meetings"] = [
            m for m in meetings
            if m.get("id") != meeting_id and m.get("gcalId") != meeting_id
        ]
        if len(proj["meetings"]) < before_count:
            self._save_registry()
            return True
        return False

    def add_deliverable(self, project_id: str, deliverable_data: dict[str, Any]) -> dict[str, Any]:
        """Add a milestone deliverable to a project."""
        proj = self._projects.get(project_id)
        if not proj:
            raise KeyError(f"Project '{project_id}' not found")
        if "deliverables" not in proj:
            proj["deliverables"] = []
        proj["deliverables"].insert(0, deliverable_data)
        self._save_registry()
        return deliverable_data

    def update_deliverable(self, project_id: str, deliverable_id: str, updates: dict[str, Any]) -> dict[str, Any]:
        """Update deliverable status or progress."""
        proj = self._projects.get(project_id)
        if not proj:
            raise KeyError(f"Project '{project_id}' not found")
        found = None
        for item in proj.get("deliverables", []):
            if item.get("id") == deliverable_id:
                item.update(updates)
                found = item
                break
        if not found:
            raise KeyError(f"Deliverable '{deliverable_id}' not found")
        self._save_registry()
        return found

    def upload_meeting_transcript(
        self,
        meeting_id: str,
        filename: str,
        content: bytes,
        target_project_id: str | None = None,
    ) -> dict[str, Any]:
        """Save and index a meeting transcript into the project's KB or general KB."""
        # Find meeting across projects or unassigned
        meeting = None
        current_project_id = None
        for pid, p in self._projects.items():
            for m in p.get("meetings", []):
                if m.get("id") == meeting_id or m.get("gcalId") == meeting_id:
                    meeting = m
                    current_project_id = pid
                    break
            if meeting:
                break

        if not meeting:
            for m in self._unassigned_meetings:
                if m.get("id") == meeting_id or m.get("gcalId") == meeting_id:
                    meeting = m
                    current_project_id = None
                    break

        if not meeting:
            raise KeyError(f"Meeting '{meeting_id}' not found")

        # Determine effective project ID
        effective_project_id = target_project_id if target_project_id is not None else current_project_id
        if effective_project_id in ("unassigned", "null", "none", "", "general"):
            effective_project_id = None

        # Sanitize filename
        safe_filename = Path(filename).name.replace(" ", "_")
        if not any(safe_filename.endswith(ext) for ext in (".txt", ".vtt", ".docx", ".pdf", ".md")):
            safe_filename += ".txt"

        # Determine target folder and KB
        if effective_project_id and effective_project_id in self._projects:
            proj = self._projects[effective_project_id]
            target_dir = Path(proj["folder_path"]) / "transcripts"
            target_dir.mkdir(parents=True, exist_ok=True)
            saved_path = target_dir / safe_filename
            saved_path.write_bytes(content)

            kb = self.get_project_kb(effective_project_id)
            doc_res = kb.ingest_file(saved_path, title=f"Transcript: {meeting.get('title', 'Meeting')}")

            # Reassign meeting to project if changed
            if current_project_id != effective_project_id:
                if current_project_id:
                    self._projects[current_project_id]["meetings"] = [
                        m for m in self._projects[current_project_id].get("meetings", [])
                        if m.get("id") != meeting_id and m.get("gcalId") != meeting_id
                    ]
                else:
                    self._unassigned_meetings = [
                        m for m in self._unassigned_meetings
                        if m.get("id") != meeting_id and m.get("gcalId") != meeting_id
                    ]

                meeting["projectId"] = effective_project_id
                meeting["projectName"] = proj.get("name")
                meeting["projectColor"] = proj.get("color", "#6366f1")

                if "meetings" not in proj:
                    proj["meetings"] = []
                proj["meetings"].insert(0, meeting)
        else:
            # General / Unassigned folder
            general_dir = self.home_folder / "general" / "transcripts"
            general_dir.mkdir(parents=True, exist_ok=True)
            saved_path = general_dir / safe_filename
            saved_path.write_bytes(content)

            general_kb = self.get_general_kb()
            doc_res = general_kb.ingest_file(saved_path, title=f"Transcript: {meeting.get('title', 'Meeting')}")

            # If it was assigned before, move to unassigned
            if current_project_id and current_project_id in self._projects:
                self._projects[current_project_id]["meetings"] = [
                    m for m in self._projects[current_project_id].get("meetings", [])
                    if m.get("id") != meeting_id and m.get("gcalId") != meeting_id
                ]
                meeting["projectId"] = None
                meeting["projectName"] = None
                meeting["projectColor"] = "#94a3b8"
                self._unassigned_meetings.insert(0, meeting)

        # Update meeting metadata
        meeting["hasTranscript"] = True
        meeting["transcriptFile"] = safe_filename
        meeting["transcriptPath"] = str(saved_path)
        meeting["transcriptDocId"] = doc_res.get("document_id")
        meeting["prepDoc"] = safe_filename

        self._save_registry()
        return {
            "success": True,
            "meeting": meeting,
            "document": doc_res,
            "project_id": effective_project_id or "general",
            "saved_path": str(saved_path),
        }

    def get_synced_emails(self) -> list[dict[str, Any]]:
        """Return all synchronized email messages."""
        return self._synced_emails

    def save_synced_emails(self, emails: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Upsert synchronized emails in the registry."""
        existing_ids = {e.get("id") for e in self._synced_emails if e.get("id")}
        for email in emails:
            e_id = email.get("id")
            if not e_id:
                continue
            if e_id not in existing_ids:
                self._synced_emails.insert(0, email)
                existing_ids.add(e_id)
            else:
                for idx, existing in enumerate(self._synced_emails):
                    if existing.get("id") == e_id:
                        self._synced_emails[idx] = {**existing, **email}
                        break
        self._save_registry()
        return self._synced_emails
