"""
Gong Webhook Processor - Complete processing pipeline for Gong webhooks.

Integrates API enhancement, data storage, and agent notifications.
"""

from __future__ import annotations

import time
from datetime import datetime
from typing import Any

import structlog

from backend.integrations.gong_api_client import GongAPIClient
from backend.integrations.gong_redis_client import (
    NotificationPriority,
    ProcessedCallData,
    ProcessedEmailData,
    ProcessedMeetingData,
    RedisNotificationClient,
)
from backend.integrations.gong_snowflake_client import SnowflakeWebhookClient
from backend.integrations.gong_webhook_server import (
    active_background_tasks,
    data_quality_score,
)

logger = structlog.get_logger()


class WebhookProcessor:
    """Processes Gong webhooks through the complete pipeline."""

    def __init__(
        self,
        gong_api_key: str,
        snowflake_config: dict[str, str],
        redis_url: str = "redis://localhost:6379",
    ):
        self.gong_api = GongAPIClient(api_key=gong_api_key)
        self.snowflake = SnowflakeWebhookClient(**snowflake_config)
        self.redis = RedisNotificationClient(redis_url=redis_url)
        self.logger = logger.bind(component="webhook_processor")

    async def __aenter__(self):
        """Async context manager entry."""
        await self.gong_api.__aenter__()
        await self.redis.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.gong_api.__aexit__(exc_type, exc_val, exc_tb)
        await self.redis.disconnect()
        self.snowflake.close()

    async def process_call_webhook(
        self, webhook_id: str, webhook_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Process a call webhook through the complete pipeline."""
        start_time = time.time()
        call_id = webhook_data.get("call_id", "")

        processing_result = {
            "webhook_id": webhook_id,
            "call_id": call_id,
            "status": "processing",
            "stages": {},
        }

        try:
            # Stage 1: Store raw webhook data
            stage_start = time.time()
            try:
                await self.snowflake.store_raw_webhook(
                    {
                        "webhook_id": webhook_id,
                        "event_type": "call",
                        "object_id": call_id,
                        "object_type": "call",
                        **webhook_data,
                    }
                )

                processing_result["stages"]["raw_storage"] = {
                    "status": "success",
                    "duration_ms": int((time.time() - stage_start) * 1000),
                }

                await self.snowflake.log_processing_stage(
                    webhook_id,
                    "call",
                    "raw_storage",
                    "success",
                    duration_ms=int((time.time() - stage_start) * 1000),
                )
            except Exception as e:
                self.logger.error(
                    "Failed to store raw webhook", webhook_id=webhook_id, error=str(e)
                )
                processing_result["stages"]["raw_storage"] = {
                    "status": "failed",
                    "error": str(e),
                }
                raise

            # Stage 2: Enhance data with Gong API
            stage_start = time.time()
            enhanced_data = None

            try:
                enhanced_data = await self.gong_api.enhance_call_data(call_id)
                enhanced_data["webhook_id"] = webhook_id

                processing_result["stages"]["api_enhancement"] = {
                    "status": "success",
                    "duration_ms": int((time.time() - stage_start) * 1000),
                    "data_quality": self._calculate_data_quality(enhanced_data),
                }

                await self.snowflake.log_processing_stage(
                    webhook_id,
                    "call",
                    "api_enhancement",
                    "success",
                    duration_ms=int((time.time() - stage_start) * 1000),
                    metadata={
                        "quality_score": self._calculate_data_quality(enhanced_data)
                    },
                )
            except Exception as e:
                self.logger.error(
                    "Failed to enhance call data",
                    webhook_id=webhook_id,
                    call_id=call_id,
                    error=str(e),
                )
                processing_result["stages"]["api_enhancement"] = {
                    "status": "failed",
                    "error": str(e),
                }
                # Continue with partial data if enhancement fails

            # Stage 3: Store enhanced data
            if enhanced_data:
                stage_start = time.time()
                try:
                    await self.snowflake.store_enhanced_call_data(enhanced_data)

                    processing_result["stages"]["enhanced_storage"] = {
                        "status": "success",
                        "duration_ms": int((time.time() - stage_start) * 1000),
                    }

                    await self.snowflake.log_processing_stage(
                        webhook_id,
                        "call",
                        "enhanced_storage",
                        "success",
                        duration_ms=int((time.time() - stage_start) * 1000),
                    )
                except Exception as e:
                    self.logger.error(
                        "Failed to store enhanced data",
                        webhook_id=webhook_id,
                        error=str(e),
                    )
                    processing_result["stages"]["enhanced_storage"] = {
                        "status": "failed",
                        "error": str(e),
                    }

            # Stage 4: Notify Sophia agents
            stage_start = time.time()
            try:
                # Prepare notification data
                call_data = enhanced_data.get("call_data", {}) if enhanced_data else {}
                analytics = enhanced_data.get("analytics", {}) if enhanced_data else {}

                processed_call = ProcessedCallData(
                    call_id=call_id,
                    webhook_id=webhook_id,
                    title=call_data.get("title", "Unknown Call"),
                    duration_seconds=call_data.get("duration", 0),
                    participants=call_data.get("participants", []),
                    summary=call_data.get("summary"),
                    insights=self._extract_insights(enhanced_data),
                    action_items=call_data.get("action_items", []),
                    sentiment_score=analytics.get("sentiment_score"),
                    talk_ratio=analytics.get("talk_ratio"),
                    next_steps=self._determine_next_steps(enhanced_data),
                )

                # Determine priority based on insights
                priority = self._determine_priority(processed_call)

                # Send notification
                await self.redis.notify_call_processed(processed_call, priority)

                # Check for special insights
                insights = self._extract_insights(enhanced_data)
                for insight in insights:
                    if insight.get("type") in [
                        "competitor_mention",
                        "churn_risk",
                        "upsell_opportunity",
                    ]:
                        await self.redis.notify_insight_detected(
                            webhook_id,
                            insight["type"],
                            insight,
                            NotificationPriority.HIGH,
                        )

                processing_result["stages"]["notification"] = {
                    "status": "success",
                    "duration_ms": int((time.time() - stage_start) * 1000),
                    "priority": priority,
                }

                await self.snowflake.log_processing_stage(
                    webhook_id,
                    "call",
                    "notification",
                    "success",
                    duration_ms=int((time.time() - stage_start) * 1000),
                    metadata={"priority": priority},
                )
            except Exception as e:
                self.logger.error(
                    "Failed to send notification", webhook_id=webhook_id, error=str(e)
                )
                processing_result["stages"]["notification"] = {
                    "status": "failed",
                    "error": str(e),
                }

            # Update final status
            processing_result["status"] = "completed"
            processing_result["total_duration_ms"] = int(
                (time.time() - start_time) * 1000
            )

            await self.snowflake.update_webhook_status(webhook_id, "completed")

            self.logger.info(
                "Webhook processing completed",
                webhook_id=webhook_id,
                duration_ms=processing_result["total_duration_ms"],
            )

        except Exception as e:
            processing_result["status"] = "failed"
            processing_result["error"] = str(e)
            processing_result["total_duration_ms"] = int(
                (time.time() - start_time) * 1000
            )

            await self.snowflake.update_webhook_status(webhook_id, "failed", str(e))

            await self.redis.notify_processing_error(
                webhook_id, "webhook_processing_error", str(e), processing_result
            )

            self.logger.error(
                "Webhook processing failed", webhook_id=webhook_id, error=str(e)
            )
            raise

        finally:
            active_background_tasks.dec()

        return processing_result

    async def process_email_webhook(
        self, webhook_id: str, webhook_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Process an email webhook."""
        # Similar implementation to call webhook
        # Simplified for brevity
        email_id = webhook_data.get("email_id", "")

        try:
            # Store raw data
            await self.snowflake.store_raw_webhook(
                {
                    "webhook_id": webhook_id,
                    "event_type": "email",
                    "object_id": email_id,
                    "object_type": "email",
                    **webhook_data,
                }
            )

            # Enhance with API
            email_data = await self.gong_api.get_email_content(email_id)

            # Process and notify
            processed_email = ProcessedEmailData(
                email_id=email_id,
                webhook_id=webhook_id,
                subject=email_data.get("subject", ""),
                sender=email_data.get("sender", ""),
                recipients=email_data.get("recipients", []),
                sentiment=self._analyze_sentiment(email_data.get("content", "")),
                key_topics=self._extract_topics(email_data.get("content", "")),
                requires_response=self._requires_response(email_data),
            )

            await self.redis.notify_email_processed(
                processed_email,
                (
                    NotificationPriority.HIGH
                    if processed_email.requires_response
                    else NotificationPriority.LOW
                ),
            )

            await self.snowflake.update_webhook_status(webhook_id, "completed")

            return {"status": "completed", "webhook_id": webhook_id}

        except Exception as e:
            await self.snowflake.update_webhook_status(webhook_id, "failed", str(e))
            raise

    async def process_meeting_webhook(
        self, webhook_id: str, webhook_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Process a meeting webhook."""
        meeting_id = webhook_data.get("meeting_id", "")

        try:
            # Store raw data
            await self.snowflake.store_raw_webhook(
                {
                    "webhook_id": webhook_id,
                    "event_type": "meeting",
                    "object_id": meeting_id,
                    "object_type": "meeting",
                    **webhook_data,
                }
            )

            # Enhance with API
            meeting_data = await self.gong_api.get_meeting_details(meeting_id)

            # Process and notify
            processed_meeting = ProcessedMeetingData(
                meeting_id=meeting_id,
                webhook_id=webhook_id,
                title=meeting_data.get("title", ""),
                start_time=datetime.fromisoformat(meeting_data.get("start_time", "")),
                end_time=datetime.fromisoformat(meeting_data.get("end_time", "")),
                attendees=meeting_data.get("attendees", []),
                agenda_items=self._extract_agenda_items(meeting_data),
                decisions=self._extract_decisions(meeting_data),
            )

            await self.redis.notify_meeting_processed(processed_meeting)

            await self.snowflake.update_webhook_status(webhook_id, "completed")

            return {"status": "completed", "webhook_id": webhook_id}

        except Exception as e:
            await self.snowflake.update_webhook_status(webhook_id, "failed", str(e))
            raise

    def _calculate_data_quality(self, enhanced_data: dict[str, Any]) -> float:
        """Calculate data quality score."""
        if not enhanced_data:
            return 0.0

        score = 0.0
        weights = {
            "call_data": 0.3,
            "transcript": 0.3,
            "analytics": 0.2,
            "participants": 0.2,
        }

        for key, weight in weights.items():
            if enhanced_data.get(key):
                score += weight

        # Update global metric
        data_quality_score.set(score)

        return score

    def _extract_insights(
        self, enhanced_data: dict[str, Any] | None
    ) -> list[dict[str, Any]]:
        """Extract business insights from enhanced data."""
        if not enhanced_data:
            return []

        insights = []

        # Check for competitor mentions
        transcript = enhanced_data.get("transcript", {})
        if transcript:
            competitors = [
                "Competitor A",
                "Competitor B",
            ]  # Configure based on business
            for sentence in transcript.get("sentences", []):
                text = sentence.get("text", "").lower()
                for competitor in competitors:
                    if competitor.lower() in text:
                        insights.append(
                            {
                                "type": "competitor_mention",
                                "competitor": competitor,
                                "context": sentence.get("text", ""),
                                "timestamp": sentence.get("start_time"),
                            }
                        )

        # Check sentiment for churn risk
        analytics = enhanced_data.get("analytics", {})
        if analytics.get("sentiment_score", 1.0) < 0.3:
            insights.append(
                {
                    "type": "churn_risk",
                    "sentiment_score": analytics.get("sentiment_score"),
                    "indicators": ["low_sentiment", "negative_tone"],
                }
            )

        # Check for upsell opportunities
        topics = enhanced_data.get("call_data", {}).get("topics", [])
        upsell_keywords = ["expand", "growth", "scale", "additional features"]
        for topic in topics:
            if any(
                keyword in topic.get("name", "").lower() for keyword in upsell_keywords
            ):
                insights.append(
                    {
                        "type": "upsell_opportunity",
                        "topic": topic.get("name"),
                        "confidence": topic.get("confidence", 0),
                    }
                )

        return insights

    def _determine_priority(
        self, processed_call: ProcessedCallData
    ) -> NotificationPriority:
        """Determine notification priority based on call data."""
        # High priority conditions
        if any(
            insight["type"] in ["churn_risk", "competitor_mention"]
            for insight in processed_call.insights
        ):
            return NotificationPriority.HIGH

        if processed_call.action_items and len(processed_call.action_items) > 3:
            return NotificationPriority.HIGH

        # Low priority conditions
        if processed_call.duration_seconds < 300:  # Less than 5 minutes
            return NotificationPriority.LOW

        # Default to medium
        return NotificationPriority.MEDIUM

    def _determine_next_steps(self, enhanced_data: dict[str, Any] | None) -> list[str]:
        """Determine recommended next steps."""
        if not enhanced_data:
            return []

        next_steps = []

        # Based on action items
        action_items = enhanced_data.get("call_data", {}).get("action_items", [])
        for item in action_items[:3]:  # Top 3
            next_steps.append(f"Complete: {item.get('description', '')}")

        # Based on insights
        insights = self._extract_insights(enhanced_data)
        for insight in insights:
            if insight["type"] == "churn_risk":
                next_steps.append("Schedule follow-up call to address concerns")
            elif insight["type"] == "upsell_opportunity":
                next_steps.append("Prepare proposal for expanded services")

        return next_steps

    def _analyze_sentiment(self, content: str) -> str:
        """Analyze email sentiment."""
        # Simplified sentiment analysis
        # In production, use proper NLP service
        negative_words = ["disappointed", "frustrated", "unhappy", "problem"]
        positive_words = ["great", "excellent", "happy", "satisfied"]

        content_lower = content.lower()
        negative_count = sum(1 for word in negative_words if word in content_lower)
        positive_count = sum(1 for word in positive_words if word in content_lower)

        if negative_count > positive_count:
            return "negative"
        elif positive_count > negative_count:
            return "positive"
        else:
            return "neutral"

    def _extract_topics(self, content: str) -> list[str]:
        """Extract key topics from content."""
        # Simplified topic extraction
        # In production, use proper NLP service
        topics = []

        topic_keywords = {
            "pricing": ["price", "cost", "budget", "payment"],
            "support": ["help", "support", "issue", "problem"],
            "features": ["feature", "functionality", "capability"],
            "contract": ["contract", "agreement", "terms", "renewal"],
        }

        content_lower = content.lower()
        for topic, keywords in topic_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                topics.append(topic)

        return topics

    def _requires_response(self, email_data: dict[str, Any]) -> bool:
        """Determine if email requires response."""
        # Check if it's a question or request
        content = email_data.get("content", "").lower()
        question_indicators = ["?", "please", "could you", "can you", "request"]

        return any(indicator in content for indicator in question_indicators)

    def _extract_agenda_items(self, meeting_data: dict[str, Any]) -> list[str]:
        """Extract agenda items from meeting data."""
        # Simplified extraction
        return meeting_data.get("agenda", [])

    def _extract_decisions(self, meeting_data: dict[str, Any]) -> list[str]:
        """Extract decisions from meeting data."""
        # Simplified extraction
        return meeting_data.get("decisions", [])
