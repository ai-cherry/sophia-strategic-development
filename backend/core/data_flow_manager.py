"""
Sophia AI Data Flow Manager

Practical implementation of enterprise data flow with stability and scale patterns.
Focuses on engineering best practices without over-complexity.
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum

import redis.asyncio as redis_client
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.auto_esc_config import config

logger = logging.getLogger(__name__)


class CircuitBreakerState(Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


@dataclass
class DataSource:
    name: str
    source_type: str  # airbyte, webhook, api_poll, batch
    endpoint: str
    reliability_pattern: str  # circuit_breaker, retry, queue
    health_status: str = "healthy"
    last_sync: Optional[datetime] = None


@dataclass
class ProcessingTask:
    task_id: str
    source_data: Dict[str, Any]
    processing_type: str  # chunk, vectorize, enrich
    priority: int = 1  # 1=high, 2=medium, 3=low
    retry_count: int = 0
    max_retries: int = 3


class CircuitBreaker:
    """Simple circuit breaker for external service calls"""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitBreakerState.CLOSED
    
    async def call(self, func: Callable, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        if self.state == CircuitBreakerState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitBreakerState.HALF_OPEN
            else:
                raise Exception(f"Circuit breaker OPEN - service unavailable")
        
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e
    
    def _should_attempt_reset(self) -> bool:
        return (
            self.last_failure_time is not None and
            time.time() - self.last_failure_time > self.recovery_timeout
        )
    
    def _on_success(self):
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.state = CircuitBreakerState.CLOSED
            self.failure_count = 0
    
    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitBreakerState.OPEN


class IntelligentCache:
    """Multi-layer caching with business-aware TTL strategies"""
    
    def __init__(self):
        self.redis_client = None
        self.l1_cache = {}  # In-memory cache
        self.cache_strategies = {
            "executive_kpis": {"ttl": 300, "priority": "high"},      # 5 min
            "gong_summaries": {"ttl": 1800, "priority": "medium"},   # 30 min
            "competitive_data": {"ttl": 3600, "priority": "high"},   # 1 hour
            "llm_responses": {"ttl": 7200, "priority": "low"},       # 2 hours
        }
    
    async def initialize(self):
        """Initialize Redis connection"""
        try:
            self.redis_client = await redis_client.from_url(
                config.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            logger.info("Cache initialized successfully")
        except Exception as e:
            logger.warning(f"Redis unavailable, using in-memory only: {e}")
    
    async def get_with_fallback(
        self, 
        cache_key: str, 
        fallback_function: Callable,
        data_type: str = "default"
    ) -> Any:
        """Get data with intelligent caching and fallback"""
        
        # Try L1 cache (in-memory) first
        if cache_key in self.l1_cache:
            cache_data = self.l1_cache[cache_key]
            if not self._is_expired(cache_data):
                return cache_data["value"]
        
        # Try L2 cache (Redis) next
        if self.redis_client:
            try:
                cached_data = await self.redis_client.get(cache_key)
                if cached_data:
                    data = json.loads(cached_data)
                    # Populate L1 for next time
                    self.l1_cache[cache_key] = {
                        "value": data,
                        "timestamp": time.time(),
                        "ttl": self.cache_strategies.get(data_type, {"ttl": 1800})["ttl"]
                    }
                    return data
            except Exception as e:
                logger.warning(f"Redis cache error: {e}")
        
        # Fallback to source
        try:
            fresh_data = await fallback_function()
            await self._cache_data(cache_key, fresh_data, data_type)
            return fresh_data
        except Exception as e:
            logger.error(f"Fallback function failed: {e}")
            # Return stale data if available
            if cache_key in self.l1_cache:
                logger.warning("Returning stale data due to fallback failure")
                return self.l1_cache[cache_key]["value"]
            raise e
    
    async def _cache_data(self, key: str, data: Any, data_type: str):
        """Cache data in both L1 and L2"""
        strategy = self.cache_strategies.get(data_type, {"ttl": 1800})
        
        # L1 cache
        self.l1_cache[key] = {
            "value": data,
            "timestamp": time.time(),
            "ttl": strategy["ttl"]
        }
        
        # L2 cache (Redis)
        if self.redis_client:
            try:
                await self.redis_client.setex(
                    key,
                    strategy["ttl"],
                    json.dumps(data, default=str)
                )
            except Exception as e:
                logger.warning(f"Failed to cache in Redis: {e}")
    
    def _is_expired(self, cache_data: Dict) -> bool:
        """Check if cached data is expired"""
        return time.time() - cache_data["timestamp"] > cache_data["ttl"]


class DataFlowManager:
    """
    Central orchestrator for Sophia AI data pipeline
    Implements stability and scale patterns for enterprise data processing
    """
    
    def __init__(self):
        self.data_sources: Dict[str, DataSource] = {}
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.processing_queue = asyncio.Queue()
        self.dead_letter_queue = asyncio.Queue()
        self.cache = IntelligentCache()
        self.health_status = "initializing"
        
        # Processing workers
        self.worker_count = 3
        self.workers = []
        
        # Metrics
        self.metrics = {
            "processed_events": 0,
            "failed_events": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "last_health_check": None
        }
    
    async def initialize(self):
        """Initialize the data flow manager"""
        try:
            await self.cache.initialize()
            await self._register_data_sources()
            await self._start_processing_workers()
            self.health_status = "healthy"
            logger.info("DataFlowManager initialized successfully")
        except Exception as e:
            self.health_status = "unhealthy"
            logger.error(f"Failed to initialize DataFlowManager: {e}")
            raise e
    
    async def _register_data_sources(self):
        """Register all data sources with their reliability patterns"""
        sources = [
            DataSource("gong", "airbyte", config.gong_api_base_url, "circuit_breaker"),
            DataSource("hubspot", "airbyte", config.hubspot_api_base_url, "circuit_breaker"),
            # TODO: HYBRID APPROACH - Maintain existing HubSpot ingestion for training/interaction
            # PLUS add Snowflake Secure Data Sharing for enterprise analytics
            # See backend/utils/snowflake_hubspot_connector.py for blended access patterns
            DataSource("slack", "webhook", config.slack_webhook_url, "queue"),
            DataSource("linear", "airbyte", config.linear_api_base_url, "retry"),
            DataSource("github", "webhook", config.github_webhook_url, "queue"),
            DataSource("costar", "batch", config.costar_api_base_url, "retry"),
            DataSource("apollo", "api_poll", config.apollo_api_base_url, "circuit_breaker"),
        ]
        
        for source in sources:
            self.data_sources[source.name] = source
            if source.reliability_pattern == "circuit_breaker":
                self.circuit_breakers[source.name] = CircuitBreaker()
        
        logger.info(f"Registered {len(sources)} data sources")
    
    async def _start_processing_workers(self):
        """Start async workers for processing tasks"""
        for i in range(self.worker_count):
            worker = asyncio.create_task(self._processing_worker(f"worker-{i}"))
            self.workers.append(worker)
        
        logger.info(f"Started {self.worker_count} processing workers")
    
    async def _processing_worker(self, worker_name: str):
        """Background worker for processing data tasks"""
        logger.info(f"Processing worker {worker_name} started")
        
        while True:
            try:
                # Get task from queue with timeout
                task = await asyncio.wait_for(
                    self.processing_queue.get(), 
                    timeout=30
                )
                
                await self._process_task(task, worker_name)
                self.processing_queue.task_done()
                
            except asyncio.TimeoutError:
                # No tasks available, continue waiting
                continue
            except Exception as e:
                logger.error(f"Worker {worker_name} error: {e}")
                await asyncio.sleep(1)  # Brief pause before retrying
    
    async def _process_task(self, task: ProcessingTask, worker_name: str):
        """Process a single data task with retry logic"""
        try:
            logger.debug(f"Worker {worker_name} processing task {task.task_id}")
            
            if task.processing_type == "chunk":
                result = await self._chunk_data(task.source_data)
            elif task.processing_type == "vectorize":
                result = await self._vectorize_data(task.source_data)
            elif task.processing_type == "enrich":
                result = await self._enrich_data(task.source_data)
            else:
                raise ValueError(f"Unknown processing type: {task.processing_type}")
            
            # Store processed result
            await self._store_processed_data(task.task_id, result)
            self.metrics["processed_events"] += 1
            
            logger.debug(f"Task {task.task_id} completed successfully")
            
        except Exception as e:
            logger.error(f"Task {task.task_id} failed: {e}")
            task.retry_count += 1
            
            if task.retry_count < task.max_retries:
                # Exponential backoff retry
                delay = 2 ** task.retry_count
                await asyncio.sleep(delay)
                await self.processing_queue.put(task)
                logger.info(f"Task {task.task_id} queued for retry {task.retry_count}/{task.max_retries}")
            else:
                # Send to dead letter queue
                await self.dead_letter_queue.put({
                    "task": task,
                    "error": str(e),
                    "timestamp": datetime.now(),
                    "worker": worker_name
                })
                self.metrics["failed_events"] += 1
                logger.error(f"Task {task.task_id} sent to dead letter queue after {task.max_retries} retries")
    
    async def ingest_data(self, source_name: str, data: Dict[str, Any]) -> bool:
        """Ingest data from external source with reliability patterns"""
        source = self.data_sources.get(source_name)
        if not source:
            logger.error(f"Unknown data source: {source_name}")
            return False
        
        try:
            # Apply reliability pattern
            if source.reliability_pattern == "circuit_breaker":
                circuit_breaker = self.circuit_breakers[source_name]
                await circuit_breaker.call(self._validate_and_queue_data, source_name, data)
            elif source.reliability_pattern == "queue":
                await self._validate_and_queue_data(source_name, data)
            elif source.reliability_pattern == "retry":
                await self._retry_validate_and_queue_data(source_name, data)
            
            source.last_sync = datetime.now()
            source.health_status = "healthy"
            return True
            
        except Exception as e:
            logger.error(f"Failed to ingest data from {source_name}: {e}")
            source.health_status = "unhealthy"
            return False
    
    async def _validate_and_queue_data(self, source_name: str, data: Dict[str, Any]):
        """Validate data and queue for processing"""
        # Basic validation
        if not data or not isinstance(data, dict):
            raise ValueError("Invalid data format")
        
        # Create processing tasks based on data type
        tasks = []
        
        if source_name == "gong" and "transcript" in data:
            tasks.append(ProcessingTask(
                task_id=f"gong-chunk-{data.get('call_id', 'unknown')}",
                source_data=data,
                processing_type="chunk",
                priority=1
            ))
        
        if "text_content" in data:
            tasks.append(ProcessingTask(
                task_id=f"{source_name}-vectorize-{int(time.time())}",
                source_data=data,
                processing_type="vectorize",
                priority=2
            ))
        
        # Queue tasks for processing
        for task in tasks:
            await self.processing_queue.put(task)
        
        logger.info(f"Queued {len(tasks)} processing tasks for {source_name}")
    
    async def _retry_validate_and_queue_data(self, source_name: str, data: Dict[str, Any], max_retries: int = 3):
        """Validate and queue data with retry logic"""
        for attempt in range(max_retries):
            try:
                await self._validate_and_queue_data(source_name, data)
                return
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
    
    async def _chunk_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Intelligent chunking based on content type"""
        if "transcript" in data:
            # Gong call chunking by speaker turns
            chunks = []
            current_chunk = []
            current_speaker = None
            
            for turn in data["transcript"].get("turns", []):
                if turn.get("speaker") != current_speaker and current_chunk:
                    chunks.append({
                        "content": " ".join(current_chunk),
                        "speaker": current_speaker,
                        "context": "conversation_turn",
                        "metadata": {"turn_count": len(current_chunk)}
                    })
                    current_chunk = []
                
                current_chunk.append(turn.get("text", ""))
                current_speaker = turn.get("speaker")
            
            # Add final chunk
            if current_chunk:
                chunks.append({
                    "content": " ".join(current_chunk),
                    "speaker": current_speaker,
                    "context": "conversation_turn",
                    "metadata": {"turn_count": len(current_chunk)}
                })
            
            return {"chunks": chunks, "chunk_type": "speaker_turns"}
        
        elif "document_text" in data:
            # Document chunking by semantic sections
            text = data["document_text"]
            # Simple sentence-based chunking (can be enhanced with semantic analysis)
            sentences = text.split('. ')
            chunks = []
            current_chunk = []
            current_length = 0
            max_chunk_length = 1000
            
            for sentence in sentences:
                if current_length + len(sentence) > max_chunk_length and current_chunk:
                    chunks.append({
                        "content": '. '.join(current_chunk) + '.',
                        "context": "document_section",
                        "metadata": {"sentence_count": len(current_chunk)}
                    })
                    current_chunk = []
                    current_length = 0
                
                current_chunk.append(sentence)
                current_length += len(sentence)
            
            # Add final chunk
            if current_chunk:
                chunks.append({
                    "content": '. '.join(current_chunk) + '.',
                    "context": "document_section",
                    "metadata": {"sentence_count": len(current_chunk)}
                })
            
            return {"chunks": chunks, "chunk_type": "semantic_sections"}
        
        else:
            # Default chunking
            return {"chunks": [{"content": str(data), "context": "raw_data"}], "chunk_type": "raw"}
    
    async def _vectorize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate embeddings for chunks"""
        # This would integrate with OpenAI/Cohere for embeddings
        # For now, return placeholder
        return {
            "embeddings_generated": True,
            "embedding_model": "text-embedding-3-large",
            "chunk_count": len(data.get("chunks", []))
        }
    
    async def _enrich_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich data with business context"""
        # Extract business entities, sentiment, etc.
        return {
            "enriched": True,
            "business_entities": {
                "competitors": [],
                "products": [],
                "customers": []
            },
            "sentiment_score": 0.0
        }
    
    async def _store_processed_data(self, task_id: str, result: Dict[str, Any]):
        """Store processed data in appropriate storage systems"""
        # This would integrate with Snowflake, Pinecone, etc.
        logger.debug(f"Storing processed data for task {task_id}")
        # Implementation would depend on result type and storage destination
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status"""
        source_health = {}
        for name, source in self.data_sources.items():
            source_health[name] = {
                "status": source.health_status,
                "last_sync": source.last_sync.isoformat() if source.last_sync else None
            }
        
        circuit_breaker_status = {}
        for name, cb in self.circuit_breakers.items():
            circuit_breaker_status[name] = {
                "state": cb.state.value,
                "failure_count": cb.failure_count
            }
        
        queue_status = {
            "processing_queue_size": self.processing_queue.qsize(),
            "dead_letter_queue_size": self.dead_letter_queue.qsize(),
            "active_workers": len([w for w in self.workers if not w.done()])
        }
        
        self.metrics["last_health_check"] = datetime.now().isoformat()
        
        return {
            "overall_status": self.health_status,
            "data_sources": source_health,
            "circuit_breakers": circuit_breaker_status,
            "queues": queue_status,
            "metrics": self.metrics,
            "cache_status": "healthy" if self.cache.redis_client else "degraded"
        }
    
    async def shutdown(self):
        """Graceful shutdown of data flow manager"""
        logger.info("Shutting down DataFlowManager...")
        
        # Cancel workers
        for worker in self.workers:
            worker.cancel()
        
        # Wait for current tasks to complete
        await self.processing_queue.join()
        
        # Close Redis connection
        if self.cache.redis_client:
            await self.cache.redis_client.close()
        
        logger.info("DataFlowManager shutdown complete")


# Global instance
data_flow_manager = DataFlowManager()


async def get_data_flow_manager() -> DataFlowManager:
    """Get the global data flow manager instance"""
    if data_flow_manager.health_status == "initializing":
        await data_flow_manager.initialize()
    return data_flow_manager 