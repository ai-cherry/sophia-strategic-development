"""Codebase Awareness MCP Server.

Provides tools for AI assistants to understand the Sophia codebase architecture.
"""

import asyncio
import json
from pathlib import Path
from typing import List

from mcp.types import CallToolRequest, ListToolsRequest, Resource, TextContent, Tool

from backend.codebase_awareness.code_ingestion import CodebaseIngestionPipeline
from backend.knowledge_base.metadata_store import MetadataStore
from backend.knowledge_base.vector_store import VectorStore
from backend.mcp.base_mcp_server import BaseMCPServer, setup_logging


class CodebaseAwarenessMCPServer(BaseMCPServer):
    """MCP Server that provides structured, searchable access to the codebase itself."""

    CODEBASE_INDEX_NAME = "sophia-codebase-awareness"

    def __init__(self):
        super().__init__("codebase_awareness")
        self.vector_store = None
        self.ingestion_pipeline = None

    async def initialize_integration(self):
        """Initializes the components for codebase awareness."""self.vector_store = VectorStore().

        self.vector_store.INDEX_NAME = self.CODEBASE_INDEX_NAME

        # This server doesn't need a persistent metadata store for now,
        # as all relevant metadata is stored in Pinecone with the vectors.
        metadata_store = MetadataStore()

        project_root = Path(__file__).parent.parent.parent
        self.ingestion_pipeline = CodebaseIngestionPipeline(
            self.vector_store, metadata_store, project_root
        )

        # The integration client is the vector store itself
        self.integration_client = self.vector_store
        await self.vector_store.initialize()

    async def list_resources(self, request: any) -> List[Resource]:
        return []  # This server is tool-focused

    async def get_resource(self, request: any) -> str:
        return json.dumps(
            {"error": "This server does not provide resources, only tools."}
        )

    async def list_tools(self, request: ListToolsRequest) -> List[Tool]:
        """Lists the specialized tools for codebase awareness."""return [.

            Tool(
                name="find_relevant_code",
                description="Performs semantic search for code components (functions, classes, APIs, etc.).",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Natural language query describing the desired code.",
                        },
                        "top_k": {"type": "integer", "default": 5},
                        "item_type": {
                            "type": "string",
                            "description": "Optional filter by item type (e.g., 'python_function', 'api_endpoint').",
                        },
                    },
                    "required": ["query"],
                },
            ),
            Tool(
                name="get_file_summary",
                description="Summarizes the purpose and components of a specific code file.",
                inputSchema={
                    "type": "object",
                    "properties": {"file_path": {"type": "string"}},
                    "required": ["file_path"],
                },
            ),
            Tool(
                name="ingest_codebase",
                description="Triggers a full scan and ingestion of the entire project codebase.",
                inputSchema={"type": "object", "properties": {}},
            ),
        ]

    async def call_tool(self, request: CallToolRequest) -> List[TextContent]:
        """Handles a tool call for codebase awareness."""tool_name = request.params.name.

        args = request.params.arguments or {}
        result = None

        if tool_name == "find_relevant_code":
            filters = None
            if args.get("item_type"):
                filters = {"type": args.get("item_type")}

            search_results = await self.vector_store.query(
                query_text=args["query"],
                top_k=args.get("top_k", 5),
                filter_dict=filters,
            )
            # Format for readability
            result = [
                f"Found in {res['metadata']['file_path']}:\nScore: {res['score']:.4f}\nContent: {res['content']}\n---"
                for res in search_results
            ]
            result = "\n".join(result) if result else "No relevant code found."

        elif tool_name == "ingest_codebase":
            # This can be a long-running task. We start it but don't wait.
            asyncio.create_task(self.ingestion_pipeline.ingest_codebase())
            result = {
                "status": "success",
                "message": "Codebase ingestion process started in the background.",
            }

        elif tool_name == "get_file_summary":
            # This would require an LLM call to summarize. For now, we'll return file components.
            # A full implementation would use the BrainAgent's Portkey client.
            file_path = Path(args["file_path"])
            if not file_path.exists():
                result = {"error": "File not found."}
            else:
                content = file_path.read_text(encoding="utf-8")
                components = ArchitectureParser.parse_python_code(
                    content, str(file_path)
                )
                result = {
                    "file_path": str(file_path),
                    "summary": f"File contains {len(components)} functions/classes.",
                    "components": [
                        f"{item['type']}: {item['name']}" for item in components
                    ],
                }
        else:
            result = {"error": f"Unknown tool: {tool_name}"}

        # Ensure the result is a JSON-serializable string
        if not isinstance(result, str):
            result = json.dumps(result, indent=2)

        return [TextContent(type="text", text=result)]


async def main():
    """Main entry point for the Codebase Awareness MCP server."""
    setup_logging()
    server = CodebaseAwarenessMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
