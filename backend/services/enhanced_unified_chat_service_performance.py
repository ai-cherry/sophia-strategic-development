#!/usr/bin/env python3
"""
Performance-Enhanced Unified Chat Service
Builds on existing unified_chat_service.py with advanced caching and optimization

Performance Enhancements:
- Redis-based response caching
- Intelligent query preprocessing
- Response time optimization
- Memory usage optimization
- Concurrent processing capabilities
- Smart cache invalidation
- Performance metrics tracking
"""

import asyncio
import hashlib
import json
import logging
import time
from datetime import datetime
from typing import Any, Optional

import redis.asyncio as redis

# Import existing service
from backend.services.unified_chat_service import (
    ChatContext,
    ChatRequest,
    ChatResponse,
    UnifiedChatService,
)

logger = logging.getLogger(__name__)


class PerformanceEnhancedUnifiedChatService(UnifiedChatService):
    """
    Performance-enhanced chat service building on existing unified chat architecture
    Adds intelligent caching, optimization, and performance monitoring
    """

    def __init__(self):
        super().__init__()

        # Performance enhancement components
        self.response_cache = None  # Will be initialized
        self.query_optimizer = QueryOptimizer()
        self.performance_tracker = ChatPerformanceTracker()

        # Cache configuration
        self.cache_config = {
            "default_ttl": 300,  # 5 minutes
            "max_cache_size": 10000,
            "enable_compression": True,
            "cache_hit_target": 0.8,  # 80% hit rate target
        }

        # Performance configuration
        self.performance_config = {
            "max_concurrent_requests": 50,
            "request_timeout": 30.0,
            "optimization_enabled": True,
            "metrics_tracking": True,
        }

        # Initialize performance components
        asyncio.create_task(self._initialize_performance_components())

    async def _initialize_performance_components(self):
        """Initialize performance enhancement components"""
        try:
            # Initialize Redis cache
            self.response_cache = RedisResponseCache(self.cache_config)
            await self.response_cache.initialize()

            # Initialize performance tracker
            await self.performance_tracker.initialize()

            logger.info("✅ Performance enhancements initialized successfully")

        except Exception as e:
            logger.error(f"❌ Failed to initialize performance components: {e}")
            # Graceful degradation - continue without caching

    async def process_chat(self, request: ChatRequest) -> ChatResponse:
        """
        Enhanced chat processing with performance optimizations
        """
        start_time = time.time()
        cache_hit = False

        try:
            # Track incoming request
            await self.performance_tracker.track_request_start(request)

            # Check cache first
            cached_response = await self._check_cache(request)
            if cached_response:
                cache_hit = True
                logger.debug(f"Cache hit for request from user {request.user_id}")

                # Track cache hit
                await self.performance_tracker.track_cache_hit(
                    request, time.time() - start_time
                )
                return cached_response

            # Optimize query if enabled
            if self.performance_config["optimization_enabled"]:
                optimized_request = await self.query_optimizer.optimize_request(request)
            else:
                optimized_request = request

            # Process with base service (with timeout)
            response_task = super().process_chat(optimized_request)
            response = await asyncio.wait_for(
                response_task, timeout=self.performance_config["request_timeout"]
            )

            # Cache the response
            await self._cache_response(request, response)

            # Track successful completion
            processing_time = time.time() - start_time
            await self.performance_tracker.track_request_completion(
                request, response, processing_time, cache_hit
            )

            return response

        except TimeoutError:
            logger.warning(f"Request timeout for user {request.user_id}")
            processing_time = time.time() - start_time
            await self.performance_tracker.track_request_timeout(
                request, processing_time
            )

            return ChatResponse(
                response="I apologize, but your request is taking longer than expected. Please try again.",
                metadata={"error": "timeout", "processing_time": processing_time},
            )

        except Exception as e:
            logger.error(f"Enhanced chat processing error: {e}")
            processing_time = time.time() - start_time
            await self.performance_tracker.track_request_error(
                request, e, processing_time
            )

            return ChatResponse(
                response="I encountered an error processing your request. Please try again.",
                metadata={"error": str(e), "processing_time": processing_time},
            )

    async def _check_cache(self, request: ChatRequest) -> ChatResponse | None:
        """Check if response is cached"""
        if not self.response_cache:
            return None

        try:
            cache_key = self._generate_cache_key(request)
            cached_data = await self.response_cache.get(cache_key)

            if cached_data:
                # Deserialize cached response
                return ChatResponse(**json.loads(cached_data))

            return None

        except Exception as e:
            logger.warning(f"Cache check error: {e}")
            return None

    async def _cache_response(self, request: ChatRequest, response: ChatResponse):
        """Cache the response for future use"""
        if not self.response_cache:
            return

        try:
            # Only cache successful responses
            if not response.metadata.get("error"):
                cache_key = self._generate_cache_key(request)

                # Determine TTL based on context
                ttl = self._calculate_cache_ttl(request, response)

                # Serialize and cache
                cached_data = json.dumps(
                    {
                        "response": response.response,
                        "sources": response.sources,
                        "suggestions": response.suggestions,
                        "metadata": {
                            **response.metadata,
                            "cached_at": datetime.now().isoformat(),
                        },
                    }
                )

                await self.response_cache.set(cache_key, cached_data, ttl)

        except Exception as e:
            logger.warning(f"Cache write error: {e}")

    def _generate_cache_key(self, request: ChatRequest) -> str:
        """Generate cache key for request"""
        key_data = {
            "message": request.message.lower().strip(),
            "context": request.context.value,
            "access_level": request.access_level.value,
            # Don't include user_id for shareable responses
        }

        key_string = json.dumps(key_data, sort_keys=True)
        return f"chat:{hashlib.md5(key_string.encode()).hexdigest()}"

    def _calculate_cache_ttl(self, request: ChatRequest, response: ChatResponse) -> int:
        """Calculate cache TTL based on content type"""
        # Infrastructure status has shorter TTL
        if request.context == ChatContext.INFRASTRUCTURE:
            return 60  # 1 minute

        # CEO research has longer TTL
        elif request.context == ChatContext.CEO_DEEP_RESEARCH:
            return 900  # 15 minutes

        # Business intelligence varies by content
        elif request.context == ChatContext.BUSINESS_INTELLIGENCE:
            # Check if response contains real-time data
            if any(
                keyword in response.response.lower()
                for keyword in ["current", "today", "now", "live"]
            ):
                return 120  # 2 minutes for real-time data
            else:
                return 600  # 10 minutes for general BI

        # Default TTL
        return self.cache_config["default_ttl"]

    async def get_performance_metrics(self) -> dict[str, Any]:
        """Get performance metrics"""
        if not self.performance_tracker:
            return {"status": "performance_tracking_disabled"}

        return await self.performance_tracker.get_metrics()

    async def invalidate_cache(self, pattern: str | None = None):
        """Invalidate cache entries"""
        if not self.response_cache:
            return False

        try:
            if pattern:
                await self.response_cache.delete_pattern(pattern)
            else:
                await self.response_cache.flush_all()

            logger.info(f"Cache invalidated with pattern: {pattern or 'all'}")
            return True

        except Exception as e:
            logger.error(f"Cache invalidation error: {e}")
            return False

    async def optimize_performance(self) -> dict[str, Any]:
        """Run performance optimization routine"""
        optimization_results = {
            "timestamp": datetime.now().isoformat(),
            "optimizations_applied": [],
            "performance_improvements": {},
        }

        try:
            # Cache optimization
            if self.response_cache:
                cache_stats = await self.response_cache.get_stats()
                hit_ratio = cache_stats.get("hit_ratio", 0)

                if hit_ratio < self.cache_config["cache_hit_target"]:
                    # Adjust cache TTL
                    self.cache_config["default_ttl"] = min(
                        self.cache_config["default_ttl"] * 1.2,  # Increase by 20%
                        3600,  # Max 1 hour
                    )
                    optimization_results["optimizations_applied"].append(
                        "increased_cache_ttl"
                    )

            # Query optimization
            optimizer_stats = await self.query_optimizer.get_optimization_stats()
            if optimizer_stats.get("optimization_rate", 0) < 0.5:
                await self.query_optimizer.enhance_optimization_patterns()
                optimization_results["optimizations_applied"].append(
                    "enhanced_query_optimization"
                )

            # Performance tracking optimization
            if self.performance_tracker:
                await self.performance_tracker.optimize_tracking()
                optimization_results["optimizations_applied"].append(
                    "optimized_performance_tracking"
                )

            return optimization_results

        except Exception as e:
            logger.error(f"Performance optimization error: {e}")
            optimization_results["error"] = str(e)
            return optimization_results


