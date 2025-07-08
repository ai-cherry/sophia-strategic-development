"""Canonical base class for all MCP servers."""
from fastapi import FastAPI


class StandardizedMCPServer:
    """Simple FastAPI-based MCP server with a health route."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.app = FastAPI(title=f"{name} MCP Server")
        self._add_routes()

    def _add_routes(self) -> None:
        @self.app.get("/health")
        async def health() -> dict[str, str]:
            return {"status": "healthy", "server": self.name}
