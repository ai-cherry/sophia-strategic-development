"""
Comprehensive Memory Management System
Orchestrates memory components for optimal performance.
This is a simplified version focusing on a robust two-tiered memory system.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from .enhanced_embedding_manager import enhanced_embedding_manager
from ..vector.vector_integration_updated import VectorIntegration
from ..agents.core.persistent_memory import PersistentMemory

logger = logging.getLogger(__name__)

class MemoryOperationType(Enum):
    """Types of memory operations"""
    STORE = "store"
    RETRIEVE = "retrieve"
    UPDATE = "update"
    DELETE = "delete"
    SEARCH = "search"

@dataclass
class MemoryRequest:
    """Memory operation request"""
    operation: MemoryOperationType
    agent_id: str
    content: Optional[str] = None
    memory_id: Optional[str] = None
    query: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class MemoryResponse:
    """Memory operation response"""
    success: bool
    operation: MemoryOperationType
    data: Any
    processing_time: float
    error_message: Optional[str] = None

class ComprehensiveMemoryManager:
    """Manages a two-tiered memory system: a Vector Store and a Persistent KV Store."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Core components
        self.embedding_manager = enhanced_embedding_manager
        self.vector_integration = VectorIntegration()
        self.persistent_memory = PersistentMemory()
        
        self.initialized = False
    
    async def initialize(self):
        """Initialize all memory components"""
        if self.initialized: return
        
        self.logger.info("Initializing comprehensive memory manager...")
        await self.embedding_manager.initialize()
        await self.vector_integration.initialize()
        self.initialized = True
        self.logger.info("Comprehensive memory manager initialized successfully")
    
    async def process_memory_request(self, request: MemoryRequest) -> MemoryResponse:
        """Process a memory operation request"""
        start_time = datetime.now()
        try:
            handler_map = {
                MemoryOperationType.STORE: self._handle_store_request,
                MemoryOperationType.RETRIEVE: self._handle_retrieve_request,
                MemoryOperationType.DELETE: self._handle_delete_request,
            }
            handler = handler_map.get(request.operation)
            if not handler:
                raise ValueError(f"Unsupported operation: {request.operation}")
            
            result = await handler(request)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            return MemoryResponse(success=True, operation=request.operation, data=result, processing_time=processing_time)
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            self.logger.error(f"Memory request failed: {e}")
            return MemoryResponse(success=False, operation=request.operation, data=None, processing_time=processing_time, error_message=str(e))

    async def _handle_store_request(self, request: MemoryRequest) -> Dict[str, Any]:
        """Handle memory storage request."""
        if not request.content:
            raise ValueError("Content is required for store operation")
        
        embedding, emb_metadata = await self.embedding_manager.generate_text_embedding(text=request.content)
        
        metadata = {
            "agent_id": request.agent_id,
            "content": request.content,
            "created_timestamp": datetime.now().isoformat(),
            **(request.metadata or {})
        }
        
        memory_id = f"{request.agent_id}_{emb_metadata.content_hash}"
        
        await self.vector_integration.index_content(
            content_id=memory_id,
            text=request.content,
            metadata=metadata
        )
        
        await self.persistent_memory.store_memory(
            agent_id=request.agent_id,
            memory_type="vector_link",
            content={"vector_id": memory_id, "text_preview": request.content[:100]},
            metadata=metadata
        )
        
        return {"memory_id": memory_id, "status": "stored"}
    
    async def _handle_retrieve_request(self, request: MemoryRequest) -> Dict[str, Any]:
        if not request.query:
            raise ValueError("Query is required for retrieve operation")
        
        vector_memories = await self.vector_integration.search_pinecone(
            query=request.query,
            top_k=10,
            filter_metadata={"agent_id": request.agent_id}
        )
        
        persistent_memories = await self.persistent_memory.retrieve_memories(
            agent_id=request.agent_id,
            query=request.query,
            limit=10
        )
        
        return {
            "vector_memories": vector_memories,
            "persistent_memories": persistent_memories
        }
    
    async def _handle_delete_request(self, request: MemoryRequest) -> Dict[str, Any]:
        if not request.memory_id:
            raise ValueError("Memory ID is required for delete operation")
        
        await self.vector_integration.delete_content(request.memory_id)
        # Note: Deleting from the simple file-based persistent store is more complex
        # and is omitted in this simplified version.
        
        return {"memory_id": request.memory_id, "status": "deleted"}

# Global instance
comprehensive_memory_manager = ComprehensiveMemoryManager()

