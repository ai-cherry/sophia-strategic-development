# File: backend/services/comprehensive_memory_service.py

from typing import List, Any, Optional
import json

from backend.agents.enhanced.data_models import MemoryRecord
from backend.utils.enhanced_snowflake_cortex_service import EnhancedSnowflakeCortexService
from backend.core.hierarchical_cache import HierarchicalCache
from backend.utils.logging import get_logger

try:
    import pinecone
    PINECONE_AVAILABLE = True
except ImportError:
    PINECONE_AVAILABLE = False

logger = get_logger(__name__)

class ComprehensiveMemoryService:
    """
    A centralized service for all memory operations, acting as a single source of truth.
    It orchestrates interactions with Snowflake, vector databases (Pinecone), and caching layers.
    """

    def __init__(self):
        self.cortex_service = EnhancedSnowflakeCortexService()
        self.cache = HierarchicalCache()
        self.pinecone_index = self._initialize_pinecone()

    def _initialize_pinecone(self) -> Optional[Any]:
        """Initializes the Pinecone index if configured."""
        if not PINECONE_AVAILABLE:
            logger.info("Pinecone SDK not installed, vector search will be limited to Snowflake.")
            return None
        
        from backend.core.auto_esc_config import get_config_value
        api_key = get_config_value("pinecone_api_key")
        environment = get_config_value("pinecone_environment")
        
        if not api_key or not environment:
            logger.warning("Pinecone API key or environment not configured.")
            return None
        
        try:
            pinecone.init(api_key=api_key, environment=environment)
            index_name = "sophia-ai-memory"
            if index_name not in pinecone.list_indexes():
                pinecone.create_index(name=index_name, dimension=1536, metric="cosine")
            logger.info("Pinecone initialized successfully.")
            return pinecone.Index(index_name)
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone: {e}", exc_info=True)
            return None

    async def store_memory(self, memory_record: MemoryRecord) -> str:
        """
        Stores a memory record in the appropriate backend (Snowflake, Pinecone).
        This is the single authoritative method for creating memories.
        """
        logger.info(f"Storing memory: {memory_record.id} in category {memory_record.category}")

        # 1. Generate embedding if not present
        if not memory_record.embedding:
            memory_record.embedding = await self.cortex_service.generate_embedding(memory_record.content)

        # 2. Store in Snowflake (as the primary source of truth)
        # This is a conceptual query; a real implementation would be more complex.
        # It would insert into the MEMORY_RECORDS table from our schema.
        await self.cortex_service.execute_query(
            "INSERT INTO AI_MEMORY.MEMORY_RECORDS (MEMORY_ID, CONTENT_SUMMARY, CATEGORY, TAGS) VALUES (%s, %s, %s, %s);",
            (memory_record.id, memory_record.content[:200], memory_record.category, json.dumps(memory_record.tags))
        )

        # 3. Upsert to Pinecone for vector search
        if self.pinecone_index and memory_record.embedding:
            metadata = {
                "category": memory_record.category,
                "tags": memory_record.tags,
                "importance_score": memory_record.importance_score,
                "created_at": memory_record.created_at.isoformat()
            }
            self.pinecone_index.upsert(vectors=[(memory_record.id, memory_record.embedding, metadata)])
            logger.info(f"Upserted memory {memory_record.id} to Pinecone.")

        # 4. Update cache
        await self.cache.set(f"memory:{memory_record.id}", memory_record.dict())
        
        return memory_record.id

    async def recall_memories(self, query: str, top_k: int = 5, category: Optional[str] = None) -> List[MemoryRecord]:
        """
        Recalls memories using a hybrid search strategy (vector search + metadata filtering).
        """
        logger.info(f"Recalling memories for query: '{query}'")
        
        query_embedding = await self.cortex_service.generate_embedding(query)
        
        if not self.pinecone_index or not query_embedding:
            logger.warning("Cannot perform vector search. Pinecone not configured or embedding failed.")
            return []

        pinecone_filter = {}
        if category:
            pinecone_filter['category'] = {'$eq': category}

        search_results = self.pinecone_index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True,
            filter=pinecone_filter
        )
        
        recalled_memories = []
        for match in search_results['matches']:
            # In a real app, we'd fetch the full record from Snowflake using the ID.
            # Here, we'll reconstruct from metadata for demonstration.
            recalled_memories.append(MemoryRecord(
                id=match['id'],
                content="Full content would be fetched from Snowflake.",
                category=match['metadata'].get('category'),
                tags=match['metadata'].get('tags', []),
                importance_score=match['metadata'].get('importance_score', 0.5)
                # ... and other fields
            ))
        
        logger.info(f"Recalled {len(recalled_memories)} memories.")
        return recalled_memories

    async def get_memory_by_id(self, memory_id: str) -> Optional[MemoryRecord]:
        """Retrieves a single memory by its unique ID."""
        cached_memory = await self.cache.get(f"memory:{memory_id}")
        if cached_memory:
            return MemoryRecord(**cached_memory)
            
        # If not in cache, fetch from Snowflake
        # Conceptual query
        result = await self.cortex_service.execute_query(
            "SELECT * FROM AI_MEMORY.MEMORY_RECORDS WHERE MEMORY_ID = %s;",
            (memory_id,)
        )
        if result:
            # Reconstruct the MemoryRecord object
            # ...
            return MemoryRecord(**result[0])
        return None 