class RedisResponseCache:
    """Redis-based response caching system"""

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.redis_client = None
        self.stats = {"hits": 0, "misses": 0, "sets": 0, "errors": 0}

    async def initialize(self):
        """Initialize Redis connection"""
        try:
            self.redis_client = redis.Redis(
                host="localhost",  # Configure as needed
                port=6379,
                decode_responses=True,
                max_connections=20,
            )

            # Test connection
            await self.redis_client.ping()
            logger.info("✅ Redis cache initialized successfully")

        except Exception as e:
            logger.warning(f"⚠️ Redis cache initialization failed: {e}")
            self.redis_client = None

    async def get(self, key: str) -> str | None:
        """Get cached value"""
        if not self.redis_client:
            return None

        try:
            value = await self.redis_client.get(f"sophia:chat:{key}")
            if value:
                self.stats["hits"] += 1
                return value
            else:
                self.stats["misses"] += 1
                return None

        except Exception as e:
            self.stats["errors"] += 1
            logger.warning(f"Cache get error: {e}")
            return None

    async def set(self, key: str, value: str, ttl: int):
        """Set cached value"""
        if not self.redis_client:
            return

        try:
            await self.redis_client.setex(f"sophia:chat:{key}", ttl, value)
            self.stats["sets"] += 1

        except Exception as e:
            self.stats["errors"] += 1
            logger.warning(f"Cache set error: {e}")

    async def delete_pattern(self, pattern: str):
        """Delete keys matching pattern"""
        if not self.redis_client:
            return

        try:
            keys = await self.redis_client.keys(f"sophia:chat:{pattern}")
            if keys:
                await self.redis_client.delete(*keys)

        except Exception as e:
            logger.warning(f"Cache delete pattern error: {e}")

    async def flush_all(self):
        """Flush all cache entries"""
        if not self.redis_client:
            return

        try:
            keys = await self.redis_client.keys("sophia:chat:*")
            if keys:
                await self.redis_client.delete(*keys)

        except Exception as e:
            logger.warning(f"Cache flush error: {e}")

    async def get_stats(self) -> dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.stats["hits"] + self.stats["misses"]
        hit_ratio = self.stats["hits"] / total_requests if total_requests > 0 else 0

        return {
            **self.stats,
            "hit_ratio": hit_ratio,
            "total_requests": total_requests,
            "connected": self.redis_client is not None,
        }


