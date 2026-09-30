import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from app.projects.manager import ProjectManager

mgr = ProjectManager.get_instance()
pids = [
    "proj_finedge_ai_automated_credit_underwriting",
    "proj_apex_healthtech_clinical_stratification",
    "proj_nexus_logistics_autonomous_fleet_telematics",
    "proj_cybershield_defense_fedramp_zero_trust",
    "proj_omnicommerce_retail_visual_search_engine"
]

print("=" * 80)
print("AUDITING ALL 5 PROJECTS")
print("=" * 80)

for pid in pids:
    p = mgr._projects.get(pid)
    if not p:
        print(f"Skipping {pid} (not found)")
        continue
    print(f"\nAuditing [{p.get('code')}] {p.get('name')}...")
    res = mgr.run_project_ai_audit(pid)
    analysis = res["analysis"]
    print(f"  [OK] Completion: {analysis.get('overallCompletion')}% | Health: {analysis.get('health')}")
    print(f"  [OK] Deliverables Audited: {len(analysis.get('deliverableAudits', []))}")
    print(f"  [OK] Candidate Milestones Discovered: {len(analysis.get('discoveredDeliverables', []))}")
    print(f"  [OK] Audit Report Path: {analysis.get('latestReportPath')}")

print("\n" + "=" * 80)
print("FINAL AUDIT SUMMARY ACROSS ALL 5 PROJECTS")
print("=" * 80)
for pid in pids:
    p = mgr._projects[pid]
    code = p.get("code")
    name = p.get("name")
    prog = p.get("progress")
    health = (p.get("ai_analysis") or {}).get("health", "on_track")
    d_count = len(p.get("deliverables", []))
    print(f"  [{code}] {name}: Progress={prog}%, Health={health.upper()}, Milestones={d_count}")
print("=" * 80)
