"""Model Context Protocol (MCP) server integration for Coordin8."""

from typing import Any
from app.core.logging import logger
from app.mcp.tools import Coordin8Tools


class MCPServer:
    """Provides standard MCP tool endpoints for OpenWorker integration."""

    def __init__(self, name: str = "coordin8-knowledge-server") -> None:
        self.name = name

    def list_tools(self) -> list[dict[str, Any]]:
        """Return list of available MCP tools and their parameter schemas."""
        return [
            {
                "name": "search_knowledge",
                "description": "Search the multimodal knowledge base hierarchically",
                "input_schema": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
            },
            {
                "name": "find_documents",
                "description": "Find relevant documents by summary",
                "input_schema": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
            },
            {
                "name": "read_document",
                "description": "Read normalized markdown for a document",
                "input_schema": {"type": "object", "properties": {"document_id": {"type": "string"}}, "required": ["document_id"]},
            },
            {
                "name": "analyze_spreadsheet",
                "description": "Perform safe calculations on spreadsheet data",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "document_id": {"type": "string"},
                        "sheet_name": {"type": "string"},
                        "operation": {"type": "string"},
                        "column": {"type": "string"},
                    },
                    "required": ["document_id", "sheet_name", "operation", "column"],
                },
            },
        ]
