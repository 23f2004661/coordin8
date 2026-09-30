import json
import shutil
from pathlib import Path
from qdrant_client import QdrantClient

DESKTOP_HOME = Path(r"C:\Users\ssrin\Desktop\Coordin8 Home")
BACKEND_DATA = Path(r"c:\Users\ssrin\Desktop\1. Projects\Coordin8\coordin8\backend\data")
PROJECTS_KBS = BACKEND_DATA / "projects_kbs"
REGISTRY_PATH = BACKEND_DATA / "projects_registry.json"

TARGET_DELETED_PROJECT_IDS = [
    "proj_acme_robotics_intelligence",
    "proj_alpha_test_project",
    "proj_existing_research_docs",
    "proj_learning_robotics_hf",
]

TARGET_DELETED_DESKTOP_FOLDERS = [
    "Acme Robotics Intelligence",
    "Alpha Test Project",
    "Existing Research Docs",
    "Learning Robotics HF",
]

TARGET_DELETED_KB_NAMES = [
    "proj_acme_robotics_intelligence",
    "proj_alpha_test_project",
    "proj_existing_research_docs",
    "proj_existing_research_project",
    "proj_learning_robotics_hf",
]

def perform_cleanup():
    print("=== STARTING CLEANUP OF UNWANTED PROJECTS ===")

    # 1. Delete physical folders from Desktop / Coordin8 Home
    print("\n--- 1. Desktop Folders ---")
    for folder_name in TARGET_DELETED_DESKTOP_FOLDERS:
        folder_path = DESKTOP_HOME / folder_name
        if folder_path.exists():
            print(f"Removing Desktop folder: {folder_path}")
            shutil.rmtree(folder_path, ignore_errors=False)
        else:
            print(f"Folder already does not exist: {folder_path}")

    # 2. Delete Knowledge Base on-disk storage
    print("\n--- 2. On-Disk Project Knowledge Bases ---")
    for kb_name in TARGET_DELETED_KB_NAMES:
        kb_path = PROJECTS_KBS / kb_name
        if kb_path.exists():
            print(f"Removing KB folder: {kb_path}")
            shutil.rmtree(kb_path, ignore_errors=False)
        else:
            print(f"KB folder already does not exist: {kb_path}")

    # 3. Delete Qdrant Collections
    print("\n--- 3. Qdrant Collections ---")
    client = QdrantClient(url="http://localhost:6333", timeout=5.0)
    existing_cols = {c.name for c in client.get_collections().collections}
    for kb_name in TARGET_DELETED_KB_NAMES:
        prefix = f"kb_{kb_name}"
        suffixes = ["assets", "chunks", "document_summaries", "section_summaries"]
        for s in suffixes:
            col_name = f"{prefix}_{s}"
            if col_name in existing_cols:
                print(f"Deleting Qdrant collection: {col_name}")
                client.delete_collection(collection_name=col_name)
            else:
                print(f"Collection {col_name} not found in Qdrant (already absent)")

    # 4. Update projects_registry.json
    print("\n--- 4. projects_registry.json ---")
    if REGISTRY_PATH.exists():
        with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
            registry = json.load(f)

        projects = registry.get("projects", {})
        for pid in TARGET_DELETED_PROJECT_IDS:
            if pid in projects:
                name = projects[pid].get("name", pid)
                print(f"Removing {pid} ({name}) from registry projects")
                del projects[pid]

        # Clean synced_emails
        synced_emails = registry.get("synced_emails", [])
        for email in synced_emails:
            if email.get("projectId") in TARGET_DELETED_PROJECT_IDS:
                print(f"Setting projectId to None for email: {email.get('id')} ({email.get('subject', '')[:30]})")
                email["projectId"] = None

        with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
            json.dump(registry, f, indent=2)
        print("Updated projects_registry.json successfully.")

    print("\n=== VERIFICATION OF REMAINING STATE ===")
    # Verify Desktop folders
    remaining_desktop = [p.name for p in DESKTOP_HOME.iterdir() if p.is_dir()]
    print("Remaining Desktop folders:", remaining_desktop)

    # Verify Project KBs
    remaining_kbs = [p.name for p in PROJECTS_KBS.iterdir() if p.is_dir()]
    print("Remaining Project KBs:", remaining_kbs)

    # Verify Qdrant Collections
    remaining_cols = [c.name for c in client.get_collections().collections if c.name.startswith("kb_proj_")]
    print("Remaining kb_proj_* Qdrant collections:", remaining_cols)

    # Verify Registry Projects
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        reg = json.load(f)
    print("Remaining registered projects:", list(reg.get("projects", {}).keys()))

if __name__ == "__main__":
    perform_cleanup()
