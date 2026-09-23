"""Runnable OpenWorker Integration Example using Coordin8 KnowledgeBase SDK.

Demonstrates:
1. Dynamic creation of an isolated KnowledgeBase.
2. Ingestion of markdown and text documents.
3. Hierarchical search with provenance and scores.
4. Citation-grounded context prompt assembly for LLMs.
5. Exporting and executing native agent tool calls.
6. Clean resource disposal.
"""

from pathlib import Path
import sys
import tempfile

# Force UTF-8 on Windows terminal output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Add backend directory to sys.path so app can be imported standalone
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app import KnowledgeBase


def main():
    print("=" * 70)
    print("  Coordin8 -> OpenWorker Integration Demonstration")
    print("=" * 70)

    # Use a temporary workspace for this demonstration
    with tempfile.TemporaryDirectory() as temp_dir:
        workspace = Path(temp_dir) / "openworker_workspace"

        print(f"\n[1] Initializing isolated KnowledgeBase in: {workspace}")
        kb = KnowledgeBase(
            kb_id="openworker_demo_agent",
            storage_dir=workspace,
        )

        try:
            # 1. Ingest a document
            sample_doc = (
                "# Platform Engineering Handbook\n\n"
                "## Architecture Principles\n"
                "All internal microservices must communicate over gRPC with mTLS.\n"
                "Public APIs are exposed through the Envoy gateway.\n\n"
                "## Reliability SLAs\n"
                "Core payment services must maintain 99.99% availability.\n"
                "Maximum P99 response latency is strictly capped at 45 milliseconds.\n\n"
                "## Deployment Rules\n"
                "Production deployments require signed commits and approval from the Tech Lead."
            ).encode("utf-8")

            print("\n[2] Ingesting document into KnowledgeBase...")
            result = kb.ingest_bytes(
                content=sample_doc,
                filename="engineering_handbook.md",
                title="Engineering Handbook",
            )
            print(f"    -> Document ID : {result['document_id']}")
            print(f"    -> Status      : {result['status']}")
            print(f"    -> Modality    : {result['file_type']}")
            print(f"    -> Summary     : {result['summary'][:80]}...")

            # 2. Hierarchical Search
            query = "What is the maximum allowed P99 latency and what protocol is required?"
            print(f"\n[3] Executing hierarchical hybrid search for query:\n    '{query}'")
            search_results = kb.search(query, limit=2)

            print(f"    -> Candidate documents evaluated: {search_results['candidate_documents']}")
            print(f"    -> Top matches returned        : {len(search_results['results'])}")
            for rank, match in enumerate(search_results["results"], start=1):
                clean_prov = str(match["provenance"]).replace("\u2192", "->")
                clean_lineage = str(match["lineage"]).replace("\u2192", "->")
                print(f"\n    Match [{rank}]: {match['document_title']} ({clean_prov})")
                print(f"    Lineage : {clean_lineage}")
                print(f"    Score   : {match['score']} (Dense: {match['dense_score']}, Sparse: {match['sparse_score']})")
                print(f"    Snippet : {match['content'][:110]}...")

            # 3. Context Assembly
            print("\n[4] Assembling LLM prompt context with citations...")
            ctx = kb.query_context("P99 latency SLA", limit=2)
            print("    -> Prompt Context Block:")
            for line in ctx["formatted_context"].splitlines():
                print(f"       | {line}")
            print(f"    -> Estimated Token Count: {ctx['estimated_tokens']}")

            # 4. Agent Tool Calling
            print("\n[5] Demonstrating agent tool calling interface (OpenWorker schema)...")
            tools = kb.as_tools()
            print(f"    -> Registered tool schemas: {[t['name'] for t in tools]}")

            # Simulate agent dispatching a tool call
            print("    -> Simulating agent call: search_knowledge(query='deployment approval')")
            tool_res = kb.execute_tool(
                "search_knowledge",
                {"query": "deployment approval", "limit": 1},
            )
            top_chunk = tool_res["results"][0]
            print(f"    -> Tool Result Content: {top_chunk['content'][:90]}...")

        finally:
            # 5. Clean up
            print("\n[6] Disposing KnowledgeBase resources...")
            kb.close()
            print("    -> Done! Integration demonstration completed successfully.")


if __name__ == "__main__":
    main()
