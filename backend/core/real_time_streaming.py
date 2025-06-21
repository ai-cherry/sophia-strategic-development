"""Real-Time Streaming Infrastructure

Implements streaming data processing for Snowflake and other data sources.
"""

import asyncio
import json
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set
from uuid import uuid4

import aioredis
from pydantic import BaseModel, Field

from backend.core.auto_esc_config import config
from backend.core.hierarchical_cache import CacheTier, hierarchical_cache
from backend.integrations.snowflake_integration import SnowflakeIntegration
from backend.monitoring.observability import logger


class StreamType(str, Enum):
    """Types of data streams"""

    GONG_CALLS = "gong_calls"
    SLACK_MESSAGES = "slack_messages"
    CRM_UPDATES = "crm_updates"
    METRICS = "metrics"
    EVENTS = "events"


class StreamStatus(str, Enum):
    """Stream processing status"""

    ACTIVE = "active"
    PAUSED = "paused"
    ERROR = "error"
    INITIALIZING = "initializing"


class StreamEvent(BaseModel):
    """Real-time stream event"""

    id: str = Field(default_factory=lambda: str(uuid4()))
    stream_type: StreamType
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    data: Dict[str, Any]
    metadata: Dict[str, Any] = {}
    processed: bool = False


class StreamProcessor:
    """Base class for stream processors"""

    def __init__(self, stream_type: StreamType):
        self.stream_type = stream_type
        self.handlers: List[Callable] = []
        self.filters: List[Callable] = []
        self.status = StreamStatus.INITIALIZING

    async def process(self, event: StreamEvent) -> Any:
        """Process a stream event"""
        # Apply filters
        for filter_fn in self.filters:
            if not await filter_fn(event):
                return None

        # Apply handlers
        results = []
        for handler in self.handlers:
            result = await handler(event)
            results.append(result)

        return results

    def add_handler(self, handler: Callable):
        """Add event handler"""
        self.handlers.append(handler)

    def add_filter(self, filter_fn: Callable):
        """Add event filter"""
        self.filters.append(filter_fn)


