"""
Knowledge Base MCP Server
Exposes the Knowledge Base system to the Sophia AI MCP architecture.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List
from pathlib import Path

from mcp.types import Resource, Tool, TextContent, CallToolRequest, ListToolsRequest

from backend.mcp.base_mcp_server import BaseMCPServer, setup_logging
from backend.knowledge_base.vector_store import VectorStore
from backend.knowledge_base.metadata_store import MetadataStore
from backend.knowledge_base.ingestion import IngestionPipeline
from backend.knowledge.knowledge_manager import knowledge_manager
from backend.knowledge.hybrid_rag_manager import hybrid_rag_manager

class KnowledgeMCPServer(BaseMCPServer):
    """
    MCP Server for Sophia's Knowledge Base.
    """
    def __init__(self):
        super().__init__("knowledge") # Renamed for clarity

    async def initialize_integration(self):
        """Initializes the knowledge managers."""
        # We only need to initialize the managers, not the legacy stores
        await knowledge_manager.initialize()
        await hybrid_rag_manager.initialize()
        self.integration_client = {
            "knowledge_manager": knowledge_manager,
            "rag_manager": hybrid_rag_manager
        }
        self.logger.info("Knowledge MCP Server initialized successfully.")

    # ... list_resources and get_resource can be simplified or removed if truly tool-focused
    async def list_resources(self, request: ListResourcesRequest) -> List[Resource]:
        return []

    async def get_resource(self, request: ReadResourceRequest) -> str:
        return json.dumps({"error": "This server is tool-focused."})


    async def list_tools(self, request: ListToolsRequest) -> List[Tool]:
        """Lists available Knowledge Base tools."""
        ingestion_tools = [
            # Tools from knowledge_manager like ingest_document, delete_document etc. go here
            # This is a simplified representation
            Tool(name="ingest_document", description="Ingests a document."),
            Tool(name="delete_document", description="Deletes a document."),
            Tool(name="list_documents", description="Lists documents."),
        ]
        
        rag_tool = Tool(
            name="answer_complex_question",
            description="Answers a complex question by retrieving and reasoning over both structured and unstructured data.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The natural language question to answer."
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "Number of documents to retrieve.",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        )
        return ingestion_tools + [rag_tool]

    async def call_tool(self, request: CallToolRequest) -> List[TextContent]:
        """Handles Knowledge Base tool calls."""
        tool_name = request.params.name
        arguments = request.params.arguments or {}
        
        try:
            if tool_name == "answer_complex_question":
                result = await hybrid_rag_manager.answer_complex_question(
                    query=arguments.get("query"),
                    top_k=arguments.get("top_k", 5)
                )
            else:
                # Delegate all other tools to the primary knowledge manager
                result = await knowledge_manager.call_tool(tool_name, arguments)
            
            return [TextContent(type="text", text=json.dumps(result, default=str))]

        except Exception as e:
            self.logger.error(f"Error calling tool {tool_name}: {e}", exc_info=True)
            return [TextContent(type="text", text=json.dumps({"error": str(e)}))]

async def main():
    """Run the Knowledge Base MCP Server."""
    setup_logging()
    server = KnowledgeMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main()) 