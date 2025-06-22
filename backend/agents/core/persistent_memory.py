import asyncio
import json
import logging
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from backend.core.secret_manager import secret_manager
from backend.vector.vector_integration import vector_integration

logger = logging.getLogger(__name__)


class PersistentMemory:
    """A simple file-based persistent memory store for agents.

            Each agent's memory is stored in a separate JSON file
    """
    def __init__(self, storage_path: str = "./agent_memory"):
        """Initialize persistent memory storage"""

        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        self.lock = asyncio.Lock()

    def _get_agent_memory_file(
        self, agent_id: str, role_partition: str = "default"
    ) -> Path:
        """Gets the memory file path for a given agent, partitioned by role"""
        partition_path = self.storage_path / role_partition
        partition_path.mkdir(exist_ok=True)
        return partition_path / f"{agent_id}_memory.json"

    async def _read_memory(
        self, agent_id: str, role_partition: str = "default"
    ) -> Dict[str, Any]:
        """Reads the entire memory for an agent"""
        memory_file = self._get_agent_memory_file(agent_id, role_partition)
        if not memory_file.exists():
            return {}

        async with self.lock:
            with open(memory_file, "r") as f:
                try:
                except Exception:
                    pass
                    return json.load(f)
                except json.JSONDecodeError:
                    return {}

    async def _write_memory(
        self,
        agent_id: str,
        memory_data: Dict[str, Any],
        role_partition: str = "default",
    ):
        """Writes the entire memory for an agent"""
        memory_file = self._get_agent_memory_file(agent_id, role_partition)
        async with self.lock:
            with open(memory_file, "w") as f:
                json.dump(memory_data, f, indent=2)

    async def store_memory(
        self,
        agent_id: str,
        memory_type: str,
        content: Any,
        metadata: Optional[Dict[str, Any]] = None,
        role_partition: str = "default",
    ):
        """Stores a specific piece of memory for an agent"""
        memory_data = await self._read_memory(agent_id, role_partition)
        if memory_type not in memory_data:
            memory_data[memory_type] = []

        memory_data[memory_type].append(
            {"content": content, "metadata": metadata or {}}
        )
        await self._write_memory(agent_id, memory_data, role_partition)

    async def retrieve_memories(
        self,
        agent_id: str,
        query: str,
        limit: int = 10,
        role_partition: str = "default",
    ) -> List[Dict[str, Any]]:
        """Retrieves memories. This is a simple implementation that returns the latest memories.

                        A real implementation would have more sophisticated querying
        """
        memory_data = await self._read_memory(agent_id, role_partition)
        all_memories = []
        for mem_type in memory_data:
            all_memories.extend(memory_data[mem_type])

        # Return the most recent memories, regardless of query for this simple version
        return all_memories[-limit:]


            class Mem0PersistentMemory(PersistentMemory):
    """Persistent memory using mem0 for long-term context"""
    def __init__(

        self,
        agent_id: str,
        memory_type: str = "buffer",
        redis_url: Optional[str] = None,
        ttl: int = 86400,
        mem0_url: Optional[str] = None,
    ):
        """Initialize mem0 persistent memory.

                        Args:
                            agent_id: Unique identifier for the agent
                            memory_type: Type of memory to use ("buffer" or "summary")
                            redis_url: Redis URL for persistent storage (if None, will use environment variable)
                            ttl: Time to live for memory in seconds (default: 24 hours)
                            mem0_url: mem0 API URL (if None, will use environment variable)
        """super().__init__()  # Parent class only takes storage_path

        self.agent_id = agent_id
        self.memory_type = memory_type
        self.redis_url = redis_url
        self.ttl = ttl
        self.mem0_url = mem0_url
        self.mem0_client = None
        self.logger = logging.getLogger(__name__)

            async def initialize(self):
        """Initialize the memory"""
        try:
        except Exception:
            pass
            # Get mem0 URL if not provided
            if not self.mem0_url:
                self.mem0_url = os.environ.get("MEM0_URL")

                if not self.mem0_url:
                    # Try to get from secret manager
                    try:
                    except Exception:
                        pass
                        self.mem0_url = await secret_manager.get_secret(
                            "mem0_url", "memory"
                        )
                    except Exception:
                        # Default to local mem0
                        self.mem0_url = "http://localhost:8000"

            # Initialize mem0 client
            import aiohttp

            self.mem0_client = aiohttp.ClientSession(
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                }
            )

            self.logger.info(
                f"Initialized mem0 persistent memory for agent {self.agent_id}"
            )
        except Exception as e:
            self.logger.error(f"Failed to initialize mem0 persistent memory: {e}")
            raise

    async def close(self):
        """Close the memory"""
        if self.mem0_client:

            await self.mem0_client.close()
            self.mem0_client = None

    async def add_user_message(self, message: str):
        """Add a user message to the memory"""
        # Store in file-based memory

        await self.store_memory(
            self.agent_id, "conversation", {"role": "user", "content": message}
        )

        # Also add to mem0
        await self._add_to_mem0("user", message)

    async def add_ai_message(self, message: str):
        """Add an AI message to the memory"""
        # Store in file-based memory

        await self.store_memory(
            self.agent_id, "conversation", {"role": "ai", "content": message}
        )

        # Also add to mem0
        await self._add_to_mem0("ai", message)

    async def _add_to_mem0(self, role: str, message: str):
        """Add a message to mem0"""
        if not self.mem0_client:

            return

        try:
        except Exception:
            pass
            # Prepare payload
            payload = {
                "agent_id": self.agent_id,
                "role": role,
                "content": message,
                "timestamp": datetime.now().isoformat(),
            }

            # Send to mem0
            async with self.mem0_client.post(
                f"{self.mem0_url}/api/memory", json=payload
            ) as response:
                if response.status >= 400:
                    response_text = await response.text()
                    self.logger.error(
                        f"Failed to add message to mem0: {response.status} - {response_text}"
                    )

        except Exception as e:
            self.logger.error(f"Error adding message to mem0: {e}")

    async def search_memory(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search memory for relevant messages"""
        if not self.mem0_client:

            await self.initialize()

        try:
        except Exception:
            pass
            # Prepare payload
            payload = {"agent_id": self.agent_id, "query": query, "limit": limit}

            # Send to mem0
            async with self.mem0_client.post(
                f"{self.mem0_url}/api/memory/search", json=payload
            ) as response:
                if response.status >= 400:
                    response_text = await response.text()
                    self.logger.error(
                        f"Failed to search mem0: {response.status} - {response_text}"
                    )
                    return []

                result = await response.json()
                return result.get("results", [])

        except Exception as e:
            self.logger.error(f"Error searching mem0: {e}")
            return []

    async def get_relevant_context(self, query: str, limit: int = 5) -> str:
        """Get relevant context for a query"""
        results = await self.search_memory(query, limit)
        if not results:
            return ""

        # Format results as context
        context = "Relevant past interactions:\n\n"

        for result in results:
            role = result.get("role", "unknown")
            content = result.get("content", "")
            timestamp = result.get("timestamp", "")

            if role == "user":
                context += f"User ({timestamp}): {content}\n"
            elif role == "ai":
                context += f"AI ({timestamp}): {content}\n"
            else:
                context += f"{role.capitalize()} ({timestamp}): {content}\n"

            context += "\n"

        return context

    async def load_memory_variables(self) -> Dict[str, Any]:
        """Load memory variables"""
        variables = {}

        # Add mem0 context
        try:
        except Exception:
            pass
            # Get most recent messages as context
            recent_context = await self.get_relevant_context("recent", 3)

            if recent_context:
                variables["long_term_memory"] = recent_context

        except Exception as e:
            self.logger.error(f"Error loading mem0 variables: {e}")

        return variables


class VectorPersistentMemory(PersistentMemory):
    """Persistent memory using vector database for long-term context"""
    def __init__(

        self,
        agent_id: str,
        memory_type: str = "buffer",
        redis_url: Optional[str] = None,
        ttl: int = 86400,
        vector_db: str = "pinecone",
        collection: Optional[str] = None,
    ):
        """Initialize vector persistent memory.

                        Args:
                            agent_id: Unique identifier for the agent
                            memory_type: Type of memory to use ("buffer" or "summary")
                            redis_url: Redis URL for persistent storage (if None, will use environment variable)
                            ttl: Time to live for memory in seconds (default: 24 hours)
                            vector_db: Vector database to use ("pinecone" or "weaviate")
                            collection: Collection or namespace to use (if None, will use agent_id)
        """super().__init__()  # Parent class only takes storage_path
        self.agent_id = agent_id
        self.memory_type = memory_type
        self.redis_url = redis_url
        self.ttl = ttl
        self.vector_db = vector_db
        self.collection = collection or f"sophia_memory_{agent_id}"
        self.vector_client = vector_integration  # Use the singleton
        self.logger = logging.getLogger(__name__)

            async def initialize(self):
        """Initialize the memory"""
        try:
        except Exception:
            pass
            # The vector_integration singleton handles its own initialization
            if not self.vector_client.initialized:
                await self.vector_client.initialize()

            self.logger.info(
                f"Initialized vector persistent memory for agent {self.agent_id} using '{self.vector_db}'"
            )
        except Exception as e:
            self.logger.error(f"Failed to initialize vector persistent memory: {e}")
            raise

    async def add_user_message(self, message: str):
        """Add a user message to the memory"""
        # Store in file-based memory

        await self.store_memory(
            self.agent_id, "conversation", {"role": "user", "content": message}
        )

        # Also add to vector database
        await self._add_to_vector_db("user", message)

    async def add_ai_message(self, message: str):
        """Add an AI message to the memory"""
        # Store in file-based memory

        await self.store_memory(
            self.agent_id, "conversation", {"role": "ai", "content": message}
        )

        # Also add to vector database
        await self._add_to_vector_db("ai", message)

    async def _add_to_vector_db(self, role: str, message: str):
        """Add a message to vector database"""
        try:
        except Exception:
            pass
            item_id = str(uuid.uuid4())
            metadata = {
                "agent_id": self.agent_id,
                "role": role,
                "content": message,
                "timestamp": datetime.now().isoformat(),
                "collection": self.collection,
            }

            if self.vector_db == "pinecone":
                await self.vector_client.index_content_pinecone(
                    item_id, message, metadata
                )
            elif self.vector_db == "weaviate":
                await self.vector_client.index_content_weaviate(
                    item_id, message, metadata
                )

        except Exception as e:
            self.logger.error(f"Error adding message to vector database: {e}")

    async def search_memory(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search memory for relevant messages"""
        try:
        except Exception:
            pass
            if self.vector_db == "pinecone":
                # Pinecone filter needs to be adjusted based on VectorIntegration's expectation
                pinecone_filter = {"collection": self.collection}
                return await self.vector_client.search_pinecone(
                    query, top_k=limit, filter_metadata=pinecone_filter
                )
            elif self.vector_db == "weaviate":
                # Weaviate filtering might be handled differently, e.g., by class name
                # This assumes a 'collection' filter can be mapped to a Weaviate 'where' filter
                return await self.vector_client.search_weaviate(
                    query, top_k=limit, category_filter=self.collection
                )
            return []

        except Exception as e:
            self.logger.error(f"Error searching vector database: {e}")
            return []

    async def get_relevant_context(self, query: str, limit: int = 5) -> str:
        """Get relevant context for a query"""
        results = await self.search_memory(query, limit)
        if not results:
            return ""

        # Format results as context
        context = "Relevant past interactions:\n\n"

        for result in results:
            role = result.get("role", "unknown")
            content = result.get("content", "")
            timestamp = result.get("timestamp", "")

            if role == "user":
                context += f"User ({timestamp}): {content}\n"
            elif role == "ai":
                context += f"AI ({timestamp}): {content}\n"
            else:
                context += f"{role.capitalize()} ({timestamp}): {content}\n"

            context += "\n"

        return context

    async def load_memory_variables(self) -> Dict[str, Any]:
        """Load memory variables"""
        variables = {}

        # Add vector context
        try:
        except Exception:
            pass
            # Get most recent messages as context
            recent_context = await self.get_relevant_context("recent", 3)

            if recent_context:
                variables["long_term_memory"] = recent_context

        except Exception as e:
            self.logger.error(f"Error loading vector variables: {e}")

        return variables
