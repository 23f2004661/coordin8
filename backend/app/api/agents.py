"""OpenWorker Agent API endpoints for Coordin8.

Exposes REST routes to instantiate OpenWorker agents, ingest documents into
agent-scoped vector databases, query knowledge, execute tool calls, and run
autonomous agent tasks.
"""

from typing import Any
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field

from app.openworker.harness import get_harness

router = APIRouter(prefix="/agents", tags=["openworker-agents"])


class CreateAgentRequest(BaseModel):
    agent_id: str | None = None
    role: str = "Research & Knowledge Specialist"
    system_instruction: str | None = None


class ChatAgentRequest(BaseModel):
    query: str
    max_steps: int = Field(default=5, ge=1, le=10)


class ExecuteToolRequest(BaseModel):
    tool_name: str
    arguments: dict[str, Any] = Field(default_factory=dict)


@router.post("", status_code=201)
def create_agent(request: CreateAgentRequest):
    """Instantiate a new OpenWorkerAgent with its own private KnowledgeBase."""
    harness = get_harness()
    if request.agent_id and harness.get_agent(request.agent_id):
        raise HTTPException(status_code=409, detail=f"Agent '{request.agent_id}' already exists.")

    agent = harness.create_agent(
        agent_id=request.agent_id,
        role=request.role,
        system_instruction=request.system_instruction,
    )
    return {
        "success": True,
        "agent_id": agent.agent_id,
        "role": agent.role,
        "workspace": str(agent.workspace_path),
        "collections_prefix": agent.kb.collection_prefix,
    }


@router.get("")
def list_agents():
    """List all registered OpenWorker agents and their private knowledge bases."""
    harness = get_harness()
    return {"agents": harness.list_agents()}


@router.get("/{agent_id}")
def get_agent_details(agent_id: str):
    """Retrieve metadata, documents count, and tools for an agent."""
    harness = get_harness()
    agent = harness.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found.")

    return {
        "agent_id": agent.agent_id,
        "role": agent.role,
        "workspace": str(agent.workspace_path),
        "collections_prefix": agent.kb.collection_prefix,
        "documents": agent.list_documents(),
        "tools": [t["name"] for t in agent.get_tool_definitions()],
    }


@router.get("/{agent_id}/tools")
def get_agent_tools(agent_id: str):
    """Export tool declarations formatted for OpenWorker / OpenAI function calling."""
    harness = get_harness()
    agent = harness.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found.")

    return {"agent_id": agent_id, "tools": agent.get_tool_definitions()}


@router.post("/{agent_id}/tool_call")
def call_agent_tool(agent_id: str, request: ExecuteToolRequest):
    """Execute a single tool call on an agent's private KnowledgeBase."""
    harness = get_harness()
    agent = harness.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found.")

    try:
        result = agent.execute_tool(request.tool_name, request.arguments)
        return {"agent_id": agent_id, "tool_name": request.tool_name, "result": result}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/{agent_id}/ingest")
async def ingest_document_to_agent(
    agent_id: str,
    file: UploadFile = File(...),
    title: str | None = Form(None),
):
    """Upload and ingest a file directly into an agent's private vector DB."""
    harness = get_harness()
    agent = harness.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found.")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        result = agent.ingest_bytes(
            content=content,
            filename=file.filename or "uploaded_file",
            title=title or file.filename,
        )
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {exc}")


@router.post("/{agent_id}/chat")
def chat_with_agent(agent_id: str, request: ChatAgentRequest):
    """Run an autonomous task with ReAct reasoning and grounded evidence synthesis."""
    harness = get_harness()
    agent = harness.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found.")

    task_result = agent.run_task(task_prompt=request.query, max_steps=request.max_steps)
    return {
        "task_id": task_result.task_id,
        "agent_id": task_result.agent_id,
        "query": task_result.query,
        "answer": task_result.answer,
        "kb_id": task_result.kb_id,
        "steps": [
            {
                "step": s.step_number,
                "thought": s.thought,
                "tool_name": s.tool_name,
                "tool_args": s.tool_args,
                "tool_output": s.tool_output,
                "final_response": s.final_response,
            }
            for s in task_result.steps
        ],
        "evidence_used": task_result.evidence_used,
    }


@router.delete("/{agent_id}")
def delete_agent(agent_id: str):
    """Tear down agent and remove its private database and files."""
    harness = get_harness()
    if not harness.get_agent(agent_id):
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found.")

    success = harness.delete_agent(agent_id)
    return {"success": success, "deleted_agent_id": agent_id}