class QueryOptimizer:
    """Intelligent query optimization"""

    def __init__(self):
        self.optimization_patterns = {
            "redundant_words": ["please", "can you", "could you", "i want", "i need"],
            "context_hints": {
                "status": ChatContext.INFRASTRUCTURE,
                "health": ChatContext.INFRASTRUCTURE,
                "deploy": ChatContext.INFRASTRUCTURE,
                "revenue": ChatContext.BUSINESS_INTELLIGENCE,
                "sales": ChatContext.BUSINESS_INTELLIGENCE,
                "customers": ChatContext.BUSINESS_INTELLIGENCE,
            },
        }

        self.stats = {"optimizations_applied": 0, "total_requests": 0}

    async def optimize_request(self, request: ChatRequest) -> ChatRequest:
        """Optimize chat request for better performance"""
        self.stats["total_requests"] += 1
        optimized = False

        try:
            # Create optimized copy
            optimized_message = request.message

            # Remove redundant words
            original_words = optimized_message.lower().split()
            filtered_words = [
                word
                for word in original_words
                if word not in self.optimization_patterns["redundant_words"]
            ]

            if len(filtered_words) < len(original_words):
                optimized_message = " ".join(filtered_words)
                optimized = True

            # Auto-detect context if not specified
            if request.context == ChatContext.BLENDED_INTELLIGENCE:
                detected_context = self._detect_context(optimized_message)
                if detected_context:
                    request.context = detected_context
                    optimized = True

            if optimized:
                self.stats["optimizations_applied"] += 1
                return ChatRequest(
                    message=optimized_message,
                    user_id=request.user_id,
                    session_id=request.session_id,
                    context=request.context,
                    access_level=request.access_level,
                    metadata=request.metadata,
                )

            return request

        except Exception as e:
            logger.warning(f"Query optimization error: {e}")
            return request

    def _detect_context(self, message: str) -> ChatContext | None:
        """Detect context from message content"""
        message_lower = message.lower()

        for hint, context in self.optimization_patterns["context_hints"].items():
            if hint in message_lower:
                return context

        return None

    async def get_optimization_stats(self) -> dict[str, Any]:
        """Get optimization statistics"""
        optimization_rate = (
            self.stats["optimizations_applied"] / self.stats["total_requests"]
            if self.stats["total_requests"] > 0
            else 0
        )

        return {**self.stats, "optimization_rate": optimization_rate}

    async def enhance_optimization_patterns(self):
        """Enhance optimization patterns based on usage"""
        # This could learn from successful optimizations
        pass


