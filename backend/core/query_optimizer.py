"""
Query Pattern Optimizations
Implements efficient query patterns and caching strategies
"""

import asyncio
import logging
import hashlib
import json
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
import time

logger = logging.getLogger(__name__)

@dataclass
class QueryResult:
    """Query result with metadata"""
    data: Any
    execution_time: float
    cached: bool = False
    cache_key: Optional[str] = None

class QueryOptimizer:
    """Optimizes Qdrant queries for better performance"""
    
    def __init__(self, cache_ttl: int = 300):  # 5 minute cache
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._cache_ttl = cache_ttl
        
    def _generate_cache_key(self, collection_name: str, query_params: Dict[str, Any]) -> str:
        """Generate cache key for query"""
        # Create deterministic hash from query parameters
        query_str = json.dumps(query_params, sort_keys=True)
        cache_input = f"{collection_name}:{query_str}"
        return hashlib.md5(cache_input.encode()).hexdigest()
    
    def _is_cache_valid(self, cache_entry: Dict[str, Any]) -> bool:
        """Check if cache entry is still valid"""
        return time.time() - cache_entry["timestamp"] < self._cache_ttl
    
    async def execute_search_with_cache(
        self,
        qdrant_client,
        collection_name: str,
        query_vector: Optional[List[float]] = None,
        query_filter: Optional[Dict[str, Any]] = None,
        limit: int = 10,
        offset: int = 0
    ) -> QueryResult:
        """Execute search query with caching"""
        from backend.core.memory_service_monitor import get_memory_monitor
        
        monitor = get_memory_monitor()
        start_time = time.time()
        
        # Generate cache key
        query_params = {
            "query_vector": query_vector,
            "query_filter": query_filter,
            "limit": limit,
            "offset": offset
        }
        cache_key = self._generate_cache_key(collection_name, query_params)
        
        # Check cache first
        if cache_key in self._cache and self._is_cache_valid(self._cache[cache_key]):
            monitor.record_cache_hit()
            execution_time = time.time() - start_time
            monitor.record_query(execution_time, True)
            
            return QueryResult(
                data=self._cache[cache_key]["data"],
                execution_time=execution_time,
                cached=True,
                cache_key=cache_key
            )
        
        # Execute query
        try:
            if query_vector:
                results = await asyncio.to_thread(
                    qdrant_client.search,
                    collection_name=collection_name,
                    query_vector=query_vector,
                    query_filter=query_filter,
                    limit=limit,
                    offset=offset
                )
            else:
                results = await asyncio.to_thread(
                    qdrant_client.scroll,
                    collection_name=collection_name,
                    scroll_filter=query_filter,
                    limit=limit,
                    offset=offset
                )
            
            execution_time = time.time() - start_time
            
            # Cache result
            self._cache[cache_key] = {
                "data": results,
                "timestamp": time.time()
            }
            
            monitor.record_cache_miss()
            monitor.record_query(execution_time, True)
            
            return QueryResult(
                data=results,
                execution_time=execution_time,
                cached=False,
                cache_key=cache_key
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            monitor.record_query(execution_time, False)
            logger.error(f"❌ Query execution failed: {e}")
            raise
    
    async def execute_batch_search(
        self,
        qdrant_client,
        collection_name: str,
        queries: List[Dict[str, Any]]
    ) -> List[QueryResult]:
        """Execute multiple queries in batch for better performance"""
        tasks = []
        
        for query in queries:
            task = self.execute_search_with_cache(
                qdrant_client,
                collection_name,
                **query
            )
            tasks.append(task)
        
        # Execute all queries concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert exceptions to error results
        processed_results = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"❌ Batch query failed: {result}")
                processed_results.append(QueryResult(
                    data=None,
                    execution_time=0.0,
                    cached=False
                ))
            else:
                processed_results.append(result)
        
        return processed_results
    
    def clear_cache(self):
        """Clear query cache"""
        self._cache.clear()
        logger.info("🧹 Query cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        valid_entries = sum(
            1 for entry in self._cache.values()
            if self._is_cache_valid(entry)
        )
        
        return {
            "total_entries": len(self._cache),
            "valid_entries": valid_entries,
            "cache_size_mb": len(str(self._cache)) / 1024 / 1024
        }

# Global query optimizer
_query_optimizer: Optional[QueryOptimizer] = None

def get_query_optimizer() -> QueryOptimizer:
    """Get global query optimizer"""
    global _query_optimizer
    
    if _query_optimizer is None:
        _query_optimizer = QueryOptimizer()
    
    return _query_optimizer
