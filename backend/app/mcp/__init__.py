"""MCP package for Coordin8."""

from typing import Any
from app.mcp.tools import Coordin8Tools


def __getattr__(name: str) -> Any:
    if name == "MCPServer":
        from app.mcp.server import MCPServer
        return MCPServer
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ["MCPServer", "Coordin8Tools"]