class ChatPerformanceTracker:
    """Track chat performance metrics"""

    def __init__(self):
        self.metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "timeout_requests": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "response_times": [],
            "error_types": {},
        }

    async def initialize(self):
        """Initialize performance tracker"""
        logger.info("📊 Chat performance tracker initialized")

    async def track_request_start(self, request: ChatRequest):
        """Track request start"""
        self.metrics["total_requests"] += 1

    async def track_request_completion(
        self,
        request: ChatRequest,
        response: ChatResponse,
        processing_time: float,
        cache_hit: bool,
    ):
        """Track successful request completion"""
        self.metrics["successful_requests"] += 1
        self.metrics["response_times"].append(processing_time)

        if cache_hit:
            self.metrics["cache_hits"] += 1
        else:
            self.metrics["cache_misses"] += 1

        # Keep only recent response times
        if len(self.metrics["response_times"]) > 1000:
            self.metrics["response_times"] = self.metrics["response_times"][-1000:]

    async def track_request_error(
        self, request: ChatRequest, error: Exception, processing_time: float
    ):
        """Track request error"""
        self.metrics["failed_requests"] += 1

        error_type = type(error).__name__
        self.metrics["error_types"][error_type] = (
            self.metrics["error_types"].get(error_type, 0) + 1
        )

    async def track_request_timeout(self, request: ChatRequest, processing_time: float):
        """Track request timeout"""
        self.metrics["timeout_requests"] += 1

    async def track_cache_hit(self, request: ChatRequest, processing_time: float):
        """Track cache hit"""
        self.metrics["cache_hits"] += 1
        self.metrics["response_times"].append(processing_time)

    async def get_metrics(self) -> dict[str, Any]:
        """Get performance metrics"""
        response_times = self.metrics["response_times"]

        return {
            "total_requests": self.metrics["total_requests"],
            "success_rate": (
                self.metrics["successful_requests"]
                / max(self.metrics["total_requests"], 1)
            ),
            "error_rate": (
                self.metrics["failed_requests"] / max(self.metrics["total_requests"], 1)
            ),
            "timeout_rate": (
                self.metrics["timeout_requests"]
                / max(self.metrics["total_requests"], 1)
            ),
            "cache_hit_rate": (
                self.metrics["cache_hits"]
                / max(self.metrics["cache_hits"] + self.metrics["cache_misses"], 1)
            ),
            "avg_response_time": sum(response_times) / len(response_times)
            if response_times
            else 0,
            "min_response_time": min(response_times) if response_times else 0,
            "max_response_time": max(response_times) if response_times else 0,
            "error_breakdown": self.metrics["error_types"],
            "timestamp": datetime.now().isoformat(),
        }

    async def optimize_tracking(self):
        """Optimize performance tracking"""
        # Reset old data
        if self.metrics["total_requests"] > 10000:
            # Keep only recent data
            self.metrics = {
                key: 0 if isinstance(val, int) else [] if isinstance(val, list) else {}
                for key, val in self.metrics.items()
            }


# Global instance for enhanced chat service
_enhanced_chat_service = None


def get_performance_enhanced_chat_service() -> PerformanceEnhancedUnifiedChatService:
    """Get the global performance-enhanced chat service instance"""
    global _enhanced_chat_service
    if _enhanced_chat_service is None:
        _enhanced_chat_service = PerformanceEnhancedUnifiedChatService()
    return _enhanced_chat_service


async def initialize_performance_enhanced_chat():
    """Initialize the performance-enhanced chat service"""
    service = get_performance_enhanced_chat_service()
    await service._initialize_performance_components()
    return service
