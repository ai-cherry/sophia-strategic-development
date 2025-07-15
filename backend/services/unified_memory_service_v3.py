"""
Unified Memory Service V3 - Pure Qdrant Architecture
Provides comprehensive memory management using only Qdrant vector database
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct, Filter, FieldCondition, 
    MatchValue, CollectionInfo, UpdateResult
)
from qdrant_client.http import models

from backend.core.auto_esc_config import get_config_value

logger = logging.getLogger(__name__)

@dataclass
class CollectionConfig:
    """Configuration for Qdrant collections"""
    name: str
    vector_size: int = 768
    distance: Distance = Distance.COSINE
    shard_number: int = 1
    replication_factor: int = 1
    on_disk_payload: bool = True
    hnsw_config: Optional[Dict[str, Any]] = None

class UnifiedMemoryServiceV3:
    """
    Pure Qdrant Memory Service - No other vector databases
    Provides unified memory management with Qdrant as the single source of truth
    """
    
    def __init__(self):
        self.client: Optional[QdrantClient] = None
        self.initialized = False
        self.collections = {
            "knowledge": CollectionConfig(
                name="sophia_knowledge",
                vector_size=768,
                distance=Distance.COSINE,
                shard_number=2,
                hnsw_config={"m": 16, "ef_construct": 200}
            ),
            "conversations": CollectionConfig(
                name="sophia_conversations",
                vector_size=768,
                distance=Distance.COSINE,
                shard_number=1,
                hnsw_config={"m": 16, "ef_construct": 100}
            ),
            "business_intelligence": CollectionConfig(
                name="sophia_business_intelligence",
                vector_size=768,
                distance=Distance.COSINE,
                shard_number=2,
                hnsw_config={"m": 24, "ef_construct": 200}
            ),
            "competitors": CollectionConfig(
                name="sophia_competitors",
                vector_size=768,
                distance=Distance.COSINE,
                shard_number=3,
                replication_factor=2,
                hnsw_config={"m": 24, "ef_construct": 200}
            ),
            "competitor_events": CollectionConfig(
                name="sophia_competitor_events",
                vector_size=768,
                distance=Distance.COSINE,
                shard_number=1,
                hnsw_config={"m": 16, "ef_construct": 100}
            )
        }
    
    async def initialize(self) -> None:
        """Initialize Qdrant client and collections"""
        if self.initialized:
            return
        
        try:
            # Get Qdrant configuration
            QDRANT_URL = get_config_value("QDRANT_URL") or "http://localhost:6333"
            QDRANT_api_key = get_config_value("QDRANT_api_key")
            
            # Initialize client
            self.client = QdrantClient(
                url=QDRANT_URL,
                api_key=QDRANT_api_key,
                timeout=60
            )
            
            # Create collections
            await self._create_collections()
            
            self.initialized = True
            logger.info("✅ Pure Qdrant Memory Service V3 initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Qdrant Memory Service: {e}")
            raise
    
    async def _create_collections(self) -> None:
        """Create all required collections"""
        for collection_key, config in self.collections.items():
            try:
                # Check if collection exists
                collections = self.client.get_collections().collections
                collection_names = [c.name for c in collections]
                
                if config.name not in collection_names:
                    # Create collection
                    self.client.create_collection(
                        collection_name=config.name,
                        vectors_config=VectorParams(
                            size=config.vector_size,
                            distance=config.distance
                        ),
                        shard_number=config.shard_number,
                        replication_factor=config.replication_factor,
                        on_disk_payload=config.on_disk_payload,
                        hnsw_config=config.hnsw_config
                    )
                    logger.info(f"✅ Created collection: {config.name}")
                else:
                    logger.info(f"📋 Collection already exists: {config.name}")
                    
            except Exception as e:
                logger.error(f"❌ Failed to create collection {config.name}: {e}")
                raise
    
    async def store_knowledge(
        self,
        content: str,
        metadata: Dict[str, Any],
        vector: List[float],
        point_id: Optional[str] = None
    ) -> str:
        """Store knowledge in Qdrant"""
        if not self.initialized:
            await self.initialize()
        
        try:
            # Generate point ID if not provided
            if not point_id:
                point_id = f"knowledge_{datetime.now().timestamp()}"
            
            # Create point
            point = PointStruct(
                id=point_id,
                vector=vector,
                payload={
                    "content": content,
                    "timestamp": datetime.now().isoformat(),
                    **metadata
                }
            )
            
            # Store in Qdrant
            result = self.client.upsert(
                collection_name=self.collections["knowledge"].name,
                points=[point]
            )
            
            logger.info(f"✅ Stored knowledge: {point_id}")
            return point_id
            
        except Exception as e:
            logger.error(f"❌ Failed to store knowledge: {e}")
            raise
    
    async def search_knowledge(
        self,
        query_vector: List[float],
        limit: int = 10,
        metadata_filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search knowledge in Qdrant"""
        if not self.initialized:
            await self.initialize()
        
        try:
            # Build filter
            query_filter = None
            if metadata_filter:
                conditions = []
                for key, value in metadata_filter.items():
                    conditions.append(
                        FieldCondition(
                            key=key,
                            match=MatchValue(value=value)
                        )
                    )
                query_filter = Filter(must=conditions)
            
            # Search
            results = self.client.search(
                collection_name=self.collections["knowledge"].name,
                query_vector=query_vector,
                query_filter=query_filter,
                limit=limit,
                with_payload=True
            )
            
            # Format results
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "id": result.id,
                    "score": result.score,
                    "content": result.payload.get("content", ""),
                    "metadata": {k: v for k, v in result.payload.items() if k != "content"}
                })
            
            logger.info(f"🔍 Found {len(formatted_results)} knowledge results")
            return formatted_results
            
        except Exception as e:
            logger.error(f"❌ Failed to search knowledge: {e}")
            raise
    
    async def store_conversation(
        self,
        conversation_id: str,
        content: str,
        metadata: Dict[str, Any],
        vector: List[float]
    ) -> str:
        """Store conversation in Qdrant"""
        if not self.initialized:
            await self.initialize()
        
        try:
            point_id = f"conv_{conversation_id}_{datetime.now().timestamp()}"
            
            point = PointStruct(
                id=point_id,
                vector=vector,
                payload={
                    "conversation_id": conversation_id,
                    "content": content,
                    "timestamp": datetime.now().isoformat(),
                    **metadata
                }
            )
            
            result = self.client.upsert(
                collection_name=self.collections["conversations"].name,
                points=[point]
            )
            
            logger.info(f"✅ Stored conversation: {point_id}")
            return point_id
            
        except Exception as e:
            logger.error(f"❌ Failed to store conversation: {e}")
            raise
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get health status of Qdrant service"""
        if not self.initialized:
            return {"status": "not_initialized", "collections": 0}
        
        try:
            # Get collections info
            collections = self.client.get_collections().collections
            collection_info = {}
            
            for collection in collections:
                if collection.name.startswith("sophia_"):
                    info = self.client.get_collection(collection.name)
                    collection_info[collection.name] = {
                        "vectors_count": info.vectors_count,
                        "points_count": info.points_count,
                        "status": info.status
                    }
            
            return {
                "status": "healthy",
                "collections": len(collection_info),
                "collection_details": collection_info,
                "architecture": "pure_qdrant"
            }
            
        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
            return {"status": "unhealthy", "error": str(e)}

# Global instance
_memory_service_v3_instance: Optional[UnifiedMemoryServiceV3] = None

async def get_memory_service() -> UnifiedMemoryServiceV3:
    """Get singleton instance of memory service"""
    global _memory_service_v3_instance
    if _memory_service_v3_instance is None:
        _memory_service_v3_instance = UnifiedMemoryServiceV3()
        await _memory_service_v3_instance.initialize()
    return _memory_service_v3_instance 