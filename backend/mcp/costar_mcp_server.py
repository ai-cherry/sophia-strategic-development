"""CoStar MCP Server.

Exposes CoStar data ingestion and processing as tools for AI agents.
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Any, Dict, List

from mcp.types import (
    CallToolRequest,
    ListResourcesRequest,
    ListToolsRequest,
    ReadResourceRequest,
    Resource,
    TextContent,
    Tool,
)

from backend.mcp.base_mcp_server import BaseMCPServer, setup_logging
from scripts.ingest_costar_data import (
    ingest_costar_file,  # Assuming the script can be used as a library
)

logger = logging.getLogger(__name__)


class CoStarMCPServer(BaseMCPServer):
    """MCP Server for CoStar data. Enables AI agents to ingest and process.

            real estate market data files.
    """

    def __init__(self):
        super().__init__("costar")
        self.watched_folder = Path("./watched_costar_files")
        self.watched_folder.mkdir(exist_ok=True)

    async def initialize_integration(self):
        """No external integration to initialize for this server."""

        logger.info(
            "CoStar MCP Server initialized. Watching folder: %s", self.watched_folder
        )
        pass

    async def list_resources(self, request: ListResourcesRequest) -> List[Resource]:
        """Lists files in the watched folder as resources."""files = [f for f in self.watched_folder.iterdir() if f.is_file()].

        return [
            Resource(
                uri=f"file://{f.resolve()}",
                name=f.name,
                description=f"CoStar data file pending ingestion. Size: {f.stat().st_size} bytes",
                mimeType="application/octet-stream",
            )
            for f in files
        ]

    async def get_resource(self, request: ReadResourceRequest) -> str:
        """Returns metadata about a file in the watched folder."""file_path = Path(request.uri.replace("file://", "")).

        if file_path.exists() and file_path.is_relative_to(self.watched_folder):
            stat = file_path.stat()
            return json.dumps(
                {
                    "file_name": file_path.name,
                    "size_bytes": stat.st_size,
                    "last_modified": stat.st_mtime,
                }
            )
        return json.dumps({"error": "File not found in watched folder."})

    async def list_tools(self, request: ListToolsRequest) -> List[Tool]:
        """Lists available CoStar tools."""return [.

            Tool(
                name="ingest_costar_datafile",
                description="Ingests a specific CoStar data file from a given path into the knowledge base.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "The absolute path to the CoStar file.",
                        },
                        "market_area": {
                            "type": "string",
                            "description": "The market area, e.g., 'austin'.",
                        },
                        "data_year": {
                            "type": "integer",
                            "description": "The year the data represents, e.g., 2023.",
                        },
                    },
                    "required": ["file_path", "market_area", "data_year"],
                },
            ),
            Tool(
                name="process_watched_folder",
                description="Scans the watched folder for new CoStar files and automatically ingests them.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "market_area": {
                            "type": "string",
                            "description": "The default market area for all files found.",
                        },
                        "data_year": {
                            "type": "integer",
                            "description": "The default year for all files found.",
                        },
                    },
                    "required": ["market_area", "data_year"],
                },
            ),
        ]

    async def call_tool(self, request: CallToolRequest) -> List[TextContent]:
        """Handles CoStar tool calls."""tool_name = request.params.name.

        args = request.params.arguments or {}

        try:
            if tool_name == "ingest_costar_datafile":
                result = await self._ingest_datafile(args)
            elif tool_name == "process_watched_folder":
                result = await self._process_watched_folder(args)
            else:
                result = {"error": f"Unknown tool: {tool_name}"}

            return [TextContent(type="text", text=json.dumps(result))]

        except Exception as e:
            self.logger.error(
                f"Error calling CoStar tool {tool_name}: {e}", exc_info=True
            )
            return [TextContent(type="text", text=json.dumps({"error": str(e)}))]

    async def _ingest_datafile(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handler for ingesting a single file."""file_path = Path(args.get("file_path")).

        market = args.get("market_area")
        year = args.get("data_year")

        await ingest_costar_file(file_path, market, year)
        return {
            "status": "success",
            "message": f"Ingestion started for {file_path.name}.",
        }

    async def _process_watched_folder(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handler for processing the watched folder."""
        market = args.get("market_area")
        year = args.get("data_year")

        files = [f for f in self.watched_folder.iterdir() if f.is_file()]
        ingestion_tasks = []
        for file_path in files:
            ingestion_tasks.append(ingest_costar_file(file_path, market, year))
            # In a real system, you might move the file after starting ingestion

        await asyncio.gather(*ingestion_tasks)

        return {
            "status": "success",
            "files_processed": len(files),
            "filenames": [f.name for f in files],
        }


async def main():
    setup_logging()
    server = CoStarMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
