"""
Lightweight MCP Shim
Replaces anthropic-mcp-python-sdk with a minimal FastAPI-based implementation
"""

from collections.abc import Callable
from functools import wraps
from typing import Any

import structlog
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = structlog.get_logger(__name__)

# Global registry for MCP tools
_mcp_tools_registry: dict[str, dict[str, Any]] = {}

# Create a router for MCP endpoints
router = APIRouter(prefix="/mcp", tags=["MCP Tools"])


class MCPToolRequest(BaseModel):
    """Standard MCP tool request format"""

    tool_name: str
    parameters: dict[str, Any] = Field(default_factory=dict)
    context: dict[str, Any] | None = Field(default_factory=dict)


class MCPToolResponse(BaseModel):
    """Standard MCP tool response format"""

    success: bool
    result: Any | None = None
    error: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


def mcp_tool(*, name: str, description: str, parameters: dict[str, Any] | None = None):
    """
    Decorator to register a function as an MCP tool

    Args:
        name: Tool name (must be unique)
        description: Human-readable description
        parameters: Optional parameter schema
    """

    def decorator(func: Callable) -> Callable:
        # Register the tool
        _mcp_tools_registry[name] = {
            "name": name,
            "description": description,
            "parameters": parameters or {},
            "function": func,
            "module": func.__module__,
            "qualname": func.__qualname__,
        }

        # Create FastAPI endpoint
        @router.post(f"/tools/{name}", response_model=MCPToolResponse)
        @wraps(func)
        async def wrapper(request: MCPToolRequest) -> MCPToolResponse:
            try:
                # Validate tool name
                if request.tool_name != name:
                    raise ValueError(
                        f"Tool name mismatch: {request.tool_name} != {name}"
                    )

                # Log invocation
                logger.info(
                    "mcp_tool_invoked", tool_name=name, parameters=request.parameters
                )

                # Call the actual function
                if func.__code__.co_flags & 0x80:  # Check if async
                    result = await func(**request.parameters)
                else:
                    result = func(**request.parameters)

                return MCPToolResponse(
                    success=True,
                    result=result,
                    metadata={"tool_name": name, "module": func.__module__},
                )

            except Exception as e:
                logger.error(
                    "mcp_tool_error", tool_name=name, error=str(e), exc_info=True
                )
                return MCPToolResponse(
                    success=False, error=str(e), metadata={"tool_name": name}
                )

        # Preserve original function for direct calls
        wrapper.original = func
        wrapper.mcp_metadata = _mcp_tools_registry[name]

        return wrapper

    return decorator


@router.get("/tools", response_model=list[dict[str, Any]])
async def list_mcp_tools():
    """List all registered MCP tools"""
    tools = []
    for name, metadata in _mcp_tools_registry.items():
        tools.append(
            {
                "name": name,
                "description": metadata["description"],
                "parameters": metadata["parameters"],
                "module": metadata["module"],
            }
        )
    return tools


@router.get("/tools/{tool_name}", response_model=dict[str, Any])
async def get_mcp_tool(tool_name: str):
    """Get metadata for a specific MCP tool"""
    if tool_name not in _mcp_tools_registry:
        raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")

    metadata = _mcp_tools_registry[tool_name].copy()
    metadata.pop("function")  # Don't expose the function object
    return metadata


class MCPServer:
    """
    Base class for MCP servers
    Provides common functionality for all MCP server implementations
    """

    def __init__(self, name: str, version: str = "1.0.0"):
        self.name = name
        self.version = version
        self.tools: dict[str, Callable] = {}
        self.logger = structlog.get_logger(name)

    def register_tool(self, func: Callable, name: str | None = None):
        """Register a tool function"""
        tool_name = name or func.__name__
        self.tools[tool_name] = func
        self.logger.info(f"Registered tool: {tool_name}")

    def get_tool(self, name: str) -> Callable | None:
        """Get a registered tool by name"""
        return self.tools.get(name)

    def list_tools(self) -> list[str]:
        """List all registered tool names"""
        return list(self.tools.keys())

    async def handle_request(self, request: MCPToolRequest) -> MCPToolResponse:
        """Handle an incoming MCP tool request"""
        tool = self.get_tool(request.tool_name)

        if not tool:
            return MCPToolResponse(
                success=False,
                error=f"Tool '{request.tool_name}' not found in server '{self.name}'",
            )

        try:
            # Execute the tool
            if tool.__code__.co_flags & 0x80:  # Async function
                result = await tool(**request.parameters)
            else:
                result = tool(**request.parameters)

            return MCPToolResponse(
                success=True,
                result=result,
                metadata={
                    "server": self.name,
                    "version": self.version,
                    "tool": request.tool_name,
                },
            )

        except Exception as e:
            self.logger.error(
                "tool_execution_error",
                tool=request.tool_name,
                error=str(e),
                exc_info=True,
            )
            return MCPToolResponse(
                success=False,
                error=str(e),
                metadata={"server": self.name, "tool": request.tool_name},
            )


# Compatibility exports
__all__ = [
    "MCPServer",
    "MCPToolRequest",
    "MCPToolResponse",
    "get_mcp_tool",
    "list_mcp_tools",
    "mcp_tool",
    "router",
]
