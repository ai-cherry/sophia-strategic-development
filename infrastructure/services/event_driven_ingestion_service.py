#!/usr/bin/env python3
"""
Event-Driven Ingestion Service for Sophia AI
Phase 3: Rapid Foundation Implementation (August 2025)

Extends the existing EnhancedIngestionService with event-driven orchestration,
building on Phase 2 polyglot MCP ecosystem for enterprise-grade performance.
"""

from backend.services.sophia_unified_memory_service import get_memory_service, SophiaUnifiedMemoryService
import asyncio
import json
import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4

import aioredis

from core.config_manager import get_config_value

# Import our existing enhanced ingestion service
from infrastructure.services.enhanced_ingestion_service import (
    EnhancedIngestionService,
)

logger = logging.getLogger(__name__)


class EventType(str, Enum):
    """Event types for ingestion orchestration"""

    INGESTION_INITIATED = "ingestion.initiated"
    PROCESSING_STARTED = "processing.started"
    METADATA_REQUESTED = "metadata.requested"
    METADATA_RECEIVED = "metadata.received"
    CHUNKING_STARTED = "chunking.started"
    CHUNK_PREVIEW_READY = "chunk.preview.ready"
    CHUNK_APPROVED = "chunk.approved"
    EMBEDDING_STARTED = "embedding.started"
    PROGRESS_UPDATE = "progress.update"
    INGESTION_COMPLETED = "ingestion.completed"
    INGESTION_FAILED = "ingestion.failed"


