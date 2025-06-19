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

class KnowledgeMCPServer(BaseMCPServer):
    """
    MCP Server for Knowledge Base operations.
    Provides tools for document ingestion, querying, and management.
    """

    def __init__(self):
        super().__init__("knowledge_base")
        self.vector_store = None
        self.metadata_store = None
        self.ingestion_pipeline = None

    async def initialize_integration(self):
        """Initialize the Knowledge Base components."""
        try:
            self.vector_store = VectorStore()
            await self.vector_store.initialize()
            
            self.metadata_store = MetadataStore()
            
            self.ingestion_pipeline = IngestionPipeline(
                vector_store=self.vector_store,
                metadata_store=self.metadata_store
            )
            
            self.integration_client = {
                "vector_store": self.vector_store,
                "metadata_store": self.metadata_store,
                "ingestion_pipeline": self.ingestion_pipeline
            }
            
            self.logger.info("Knowledge Base integration initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Knowledge Base integration: {e}")
            raise

    async def list_resources(self, request: any) -> List[Resource]:
        """Knowledge Base server is tool-focused."""
        return []

    async def get_resource(self, request: any) -> str:
        """Knowledge Base server is tool-focused."""
        return json.dumps({"error": "This server does not provide resources, only tools."})

    async def list_tools(self, request: ListToolsRequest) -> List[Tool]:
        """List available Knowledge Base tools."""
        return [
            Tool(
                name="ingest_document",
                description="Ingest a document into the knowledge base",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the document file"
                        },
                        "document_type": {
                            "type": "string",
                            "description": "Type of document (e.g., 'sales_deck', 'employee_handbook')"
                        },
                        "tags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Tags to associate with the document"
                        }
                    },
                    "required": ["file_path", "document_type"]
                }
            ),
            Tool(
                name="query_knowledge",
                description="Query the knowledge base for information",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Natural language query"
                        },
                        "top_k": {
                            "type": "integer",
                            "description": "Maximum number of results to return",
                            "default": 5
                        },
                        "filters": {
                            "type": "object",
                            "description": "Metadata filters to apply",
                            "properties": {
                                "document_type": {"type": "string"},
                                "tags": {"type": "array", "items": {"type": "string"}}
                            }
                        }
                    },
                    "required": ["query"]
                }
            ),
            Tool(
                name="list_documents",
                description="List all documents in the knowledge base",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "document_type": {
                            "type": "string",
                            "description": "Filter by document type"
                        },
                        "tags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Filter by tags"
                        }
                    }
                }
            ),
            Tool(
                name="get_document_info",
                description="Get detailed information about a specific document",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "document_id": {
                            "type": "string",
                            "description": "Document ID"
                        }
                    },
                    "required": ["document_id"]
                }
            ),
            Tool(
                name="delete_document",
                description="Delete a document from the knowledge base",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "document_id": {
                            "type": "string",
                            "description": "Document ID to delete"
                        }
                    },
                    "required": ["document_id"]
                }
            )
        ]

    async def call_tool(self, request: CallToolRequest) -> List[TextContent]:
        """Handle tool calls for Knowledge Base operations."""
        tool_name = request.params.name
        arguments = request.params.arguments or {}

        try:
            if tool_name == "ingest_document":
                result = await self._ingest_document(arguments)
            elif tool_name == "query_knowledge":
                result = await self._query_knowledge(arguments)
            elif tool_name == "list_documents":
                result = await self._list_documents(arguments)
            elif tool_name == "get_document_info":
                result = await self._get_document_info(arguments)
            elif tool_name == "delete_document":
                result = await self._delete_document(arguments)
            else:
                result = {"error": f"Unknown tool: {tool_name}"}

            return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]

        except Exception as e:
            self.logger.error(f"Knowledge Base tool execution failed: {e}")
            error_result = {"error": f"Tool execution failed: {str(e)}"}
            return [TextContent(type="text", text=json.dumps(error_result))]

    async def _ingest_document(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Ingest a document into the knowledge base."""
        file_path = Path(arguments["file_path"])
        document_type = arguments["document_type"]
        tags = arguments.get("tags", [])

        if not file_path.exists():
            return {"error": f"File not found: {file_path}"}

        try:
            await self.ingestion_pipeline.ingest_document(
                file_path=file_path,
                document_type=document_type,
                tags=tags
            )
            
            return {
                "success": True,
                "message": f"Document {file_path.name} ingested successfully",
                "file_name": file_path.name,
                "document_type": document_type,
                "tags": tags
            }
        except Exception as e:
            return {"error": f"Ingestion failed: {str(e)}"}

    async def _query_knowledge(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Query the knowledge base."""
        query = arguments["query"]
        top_k = arguments.get("top_k", 5)
        filters = arguments.get("filters", {})

        try:
            # Convert filters to Pinecone format
            pinecone_filters = {}
            if "document_type" in filters:
                pinecone_filters["document_type"] = filters["document_type"]
            if "tags" in filters:
                # For tags, we might need to check if any of the provided tags match
                # This depends on how tags are stored in metadata
                pinecone_filters["tags"] = {"$in": filters["tags"]}

            results = await self.vector_store.query(
                query_text=query,
                top_k=top_k,
                filter_dict=pinecone_filters if pinecone_filters else None
            )

            return {
                "success": True,
                "query": query,
                "results": results,
                "count": len(results)
            }
        except Exception as e:
            return {"error": f"Query failed: {str(e)}"}

    async def _list_documents(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """List documents in the knowledge base."""
        document_type = arguments.get("document_type")
        tags = arguments.get("tags", [])

        try:
            documents = self.metadata_store.list_documents(
                document_type=document_type,
                tags=tags
            )
            
            return {
                "success": True,
                "documents": [
                    {
                        "document_id": doc.document_id,
                        "file_name": doc.file_name,
                        "document_type": doc.document_type,
                        "tags": doc.tags,
                        "created_at": doc.created_at.isoformat() if doc.created_at else None
                    }
                    for doc in documents
                ],
                "count": len(documents)
            }
        except Exception as e:
            return {"error": f"Failed to list documents: {str(e)}"}

    async def _get_document_info(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed information about a document."""
        document_id = arguments["document_id"]

        try:
            document = self.metadata_store.get_document(document_id)
            if not document:
                return {"error": f"Document not found: {document_id}"}

            chunks = self.metadata_store.get_chunks_for_document(document_id)
            
            return {
                "success": True,
                "document": {
                    "document_id": document.document_id,
                    "file_name": document.file_name,
                    "document_type": document.document_type,
                    "tags": document.tags,
                    "source": document.source,
                    "created_at": document.created_at.isoformat() if document.created_at else None
                },
                "chunks_count": len(chunks),
                "chunks": [
                    {
                        "content_preview": chunk.content[:200] + "..." if len(chunk.content) > 200 else chunk.content,
                        "metadata": chunk.metadata
                    }
                    for chunk in chunks[:5]  # Show first 5 chunks
                ]
            }
        except Exception as e:
            return {"error": f"Failed to get document info: {str(e)}"}

    async def _delete_document(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a document from the knowledge base."""
        document_id = arguments["document_id"]

        try:
            # Get document info first
            document = self.metadata_store.get_document(document_id)
            if not document:
                return {"error": f"Document not found: {document_id}"}

            # Delete from metadata store
            chunks = self.metadata_store.get_chunks_for_document(document_id)
            self.metadata_store.delete_document(document_id)

            # Delete from vector store (if it supports deletion)
            # Note: This would need to be implemented in the VectorStore class
            # For now, we'll just note that vectors should be deleted
            
            return {
                "success": True,
                "message": f"Document {document.file_name} deleted successfully",
                "document_id": document_id,
                "chunks_deleted": len(chunks)
            }
        except Exception as e:
            return {"error": f"Failed to delete document: {str(e)}"}


async def main():
    """Run the Knowledge Base MCP Server."""
    setup_logging()
    server = KnowledgeMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main()) 