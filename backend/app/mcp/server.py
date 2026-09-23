"""Model Context Protocol (MCP) server integration for Coordin8.

Provides standard MCP tool endpoints and JSON-RPC stdio transport for OpenWorker integration.
Conforms to Milestone 9 of ProjectDetails.md.
"""

import json
import sys
from typing import Any

from app.core.logging import logger
from app.mcp.tools import Coordin8Tools


class MCPServer:
    """Provides standard MCP tool endpoints for OpenWorker integration."""

    def __init__(
        self,
        name: str = "coordin8-knowledge-server",
        tools: Coordin8Tools | None = None,
    ) -> None:
        self.name = name
        self.tools = tools or Coordin8Tools()

    def list_tools(self) -> list[dict[str, Any]]:
        """Return list of available MCP tools and their parameter schemas."""
        return [
            {
                "name": "create_knowledge_base",
                "description": "Create a new isolated vector database and knowledge repository",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "kb_id": {"type": "string", "description": "Unique identifier for this knowledge base"}
                    },
                    "required": ["kb_id"],
                },
            },
            {
                "name": "list_knowledge_bases",
                "description": "List all active knowledge bases",
                "input_schema": {"type": "object", "properties": {}},
            },
            {
                "name": "ingest_document",
                "description": "Ingest and index a local file into a knowledge base",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "file_path": {"type": "string", "description": "Path to document file"},
                        "kb_id": {"type": "string", "description": "Target knowledge base id", "default": "default"},
                        "title": {"type": "string", "description": "Optional custom document title"},
                    },
                    "required": ["file_path"],
                },
            },
            {
                "name": "search_knowledge",
                "description": "Search the multimodal knowledge base hierarchically",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "kb_id": {"type": "string", "description": "Target knowledge base id", "default": "default"},
                        "limit": {"type": "integer", "description": "Number of results to return", "default": 5},
                        "document_id": {"type": "string", "description": "Optional document filter"},
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "query_context",
                "description": "Retrieve grounded citation prompt context ready for LLMs",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Query to retrieve evidence for"},
                        "kb_id": {"type": "string", "description": "Target knowledge base id", "default": "default"},
                        "limit": {"type": "integer", "description": "Max evidence blocks", "default": 5},
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "find_documents",
                "description": "Find relevant documents by summary and topic",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "kb_id": {"type": "string", "description": "Target knowledge base id", "default": "default"},
                        "modalities": {"type": "array", "items": {"type": "string"}, "description": "Modality filters"},
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "read_document",
                "description": "Read normalized markdown for a document",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "document_id": {"type": "string", "description": "Document identifier"},
                        "kb_id": {"type": "string", "description": "Target knowledge base id", "default": "default"},
                    },
                    "required": ["document_id"],
                },
            },
            {
                "name": "read_section",
                "description": "Read section chunks and provenance for a document",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "document_id": {"type": "string"},
                        "section_id": {"type": "string"},
                        "kb_id": {"type": "string", "default": "default"},
                    },
                    "required": ["document_id", "section_id"],
                },
            },
            {
                "name": "analyze_spreadsheet",
                "description": "Perform safe calculations on spreadsheet data",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "document_id": {"type": "string"},
                        "sheet_name": {"type": "string"},
                        "operation": {"type": "string", "enum": ["sum", "average", "count", "min", "max", "filter"]},
                        "column": {"type": "string"},
                        "kb_id": {"type": "string", "default": "default"},
                    },
                    "required": ["document_id", "sheet_name", "operation", "column"],
                },
            },
        ]

    def call_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute a tool call by name with given arguments."""
        kb_id = arguments.get("kb_id", "default")
        try:
            if name == "create_knowledge_base":
                return self.tools.create_knowledge_base(kb_id=arguments["kb_id"])
            elif name == "list_knowledge_bases":
                return self.tools.list_knowledge_bases()
            elif name == "ingest_document":
                return self.tools.ingest_document(
                    file_path=arguments["file_path"],
                    kb_id=kb_id,
                    title=arguments.get("title"),
                )
            elif name == "search_knowledge":
                return self.tools.search_knowledge(
                    query=arguments["query"],
                    kb_id=kb_id,
                    limit=arguments.get("limit", 5),
                    document_id=arguments.get("document_id"),
                )
            elif name == "query_context":
                return self.tools.query_context(
                    query=arguments["query"],
                    kb_id=kb_id,
                    limit=arguments.get("limit", 5),
                )
            elif name == "find_documents":
                return self.tools.find_documents(
                    query=arguments["query"],
                    kb_id=kb_id,
                    modalities=arguments.get("modalities"),
                )
            elif name == "read_document":
                return self.tools.read_document(
                    document_id=arguments["document_id"],
                    kb_id=kb_id,
                )
            elif name == "read_section":
                return self.tools.read_section(
                    document_id=arguments["document_id"],
                    section_id=arguments["section_id"],
                    kb_id=kb_id,
                )
            elif name == "analyze_spreadsheet":
                return self.tools.analyze_spreadsheet(
                    document_id=arguments["document_id"],
                    sheet_name=arguments["sheet_name"],
                    operation=arguments["operation"],
                    column=arguments["column"],
                    kb_id=kb_id,
                )
            else:
                return {"error": f"Unknown tool: '{name}'"}
        except Exception as exc:
            logger.exception("Error executing MCP tool %s: %s", name, exc)
            return {"error": str(exc)}

    def run_stdio_loop(self) -> None:
        """Run standard MCP stdio loop for OpenWorker / Claude Desktop IPC."""
        logger.info("Starting Coordin8 MCP Server stdio loop...")
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            try:
                request = json.loads(line)
                method = request.get("method")
                req_id = request.get("id")

                if method == "tools/list":
                    response = {"jsonrpc": "2.0", "id": req_id, "result": {"tools": self.list_tools()}}
                elif method == "tools/call":
                    params = request.get("params", {})
                    tool_name = params.get("name")
                    arguments = params.get("arguments", {})
                    result = self.call_tool(tool_name, arguments)
                    response = {"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": json.dumps(result)}]}}
                else:
                    response = {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Method '{method}' not found"}}

                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()
            except Exception as exc:
                err_resp = {"jsonrpc": "2.0", "error": {"code": -32700, "message": str(exc)}}
                sys.stdout.write(json.dumps(err_resp) + "\n")
                sys.stdout.flush()


if __name__ == "__main__":
    server = MCPServer()
    server.run_stdio_loop()