@dataclass
class IngestionEvent:
    """Event data structure for ingestion orchestration"""

    event_id: str
    event_type: EventType
    job_id: str
    user_id: str
    timestamp: datetime
    payload: dict[str, Any]
    metadata: dict[str, Any] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "job_id": self.job_id,
            "user_id": self.user_id,
            "timestamp": self.timestamp.isoformat(),
            "payload": self.payload,
            "metadata": self.metadata or {},
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "IngestionEvent":
        """Create from dictionary"""
        return cls(
            event_id=data["event_id"],
            event_type=EventType(data["event_type"]),
            job_id=data["job_id"],
            user_id=data["user_id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            payload=data["payload"],
            metadata=data.get("metadata", {}),
        )


class IngestionEventBus:
    """Event bus for ingestion orchestration using Redis as message broker"""

    def __init__(self):
        self.redis: aioredis.Redis | None = None
        self.subscribers: dict[str, list[callable]] = {}
        self.is_running = False

    async def initialize(self):
        """Initialize Redis connection"""
        try:
            # Get Redis connection details from config
            redis_url = await get_config_value("redis_url", "redis://localhost:6379")
            self.redis = aioredis.from_url(redis_url, decode_responses=True)

            # Test connection
            await self.redis.ping()
            logger.info("✅ Event bus initialized with Redis")

        except Exception as e:
            logger.warning(f"⚠️ Redis not available, using in-memory fallback: {e}")
            # Fallback to in-memory event handling for development
            self.redis = None

    async def publish(self, event: IngestionEvent):
        """Publish event to the bus"""
        try:
            event_data = json.dumps(event.to_dict())

            if self.redis:
                # Publish to Redis
                await self.redis.publish(
                    f"ingestion:{event.event_type.value}", event_data
                )

                # Store in stream for replay capability
                await self.redis.xadd(
                    f"ingestion_stream:{event.job_id}",
                    event.to_dict(),
                    maxlen=1000,  # Keep last 1000 events per job
                )
            else:
                # In-memory fallback - directly call subscribers
                await self._handle_in_memory_event(event)

            logger.debug(
                f"📤 Published event: {event.event_type.value} for job {event.job_id}"
            )

        except Exception as e:
            logger.exception(f"❌ Failed to publish event: {e}")
            raise

    async def subscribe(self, event_pattern: str, handler: callable):
        """Subscribe to events matching pattern"""
        if event_pattern not in self.subscribers:
            self.subscribers[event_pattern] = []
        self.subscribers[event_pattern].append(handler)

        if self.redis and not self.is_running:
            # Start Redis subscriber task
            asyncio.create_task(self._redis_subscriber())
            self.is_running = True

    async def _redis_subscriber(self):
        """Redis subscriber task"""
        try:
            pubsub = self.redis.pubsub()
            await pubsub.psubscribe("ingestion:*")

            async for message in pubsub.listen():
                if message["type"] == "pmessage":
                    try:
                        event_data = json.loads(message["data"])
                        event = IngestionEvent.from_dict(event_data)
                        await self._handle_event(event)
                    except Exception as e:
                        logger.exception(f"❌ Error handling Redis event: {e}")

        except Exception as e:
            logger.exception(f"❌ Redis subscriber error: {e}")

    async def _handle_event(self, event: IngestionEvent):
        """Handle incoming event by calling subscribers"""
        for pattern, handlers in self.subscribers.items():
            if self._pattern_matches(pattern, event.event_type.value):
                for handler in handlers:
                    try:
                        await handler(event)
                    except Exception as e:
                        logger.exception(f"❌ Event handler error: {e}")

    async def _handle_in_memory_event(self, event: IngestionEvent):
        """Handle event in memory (fallback mode)"""
        await self._handle_event(event)

    def _pattern_matches(self, pattern: str, event_type: str) -> bool:
        """Simple pattern matching for event types"""
        if pattern == "*":
            return True
        if pattern.endswith("*"):
            return event_type.startswith(pattern[:-1])
        return pattern == event_type


class EventDrivenIngestionService(EnhancedIngestionService):
    """
    Event-driven ingestion service extending EnhancedIngestionService
    Implements enterprise-grade event orchestration while maintaining backwards compatibility
    """

    def __init__(self, 
        # Initialize parent class


        # Event-driven components
        self.event_bus = IngestionEventBus()
        self.event_driven_enabled = True  # Feature flag

        # Performance metrics
        self.metrics = {
            "events_published": 0,
            "events_processed": 0,
            "avg_processing_time": 0.0,
            "last_event_time": None,
        }

    async def initialize(self):
        """Initialize event-driven components"""
        try:
            # Initialize parent service
            await self.connect()

            # Initialize event bus
            await self.event_bus.initialize()

            logger.info("✅ Event-driven ingestion service initialized")

        except Exception as e:
            logger.exception(f"❌ Failed to initialize event-driven service: {e}")
            raise

    async def create_ingestion_job_event_driven(
        self,
        user_id: str,
        filename: str,
        file_content: bytes,
        file_type: str,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """
        Create ingestion job with event-driven processing
        New primary method for Phase 3
        """
        try:
            # Create job using parent method
            job = await self.create_ingestion_job(
                user_id, filename, file_content, file_type, metadata
            )

            if self.event_driven_enabled:
                # Publish ingestion initiated event
                event = IngestionEvent(
                    event_id=str(uuid4()),
                    event_type=EventType.INGESTION_INITIATED,
                    job_id=job.job_id,
                    user_id=user_id,
                    timestamp=datetime.now(),
                    payload={
                        "filename": filename,
                        "file_type": file_type,
                        "file_size": len(file_content),
                        "metadata": metadata or {},
                    },
                )

                await self.event_bus.publish(event)
                self.metrics["events_published"] += 1
                self.metrics["last_event_time"] = datetime.now()

                logger.info(f"📤 Published ingestion event for job {job.job_id}")
            else:
                # Fallback to direct processing
                asyncio.create_task(self.process_file_async(job.job_id, file_content))

            return job.job_id

        except Exception as e:
            logger.exception(f"❌ Failed to create event-driven ingestion job: {e}")
            raise

    async def publish_progress_event(self, job_id: str, progress_data: dict[str, Any]):
        """Publish progress update event for real-time streaming"""
        try:
            event = IngestionEvent(
                event_id=str(uuid4()),
                event_type=EventType.PROGRESS_UPDATE,
                job_id=job_id,
                user_id=progress_data.get("user_id", "system"),
                timestamp=datetime.now(),
                payload=progress_data,
            )

            await self.event_bus.publish(event)

        except Exception as e:
            logger.exception(f"❌ Failed to publish progress event: {e}")

    async def get_service_metrics(self) -> dict[str, Any]:
        """Get event-driven service metrics"""
        return {
            "service_type": "event_driven_ingestion",
            "event_driven_enabled": self.event_driven_enabled,
            "events_published": self.metrics["events_published"],
            "events_processed": self.metrics["events_processed"],
            "avg_processing_time": self.metrics["avg_processing_time"],
            "last_event_time": (
                self.metrics["last_event_time"].isoformat()
                if self.metrics["last_event_time"]
                else None
            ),
        }

    async def shutdown(self):
        """Graceful shutdown of event-driven components"""
        try:
            logger.info("🛑 Shutting down event-driven ingestion service...")

            # Close event bus connections
            if self.event_bus.redis:
                await self.event_bus.redis.close()

            # Disconnect parent service
            await self.disconnect()

            logger.info("✅ Event-driven ingestion service shutdown complete")

        except Exception as e:
            logger.exception(f"❌ Error during shutdown: {e}")


# Convenience functions for integration


async def create_event_driven_ingestion_service() -> EventDrivenIngestionService:
    """Create and initialize event-driven ingestion service"""
    service = EventDrivenIngestionService()
    await service.initialize()
    return service


if __name__ == "__main__":
    # Test the event-driven ingestion service
    async def main():
        logger.info("🧪 Testing event-driven ingestion service...")
        service = await create_event_driven_ingestion_service()

        try:
            # Test job creation
            job_id = await service.create_ingestion_job_event_driven(
                user_id="test_user",
                filename="test_document.txt",
                file_content=b"This is a test document for event-driven ingestion.",
                file_type="text/plain",
                metadata={"department": "Engineering", "priority": "high"},
            )

            logger.info(f"✅ Created test job: {job_id}")

            # Get metrics
            metrics = await service.get_service_metrics()
            logger.info(f"📊 Service metrics: {metrics}")

        except Exception as e:
            logger.exception(f"❌ Test failed: {e}")
        finally:
            await service.shutdown()

    asyncio.run(main())