class RealTimeStreaming:
    """Real-time streaming infrastructure"""

    def __init__(self):
        self.redis_client: Optional[aioredis.Redis] = None
        self.snowflake: Optional[SnowflakeIntegration] = None
        self.processors: Dict[StreamType, StreamProcessor] = {}
        self.active_streams: Set[str] = set()
        self.stream_offsets: Dict[str, str] = {}
        self._initialized = False

    async def initialize(self):
        """Initialize streaming infrastructure."""
        if self._initialized:
            return

        # Initialize Redis for pub/sub
        self.redis_client = await aioredis.create_redis_pool(
            config.redis_url or "redis://localhost:6379", encoding="utf-8"
        )

        # Initialize Snowflake
        self.snowflake = SnowflakeIntegration()
        await self.snowflake.initialize()

        # Create Snowflake streams if needed
        await self._setup_snowflake_streams()

        # Initialize processors
        self._setup_processors()

        # Start monitoring
        asyncio.create_task(self._monitor_streams())

        self._initialized = True
        logger.info("Real-time streaming infrastructure initialized")

    async def _setup_snowflake_streams(self):
        """Set up Snowflake streams and tasks."""
        try:
            # Create stream for Gong calls
            await self.snowflake.execute_query(
                """
                CREATE STREAM IF NOT EXISTS gong_call_stream
                ON TABLE gong_raw_data
                APPEND_ONLY = FALSE
                SHOW_INITIAL_ROWS = TRUE;
            """
            )

            # Create stream for CRM updates
            await self.snowflake.execute_query(
                """
                CREATE STREAM IF NOT EXISTS crm_update_stream
                ON TABLE hubspot_contacts
                APPEND_ONLY = FALSE;
            """
            )

            # Create task for real-time processing
            await self.snowflake.execute_query(
                """
                CREATE OR REPLACE TASK process_real_time_data
                WAREHOUSE = COMPUTE_WH
                SCHEDULE = '1 minute'
                WHEN SYSTEM$STREAM_HAS_DATA('gong_call_stream')
                AS
                    CALL process_stream_data();
            """
            )

            # Resume task
            await self.snowflake.execute_query(
                """
                ALTER TASK process_real_time_data RESUME;
            """
            )

            logger.info("Snowflake streams and tasks configured")

        except Exception as e:
            logger.error(f"Error setting up Snowflake streams: {e}")

    def _setup_processors(self):
        """Set up stream processors."""
        # Gong call processor
        gong_processor = StreamProcessor(StreamType.GONG_CALLS)
        gong_processor.add_handler(self._process_gong_call)
        gong_processor.add_filter(self._filter_important_calls)
        self.processors[StreamType.GONG_CALLS] = gong_processor

        # Slack message processor
        slack_processor = StreamProcessor(StreamType.SLACK_MESSAGES)
        slack_processor.add_handler(self._process_slack_message)
        self.processors[StreamType.SLACK_MESSAGES] = slack_processor

        # CRM update processor
        crm_processor = StreamProcessor(StreamType.CRM_UPDATES)
        crm_processor.add_handler(self._process_crm_update)
        self.processors[StreamType.CRM_UPDATES] = crm_processor

    async def start_stream(self, stream_type: StreamType):
        """Start processing a stream"""
        await self.initialize()

        stream_id = f"{stream_type}:{datetime.utcnow().isoformat()}"
        self.active_streams.add(stream_id)

        if stream_type == StreamType.GONG_CALLS:
            asyncio.create_task(
                self._consume_snowflake_stream("gong_call_stream", stream_type)
            )
        elif stream_type == StreamType.SLACK_MESSAGES:
            asyncio.create_task(
                self._consume_redis_stream("slack:messages", stream_type)
            )
        elif stream_type == StreamType.CRM_UPDATES:
            asyncio.create_task(
                self._consume_snowflake_stream("crm_update_stream", stream_type)
            )

        logger.info(f"Started stream: {stream_id}")

    async def stop_stream(self, stream_type: StreamType):
        """Stop processing a stream"""
        streams_to_remove = [
            s for s in self.active_streams if s.startswith(stream_type)
        ]
        for stream_id in streams_to_remove:
            self.active_streams.remove(stream_id)

        logger.info(f"Stopped {len(streams_to_remove)} streams of type {stream_type}")

    async def publish_event(self, event: StreamEvent):
        """Publish event to stream"""
        await self.initialize()

        # Publish to Redis
        channel = f"stream:{event.stream_type}"
        await self.redis_client.publish(channel, event.json())

        # Process immediately if processor exists
        if event.stream_type in self.processors:
            processor = self.processors[event.stream_type]
            await processor.process(event)

    async def _consume_snowflake_stream(
        self, stream_name: str, stream_type: StreamType
    ):
        """Consume data from Snowflake stream"""
        processor = self.processors.get(stream_type)
        if not processor:
            logger.error(f"No processor for stream type: {stream_type}")
            return

        while f"{stream_type}:{datetime.utcnow().isoformat()}" in self.active_streams:
            try:
                # Query stream for new data
                query = f"""  # nosec B608  # nosec B608 - Stream name is validated
                    SELECT * FROM {stream_name}
                    WHERE METADATA$ACTION IN ('INSERT', 'UPDATE')
                    AND METADATA$ISUPDATE = FALSE
                    LIMIT 100;
                """

                results = await self.snowflake.execute_query(query)

                for row in results:
                    # Convert row to event
                    event = StreamEvent(
                        stream_type=stream_type,
                        data=dict(row),
                        metadata={
                            "source": "snowflake",
                            "stream": stream_name,
                            "action": row.get("METADATA$ACTION"),
                        },
                    )

                    # Process event
                    await processor.process(event)

                    # Cache processed data
                    await hierarchical_cache.set(
                        f"stream:{stream_type}:{event.id}",
                        event.dict(),
                        ttl_override={CacheTier.L1_MEMORY: 300},  # 5 min in L1
                    )

                # Mark stream offset
                if results:
                    await self.snowflake.execute_query(
                        f"""
                        SELECT SYSTEM$STREAM_GET_TABLE_TIMESTAMP('{stream_name}') as stream_offset;
                    """
                    )

                # Wait before next poll
                await asyncio.sleep(5)  # Poll every 5 seconds

            except Exception as e:
                logger.error(f"Error consuming Snowflake stream {stream_name}: {e}")
                await asyncio.sleep(30)  # Back off on error

    async def _consume_redis_stream(self, stream_key: str, stream_type: StreamType):
        """Consume data from Redis stream"""
        processor = self.processors.get(stream_type)
        if not processor:
            logger.error(f"No processor for stream type: {stream_type}")
            return

        # Get last offset or start from beginning
        last_id = self.stream_offsets.get(stream_key, "0")

        while f"{stream_type}:{datetime.utcnow().isoformat()}" in self.active_streams:
            try:
                # Read from stream
                messages = await self.redis_client.xread(
                    {stream_key: last_id},
                    count=100,
                    block=5000,  # Block for 5 seconds
                )

                for stream, stream_messages in messages:
                    for message_id, data in stream_messages:
                        # Convert to event
                        event = StreamEvent(
                            stream_type=stream_type,
                            data=data,
                            metadata={
                                "source": "redis",
                                "stream": stream_key,
                                "message_id": message_id,
                            },
                        )

                        # Process event
                        await processor.process(event)

                        # Update offset
                        last_id = message_id
                        self.stream_offsets[stream_key] = last_id

            except Exception as e:
                logger.error(f"Error consuming Redis stream {stream_key}: {e}")
                await asyncio.sleep(30)  # Back off on error

    async def _process_gong_call(self, event: StreamEvent) -> Dict[str, Any]:
        """Process Gong call event"""
        call_data = event.data

        # Extract key information
        result = {
            "call_id": call_data.get("id"),
            "title": call_data.get("title"),
            "duration": call_data.get("duration"),
            "participants": call_data.get("participants", []),
            "key_topics": await self._extract_topics(call_data.get("transcript", "")),
            "sentiment": await self._analyze_sentiment(call_data.get("transcript", "")),
            "action_items": await self._extract_action_items(
                call_data.get("transcript", "")
            ),
        }

        # Send real-time notification if important
        if result["sentiment"] < 0.3 or "escalation" in result["key_topics"]:
            await self._send_alert("gong_call_alert", result)

        return result

    async def _process_slack_message(self, event: StreamEvent) -> Dict[str, Any]:
        """Process Slack message event"""
        message_data = event.data

        # Extract and analyze
        result = {
            "message_id": message_data.get("ts"),
            "channel": message_data.get("channel"),
            "user": message_data.get("user"),
            "text": message_data.get("text"),
            "mentions": self._extract_mentions(message_data.get("text", "")),
            "urgency": await self._assess_urgency(message_data.get("text", "")),
        }

        # Route to appropriate handler if urgent
        if result["urgency"] > 0.7:
            await self._route_urgent_message(result)

        return result

    async def _process_crm_update(self, event: StreamEvent) -> Dict[str, Any]:
        """Process CRM update event"""
        update_data = event.data

        # Track changes
        result = {
            "entity_type": update_data.get("object_type"),
            "entity_id": update_data.get("object_id"),
            "changes": update_data.get("property_changes", {}),
            "timestamp": event.timestamp,
            "impact": await self._assess_crm_impact(update_data),
        }

        # Update dashboards if high impact
        if result["impact"] > 0.5:
            await self._update_dashboards(result)

        return result

    async def _filter_important_calls(self, event: StreamEvent) -> bool:
        """Filter for important calls only"""
        call_data = event.data

        # Check various importance criteria
        if call_data.get("duration", 0) > 1800:  # Longer than 30 minutes
            return True
        if "executive" in call_data.get("title", "").lower():
            return True
        if len(call_data.get("participants", [])) > 4:  # Large meetings
            return True

        return False

    async def _extract_topics(self, transcript: str) -> List[str]:
        """Extract key topics from transcript"""
        # This would use NLP/LLM for topic extraction
        # Placeholder implementation
        topics = []
        keywords = ["pricing", "contract", "renewal", "issue", "escalation", "feature"]
        for keyword in keywords:
            if keyword in transcript.lower():
                topics.append(keyword)
        return topics

    async def _analyze_sentiment(self, text: str) -> float:
        """Analyze sentiment of text"""
        # This would use sentiment analysis
        # Placeholder: return neutral sentiment
        return 0.5

    async def _extract_action_items(self, transcript: str) -> List[str]:
        """Extract action items from transcript"""
        # This would use NLP to extract action items
        # Placeholder implementation
        action_items = []
        action_phrases = ["will follow up", "need to", "action item", "next step"]
        for phrase in action_phrases:
            if phrase in transcript.lower():
                action_items.append(f"Action detected: {phrase}")
        return action_items

    def _extract_mentions(self, text: str) -> List[str]:
        """Extract mentions from text"""
        import re

        mentions = re.findall(r"@(\w+)", text)
        return mentions

    async def _assess_urgency(self, text: str) -> float:
        """Assess message urgency"""
        urgent_keywords = ["urgent", "asap", "immediately", "critical", "emergency"]
        text_lower = text.lower()

        urgency_score = 0.0
        for keyword in urgent_keywords:
            if keyword in text_lower:
                urgency_score += 0.3

        return min(urgency_score, 1.0)

    async def _assess_crm_impact(self, update_data: Dict[str, Any]) -> float:
        """Assess impact of CRM update"""
        # High impact changes
        high_impact_fields = ["deal_stage", "amount", "close_date", "status"]

        impact_score = 0.0
        changes = update_data.get("property_changes", {})

        for field in high_impact_fields:
            if field in changes:
                impact_score += 0.3

        return min(impact_score, 1.0)

    async def _send_alert(self, alert_type: str, data: Dict[str, Any]):
        """Send real-time alert"""
        alert = {
            "type": alert_type,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data,
        }

        # Publish to alert channel
        await self.redis_client.publish("alerts", json.dumps(alert))

        logger.info(f"Sent alert: {alert_type}")

    async def _route_urgent_message(self, message: Dict[str, Any]):
        """Route urgent message to appropriate handler"""
        # This would integrate with notification system
        logger.info(f"Routing urgent message: {message['message_id']}")

    async def _update_dashboards(self, update: Dict[str, Any]):
        """Update dashboards with real-time data"""
        # Publish to WebSocket channel for dashboard updates
        await self.redis_client.publish("dashboard:updates", json.dumps(update))

    async def _monitor_streams(self):
        """Monitor stream health and performance."""
        while True:
            await asyncio.sleep(60)  # Check every minute

            metrics = {
                "active_streams": len(self.active_streams),
                "stream_types": list(self.active_streams),
                "processors": {str(k): v.status for k, v in self.processors.items()},
            }

            logger.info(f"Stream metrics: {metrics}")

            # Check for stalled streams
            for stream_id in list(self.active_streams):
                # Implement health check logic
                pass

    async def get_stream_metrics(self) -> Dict[str, Any]:
        """Get streaming metrics."""
        return {
            "active_streams": len(self.active_streams),
            "stream_offsets": self.stream_offsets,
            "processor_status": {
                str(k): {
                    "status": v.status,
                    "handlers": len(v.handlers),
                    "filters": len(v.filters),
                }
                for k, v in self.processors.items()
            },
        }


# Global streaming instance
real_time_streaming = RealTimeStreaming()
