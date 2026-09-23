"""OpenWorker Agent Implementation for Coordin8.

Provides an autonomous agent class that dynamically instantiates its own isolated
KnowledgeBase vector database, manages private document collections, and executes
agentic tool calls (ingestion, hierarchical search, context query, spreadsheet analysis).
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable
import uuid

from app.core.logging import logger
from app.knowledge_base import KnowledgeBase
from app.llm.client import LLMClient


@dataclass
class AgentStep:
    """A single step in the agent's reasoning / execution trajectory."""
    step_number: int
    thought: str
    tool_name: str | None = None
    tool_args: dict[str, Any] | None = None
    tool_output: Any | None = None
    final_response: str | None = None


@dataclass
class AgentTaskResult:
    """Result of an agent running an end-to-end task."""
    task_id: str
    agent_id: str
    query: str
    answer: str
    steps: list[AgentStep] = field(default_factory=list)
    evidence_used: list[dict[str, Any]] = field(default_factory=list)
    kb_id: str = ""


class OpenWorkerAgent:
    """Autonomous OpenWorker agent that owns its own private KnowledgeBase."""

    def __init__(
        self,
        agent_id: str | None = None,
        role: str = "Research & Knowledge Specialist",
        workspace_dir: str | Path | None = None,
        qdrant_url: str | None = None,
        db_url: str | None = None,
        llm_client: LLMClient | None = None,
        system_instruction: str | None = None,
    ) -> None:
        self.agent_id = agent_id or f"agent_{uuid.uuid4().hex[:8]}"
        self.role = role
        self.system_instruction = system_instruction or (
            f"You are OpenWorker Agent '{self.agent_id}', specializing in {self.role}. "
            "You have access to an isolated, private KnowledgeBase. Ground all answers in retrieved evidence."
        )

        # 1. Scoped Workspace Directory
        base_ws = Path(workspace_dir or "./data/openworker_workspaces")
        self.workspace_path = (base_ws / self.agent_id).resolve()
        self.workspace_path.mkdir(parents=True, exist_ok=True)

        # 2. Private, isolated KnowledgeBase (custom class instantiation)
        self.kb = KnowledgeBase(
            kb_id=self.agent_id,
            storage_dir=self.workspace_path,
            db_url=db_url,
            qdrant_url=qdrant_url,
            collection_prefix=f"ow_{self.agent_id}",
        )

        # 3. LLM and Conversation History
        self.llm = llm_client or LLMClient()
        self.history: list[dict[str, str]] = []

        logger.info(
            "Initialized OpenWorkerAgent '%s' with isolated workspace: %s",
            self.agent_id,
            self.workspace_path,
        )

    # -------------------------------------------------------------------------
    # Ingestion & Document Operations
    # -------------------------------------------------------------------------

    def ingest_file(self, file_path: str | Path, title: str | None = None) -> dict[str, Any]:
        """Ingest a local document into this agent's private vector DB."""
        return self.kb.ingest_file(file_path=file_path, title=title)

    def ingest_bytes(
        self,
        content: bytes,
        filename: str,
        title: str | None = None,
    ) -> dict[str, Any]:
        """Ingest raw document bytes into this agent's private vector DB."""
        return self.kb.ingest_bytes(content=content, filename=filename, title=title)

    def list_documents(self) -> list[dict[str, Any]]:
        """List all documents registered in this agent's private store."""
        return self.kb.list_documents()

    def read_document(self, document_id: str) -> str | None:
        """Read full canonical markdown representation of a document."""
        return self.kb.read_document(document_id)

    # -------------------------------------------------------------------------
    # Retrieval & Search Operations
    # -------------------------------------------------------------------------

    def search(self, query: str, limit: int = 5, document_id: str | None = None) -> dict[str, Any]:
        """Perform hierarchical hybrid search across private vector collections."""
        return self.kb.search(query=query, limit=limit, document_id=document_id)

    def query_context(self, query: str, limit: int = 3) -> dict[str, Any]:
        """Retrieve assembled evidence context with citations."""
        return self.kb.query_context(query=query, limit=limit)

    def analyze_spreadsheet(
        self,
        document_id: str,
        sheet_name: str,
        operation: str,
        column: str,
    ) -> dict[str, Any]:
        """Execute deterministic spreadsheet computation without hallucination."""
        return self.kb.analyze_spreadsheet(
            document_id=document_id,
            sheet_name=sheet_name,
            operation=operation,
            column=column,
        )

    # -------------------------------------------------------------------------
    # Tool Registration & Execution
    # -------------------------------------------------------------------------

    def get_tool_definitions(self) -> list[dict[str, Any]]:
        """Export tool calling definitions for OpenWorker / OpenAI schemas."""
        tools = self.kb.as_tools()
        # Add agent-level tool for self-reflection / summary
        tools.append({
            "name": "get_agent_info",
            "description": "Get current agent ID, workspace path, and collection status.",
            "parameters": {"type": "object", "properties": {}},
        })
        return tools

    def execute_tool(self, tool_name: str, arguments: dict[str, Any]) -> Any:
        """Execute tool call on the agent or its underlying KnowledgeBase."""
        if tool_name == "get_agent_info":
            return {
                "agent_id": self.agent_id,
                "role": self.role,
                "workspace": str(self.workspace_path),
                "collections_prefix": self.kb.collection_prefix,
                "total_documents": len(self.kb.list_documents()),
            }
        return self.kb.execute_tool(tool_name, arguments)

    # -------------------------------------------------------------------------
    # Autonomous Reasoning / Execution Loop
    # -------------------------------------------------------------------------

    def run_task(self, task_prompt: str, max_steps: int = 5) -> AgentTaskResult:
        """Run an autonomous task using ReAct reasoning and KnowledgeBase tools."""
        task_id = f"task_{uuid.uuid4().hex[:8]}"
        steps: list[AgentStep] = []
        evidence_collected: list[dict[str, Any]] = []

        logger.info("[%s] Beginning task '%s': %s", self.agent_id, task_id, task_prompt)

        # Step 1: Discover relevant documents or retrieve prompt-ready context
        step_1_thought = f"Analyze task and query private knowledge base for grounded context on: '{task_prompt}'"
        ctx_result = self.kb.query_context(task_prompt, limit=3)
        formatted_context = ctx_result.get("formatted_context", "")
        evidence_units = ctx_result.get("evidence_units", [])

        steps.append(
            AgentStep(
                step_number=1,
                thought=step_1_thought,
                tool_name="query_context",
                tool_args={"query": task_prompt, "limit": 3},
                tool_output={
                    "evidence_units_found": len(evidence_units),
                    "estimated_tokens": ctx_result.get("estimated_tokens", 0),
                },
            )
        )
        evidence_collected.extend(evidence_units)

        # Step 2: If no direct evidence is found, attempt broad hybrid search
        if not evidence_units:
            step_2_thought = "Direct context was empty. Attempting broader hierarchical hybrid search."
            search_res = self.kb.search(task_prompt, limit=3)
            search_matches = search_res.get("results", [])
            steps.append(
                AgentStep(
                    step_number=2,
                    thought=step_2_thought,
                    tool_name="search_knowledge",
                    tool_args={"query": task_prompt, "limit": 3},
                    tool_output={"matches_found": len(search_matches)},
                )
            )
            if search_matches:
                # Build context from search matches
                context_parts = []
                for idx, m in enumerate(search_matches, start=1):
                    context_parts.append(
                        f"--- EVIDENCE ITEM [{idx}] ---\n"
                        f"Source: Doc {m['document_id']} ({m['provenance']})\n"
                        f"Content:\n{m['content']}\n"
                    )
                formatted_context = "\n".join(context_parts)

        # Step 3: Synthesis step using LLMClient (or grounded synthesis fallback)
        step_synth_thought = "Synthesizing final answer grounded in retrieved knowledge base evidence."
        if formatted_context.strip():
            answer = self.llm.generate_answer(query=task_prompt, context_text=formatted_context)
        else:
            docs = self.kb.list_documents()
            if not docs:
                answer = (
                    f"Agent '{self.agent_id}' has no documents ingested into its private knowledge base yet. "
                    f"Please ingest relevant files using kb.ingest_file() or the ingest tool."
                )
            else:
                answer = (
                    f"No direct evidence matching '{task_prompt}' was found in Agent '{self.agent_id}'s "
                    f"knowledge base ({len(docs)} documents indexed)."
                )

        steps.append(
            AgentStep(
                step_number=len(steps) + 1,
                thought=step_synth_thought,
                final_response=answer,
            )
        )

        # Record in history
        self.history.append({"user": task_prompt, "assistant": answer})

        return AgentTaskResult(
            task_id=task_id,
            agent_id=self.agent_id,
            query=task_prompt,
            answer=answer,
            steps=steps,
            evidence_used=evidence_collected,
            kb_id=self.kb.kb_id,
        )

    def close(self) -> None:
        """Dispose of underlying KnowledgeBase database handles cleanly."""
        try:
            self.kb.close()
        except Exception as exc:
            logger.warning("Error closing agent %s: %s", self.agent_id, exc)
