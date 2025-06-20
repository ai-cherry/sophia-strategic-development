"""
Comprehensive Memory Management System
Orchestrates all memory components for optimal performance
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

from .enhanced_embedding_manager import enhanced_embedding_manager
from .advanced_memory_consolidator import advanced_memory_consolidator
from ..vector.vector_integration_updated import VectorIntegration
from ..chunking.sophia_chunking_pipeline import SophiaChunkingPipeline
from ..agents.core.persistent_memory import PersistentMemory

logger = logging.getLogger(__name__)

class MemoryOperationType(Enum):
    """Types of memory operations"""
    STORE = "store"
    RETRIEVE = "retrieve"
    UPDATE = "update"
    DELETE = "delete"
    CONSOLIDATE = "consolidate"
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
    context: Optional[Dict[str, Any]] = None

@dataclass
class MemoryResponse:
    """Memory operation response"""
    success: bool
    operation: MemoryOperationType
    data: Any
    metadata: Dict[str, Any]
    processing_time: float
    error_message: Optional[str] = None

class ComprehensiveMemoryManager:
    """Comprehensive memory management system orchestrating all components"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Core components
        self.embedding_manager = enhanced_embedding_manager
        self.memory_consolidator = advanced_memory_consolidator
        self.vector_integration = VectorIntegration()
        self.chunking_pipeline = SophiaChunkingPipeline()
        self.persistent_memory = PersistentMemory()
        
        # Memory configuration
        self.memory_config = {
            "max_chunk_size": 512,
            "chunk_overlap": 50,
            "embedding_model": "domain_specific",
            "consolidation_interval": 24,  # hours
            "max_memories_per_agent": 100000,
            "importance_threshold": 0.5,
            "similarity_threshold": 0.7
        }
        
        # Performance tracking
        self.performance_stats = {
            "total_operations": 0,
            "successful_operations": 0,
            "avg_response_time": 0.0,
            "operations_by_type": {},
            "memory_usage": {
                "total_memories": 0,
                "active_agents": 0,
                "storage_size_mb": 0.0
            }
        }
        
        # Active consolidation tasks
        self.consolidation_tasks = {}
        
        self.initialized = False
    
    async def initialize(self):
        """Initialize all memory components"""
        if self.initialized:
            return
        
        try:
            self.logger.info("Initializing comprehensive memory manager...")
            
            # Initialize all components
            await self.embedding_manager.initialize()
            await self.memory_consolidator.initialize()
            await self.vector_integration.initialize()
            await self.chunking_pipeline.initialize()
            
            # Start automatic consolidation for existing agents
            await self._start_automatic_consolidation()
            
            self.initialized = True
            self.logger.info("Comprehensive memory manager initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize memory manager: {e}")
            raise
    
    async def process_memory_request(self, request: MemoryRequest) -> MemoryResponse:
        """Process a memory operation request"""
        
        if not self.initialized:
            await self.initialize()
        
        start_time = datetime.now()
        
        try:
            # Route request to appropriate handler
            if request.operation == MemoryOperationType.STORE:
                result = await self._handle_store_request(request)
            elif request.operation == MemoryOperationType.RETRIEVE:
                result = await self._handle_retrieve_request(request)
            elif request.operation == MemoryOperationType.UPDATE:
                result = await self._handle_update_request(request)
            elif request.operation == MemoryOperationType.DELETE:
                result = await self._handle_delete_request(request)
            elif request.operation == MemoryOperationType.CONSOLIDATE:
                result = await self._handle_consolidate_request(request)
            elif request.operation == MemoryOperationType.SEARCH:
                result = await self._handle_search_request(request)
            else:
                raise ValueError(f"Unsupported operation: {request.operation}")
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Create response
            response = MemoryResponse(
                success=True,
                operation=request.operation,
                data=result,
                metadata={
                    "agent_id": request.agent_id,
                    "timestamp": datetime.now().isoformat(),
                    "components_used": self._get_components_used(request.operation)
                },
                processing_time=processing_time
            )
            
            # Update performance stats
            self._update_performance_stats(request.operation, processing_time, True)
            
            return response
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            
            self.logger.error(f"Memory request failed: {e}")
            
            # Update performance stats
            self._update_performance_stats(request.operation, processing_time, False)
            
            return MemoryResponse(
                success=False,
                operation=request.operation,
                data=None,
                metadata={
                    "agent_id": request.agent_id,
                    "timestamp": datetime.now().isoformat(),
                    "error_details": str(e)
                },
                processing_time=processing_time,
                error_message=str(e)
            )
    
    async def _handle_store_request(self, request: MemoryRequest) -> Dict[str, Any]:
        """Handle memory storage request"""
        
        if not request.content:
            raise ValueError("Content is required for store operation")
        
        # Step 1: Chunk the content
        chunks = await self.chunking_pipeline.chunk_content(
            content=request.content,
            content_type="text",
            max_chunk_size=self.memory_config["max_chunk_size"],
            overlap=self.memory_config["chunk_overlap"]
        )
        
        stored_memories = []
        
        # Step 2: Process each chunk
        for i, chunk in enumerate(chunks):
            # Generate embedding
            embedding, emb_metadata = await self.embedding_manager.generate_text_embedding(
                text=chunk["content"],
                model_type=self.memory_config["embedding_model"],
                domain_context="apartment_industry"
            )
            
            # Prepare metadata
            chunk_metadata = {
                "agent_id": request.agent_id,
                "content": chunk["content"],
                "chunk_index": i,
                "total_chunks": len(chunks),
                "original_content_length": len(request.content),
                "chunk_metadata": chunk["metadata"],
                "embedding_metadata": emb_metadata.__dict__,
                "created_timestamp": datetime.now().isoformat(),
                "tier": "short_term",
                "importance_score": self._calculate_initial_importance(chunk["content"]),
                **(request.metadata or {})
            }
            
            # Store in vector database
            memory_id = f"{request.agent_id}_{datetime.now().isoformat()}_{i}"
            
            await self.vector_integration.index_content(
                content_id=memory_id,
                text=chunk["content"],
                metadata=chunk_metadata
            )
            
            stored_memories.append({
                "memory_id": memory_id,
                "chunk_index": i,
                "content_length": len(chunk["content"]),
                "embedding_dimension": len(embedding)
            })
        
        # Step 3: Store in persistent memory for agent context
        await self.persistent_memory.store_memory(
            agent_id=request.agent_id,
            memory_type="episodic",
            content=request.content,
            metadata={
                "chunks_stored": len(chunks),
                "vector_memory_ids": [mem["memory_id"] for mem in stored_memories],
                **(request.metadata or {})
            }
        )
        
        return {
            "memories_stored": len(stored_memories),
            "chunks_created": len(chunks),
            "memory_details": stored_memories,
            "total_content_length": len(request.content)
        }
    
    async def _handle_retrieve_request(self, request: MemoryRequest) -> Dict[str, Any]:
        """Handle memory retrieval request"""
        
        if not request.query:
            raise ValueError("Query is required for retrieve operation")
        
        # Step 1: Generate query embedding
        query_embedding, _ = await self.embedding_manager.generate_text_embedding(
            text=request.query,
            model_type=self.memory_config["embedding_model"],
            domain_context="apartment_industry"
        )
        
        # Step 2: Search vector database
        search_results = await self.vector_integration.search_pinecone(
            query=request.query,
            top_k=20,  # Get more results for better ranking
            filter_metadata={"agent_id": request.agent_id}
        )
        
        # Step 3: Rank and filter results
        ranked_results = self._rank_search_results(
            search_results, 
            request.query, 
            request.context or {}
        )
        
        # Step 4: Retrieve related persistent memories
        persistent_memories = await self.persistent_memory.retrieve_memories(
            agent_id=request.agent_id,
            query=request.query,
            limit=10
        )
        
        return {
            "vector_memories": ranked_results[:10],  # Top 10 results
            "persistent_memories": persistent_memories,
            "total_found": len(search_results),
            "query_processed": request.query,
            "ranking_applied": True
        }
    
    async def _handle_update_request(self, request: MemoryRequest) -> Dict[str, Any]:
        """Handle memory update request"""
        
        if not request.memory_id:
            raise ValueError("Memory ID is required for update operation")
        
        # Update vector database entry
        if request.content:
            # Generate new embedding
            embedding, emb_metadata = await self.embedding_manager.generate_text_embedding(
                text=request.content,
                model_type=self.memory_config["embedding_model"]
            )
            
            # Update metadata
            updated_metadata = {
                "updated_timestamp": datetime.now().isoformat(),
                "embedding_metadata": emb_metadata.__dict__,
                **(request.metadata or {})
            }
            
            await self.vector_integration.index_content(
                content_id=request.memory_id,
                text=request.content,
                metadata=updated_metadata
            )
        
        return {
            "memory_id": request.memory_id,
            "updated": True,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _handle_delete_request(self, request: MemoryRequest) -> Dict[str, Any]:
        """Handle memory deletion request"""
        
        if not request.memory_id:
            raise ValueError("Memory ID is required for delete operation")
        
        # Delete from vector database
        await self.vector_integration.delete_content(request.memory_id)
        
        return {
            "memory_id": request.memory_id,
            "deleted": True,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _handle_consolidate_request(self, request: MemoryRequest) -> Dict[str, Any]:
        """Handle memory consolidation request"""
        
        # Trigger consolidation for agent
        consolidation_results = await self.memory_consolidator.consolidate_memories(
            request.agent_id
        )
        
        return consolidation_results
    
    async def _handle_search_request(self, request: MemoryRequest) -> Dict[str, Any]:
        """Handle memory search request"""
        
        if not request.query:
            raise ValueError("Query is required for search operation")
        
        # Perform semantic search
        search_results = await self.vector_integration.search_pinecone(
            query=request.query,
            top_k=50,
            filter_metadata={"agent_id": request.agent_id}
        )
        
        # Apply advanced filtering and ranking
        filtered_results = self._apply_advanced_search_filters(
            search_results,
            request.context or {}
        )
        
        return {
            "results": filtered_results,
            "total_found": len(search_results),
            "query": request.query,
            "filters_applied": list((request.context or {}).keys())
        }
    
    def _calculate_initial_importance(self, content: str) -> float:
        """Calculate initial importance score for new content"""
        
        # Basic importance factors
        length_score = min(len(content) / 500, 1.0)  # Prefer longer content
        
        # Check for important keywords
        important_keywords = [
            "decision", "action", "revenue", "customer", "urgent", "important",
            "meeting", "deadline", "issue", "problem", "solution", "strategy"
        ]
        
        keyword_score = 0
        for keyword in important_keywords:
            if keyword.lower() in content.lower():
                keyword_score += 0.1
        
        keyword_score = min(keyword_score, 0.5)
        
        # Combine scores
        importance = (length_score * 0.3) + (keyword_score * 0.7) + 0.2  # Base score
        
        return min(importance, 1.0)
    
    def _rank_search_results(
        self, 
        results: List[Dict[str, Any]], 
        query: str, 
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Rank search results based on relevance and context"""
        
        for result in results:
            score = result.get("score", 0.0)
            metadata = result.get("metadata", {})
            
            # Boost recent memories
            created_timestamp = metadata.get("created_timestamp")
            if created_timestamp:
                try:
                    created_time = datetime.fromisoformat(created_timestamp.replace('Z', '+00:00'))
                    age_hours = (datetime.now() - created_time).total_seconds() / 3600
                    recency_boost = max(0, 1 - (age_hours / (24 * 7)))  # Decay over a week
                    score += recency_boost * 0.1
                except:
                    pass
            
            # Boost important memories
            importance_score = metadata.get("importance_score", 0.5)
            score += importance_score * 0.2
            
            # Context-based boosting
            if context.get("prefer_recent", False):
                score += recency_boost * 0.2
            
            if context.get("prefer_important", False):
                score += importance_score * 0.3
            
            result["final_score"] = score
        
        # Sort by final score
        return sorted(results, key=lambda x: x.get("final_score", 0), reverse=True)
    
    def _apply_advanced_search_filters(
        self, 
        results: List[Dict[str, Any]], 
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Apply advanced filters to search results"""
        
        filtered_results = results
        
        # Time-based filtering
        if context.get("time_range"):
            time_range = context["time_range"]
            if time_range == "today":
                cutoff = datetime.now() - timedelta(days=1)
            elif time_range == "week":
                cutoff = datetime.now() - timedelta(days=7)
            elif time_range == "month":
                cutoff = datetime.now() - timedelta(days=30)
            else:
                cutoff = None
            
            if cutoff:
                filtered_results = [
                    result for result in filtered_results
                    if self._is_memory_after_cutoff(result, cutoff)
                ]
        
        # Importance filtering
        if context.get("min_importance"):
            min_importance = context["min_importance"]
            filtered_results = [
                result for result in filtered_results
                if result.get("metadata", {}).get("importance_score", 0) >= min_importance
            ]
        
        # Content type filtering
        if context.get("content_types"):
            content_types = context["content_types"]
            filtered_results = [
                result for result in filtered_results
                if result.get("metadata", {}).get("content_type") in content_types
            ]
        
        return filtered_results
    
    def _is_memory_after_cutoff(self, memory: Dict[str, Any], cutoff: datetime) -> bool:
        """Check if memory was created after cutoff time"""
        
        try:
            created_timestamp = memory.get("metadata", {}).get("created_timestamp")
            if created_timestamp:
                created_time = datetime.fromisoformat(created_timestamp.replace('Z', '+00:00'))
                return created_time >= cutoff
        except:
            pass
        
        return False
    
    def _get_components_used(self, operation: MemoryOperationType) -> List[str]:
        """Get list of components used for operation"""
        
        components = ["embedding_manager"]
        
        if operation in [MemoryOperationType.STORE, MemoryOperationType.RETRIEVE, 
                        MemoryOperationType.SEARCH]:
            components.extend(["vector_integration", "chunking_pipeline"])
        
        if operation == MemoryOperationType.STORE:
            components.append("persistent_memory")
        
        if operation == MemoryOperationType.CONSOLIDATE:
            components.append("memory_consolidator")
        
        return components
    
    def _update_performance_stats(
        self, 
        operation: MemoryOperationType, 
        processing_time: float, 
        success: bool
    ):
        """Update performance statistics"""
        
        self.performance_stats["total_operations"] += 1
        
        if success:
            self.performance_stats["successful_operations"] += 1
        
        # Update average response time
        total_ops = self.performance_stats["total_operations"]
        current_avg = self.performance_stats["avg_response_time"]
        self.performance_stats["avg_response_time"] = (
            (current_avg * (total_ops - 1) + processing_time) / total_ops
        )
        
        # Update operation type stats
        op_name = operation.value
        if op_name not in self.performance_stats["operations_by_type"]:
            self.performance_stats["operations_by_type"][op_name] = {
                "count": 0,
                "avg_time": 0.0,
                "success_rate": 0.0
            }
        
        op_stats = self.performance_stats["operations_by_type"][op_name]
        op_stats["count"] += 1
        
        # Update average time for this operation
        op_stats["avg_time"] = (
            (op_stats["avg_time"] * (op_stats["count"] - 1) + processing_time) / 
            op_stats["count"]
        )
        
        # Update success rate
        if success:
            op_stats["success_rate"] = (
                (op_stats["success_rate"] * (op_stats["count"] - 1) + 1.0) / 
                op_stats["count"]
            )
        else:
            op_stats["success_rate"] = (
                (op_stats["success_rate"] * (op_stats["count"] - 1)) / 
                op_stats["count"]
            )
    
    async def _start_automatic_consolidation(self):
        """Start automatic consolidation for all agents"""
        
        try:
            # Get list of active agents
            active_agents = await self._get_active_agents()
            
            for agent_id in active_agents:
                if agent_id not in self.consolidation_tasks:
                    await self.memory_consolidator.schedule_automatic_consolidation(
                        agent_id, 
                        self.memory_config["consolidation_interval"]
                    )
                    self.consolidation_tasks[agent_id] = True
            
            self.logger.info(f"Started automatic consolidation for {len(active_agents)} agents")
            
        except Exception as e:
            self.logger.error(f"Failed to start automatic consolidation: {e}")
    
    async def _get_active_agents(self) -> List[str]:
        """Get list of active agents with memories"""
        
        try:
            # Query vector database for unique agent IDs
            # This is a simplified implementation
            return ["sophia_main", "apartment_assistant", "business_intelligence"]
            
        except Exception as e:
            self.logger.error(f"Failed to get active agents: {e}")
            return []
    
    async def get_memory_stats(self, agent_id: Optional[str] = None) -> Dict[str, Any]:
        """Get comprehensive memory statistics"""
        
        stats = {
            "performance": self.performance_stats.copy(),
            "embedding_stats": await self.embedding_manager.get_embedding_stats(),
            "consolidation_stats": await self.memory_consolidator.get_consolidation_stats(),
            "system_health": {
                "initialized": self.initialized,
                "active_consolidation_tasks": len(self.consolidation_tasks),
                "memory_config": self.memory_config
            }
        }
        
        if agent_id:
            # Add agent-specific stats
            agent_memories = await self.vector_integration.search_pinecone(
                query="*",
                top_k=1000,
                filter_metadata={"agent_id": agent_id}
            )
            
            stats["agent_specific"] = {
                "agent_id": agent_id,
                "total_memories": len(agent_memories),
                "memory_distribution": self._analyze_memory_distribution(agent_memories)
            }
        
        return stats
    
    def _analyze_memory_distribution(self, memories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze memory distribution for an agent"""
        
        distribution = {
            "by_tier": {},
            "by_importance": {"high": 0, "medium": 0, "low": 0},
            "by_age": {"recent": 0, "medium": 0, "old": 0}
        }
        
        now = datetime.now()
        
        for memory in memories:
            metadata = memory.get("metadata", {})
            
            # Tier distribution
            tier = metadata.get("tier", "unknown")
            distribution["by_tier"][tier] = distribution["by_tier"].get(tier, 0) + 1
            
            # Importance distribution
            importance = metadata.get("importance_score", 0.5)
            if importance >= 0.7:
                distribution["by_importance"]["high"] += 1
            elif importance >= 0.4:
                distribution["by_importance"]["medium"] += 1
            else:
                distribution["by_importance"]["low"] += 1
            
            # Age distribution
            created_timestamp = metadata.get("created_timestamp")
            if created_timestamp:
                try:
                    created_time = datetime.fromisoformat(created_timestamp.replace('Z', '+00:00'))
                    age_hours = (now - created_time).total_seconds() / 3600
                    
                    if age_hours <= 24:
                        distribution["by_age"]["recent"] += 1
                    elif age_hours <= 168:  # 1 week
                        distribution["by_age"]["medium"] += 1
                    else:
                        distribution["by_age"]["old"] += 1
                except:
                    pass
        
        return distribution

# Global instance
comprehensive_memory_manager = ComprehensiveMemoryManager()

