"""
Knowledge Base MCP Server
Exposes the knowledge base search and ingestion capabilities to the Sophia AI system.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List
from pathlib import Path

from mcp.types import Resource, Tool, TextContent, CallToolRequest, GetResourceRequest, ListResourcesRequest, ListToolsRequest

from backend.mcp.base_mcp_server import BaseMCPServer, setup_logging
from backend.knowledge_base.query import QueryEngine
from backend.knowledge_base.ingestion import IngestionPipeline
from backend.knowledge_base.vector_store import VectorStore
from backend.knowledge_base.metadata_store import MetadataStore

class KnowledgeMCPServer(BaseMCPServer):
    """
    MCP Server for the Knowledge Base.
    """

    def __init__(self):
        super().__init__("knowledge")
        self.query_engine = None
        self.ingestion_pipeline = None

    async def initialize_integration(self):
        """Initializes the knowledge base components."""
        vector_store = VectorStore()
        metadata_store = MetadataStore()
        # The integration client will be the query engine
        self.query_engine = QueryEngine(vector_store, metadata_store)
        self.ingestion_pipeline = IngestionPipeline(vector_store, metadata_store)
        self.integration_client = self.query_engine
        
        # Ensure the vector store is initialized
        await vector_store.initialize()

    async def list_resources(self, request: ListResourcesRequest) -> List[Resource]:
        """Lists available knowledge base resources."""
        return [
            Resource(
                uri="knowledge://stats",
                name="Knowledge Base Stats",
                description="Statistics about the documents and chunks in the knowledge base.",
                mimeType="application/json"
            )
        ]

    async def get_resource(self, request: GetResourceRequest) -> str:
        """Gets a specific knowledge base resource."""
        if request.uri == "knowledge://stats":
            stats = {
                "documents": len(self.query_engine.metadata_store.documents),
                "chunks": len(self.query_engine.metadata_store.chunks),
            }
            return json.dumps(stats, indent=2)
        else:
            return json.dumps({"error": f"Unknown resource: {request.uri}"})

    async def list_tools(self, request: ListToolsRequest) -> List[Tool]:
        """Lists available knowledge base tools."""
        return [
            Tool(
                name="search",
                description="Search the knowledge base with a natural language query and optional filters.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "top_k": {"type": "integer", "default": 5},
                        "filters": {"type": "object", "description": "Key-value pairs for metadata filtering."}
                    }, "required": ["query"]}
            ),
            Tool(
                name="ingest_document",
                description="Ingest a new document into the knowledge base.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "file_path": {"type": "string", "description": "The local path to the document file."},
                        "document_type": {"type": "string", "description": "A category for the document, e.g., 'sales_deck'."},
                        "tags": {"type": "array", "items": {"type": "string"}}
                    }, "required": ["file_path", "document_type"]}
            )
        ]

    async def call_tool(self, request: CallToolRequest) -> List[TextContent]:
        """Handles a knowledge base tool call."""
        tool_name = request.params.name
        args = request.params.arguments or {}
        result = None

        if tool_name == "search":
            result = await self.query_engine.search(
                query_text=args["query"],
                top_k=args.get("top_k", 5),
                filters=args.get("filters")
            )
        elif tool_name == "ingest_document":
            file_path = Path(args["file_path"])
            if not file_path.exists():
                result = {"error": f"File not found: {file_path}"}
            else:
                await self.ingestion_pipeline.ingest_document(
                    file_path=file_path,
                    document_type=args["document_type"],
                    tags=args.get("tags", [])
                )
                result = {"success": True, "message": f"Successfully started ingestion for {file_path.name}."}
        else:
            result = {"error": f"Unknown tool: {tool_name}"}

        return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]

async def main():
    """Main entry point for the Knowledge Base MCP server."""
    setup_logging()
    server = KnowledgeMCPServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main()) 