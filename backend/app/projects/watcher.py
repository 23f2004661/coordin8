"""File watcher for automatic document ingestion into dedicated project knowledge bases."""

import os
from pathlib import Path
import threading
import time
from typing import Callable
from watchdog.events import FileSystemEventHandler, FileCreatedEvent, FileModifiedEvent
from watchdog.observers import Observer

from app.core.logging import logger

SUPPORTED_EXTENSIONS = {
    ".pdf", ".docx", ".doc", ".xlsx", ".xls", ".csv",
    ".txt", ".md", ".markdown",
    ".vtt", ".srt",
    ".pptx", ".ppt",
    ".json", ".jsonl",
    ".png", ".jpg", ".jpeg",
}

IGNORED_PATTERNS = {
    ".git", ".venv", "venv", "__pycache__", "node_modules",
    ".coordin8", ".idea", ".vscode", "tmp", "temp",
}


class ProjectFileEventHandler(FileSystemEventHandler):
    """Watches a project folder and triggers ingestion into its dedicated KB."""

    def __init__(self, project_id: str, on_file_detected: Callable[[str, Path], None]):
        super().__init__()
        self.project_id = project_id
        self.on_file_detected = on_file_detected
        self._debounce_timers: dict[str, threading.Timer] = {}
        self._lock = threading.Lock()

    def _is_valid_file(self, file_path: str) -> bool:
        path = Path(file_path)
        # Skip directories
        if not path.is_file():
            return False
        # Skip temporary Office / OS files
        if path.name.startswith("~$") or path.name.startswith("."):
            return False
        # Check ignored parts
        for part in path.parts:
            if part.lower() in IGNORED_PATTERNS:
                return False
        # Check supported extension
        return path.suffix.lower() in SUPPORTED_EXTENSIONS

    def _trigger_ingest(self, file_path: str):
        path = Path(file_path)
        if not path.exists():
            return
        # Ensure file write is finished by checking size stability
        try:
            initial_size = path.stat().st_size
            time.sleep(0.3)
            if not path.exists():
                return
            if path.stat().st_size != initial_size:
                # File is still being written, reschedule
                self._schedule_ingest(file_path, delay=0.8)
                return
        except Exception:
            return

        logger.info(
            "[Watchdog] Auto-indexing detected file '%s' into project '%s' KB",
            path.name,
            self.project_id,
        )
        try:
            self.on_file_detected(self.project_id, path)
        except Exception as exc:
            logger.error(
                "[Watchdog] Error auto-ingesting '%s' into project '%s': %s",
                path.name,
                self.project_id,
                exc,
            )

    def _schedule_ingest(self, file_path: str, delay: float = 0.6):
        with self._lock:
            if file_path in self._debounce_timers:
                self._debounce_timers[file_path].cancel()
            timer = threading.Timer(delay, self._trigger_ingest, args=[file_path])
            self._debounce_timers[file_path] = timer
            timer.daemon = True
            timer.start()

    def on_created(self, event):
        if not event.is_directory and self._is_valid_file(event.src_path):
            self._schedule_ingest(event.src_path)

    def on_modified(self, event):
        if not event.is_directory and self._is_valid_file(event.src_path):
            self._schedule_ingest(event.src_path)


class ProjectWatcherManager:
    """Manages Watchdog observers for all registered project folders."""

    def __init__(self, on_file_detected: Callable[[str, Path], None]):
        self.on_file_detected = on_file_detected
        self.observer = Observer()
        self.watched_paths: dict[str, str] = {}  # project_id -> folder_path
        self._is_running = False

    def start(self):
        if not self._is_running:
            self.observer.start()
            self._is_running = True
            logger.info("[Watchdog] ProjectWatcherManager started.")

    def stop(self):
        if self._is_running:
            self.observer.stop()
            self.observer.join(timeout=3)
            self._is_running = False
            logger.info("[Watchdog] ProjectWatcherManager stopped.")

    def watch_project(self, project_id: str, folder_path: str | Path):
        path = str(Path(folder_path).resolve())
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)

        if project_id in self.watched_paths and self.watched_paths[project_id] == path:
            return

        handler = ProjectFileEventHandler(project_id, self.on_file_detected)
        try:
            self.observer.schedule(handler, path=path, recursive=True)
            self.watched_paths[project_id] = path
            logger.info(
                "[Watchdog] Monitoring project '%s' directory: %s",
                project_id,
                path,
            )
        except Exception as exc:
            logger.warning(
                "[Watchdog] Failed to schedule watch for '%s': %s",
                path,
                exc,
            )
