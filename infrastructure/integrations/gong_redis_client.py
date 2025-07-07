from datetime import UTC, datetime

"""
Redis Notification Client for Gong Webhook Processing.

Handles real-time notifications to Sophia agents via Redis pub/sub.
"""

from __future__ import annotations

import json
from enum import Enum
from typing import Any

import redis.asyncio as redis
import structlog
from pydantic import BaseModel, Field

logger = structlog.get_logger()


class NotificationPriority(str, Enum):
    """Notification priority levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class NotificationType(str, Enum):
    """Types of notifications."""

    CALL_PROCESSED = "call_processed"
    EMAIL_PROCESSED = "email_processed"
    MEETING_PROCESSED = "meeting_processed"
    PROCESSING_ERROR = "processing_error"
    INSIGHT_DETECTED = "insight_detected"
    ACTION_REQUIRED = "action_required"


class ProcessedCallData(BaseModel):
    """Processed call data for notifications."""

    call_id: str
    webhook_id: str
    title: str
    duration_seconds: int
    participants: list[dict[str, Any]]
    summary: dict[str, Any] | None = None
    insights: list[dict[str, Any]] = Field(default_factory=list)
    action_items: list[dict[str, Any]] = Field(default_factory=list)
    sentiment_score: float | None = None
    talk_ratio: float | None = None
    next_steps: list[str] = Field(default_factory=list)


class ProcessedEmailData(BaseModel):
    """Processed email data for notifications."""

    email_id: str
    webhook_id: str
    subject: str
    sender: str
    recipients: list[str]
    sentiment: str | None = None
    key_topics: list[str] = Field(default_factory=list)
    requires_response: bool = False


class ProcessedMeetingData(BaseModel):
    """Processed meeting data for notifications."""

    meeting_id: str
    webhook_id: str
    title: str
    start_time: datetime
    end_time: datetime
    attendees: list[dict[str, Any]]
    agenda_items: list[str] = Field(default_factory=list)
    decisions: list[str] = Field(default_factory=list)


class RedisNotificationClient:
    """Client for sending notifications via Redis pub/sub."""

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis: redis.Redis | None = None
        self.logger = logger.bind(component="redis_notification_client")

        # Channel configuration
        self.channels = {
            "calls": "sophia:gong:calls",
            "emails": "sophia:gong:emails",
            "meetings": "sophia:gong:meetings",
            "insights": "sophia:gong:insights",
            "errors": "sophia:gong:errors",
            "actions": "sophia:gong:actions",
        }

        # Priority channels for urgent notifications
        self.priority_channels = {
            NotificationPriority.HIGH: "sophia:gong:priority:high",
            NotificationPriority.URGENT: "sophia:gong:priority:urgent",
        }

    async def connect(self):
        """Connect to Redis."""
        if not self.redis:
            self.redis = await redis.from_url(
                self.redis_url, encoding="utf-8", decode_responses=True
            )
            self.logger.info("Connected to Redis", url=self.redis_url)

    async def disconnect(self):
        """Disconnect from Redis."""
        if self.redis:
            await self.redis.close()
            self.redis = None
            self.logger.info("Disconnected from Redis")

    async def ensure_connected(self):
        """Ensure Redis connection is active."""
        if not self.redis:
            await self.connect()

        # Test connection
        try:
            await self.redis.ping()
        except Exception:
            self.logger.warning("Redis connection lost, reconnecting...")
            await self.connect()

    async def notify_call_processed(
        self,
        call_data: ProcessedCallData,
        priority: NotificationPriority = NotificationPriority.MEDIUM,
    ):
        """Send notification for processed call."""
        await self.ensure_connected()

        message = {
            "event_type": NotificationType.CALL_PROCESSED,
            "timestamp": datetime.now(UTC).isoformat(),
            "priority": priority,
            "data": call_data.dict(),
        }

        # Publish to main channel
        await self.redis.publish(self.channels["calls"], json.dumps(message))

        # Publish to priority channel if high/urgent
        if priority in [NotificationPriority.HIGH, NotificationPriority.URGENT]:
            await self.redis.publish(
                self.priority_channels[priority], json.dumps(message)
            )

        # Store in Redis for persistence (with TTL)
        await self._store_notification(
            f"call:{call_data.call_id}",
            message,
            ttl=86400,  # 24 hours
        )

        self.logger.info(
            "Call notification sent", call_id=call_data.call_id, priority=priority
        )

    async def notify_email_processed(
        self,
        email_data: ProcessedEmailData,
        priority: NotificationPriority = NotificationPriority.LOW,
    ):
        """Send notification for processed email."""
        await self.ensure_connected()

        message = {
            "event_type": NotificationType.EMAIL_PROCESSED,
            "timestamp": datetime.now(UTC).isoformat(),
            "priority": priority,
            "data": email_data.dict(),
        }

        await self.redis.publish(self.channels["emails"], json.dumps(message))

        # Store if requires response
        if email_data.requires_response:
            await self._store_notification(
                f"email:{email_data.email_id}",
                message,
                ttl=172800,  # 48 hours
            )

        self.logger.info("Email notification sent", email_id=email_data.email_id)

    async def notify_meeting_processed(
        self,
        meeting_data: ProcessedMeetingData,
        priority: NotificationPriority = NotificationPriority.MEDIUM,
    ):
        """Send notification for processed meeting."""
        await self.ensure_connected()

        message = {
            "event_type": NotificationType.MEETING_PROCESSED,
            "timestamp": datetime.now(UTC).isoformat(),
            "priority": priority,
            "data": meeting_data.dict(),
        }

        await self.redis.publish(self.channels["meetings"], json.dumps(message))

        # Store meeting data
        await self._store_notification(
            f"meeting:{meeting_data.meeting_id}",
            message,
            ttl=604800,  # 7 days
        )

        self.logger.info(
            "Meeting notification sent", meeting_id=meeting_data.meeting_id
        )

    async def notify_insight_detected(
        self,
        webhook_id: str,
        insight_type: str,
        insight_data: dict[str, Any],
        priority: NotificationPriority = NotificationPriority.HIGH,
    ):
        """Send notification for detected insights."""
        await self.ensure_connected()

        message = {
            "event_type": NotificationType.INSIGHT_DETECTED,
            "timestamp": datetime.now(UTC).isoformat(),
            "priority": priority,
            "webhook_id": webhook_id,
            "insight_type": insight_type,
            "data": insight_data,
        }

        # Insights are high priority by default
        await self.redis.publish(self.channels["insights"], json.dumps(message))

        if priority in [NotificationPriority.HIGH, NotificationPriority.URGENT]:
            await self.redis.publish(
                self.priority_channels[priority], json.dumps(message)
            )

        self.logger.info(
            "Insight notification sent",
            webhook_id=webhook_id,
            insight_type=insight_type,
        )

    async def notify_action_required(
        self,
        action_type: str,
        action_data: dict[str, Any],
        assigned_to: str | None = None,
    ):
        """Send notification for required actions."""
        await self.ensure_connected()

        message = {
            "event_type": NotificationType.ACTION_REQUIRED,
            "timestamp": datetime.now(UTC).isoformat(),
            "priority": NotificationPriority.HIGH,
            "action_type": action_type,
            "assigned_to": assigned_to,
            "data": action_data,
        }

        # Actions are always high priority
        await self.redis.publish(self.channels["actions"], json.dumps(message))
        await self.redis.publish(
            self.priority_channels[NotificationPriority.HIGH], json.dumps(message)
        )

        # Store action for tracking
        action_id = f"action:{action_type}:{datetime.now(UTC).timestamp()}"
        await self._store_notification(action_id, message, ttl=259200)  # 3 days

        self.logger.info(
            "Action notification sent", action_type=action_type, assigned_to=assigned_to
        )

    async def notify_processing_error(
        self,
        webhook_id: str,
        error_type: str,
        error_message: str,
        error_details: dict[str, Any] | None = None,
    ):
        """Send notification for processing errors."""
        await self.ensure_connected()

        message = {
            "event_type": NotificationType.PROCESSING_ERROR,
            "timestamp": datetime.now(UTC).isoformat(),
            "priority": NotificationPriority.HIGH,
            "webhook_id": webhook_id,
            "error_type": error_type,
            "error_message": error_message,
            "error_details": error_details or {},
        }

        # Errors go to both error channel and high priority
        await self.redis.publish(self.channels["errors"], json.dumps(message))
        await self.redis.publish(
            self.priority_channels[NotificationPriority.HIGH], json.dumps(message)
        )

        # Store error for analysis
        await self._store_notification(
            f"error:{webhook_id}",
            message,
            ttl=604800,  # 7 days
        )

        self.logger.error(
            "Error notification sent", webhook_id=webhook_id, error_type=error_type
        )

    async def _store_notification(self, key: str, message: dict[str, Any], ttl: int):
        """Store notification in Redis with TTL."""
        try:
            await self.redis.setex(f"notification:{key}", ttl, json.dumps(message))
        except Exception as e:
            self.logger.warning("Failed to store notification", key=key, error=str(e))

    async def get_stored_notifications(
        self, pattern: str = "*", limit: int = 100
    ) -> list[dict[str, Any]]:
        """Retrieve stored notifications matching pattern."""
        await self.ensure_connected()

        notifications = []
        cursor = 0

        while len(notifications) < limit:
            cursor, keys = await self.redis.scan(
                cursor,
                match=f"notification:{pattern}",
                count=min(100, limit - len(notifications)),
            )

            if keys:
                # Get values for keys
                values = await self.redis.mget(keys)
                for value in values:
                    if value:
                        try:
                            notifications.append(json.loads(value))
                        except json.JSONDecodeError:
                            continue

            if cursor == 0:
                break

        return notifications[:limit]

    async def subscribe_to_channel(self, channel: str, callback: callable):
        """Subscribe to a Redis channel with callback."""
        await self.ensure_connected()

        pubsub = self.redis.pubsub()
        await pubsub.subscribe(channel)

        self.logger.info("Subscribed to channel", channel=channel)

        try:
            async for message in pubsub.listen():
                if message["type"] == "message":
                    try:
                        data = json.loads(message["data"])
                        await callback(data)
                    except Exception as e:
                        self.logger.error(
                            "Error in subscription callback",
                            channel=channel,
                            error=str(e),
                        )
        finally:
            await pubsub.unsubscribe(channel)
            await pubsub.close()

    async def get_channel_stats(self) -> dict[str, Any]:
        """Get statistics about notification channels."""
        await self.ensure_connected()

        stats = {}

        for name, channel in self.channels.items():
            # Get number of subscribers (approximate)
            pub_response = await self.redis.pubsub_numsub(channel)
            stats[name] = {
                "channel": channel,
                "subscribers": pub_response.get(channel, 0) if pub_response else 0,
            }

        return stats
