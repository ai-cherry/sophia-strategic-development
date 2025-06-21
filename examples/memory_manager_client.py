"""Memory Manager Client Example
This script demonstrates how to use the ComprehensiveMemoryManager
instead of directly accessing vector stores.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional

from backend.core.comprehensive_memory_manager import (
    MemoryOperationType,
    MemoryRequest,
    comprehensive_memory_manager,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class MemoryManagerClient:
    """Client for the ComprehensiveMemoryManager that demonstrates how to use it
    instead of directly accessing vector stores.
    """

    def __init__(self):
        self.memory_manager = comprehensive_memory_manager

    async def initialize(self):
        """Initialize the memory manager."""
        await self.memory_manager.initialize()
        logger.info("Memory manager initialized.")

    async def store_memory(
        self, agent_id: str, content: str, metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Store a memory using the ComprehensiveMemoryManager."""
        try:
            request = MemoryRequest(
                operation=MemoryOperationType.STORE,
                agent_id=agent_id,
                content=content,
                metadata=metadata or {},
            )

            response = await self.memory_manager.process_memory_request(request)

            if response.success:
                logger.info(f"Memory stored successfully for agent {agent_id}")
                return {
                    "success": True,
                    "memory_id": response.data.get("memory_id"),
                    "processing_time": response.processing_time,
                }
            else:
                logger.error(f"Failed to store memory: {response.error_message}")
                return {"success": False, "error": response.error_message}

        except Exception as e:
            logger.error(f"Error storing memory: {str(e)}")
            return {"success": False, "error": str(e)}

    async def retrieve_memory(self, agent_id: str, query: str) -> Dict[str, Any]:
        """Retrieve memories using the ComprehensiveMemoryManager."""
        try:
            request = MemoryRequest(
                operation=MemoryOperationType.RETRIEVE, agent_id=agent_id, query=query
            )

            response = await self.memory_manager.process_memory_request(request)

            if response.success:
                logger.info(
                    f"Retrieved {len(response.data.get('vector_memories', []))} vector memories and {len(response.data.get('persistent_memories', []))} persistent memories for agent {agent_id}"
                )
                return {
                    "success": True,
                    "vector_memories": response.data.get("vector_memories", []),
                    "persistent_memories": response.data.get("persistent_memories", []),
                    "processing_time": response.processing_time,
                }
            else:
                logger.error(f"Failed to retrieve memories: {response.error_message}")
                return {"success": False, "error": response.error_message}

        except Exception as e:
            logger.error(f"Error retrieving memories: {str(e)}")
            return {"success": False, "error": str(e)}

    async def delete_memory(self, agent_id: str, memory_id: str) -> Dict[str, Any]:
        """Delete a memory using the ComprehensiveMemoryManager."""
        try:
            request = MemoryRequest(
                operation=MemoryOperationType.DELETE,
                agent_id=agent_id,
                memory_id=memory_id,
            )

            response = await self.memory_manager.process_memory_request(request)

            if response.success:
                logger.info(
                    f"Memory {memory_id} deleted successfully for agent {agent_id}"
                )
                return {
                    "success": True,
                    "memory_id": memory_id,
                    "processing_time": response.processing_time,
                }
            else:
                logger.error(f"Failed to delete memory: {response.error_message}")
                return {"success": False, "error": response.error_message}

        except Exception as e:
            logger.error(f"Error deleting memory: {str(e)}")
            return {"success": False, "error": str(e)}

    async def semantic_search(
        self, agent_id: str, query: str, top_k: int = 5
    ) -> Dict[str, Any]:
        """Perform a semantic search using the ComprehensiveMemoryManager.
        This is a higher-level function that demonstrates how to use the retrieve operation
        to perform a semantic search.
        """
        try:
            # Use the retrieve operation to perform a semantic search
            result = await self.retrieve_memory(agent_id, query)

            if not result.get("success", False):
                return result

            # Process the results to create a unified list of memories
            vector_memories = result.get("vector_memories", [])
            persistent_memories = result.get("persistent_memories", [])

            # Combine and sort by relevance
            all_memories = []

            for memory in vector_memories:
                all_memories.append(
                    {
                        "id": memory.get("id"),
                        "content": memory.get("content", ""),
                        "score": memory.get("score", 0.0),
                        "source": "vector",
                        "metadata": memory.get("metadata", {}),
                    }
                )

            for memory in persistent_memories:
                all_memories.append(
                    {
                        "id": memory.get("id"),
                        "content": memory.get("content", {}).get("text_preview", ""),
                        "score": memory.get("relevance", 0.0),
                        "source": "persistent",
                        "metadata": memory.get("metadata", {}),
                    }
                )

            # Sort by score (descending) and limit to top_k
            all_memories.sort(key=lambda x: x.get("score", 0.0), reverse=True)
            top_memories = all_memories[:top_k]

            return {
                "success": True,
                "memories": top_memories,
                "total_found": len(all_memories),
                "processing_time": result.get("processing_time", 0.0),
            }

        except Exception as e:
            logger.error(f"Error performing semantic search: {str(e)}")
            return {"success": False, "error": str(e)}


async def main():
    """Main function to demonstrate the MemoryManagerClient."""
    client = MemoryManagerClient()
    try:
        await client.initialize()

        # Example agent ID
        agent_id = "demo_agent"

        # Store a memory
        logger.info("Storing a memory...")
        store_result = await client.store_memory(
            agent_id=agent_id,
            content="Pay Ready is a property management software company that helps apartment managers collect rent and manage maintenance requests.",
            metadata={
                "source": "company_description",
                "category": "company_info",
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

        print("\n--- Store Memory Result ---")
        print(json.dumps(store_result, indent=2, default=str))

        # Store another memory
        logger.info("Storing another memory...")
        store_result2 = await client.store_memory(
            agent_id=agent_id,
            content="Pay Ready's software integrates with popular property management systems like Yardi, RealPage, and AppFolio.",
            metadata={
                "source": "integration_info",
                "category": "product_info",
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

        print("\n--- Store Memory Result 2 ---")
        print(json.dumps(store_result2, indent=2, default=str))

        # Perform a semantic search
        logger.info("Performing a semantic search...")
        search_result = await client.semantic_search(
            agent_id=agent_id,
            query="What software does Pay Ready integrate with?",
            top_k=5,
        )

        print("\n--- Semantic Search Result ---")
        print(json.dumps(search_result, indent=2, default=str))

        # Delete a memory
        if store_result.get("success", False):
            memory_id = store_result.get("memory_id")
            logger.info(f"Deleting memory {memory_id}...")
            delete_result = await client.delete_memory(
                agent_id=agent_id, memory_id=memory_id
            )

            print("\n--- Delete Memory Result ---")
            print(json.dumps(delete_result, indent=2, default=str))

    finally:
        # No need to close the memory manager as it's a singleton
        pass


if __name__ == "__main__":
    asyncio.run(main())
