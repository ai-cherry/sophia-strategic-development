"""
Memory Service Lifecycle Manager
Handles proper initialization, health monitoring, and graceful shutdown
"""

import asyncio
import logging
import signal
import sys
from typing import Optional
from backend.core.qdrant_connection_pool import get_qdrant_pool, close_qdrant_pool

logger = logging.getLogger(__name__)


class MemoryServiceLifecycleManager:
    """Manages memory service lifecycle"""
    
    def __init__(self):
        self._shutdown_event = asyncio.Event()
        self._health_task: Optional[asyncio.Task] = None
        self._initialized = False
    
    async def initialize(self):
        """Initialize memory service with proper setup"""
        logger.info("🚀 Initializing Memory Service Lifecycle...")
        
        try:
            # Initialize connection pool
            pool = await get_qdrant_pool()
            
            # Setup signal handlers for graceful shutdown
            self._setup_signal_handlers()
            
            # Start health monitoring
            self._health_task = asyncio.create_task(self._health_monitor())
            
            self._initialized = True
            logger.info("✅ Memory Service Lifecycle initialized")
            
        except Exception as e:
            logger.error(f"❌ Lifecycle initialization failed: {e}")
            raise
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            logger.info(f"📡 Received signal {signum}, initiating graceful shutdown...")
            asyncio.create_task(self.shutdown())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def _health_monitor(self):
        """Monitor service health"""
        while not self._shutdown_event.is_set():
            try:
                # Get pool stats
                pool = await get_qdrant_pool()
                stats = pool.get_stats()
                
                # Log health status
                if stats.failed_connections > stats.total_connections * 0.5:
                    logger.warning("⚠️ High connection failure rate detected")
                
                if stats.average_response_time > 1.0:
                    logger.warning("⚠️ High average response time detected")
                
                # Wait for next check
                await asyncio.wait_for(
                    self._shutdown_event.wait(), timeout=30
                )
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.warning(f"⚠️ Health monitor error: {e}")
                await asyncio.sleep(30)
    
    async def shutdown(self):
        """Graceful shutdown of memory service"""
        logger.info("🔄 Starting graceful shutdown...")
        
        # Signal shutdown
        self._shutdown_event.set()
        
        # Stop health monitoring
        if self._health_task:
            self._health_task.cancel()
            try:
                await self._health_task
            except asyncio.CancelledError:
                pass
        
        # Close connection pool
        await close_qdrant_pool()
        
        logger.info("✅ Graceful shutdown complete")
    
    def is_initialized(self) -> bool:
        """Check if lifecycle is initialized"""
        return self._initialized


# Global lifecycle manager
_lifecycle_manager: Optional[MemoryServiceLifecycleManager] = None


async def get_lifecycle_manager() -> MemoryServiceLifecycleManager:
    """Get or create lifecycle manager"""
    global _lifecycle_manager
    
    if _lifecycle_manager is None:
        _lifecycle_manager = MemoryServiceLifecycleManager()
        await _lifecycle_manager.initialize()
    
    return _lifecycle_manager
