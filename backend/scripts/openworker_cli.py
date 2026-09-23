"""Interactive CLI and Runner for OpenWorker Agent Harness.

Usage:
    python scripts/openworker_cli.py --demo
    python scripts/openworker_cli.py --agent-id my_agent
"""

import argparse
from pathlib import Path
import sys
import tempfile

# Force UTF-8 on Windows terminal output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Ensure backend root is on sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.openworker import OpenWorkerAgent, OpenWorkerHarness


def run_demo():
    print("=" * 75)
    print("  Coordin8 -> OpenWorker Agentic Harness Demonstration")
    print("=" * 75)

    with tempfile.TemporaryDirectory() as temp_dir:
        harness = OpenWorkerHarness(base_workspace_dir=temp_dir)

        # 1. Instantiate Agent Alpha
        print("\n[1] Instantiating OpenWorkerAgent 'alpha_researcher'...")
        agent_alpha = harness.create_agent(
            agent_id="alpha_researcher",
            role="Autonomous Security Analyst",
        )
        print(f"    -> Agent ID   : {agent_alpha.agent_id}")
        print(f"    -> Workspace  : {agent_alpha.workspace_path}")
        print(f"    -> Collections: {agent_alpha.kb.collection_prefix}_*")

        try:
            # 2. Ingest documents into Agent Alpha's private vector DB
            print("\n[2] Agent Alpha ingesting private security policy...")
            policy_doc = (
                "# Zero Trust Network Architecture Policy\n\n"
                "## Identity & Authentication\n"
                "All internal microservices must require mTLS and SPIFFE IDs.\n"
                "Session tokens expire after strictly 15 minutes of inactivity.\n\n"
                "## Encryption Requirements\n"
                "Data at rest must be encrypted with AES-256-GCM.\n"
                "TLS 1.3 is mandatory for all inbound and outbound transit."
            ).encode("utf-8")

            res = agent_alpha.ingest_bytes(
                content=policy_doc,
                filename="zero_trust_policy.md",
                title="Zero Trust Security Policy",
            )
            print(f"    -> Ingestion Status: {res['status']} (Document ID: {res['document_id']})")
            print(f"    -> Summary: {res['summary'][:80]}...")

            # 3. Agent Alpha runs an autonomous reasoning task
            prompt = "What is the token expiration duration and required cipher for data at rest?"
            print(f"\n[3] Running autonomous task for Agent Alpha:\n    Prompt: '{prompt}'")
            task_result = agent_alpha.run_task(prompt)

            print(f"    -> Task ID: {task_result.task_id}")
            print("    -> Execution Trajectory:")
            for s in task_result.steps:
                tool_call_info = f" [Tool: {s.tool_name}]" if s.tool_name else ""
                print(f"       * Step {s.step_number}: {s.thought}{tool_call_info}")
                if s.tool_output:
                    print(f"         Output: {s.tool_output}")

            print("\n    -> Grounded Answer:")
            for line in task_result.answer.splitlines():
                print(f"       | {line}")

            # 4. Multi-Tenant Isolation Test with Agent Beta
            print("\n[4] Instantiating Agent Beta to test strict vector database isolation...")
            agent_beta = harness.create_agent(
                agent_id="beta_analyst",
                role="Financial Auditor",
            )
            beta_docs = agent_beta.list_documents()
            print(f"    -> Agent Beta document count: {len(beta_docs)} (Expected: 0, strictly isolated)")
            assert len(beta_docs) == 0, "Isolation failure: Agent Beta saw Alpha's documents!"

            beta_search = agent_beta.search("Zero Trust cipher", limit=3)
            print(f"    -> Agent Beta search results count: {len(beta_search['results'])} (Expected: 0)")
            assert len(beta_search["results"]) == 0, "Isolation failure: Beta retrieved Alpha's vectors!"

            print("    -> Multi-tenant vector isolation confirmed successfully!")

            # 5. Export tool definitions
            tools = agent_alpha.get_tool_definitions()
            print(f"\n[5] OpenWorker Tool Calling Schemas Exported ({len(tools)} tools):")
            for t in tools:
                print(f"    - {t['name']}: {t['description']}")

        finally:
            print("\n[6] Tearing down agents and cleaning up database handles...")
            harness.close_all()
            print("    -> Cleanup completed successfully.")


def main():
    parser = argparse.ArgumentParser(description="OpenWorker Agent Harness CLI")
    parser.add_argument("--demo", action="store_true", help="Run automated demonstration")
    parser.add_argument("--agent-id", type=str, default=None, help="Agent ID to run")
    args = parser.parse_args()

    if args.demo or not args.agent_id:
        run_demo()
    else:
        harness = OpenWorkerHarness()
        agent = harness.get_or_create_agent(args.agent_id)
        print(f"Connected to agent: {agent.agent_id} in {agent.workspace_path}")
        print("Type 'exit' to quit.")
        try:
            while True:
                user_input = input("\nYou: ").strip()
                if user_input.lower() in ("exit", "quit"):
                    break
                if not user_input:
                    continue
                result = agent.run_task(user_input)
                print(f"\nAgent ({agent.role}):\n{result.answer}")
        finally:
            agent.close()


if __name__ == "__main__":
    main()
