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
from app.projects.ai_deliverables import (
    run_ai_deliverables_audit,
    classify_email_context,
    breakdown_deliverable_to_tasks,
)
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
                    proj.setdefault("project_type", "internal")
                    proj.setdefault("client_name", "")
                    proj.setdefault("client_email", "")
                    proj.setdefault("problem_statement", proj.get("description", ""))
                    proj.setdefault("overall_context", "")
                    proj.setdefault("deliverables", [])
                    proj.setdefault("discovered_deliverables", [])
                    proj.setdefault("ai_analysis", None)
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

        # 2. Auto-discover physical project folders in Coordin8 Home
        if self.home_folder.exists():
            for folder in self.home_folder.iterdir():
                if (
                    folder.is_dir()
                    and folder.name not in IGNORED_PATTERNS
                    and not folder.name.startswith(".")
                    and folder.name.lower() != "general"
                ):
                    slug = slugify(folder.name)
                    pid = f"proj_{slug}"
                    already_registered = False
                    for existing_pid, existing_proj in self._projects.items():
                        try:
                            if existing_pid == pid or Path(existing_proj.get("folder_path", "")).resolve() == folder.resolve():
                                already_registered = True
                                break
                        except Exception:
                            pass
                    if not already_registered:
                        logger.info("Auto-discovered project folder in home: %s (id: %s)", folder.name, pid)
                        code = "".join([w[0] for w in folder.name.split()[:3]]).upper()
                        self._projects[pid] = {
                            "project_id": pid,
                            "name": folder.name,
                            "code": code,
                            "description": f"Workspace for {folder.name}",
                            "category": "General",
                            "color": "#10b981" if "robot" in folder.name.lower() else "#6366f1",
                            "folder_path": str(folder.resolve()),
                            "kb_id": f"kb_{slug}",
                            "creation_mode": "existing",
                            "created_at": datetime.now().isoformat(),
                            "progress": 0,
                            "project_type": "internal",
                            "client_name": "",
                            "client_email": "",
                            "problem_statement": "",
                            "overall_context": "",
                            "meetings": [],
                            "deliverables": [],
                            "discovered_deliverables": [],
                            "ai_analysis": None,
                        }

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
        project_type: str = "internal",
        client_name: str = "",
        client_email: str = "",
        problem_statement: str = "",
        overall_context: str = "",
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
            "project_type": project_type,
            "client_name": client_name,
            "client_email": client_email,
            "problem_statement": problem_statement or description,
            "overall_context": overall_context,
            "meetings": [],
            "deliverables": [],
            "discovered_deliverables": [],
            "ai_analysis": None,
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
                            "path": str(item.resolve()),
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
                                    "path": str(sub_f.resolve()),
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
        project_emails = [e for e in self._synced_emails if e.get("projectId") == project_id]

        return {
            **proj,
            "total_files": total_files,
            "folders": folders_tree,
            "emails": project_emails,
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
        if not deliverable_data.get("id"):
            deliverable_data["id"] = f"del_{int(datetime.now().timestamp() * 1000)}"
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

    def delete_deliverable(self, project_id: str, deliverable_id: str) -> bool:
        """Remove a deliverable from a project."""
        proj = self._projects.get(project_id)
        if not proj:
            raise KeyError(f"Project '{project_id}' not found")
        delivs = proj.get("deliverables", [])
        before = len(delivs)
        proj["deliverables"] = [d for d in delivs if d.get("id") != deliverable_id]
        if len(proj["deliverables"]) < before:
            self._save_registry()
            return True
        return False

    def breakdown_deliverable(self, project_id: str, deliverable_id: str) -> list[dict[str, Any]]:
        """Decompose a deliverable into operational tasks via AI and attach to deliverable."""
        proj = self._projects.get(project_id)
        if not proj:
            raise KeyError(f"Project '{project_id}' not found")
        found = None
        for item in proj.get("deliverables", []):
            if item.get("id") == deliverable_id:
                found = item
                break
        if not found:
            raise KeyError(f"Deliverable '{deliverable_id}' not found")

        tasks = breakdown_deliverable_to_tasks(proj, found)
        found["tasks"] = tasks
        self._save_registry()
        return tasks

    def get_project_tasks(self, project_id: str) -> list[dict[str, Any]]:
        """Retrieve all execution tasks across deliverables for a project."""
        proj = self._projects.get(project_id)
        if not proj:
            raise KeyError(f"Project '{project_id}' not found")
        all_tasks = []
        for d in proj.get("deliverables", []):
            deliv_id = d.get("id")
            deliv_title = d.get("title")
            for t in d.get("tasks", []):
                task_copy = dict(t)
                task_copy["deliverableId"] = deliv_id
                task_copy["deliverableTitle"] = deliv_title
                all_tasks.append(task_copy)
        return all_tasks

    def update_task(self, project_id: str, deliverable_id: str, task_id: str, updates: dict[str, Any]) -> dict[str, Any]:
        """Update status or attributes of a specific execution task."""
        proj = self._projects.get(project_id)
        if not proj:
            raise KeyError(f"Project '{project_id}' not found")
        for d in proj.get("deliverables", []):
            if d.get("id") == deliverable_id:
                for t in d.get("tasks", []):
                    if t.get("id") == task_id:
                        t.update(updates)
                        self._save_registry()
                        return t
        raise KeyError(f"Task '{task_id}' not found in deliverable '{deliverable_id}'")

    def update_project(self, project_id: str, updates: dict[str, Any]) -> dict[str, Any]:
        """Update project settings, problem statement, client details, or context."""
        proj = self._projects.get(project_id)
        if not proj:
            raise KeyError(f"Project '{project_id}' not found")

        allowed_fields = [
            "name", "description", "category", "color", "code",
            "project_type", "client_name", "client_email",
            "problem_statement", "overall_context", "progress",
        ]
        for field in allowed_fields:
            if field in updates:
                proj[field] = updates[field]

        self._save_registry()
        return self.get_project_details(project_id)

    def accept_discovered_deliverable(self, project_id: str, candidate_data: dict[str, Any]) -> dict[str, Any]:
        """Add an AI-discovered candidate deliverable into official project deliverables."""
        proj = self._projects.get(project_id)
        if not proj:
            raise KeyError(f"Project '{project_id}' not found")

        new_del = {
            "id": f"del_{int(datetime.now().timestamp() * 1000)}",
            "title": candidate_data.get("title", "New Deliverable"),
            "description": candidate_data.get("description", ""),
            "dueDate": candidate_data.get("suggestedDueDate") or candidate_data.get("dueDate") or datetime.now().strftime("%Y-%m-%d"),
            "status": "pending",
            "priority": candidate_data.get("priority", "medium"),
            "progress": 0,
            "owner": candidate_data.get("owner", "Team"),
            "source": candidate_data.get("source", "ai_discovered"),
            "sourceEvidence": candidate_data.get("sourceEvidence", ""),
            "evidenceFiles": candidate_data.get("evidenceFiles", []),
        }

        if "deliverables" not in proj:
            proj["deliverables"] = []
        proj["deliverables"].insert(0, new_del)

        # Remove from discovered_deliverables
        cand_title = candidate_data.get("title")
        proj["discovered_deliverables"] = [
            d for d in proj.get("discovered_deliverables", [])
            if d.get("title") != cand_title
        ]

        self._save_registry()
        return new_del

    def dismiss_discovered_deliverable(self, project_id: str, title: str) -> bool:
        """Dismiss an AI-discovered candidate deliverable."""
        proj = self._projects.get(project_id)
        if not proj:
            raise KeyError(f"Project '{project_id}' not found")
        proj["discovered_deliverables"] = [
            d for d in proj.get("discovered_deliverables", [])
            if d.get("title") != title
        ]
        self._save_registry()
        return True

    def run_project_ai_audit(self, project_id: str) -> dict[str, Any]:
        """Execute AI deliverable analysis and progress estimation across all documents, meetings, and emails."""
        proj = self._projects.get(project_id)
        if not proj:
            raise KeyError(f"Project '{project_id}' not found")

        kb = self.get_project_kb(project_id)
        docs = kb.list_documents()
        meetings = proj.get("meetings", [])
        emails = [e for e in self._synced_emails if e.get("projectId") == project_id]

        # Ensure all existing deliverables have unique IDs
        for i, d in enumerate(proj.get("deliverables", [])):
            if not d.get("id"):
                d["id"] = f"del_{int(datetime.now().timestamp() * 1000)}_{i}"

        audit_result = run_ai_deliverables_audit(
            project=proj,
            documents=docs,
            meetings=meetings,
            emails=emails,
        )

        # Update project deliverables with audit recommendations (match by ID or Title)
        audits_by_id = {
            str(a.get("id")): a
            for a in audit_result.get("deliverableAudits", [])
            if a.get("id") and str(a.get("id")).lower() != "none"
        }
        audits_by_title = {
            str(a.get("title", "")).lower().strip(): a
            for a in audit_result.get("deliverableAudits", [])
            if a.get("title")
        }

        for d in proj.get("deliverables", []):
            d_id = str(d.get("id"))
            d_title = str(d.get("title", "")).lower().strip()
            aud = audits_by_id.get(d_id) or audits_by_title.get(d_title)
            if aud:
                d["aiAudit"] = {
                    "estimatedProgress": aud.get("estimatedProgress", d.get("progress", 0)),
                    "recommendedStatus": aud.get("recommendedStatus", d.get("status")),
                    "evidence": aud.get("evidence", ""),
                    "evidenceFiles": aud.get("evidenceFiles", []),
                    "blockers": aud.get("blockers", ""),
                    "evaluatedAt": datetime.now().isoformat(),
                }
                # Adopt recommended progress and status
                if aud.get("estimatedProgress") is not None:
                    d["progress"] = aud["estimatedProgress"]
                if aud.get("recommendedStatus"):
                    d["status"] = aud["recommendedStatus"]

        proj["discovered_deliverables"] = audit_result.get("discoveredDeliverables", [])
        proj["ai_analysis"] = audit_result
        if audit_result.get("overallCompletion") is not None:
            proj["progress"] = audit_result["overallCompletion"]

        # Generate physical Markdown audit report on disk
        folder_path = Path(proj["folder_path"])
        audit_dir = folder_path / "audit_reports"
        audit_dir.mkdir(parents=True, exist_ok=True)

        timestamp_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        report_filename = f"Deliverable_Audit_{timestamp_str}.md"
        report_path = audit_dir / report_filename
        latest_path = audit_dir / "latest_audit_report.md"

        md_lines = [
            f"# Coordin8 AI Deliverable & Progress Audit Report",
            f"",
            f"- **Project:** {proj.get('name')}",
            f"- **Code:** {proj.get('code')}",
            f"- **Type:** {proj.get('project_type', 'internal').upper()} ({proj.get('client_name') or 'Internal Initiative'})",
            f"- **Audit Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"- **Overall Completion:** {audit_result.get('overallCompletion', 0)}%",
            f"- **Project Health:** {str(audit_result.get('health', 'on_track')).upper()}",
            f"",
            f"## Problem Statement & Strategic Objective",
            f"> {proj.get('problem_statement') or proj.get('description') or 'No problem statement defined.'}",
            f"",
            f"## Executive Status Briefing",
            f"{audit_result.get('executiveSummary', 'No summary generated.')}",
            f"",
            f"## Evidence-Anchored Deliverable Evaluations",
            f"",
        ]

        for d in proj.get("deliverables", []):
            d_audit = d.get("aiAudit", {})
            md_lines.extend([
                f"### {d.get('title')}",
                f"- **Current Status:** `{d.get('status')}` ({d.get('progress')}% progress)",
                f"- **Due Date:** {d.get('dueDate')}",
                f"- **Owner:** {d.get('owner', 'Team')}",
                f"- **Provenance / Source:** {d.get('source', 'manual')} ({d.get('sourceEvidence', 'None')})",
                f"- **AI Evidence Assessment:** {d_audit.get('evidence', 'No specific evidence identified.')}",
                f"- **Evidence Files Cited:** {', '.join(d_audit.get('evidenceFiles', [])) or 'None'}",
                f"- **Identified Blockers:** {d_audit.get('blockers') or 'None identified'}",
                f"",
            ])

        if audit_result.get("discoveredDeliverables"):
            md_lines.extend([
                f"## Candidate Deliverables Discovered from Communications & Transcripts",
                f"",
            ])
            for disc in audit_result["discoveredDeliverables"]:
                md_lines.extend([
                    f"- **{disc.get('title')}** (Priority: `{disc.get('priority')}`, Due: `{disc.get('suggestedDueDate')}`)",
                    f"  - Scope: {disc.get('description')}",
                    f"  - Origin Citation: {disc.get('sourceEvidence')}",
                    f"",
                ])

        md_lines.extend([
            f"## Ingested Artifacts Evaluated",
            f"- **Documents ({len(docs)}):** {', '.join([d.get('filename') or d.get('name', '') for d in docs]) or 'None'}",
            f"- **Meetings ({len(meetings)}):** {', '.join([m.get('title', '') for m in meetings]) or 'None'}",
            f"- **Emails ({len(emails)}):** {', '.join([e.get('subject', '') for e in emails]) or 'None'}",
            f"",
            f"---",
            f"*Generated autonomously by Coordin8 AI Deliverables Auditor*",
        ])

        report_content = "\n".join(md_lines)
        report_path.write_text(report_content, encoding="utf-8")
        latest_path.write_text(report_content, encoding="utf-8")

        audit_result["reportFile"] = str(report_path)
        audit_result["reportFilename"] = report_filename
        audit_result["latestReportPath"] = str(latest_path)
        audit_result["markdownReport"] = report_content

        self._save_registry()
        return {
            "project_id": project_id,
            "analysis": audit_result,
            "project": self.get_project_details(project_id),
        }


    def assign_email_to_project(self, email_id: str, project_id: str | None) -> dict[str, Any]:
        """Assign or unassign an email to a project, and run AI archetype classification."""
        target_email = None
        for e in self._synced_emails:
            if e.get("id") == email_id:
                target_email = e
                break
        if not target_email:
            raise KeyError(f"Email '{email_id}' not found")

        if not project_id or str(project_id).lower() in ("unassigned", "null", "none", ""):
            target_email["projectId"] = None
            target_email["projectName"] = None
            target_email["projectColor"] = "#94a3b8"
        else:
            proj = self._projects.get(project_id)
            if not proj:
                raise KeyError(f"Project '{project_id}' not found")
            target_email["projectId"] = project_id
            target_email["projectName"] = proj.get("name")
            target_email["projectColor"] = proj.get("color", "#6366f1")

            # Run semantic classification
            try:
                classification = classify_email_context(target_email, proj)
                target_email["archetype"] = classification.get("archetype")
                target_email["actionTag"] = classification.get("actionTag")
                target_email["aiSummary"] = classification.get("summary")
            except Exception as exc:
                logger.warning("Could not classify email: %s", exc)

        self._save_registry()
        return target_email


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

    def open_file_in_os(
        self,
        file_path: str | None = None,
        project_id: str | None = None,
        file_name: str | None = None,
    ) -> dict[str, Any]:
        """Open any file in its default associated OS application (Excel, Word, PDF reader, Notepad, etc.)."""
        target_path: Path | None = None

        # 1. Direct absolute or relative file_path provided and exists
        if file_path:
            p = Path(file_path)
            if p.exists() and p.is_file():
                target_path = p

        # 2. Gather candidate search directories based on project_id and project names
        search_dirs: list[Path] = []
        if project_id:
            # Check registered project
            if project_id in self._projects:
                p_fld = Path(self._projects[project_id]["folder_path"])
                if p_fld.exists() and p_fld not in search_dirs:
                    search_dirs.append(p_fld)

            # Check matching directory in home_folder by slug or name
            clean_pid = project_id.lower().replace("proj_", "").replace("-", " ").replace("_", " ").strip()
            slug_pid = project_id.lower().replace("proj_", "").replace("-", "_").strip()
            if self.home_folder.exists():
                for sub in self.home_folder.iterdir():
                    if sub.is_dir():
                        sub_name_clean = sub.name.lower().replace("-", " ").replace("_", " ").strip()
                        sub_slug = slugify(sub.name).replace("-", "_").strip()
                        if (
                            sub_slug == slug_pid
                            or sub.name.lower() == project_id.lower()
                            or sub_name_clean == clean_pid
                            or clean_pid in sub_name_clean
                        ):
                            if sub not in search_dirs:
                                search_dirs.append(sub)

        # Also add all other registered project folders as secondary search dirs
        for p_data in self._projects.values():
            fld = Path(p_data.get("folder_path", ""))
            if fld.exists() and fld not in search_dirs:
                search_dirs.append(fld)

        # 3. If file_path was given relative to a project folder
        if not target_path and file_path:
            clean_fp = Path(file_path).name
            for sdir in search_dirs:
                cand = sdir / file_path
                if cand.exists() and cand.is_file():
                    target_path = cand
                    break
                cand_audit = sdir / "audit_reports" / file_path
                if cand_audit.exists() and cand_audit.is_file():
                    target_path = cand_audit
                    break

        # 4. Search by target file name within search_dirs
        target_name = (file_name or (Path(file_path).name if file_path else "")).strip().lower()
        if not target_path and target_name:
            for sdir in search_dirs:
                if sdir.exists():
                    # Direct check in root of folder
                    for cand_f in sdir.iterdir():
                        if cand_f.is_file() and cand_f.name.lower() == target_name:
                            target_path = cand_f
                            break
                    if target_path:
                        break
                    # Check audit_reports subfolder
                    cand_audit = sdir / "audit_reports"
                    if cand_audit.exists():
                        for cand_f in cand_audit.iterdir():
                            if cand_f.is_file() and cand_f.name.lower() == target_name:
                                target_path = cand_f
                                break
                    if target_path:
                        break
                    # Recursive check in project folder
                    for f in sdir.rglob("*"):
                        if f.is_file() and f.name.lower() == target_name:
                            target_path = f
                            break
                    if target_path:
                        break

        # 5. Global search in Coordin8 Home folder recursively
        if not target_path and target_name and self.home_folder.exists():
            for f in self.home_folder.rglob("*"):
                if f.is_file() and f.name.lower() == target_name:
                    target_path = f
                    break

        # 6. Global search in projects_kbs storage artifacts (raw and derived documents)
        if not target_path and target_name:
            kbs_dir = self.storage_root / "projects_kbs"
            if kbs_dir.exists():
                for f in kbs_dir.rglob("*"):
                    if f.is_file() and f.name.lower() == target_name:
                        target_path = f
                        break

        # 7. Check general transcripts folder
        if not target_path and target_name:
            trans_dir = self.home_folder / "general" / "transcripts"
            if trans_dir.exists():
                for f in trans_dir.iterdir():
                    if f.is_file() and f.name.lower() == target_name:
                        target_path = f
                        break

        if not target_path or not target_path.exists():
            raise FileNotFoundError(f"File '{file_name or file_path}' could not be found on disk.")

        resolved = target_path.resolve()

        # Launch in native OS application using Windows ShellExecute
        if hasattr(os, "startfile"):
            os.startfile(str(resolved))
        else:
            import subprocess
            subprocess.Popen(["start", "", str(resolved)], shell=True)

        logger.info("Opened file in native OS application: %s", resolved)
        return {
            "status": "ok",
            "opened_path": str(resolved),
            "file_name": resolved.name,
            "extension": resolved.suffix.lower(),
            "message": f"Opened {resolved.name} in native application",
        }

    def open_project_folder_in_os(self, project_id: str) -> dict[str, Any]:
        """Open the physical project folder in Windows Explorer."""
        target_folder: Path | None = None
        proj = self._projects.get(project_id)
        if proj and proj.get("folder_path"):
            p = Path(proj["folder_path"])
            if p.exists():
                target_folder = p

        if not target_folder:
            clean_pid = project_id.lower().replace("proj_", "").replace("-", " ").replace("_", " ").strip()
            slug_pid = project_id.lower().replace("proj_", "").replace("-", "_").strip()
            if self.home_folder.exists():
                for sub in self.home_folder.iterdir():
                    if sub.is_dir():
                        sub_name_clean = sub.name.lower().replace("-", " ").replace("_", " ").strip()
                        sub_slug = slugify(sub.name).replace("-", "_").strip()
                        if (
                            sub_slug == slug_pid
                            or sub.name.lower() == project_id.lower()
                            or sub_name_clean == clean_pid
                            or clean_pid in sub_name_clean
                        ):
                            target_folder = sub
                            break

        if not target_folder:
            target_folder = (self.home_folder / project_id).resolve()

        target_folder.mkdir(parents=True, exist_ok=True)
        resolved = target_folder.resolve()
        if hasattr(os, "startfile"):
            os.startfile(str(resolved))
        else:
            import subprocess
            subprocess.Popen(["start", "", str(resolved)], shell=True)
        return {"status": "ok", "opened_path": str(resolved)}

