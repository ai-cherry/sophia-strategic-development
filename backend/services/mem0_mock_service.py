"""
Mock Mem0 Service for Local Development
Provides in-memory storage for testing without Kubernetes
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

logger = logging.getLogger(__name__)


class MockMem0Service:
    """Mock implementation of Mem0 for local development"""
    
    def __init__(self):
        self.memories: Dict[str, Dict[str, Any]] = {}
        self.user_memories: Dict[str, List[str]] = {}
        logger.info("✅ Mock Mem0 service initialized")
    
    async def store_conversation_memory(
        self,
        user_id: str,
        conversation: List[Dict[str, str]],
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Store conversation in memory"""
        memory_id = str(uuid4())
        
        self.memories[memory_id] = {
            "user_id": user_id,
            "conversation": conversation,
            "metadata": metadata or {},
            "created_at": datetime.now().isoformat()
        }
        
        if user_id not in self.user_memories:
            self.user_memories[user_id] = []
        self.user_memories[user_id].append(memory_id)
        
        logger.info(f"✅ Stored memory {memory_id} for user {user_id}")
        return memory_id
    
    async def recall_memories(
        self,
        user_id: str,
        query: str,
        limit: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Recall memories for a user"""
        if user_id not in self.user_memories:
            return []
        
        # Simple implementation: return most recent memories
        memory_ids = self.user_memories[user_id][-limit:]
        memories = []
        
        for memory_id in memory_ids:
            if memory_id in self.memories:
                memory = self.memories[memory_id].copy()
                memory["memory_id"] = memory_id
                memories.append(memory)
        
        logger.info(f"✅ Recalled {len(memories)} memories for user {user_id}")
        return memories
    
    async def initialize(self):
        """Initialize the service"""
        logger.info("✅ Mock Mem0 service ready")
        self.initialized = True
    
    async def close(self):
        """Close the service"""
        logger.info("✅ Mock Mem0 service closed")


# For local development, use the mock service
def get_mem0_service():
    """Get the Mem0 service instance"""
    return MockMem0Service()
