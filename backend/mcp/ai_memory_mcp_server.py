"""
AI Memory MCP Server for persistent development context.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

# Optional dependencies for embeddings and vector search
import pinecone
from openai import AsyncOpenAI

from backend.core.comprehensive_memory_manager import ComprehensiveMemoryManager
from backend.core.contextual_memory_intelligence import ContextualMemoryIntelligence
from backend.core.hierarchical_cache import HierarchicalCache

logger = logging.getLogger(__name__)


class MemoryCategory:
    """Categories for AI memory storage."""

    ARCHITECTURE = "architecture"
    BUG_SOLUTION = "bug_solution"
    CODE_DECISION = "code_decision"
    WORKFLOW = "workflow"


class MemoryRecord(BaseModel):
    """Model for a memory record."""

    id: str
    content: str
    category: str
    tags: List[str]
    embedding: Optional[List[float]] = None
    created_at: datetime = datetime.now()


class AiMemoryMCPServer:
    """AI Memory MCP Server for persistent development context."""

    def __init__(self) -> None:
        self.name = "ai_memory"
        self.description = "AI Memory for persistent development context"
        self.memory_manager = ComprehensiveMemoryManager()
        self.memory_intelligence = ContextualMemoryIntelligence(self.memory_manager)
        self.cache = HierarchicalCache()
        self.openai_client: Optional[AsyncOpenAI] = None
        self.pinecone_index: Optional[pinecone.Index] = None
        self.initialized = False

    async def initialize(self) -> None:
        """Initialize connections and prepare the server."""
        if self.initialized:
            return

        logger.info("Initializing AI Memory MCP Server...")

        openai_api_key = os.getenv("OPENAI_API_KEY")
        if openai_api_key:
            self.openai_client = AsyncOpenAI(api_key=openai_api_key)

        pinecone_api_key = os.getenv("PINECONE_API_KEY")
        pinecone_environment = os.getenv("PINECONE_ENVIRONMENT", "us-east1-gcp")
        if pinecone_api_key:
            pinecone.init(api_key=pinecone_api_key, environment=pinecone_environment)
            index_name = "sophia-ai-memory"
            if index_name not in pinecone.list_indexes():
                pinecone.create_index(
                    name=index_name,
                    dimension=1536,
                    metric="cosine",
                )
            self.pinecone_index = pinecone.Index(index_name)

        self.initialized = True
        logger.info("AI Memory MCP Server initialized successfully")

    async def get_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using OpenAI."""
        if not self.openai_client:
            return []

        try:
            response = await self.openai_client.embeddings.create(
                input=text,
                model="text-embedding-ada-002",
            )
            return response.data[0].embedding
        except Exception as exc:  # pragma: no cover - network failure
            logger.error(f"Error generating embedding: {str(exc)}")
            return []

    async def store_memory(self, content: str, category: str, tags: List[str]) -> Dict[str, Any]:
        """Store a memory with categorization and embedding."""
        if not self.initialized:
            await self.initialize()

        memory_id = f"{category}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        embedding = await self.get_embedding(content)

        memory = MemoryRecord(
            id=memory_id,
            content=content,
            category=category,
            tags=tags,
            embedding=embedding,
            created_at=datetime.now(),
        )

        if self.pinecone_index and embedding:
            try:
                self.pinecone_index.upsert(
                    vectors=[
                        (
                            memory_id,
                            embedding,
                            {
                                "category": category,
                                "tags": json.dumps(tags),
                                "created_at": memory.created_at.isoformat(),
                            },
                        )
                    ]
                )
            except Exception as exc:  # pragma: no cover - network failure
                logger.error(f"Error storing in vector database: {str(exc)}")

        await self.memory_manager.append(
            category, json.dumps(memory.model_dump(), default=str)
        )
        return {"id": memory_id, "status": "stored"}

    async def _get_memory_content(self, category: str, memory_id: str) -> str:
        """Retrieve full memory content by ID."""
        try:
            history = await self.memory_manager.history(category)
            for memory_json in history:
                try:
                    memory = json.loads(memory_json)
                    if memory.get("id") == memory_id:
                        return memory.get("content", "")
                except json.JSONDecodeError:
                    continue
        except Exception as exc:  # pragma: no cover - unexpected
            logger.error(f"Error retrieving memory content: {str(exc)}")
        return ""

    async def recall_memory(
        self, query: str, category: Optional[str] = None, limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Recall memories using semantic search."""
        if not self.initialized:
            await self.initialize()

        embedding = await self.get_embedding(query)
        results: List[Dict[str, Any]] = []

        if self.pinecone_index and embedding:
            try:
                filter_dict = {"category": category} if category else {}
                query_response = self.pinecone_index.query(
                    vector=embedding,
                    filter=filter_dict,
                    top_k=limit,
                    include_metadata=True,
                )
                for match in query_response.matches:
                    metadata = match.metadata
                    results.append(
                        {
                            "id": match.id,
                            "category": metadata.get("category", "unknown"),
                            "tags": json.loads(metadata.get("tags", "[]")),
                            "created_at": metadata.get("created_at"),
                            "relevance_score": match.score,
                            "content": await self._get_memory_content(
                                metadata.get("category", "unknown"), match.id
                            ),
                        }
                    )
            except Exception as exc:  # pragma: no cover - network failure
                logger.error(f"Error searching vector database: {str(exc)}")

        if not results and category:
            try:
                history = await self.memory_manager.history(category)
                for memory_json in history[-limit:]:
                    try:
                        memory = json.loads(memory_json)
                        results.append(
                            {
                                "id": memory.get("id", "unknown"),
                                "category": memory.get("category", "unknown"),
                                "tags": memory.get("tags", []),
                                "created_at": memory.get("created_at"),
                                "content": memory.get("content", ""),
                                "relevance_score": 0.5,
                            }
                        )
                    except json.JSONDecodeError:
                        continue
            except Exception as exc:  # pragma: no cover - unexpected
                logger.error(f"Error retrieving from memory manager: {str(exc)}")
        return results

    def get_tools(self) -> List[Dict[str, Any]]:
        """Return the list of tools provided by this MCP server."""
        return [
            {
                "name": "store_conversation",
                "description": "Store development conversations for future reference",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "content": {
                            "type": "string",
                            "description": "The conversation content to store",
                        },
                        "category": {
                            "type": "string",
                            "description": "Category for the memory (architecture, bug_solution, code_decision, workflow)",
                            "enum": [
                                "architecture",
                                "bug_solution",
                                "code_decision",
                                "workflow",
                            ],
                        },
                        "tags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Tags to associate with this memory",
                        },
                    },
                    "required": ["content", "category"],
                },
            },
            {
                "name": "recall_memory",
                "description": "Search previous decisions and solutions",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query to find relevant memories",
                        },
                        "category": {
                            "type": "string",
                            "description": "Optional category to filter results",
                            "enum": [
                                "architecture",
                                "bug_solution",
                                "code_decision",
                                "workflow",
                            ],
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results to return",
                            "default": 5,
                        },
                    },
                    "required": ["query"],
                },
            },
        ]

    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool with the given parameters."""
        if not self.initialized:
            await self.initialize()

        if tool_name == "store_conversation":
            content = parameters.get("content", "")
            category = parameters.get("category", MemoryCategory.CODE_DECISION)
            tags = parameters.get("tags", [])
            return await self.store_memory(content, category, tags)
        if tool_name == "recall_memory":
            query = parameters.get("query", "")
            category = parameters.get("category")
            limit = parameters.get("limit", 5)
            return {"results": await self.recall_memory(query, category, limit)}
        return {"error": f"Unknown tool: {tool_name}"}

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on the server."""
        if not self.initialized:
            await self.initialize()

        status = {
            "status": "operational" if self.initialized else "initializing",
            "openai_client": self.openai_client is not None,
            "pinecone_index": self.pinecone_index is not None,
            "memory_manager": True,
            "timestamp": datetime.now().isoformat(),
        }
        return status


ai_memory_server = AiMemoryMCPServer()


async def main() -> None:
    """Run the AI Memory MCP server indefinitely."""
    await ai_memory_server.initialize()
    try:
        while True:
            await asyncio.sleep(60)
    except KeyboardInterrupt:
        logger.info("Shutting down AI Memory MCP Server")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
