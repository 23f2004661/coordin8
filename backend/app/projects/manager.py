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
            except Exception as exc:
                logger.error("Error loading project registry: %s", exc)
                self._projects = {}
        else:
            self._projects = {}

    def _save_registry(self) -> None:
        try:
            payload = {
                "home_folder": str(self.home_folder),
                "updated_at": datetime.now().isoformat(),
                "projects": self._projects,
            }
            self.registry_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        except Exception as exc:
            logger.error("Error saving project registry: %s", exc)

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

    def add_meeting(self, project_id: str, meeting_data: dict[str, Any]) -> dict[str, Any]:
        """Add a scheduled meeting to a project."""
        proj = self._projects.get(project_id)
        if not proj:
            raise KeyError(f"Project '{project_id}' not found")
        if "meetings" not in proj:
            proj["meetings"] = []
        proj["meetings"].insert(0, meeting_data)
        self._save_registry()
        return meeting_data

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
