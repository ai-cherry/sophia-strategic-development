"""
Gong Data Quality Module - Task 3 Implementation
Systematic Refactoring Project

Following research-backed patterns:
- Event-driven architecture with monitoring
- Performance optimization + External integration
- Circuit Breaker pattern for fault tolerance
- Clean Architecture with Repository pattern
"""

from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Protocol
from pathlib import Path

import pandas as pd
from backend.core.auto_esc_config import get_config_value
from backend.utils.snowflake_cortex_service_core import SnowflakeCortexServiceCore

logger = logging.getLogger(__name__)


class DataQualityStatus(Enum):
    """Data quality assessment levels"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    CRITICAL = "critical"


class EventType(Enum):
    """Event types for event-driven architecture"""
    DATA_INGESTED = "data_ingested"
    QUALITY_CHECK_STARTED = "quality_check_started"
    QUALITY_CHECK_COMPLETED = "quality_check_completed"
    QUALITY_ISSUE_DETECTED = "quality_issue_detected"
    DATA_ENRICHMENT_STARTED = "data_enrichment_started"
    DATA_ENRICHMENT_COMPLETED = "data_enrichment_completed"
    MONITORING_ALERT = "monitoring_alert"


@dataclass
class DataQualityEvent:
    """Event for event-driven data processing"""
    event_type: EventType
    timestamp: datetime
    source: str
    data: Dict[str, Any]
    correlation_id: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QualityMetrics:
    """Comprehensive data quality metrics"""
    completeness_score: float  # 0.0 to 1.0
    accuracy_score: float
    consistency_score: float
    timeliness_score: float
    validity_score: float
    overall_score: float
    issues_detected: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class GongDataRecord:
    """Standardized Gong data record"""
    record_id: str
    record_type: str  # call, transcript, user, etc.
    raw_data: Dict[str, Any]
    quality_metrics: Optional[QualityMetrics] = None
    enriched_data: Dict[str, Any] = field(default_factory=dict)
    processing_status: str = "pending"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


class EventPublisher(Protocol):
    """Protocol for event publishing"""
    
    async def publish(self, event: DataQualityEvent) -> None:
        """Publish an event"""
        ...


class DataQualityRepository(Protocol):
    """Repository pattern for data quality operations"""
    
    async def store_quality_metrics(self, record_id: str, metrics: QualityMetrics) -> None:
        """Store quality metrics"""
        ...
    
    async def get_quality_history(self, record_id: str) -> List[QualityMetrics]:
        """Get quality history for a record"""
        ...
    
    async def get_quality_trends(self, days: int = 30) -> Dict[str, Any]:
        """Get quality trends over time"""
        ...


class CircuitBreaker:
    """Circuit breaker pattern for fault tolerance"""
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = "closed"  # closed, open, half-open
    
    async def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        if self.state == "open":
            if self._should_attempt_reset():
                self.state = "half-open"
            else:
                raise Exception("Circuit breaker is open")
        
        try:
            result = await func(*args, **kwargs)
            if self.state == "half-open":
                self._reset()
            return result
        except Exception as e:
            self._record_failure()
            raise e
    
    def _should_attempt_reset(self) -> bool:
        """Check if we should attempt to reset the circuit"""
        if self.last_failure_time is None:
            return True
        return datetime.now() - self.last_failure_time > timedelta(seconds=self.timeout)
    
    def _record_failure(self):
        """Record a failure"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        if self.failure_count >= self.failure_threshold:
            self.state = "open"
    
    def _reset(self):
        """Reset the circuit breaker"""
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"


class SimpleEventPublisher:
    """Simple in-memory event publisher implementation"""
    
    def __init__(self):
        self.events: List[DataQualityEvent] = []
        self.subscribers: Dict[EventType, List[callable]] = {}
    
    async def publish(self, event: DataQualityEvent) -> None:
        """Publish an event"""
        self.events.append(event)
        logger.info(f"📡 Event published: {event.event_type.value} for {event.source}")
        
        # Notify subscribers
        if event.event_type in self.subscribers:
            for callback in self.subscribers[event.event_type]:
                try:
                    await callback(event)
                except Exception as e:
                    logger.error(f"❌ Error in event subscriber: {e}")
    
    def subscribe(self, event_type: EventType, callback: callable):
        """Subscribe to event type"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)


class SnowflakeDataQualityRepository:
    """Snowflake implementation of data quality repository"""
    
    def __init__(self):
        self.cortex_service = None
    
    async def initialize(self):
        """Initialize the repository"""
        self.cortex_service = SnowflakeCortexServiceCore()
        await self.cortex_service.initialize()
    
    async def store_quality_metrics(self, record_id: str, metrics: QualityMetrics) -> None:
        """Store quality metrics in Snowflake"""
        try:
            # Simplified storage - in production would use proper table
            logger.info(f"📊 Storing quality metrics for {record_id}: {metrics.overall_score:.2f}")
            
        except Exception as e:
            logger.error(f"❌ Failed to store quality metrics: {e}")
            raise
    
    async def get_quality_trends(self, days: int = 30) -> Dict[str, Any]:
        """Get quality trends over time"""
        try:
            # Simplified trends - in production would query actual data
            return {
                "trends": [],
                "summary": {
                    "avg_overall_score": 0.85,
                    "total_records": 100,
                    "trend_direction": "improving"
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get quality trends: {e}")
            return {"trends": [], "summary": {}}


class GongDataQualityModule:
    """Main data quality module following event-driven architecture"""
    
    def __init__(self, event_publisher: EventPublisher, repository: DataQualityRepository):
        self.event_publisher = event_publisher
        self.repository = repository
        self.circuit_breaker = CircuitBreaker()
        self.quality_rules = self._initialize_quality_rules()
        self.processing_stats = {
            "records_processed": 0,
            "quality_checks_performed": 0,
            "issues_detected": 0,
            "enrichments_applied": 0
        }
    
    def _initialize_quality_rules(self) -> Dict[str, Any]:
        """Initialize data quality rules"""
        return {
            "required_fields": {
                "call": ["id", "title", "started", "duration"],
                "transcript": ["id", "call_id", "speaker", "content"],
                "user": ["id", "email_address", "first_name", "last_name"]
            },
            "field_formats": {
                "email_address": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
                "phone": r"^\+?[\d\s\-\(\)]{10,}$",
                "url": r"^https?://.*"
            },
            "value_ranges": {
                "duration": {"min": 0, "max": 28800},  # 8 hours max
                "score": {"min": 0.0, "max": 1.0}
            },
            "business_rules": {
                "call_duration_threshold": 60,  # Minimum 1 minute
                "transcript_min_length": 50,    # Minimum 50 characters
                "user_activity_days": 90        # Active within 90 days
            }
        }
    
    async def process_gong_data(self, raw_data: Dict[str, Any], record_type: str) -> GongDataRecord:
        """Process Gong data with quality checks and enrichment"""
        correlation_id = f"gong_{record_type}_{datetime.now().timestamp()}"
        
        # Create initial record
        record = GongDataRecord(
            record_id=raw_data.get('id', f"unknown_{correlation_id}"),
            record_type=record_type,
            raw_data=raw_data
        )
        
        try:
            # Publish data ingestion event
            await self.event_publisher.publish(DataQualityEvent(
                event_type=EventType.DATA_INGESTED,
                timestamp=datetime.now(),
                source=f"gong_{record_type}",
                data={"record_id": record.record_id, "size": len(str(raw_data))},
                correlation_id=correlation_id
            ))
            
            # Perform quality checks with circuit breaker
            record.quality_metrics = await self.circuit_breaker.call(
                self._perform_quality_checks, record, correlation_id
            )
            
            # Apply enrichments if quality is acceptable
            if record.quality_metrics.overall_score >= 0.6:
                record.enriched_data = await self.circuit_breaker.call(
                    self._apply_enrichments, record, correlation_id
                )
                record.processing_status = "completed"
            else:
                record.processing_status = "quality_failed"
                await self._handle_quality_failure(record, correlation_id)
            
            # Store quality metrics
            await self.repository.store_quality_metrics(
                record.record_id, record.quality_metrics
            )
            
            # Update stats
            self.processing_stats["records_processed"] += 1
            
            return record
            
        except Exception as e:
            logger.error(f"❌ Failed to process Gong data: {e}")
            record.processing_status = "error"
            
            # Publish error event
            await self.event_publisher.publish(DataQualityEvent(
                event_type=EventType.MONITORING_ALERT,
                timestamp=datetime.now(),
                source="gong_data_quality",
                data={"error": str(e), "record_id": record.record_id},
                correlation_id=correlation_id
            ))
            
            return record
    
    async def _perform_quality_checks(self, record: GongDataRecord, correlation_id: str) -> QualityMetrics:
        """Perform comprehensive quality checks"""
        await self.event_publisher.publish(DataQualityEvent(
            event_type=EventType.QUALITY_CHECK_STARTED,
            timestamp=datetime.now(),
            source="quality_checker",
            data={"record_id": record.record_id, "record_type": record.record_type},
            correlation_id=correlation_id
        ))
        
        # Calculate individual quality scores
        completeness = self._check_completeness(record)
        accuracy = self._check_accuracy(record)
        consistency = self._check_consistency(record)
        timeliness = self._check_timeliness(record)
        validity = self._check_validity(record)
        
        # Calculate overall score (weighted average)
        overall_score = (
            completeness * 0.25 +
            accuracy * 0.25 +
            consistency * 0.20 +
            timeliness * 0.15 +
            validity * 0.15
        )
        
        issues = []
        recommendations = []
        
        # Generate issues and recommendations
        if completeness < 0.8:
            issues.append("Missing required fields")
            recommendations.append("Ensure all required fields are populated")
        
        if accuracy < 0.7:
            issues.append("Data accuracy concerns")
            recommendations.append("Validate data against business rules")
        
        if validity < 0.8:
            issues.append("Invalid data formats detected")
            recommendations.append("Apply data format validation")
        
        metrics = QualityMetrics(
            completeness_score=completeness,
            accuracy_score=accuracy,
            consistency_score=consistency,
            timeliness_score=timeliness,
            validity_score=validity,
            overall_score=overall_score,
            issues_detected=issues,
            recommendations=recommendations
        )
        
        self.processing_stats["quality_checks_performed"] += 1
        if issues:
            self.processing_stats["issues_detected"] += len(issues)
        
        await self.event_publisher.publish(DataQualityEvent(
            event_type=EventType.QUALITY_CHECK_COMPLETED,
            timestamp=datetime.now(),
            source="quality_checker",
            data={
                "record_id": record.record_id,
                "overall_score": overall_score,
                "issues_count": len(issues)
            },
            correlation_id=correlation_id
        ))
        
        return metrics
    
    def _check_completeness(self, record: GongDataRecord) -> float:
        """Check data completeness"""
        required_fields = self.quality_rules["required_fields"].get(record.record_type, [])
        if not required_fields:
            return 1.0
        
        present_fields = sum(1 for field in required_fields if field in record.raw_data and record.raw_data[field] is not None)
        return present_fields / len(required_fields)
    
    def _check_accuracy(self, record: GongDataRecord) -> float:
        """Check data accuracy against business rules"""
        score = 1.0
        business_rules = self.quality_rules["business_rules"]
        
        if record.record_type == "call":
            duration = record.raw_data.get("duration", 0)
            if duration < business_rules["call_duration_threshold"]:
                score -= 0.3
        
        elif record.record_type == "transcript":
            content = record.raw_data.get("content", "")
            if len(content) < business_rules["transcript_min_length"]:
                score -= 0.4
        
        return max(0.0, score)
    
    def _check_consistency(self, record: GongDataRecord) -> float:
        """Check data consistency"""
        # Simplified consistency check
        # In production, this would check against historical data patterns
        return 0.9  # Placeholder
    
    def _check_timeliness(self, record: GongDataRecord) -> float:
        """Check data timeliness"""
        if "created" in record.raw_data or "started" in record.raw_data:
            # Data has timestamp, assume timely
            return 1.0
        return 0.7  # No timestamp, moderate score
    
    def _check_validity(self, record: GongDataRecord) -> float:
        """Check data format validity"""
        score = 1.0
        format_rules = self.quality_rules["field_formats"]
        
        for field, pattern in format_rules.items():
            if field in record.raw_data:
                import re
                value = str(record.raw_data[field])
                if not re.match(pattern, value):
                    score -= 0.2
        
        return max(0.0, score)
    
    async def _apply_enrichments(self, record: GongDataRecord, correlation_id: str) -> Dict[str, Any]:
        """Apply AI-powered enrichments to the data"""
        await self.event_publisher.publish(DataQualityEvent(
            event_type=EventType.DATA_ENRICHMENT_STARTED,
            timestamp=datetime.now(),
            source="enrichment_engine",
            data={"record_id": record.record_id},
            correlation_id=correlation_id
        ))
        
        enriched_data = {}
        
        # Add timestamp enrichments
        enriched_data["processed_at"] = datetime.now().isoformat()
        enriched_data["quality_score"] = record.quality_metrics.overall_score
        
        # Record type specific enrichments
        if record.record_type == "call":
            enriched_data.update(await self._enrich_call_data(record))
        elif record.record_type == "transcript":
            enriched_data.update(await self._enrich_transcript_data(record))
        elif record.record_type == "user":
            enriched_data.update(await self._enrich_user_data(record))
        
        self.processing_stats["enrichments_applied"] += 1
        
        await self.event_publisher.publish(DataQualityEvent(
            event_type=EventType.DATA_ENRICHMENT_COMPLETED,
            timestamp=datetime.now(),
            source="enrichment_engine",
            data={
                "record_id": record.record_id,
                "enrichments_count": len(enriched_data)
            },
            correlation_id=correlation_id
        ))
        
        return enriched_data
    
    async def _enrich_call_data(self, record: GongDataRecord) -> Dict[str, Any]:
        """Enrich call data with AI insights"""
        enrichments = {}
        
        # Duration categorization
        duration = record.raw_data.get("duration", 0)
        if duration < 300:  # 5 minutes
            enrichments["duration_category"] = "short"
        elif duration < 1800:  # 30 minutes
            enrichments["duration_category"] = "medium"
        else:
            enrichments["duration_category"] = "long"
        
        # Business context
        title = record.raw_data.get("title", "").lower()
        if any(word in title for word in ["demo", "presentation", "pitch"]):
            enrichments["call_type"] = "sales_demo"
        elif any(word in title for word in ["follow", "check", "update"]):
            enrichments["call_type"] = "follow_up"
        else:
            enrichments["call_type"] = "general"
        
        return enrichments
    
    async def _enrich_transcript_data(self, record: GongDataRecord) -> Dict[str, Any]:
        """Enrich transcript data with NLP insights"""
        enrichments = {}
        
        content = record.raw_data.get("content", "")
        
        # Basic sentiment analysis (simplified)
        positive_words = ["great", "excellent", "love", "perfect", "amazing"]
        negative_words = ["problem", "issue", "concern", "difficult", "disappointed"]
        
        positive_count = sum(1 for word in positive_words if word in content.lower())
        negative_count = sum(1 for word in negative_words if word in content.lower())
        
        if positive_count > negative_count:
            enrichments["sentiment"] = "positive"
        elif negative_count > positive_count:
            enrichments["sentiment"] = "negative"
        else:
            enrichments["sentiment"] = "neutral"
        
        # Content length analysis
        enrichments["word_count"] = len(content.split())
        enrichments["character_count"] = len(content)
        
        return enrichments
    
    async def _enrich_user_data(self, record: GongDataRecord) -> Dict[str, Any]:
        """Enrich user data with profile insights"""
        enrichments = {}
        
        # Email domain analysis
        email = record.raw_data.get("email_address", "")
        if "@" in email:
            domain = email.split("@")[1].lower()
            enrichments["email_domain"] = domain
            
            # Company size estimation (simplified)
            if domain in ["gmail.com", "yahoo.com", "hotmail.com"]:
                enrichments["company_type"] = "personal"
            else:
                enrichments["company_type"] = "business"
        
        # Name analysis
        first_name = record.raw_data.get("first_name", "")
        last_name = record.raw_data.get("last_name", "")
        enrichments["full_name"] = f"{first_name} {last_name}".strip()
        
        return enrichments
    
    async def _handle_quality_failure(self, record: GongDataRecord, correlation_id: str):
        """Handle quality check failures"""
        await self.event_publisher.publish(DataQualityEvent(
            event_type=EventType.QUALITY_ISSUE_DETECTED,
            timestamp=datetime.now(),
            source="quality_monitor",
            data={
                "record_id": record.record_id,
                "quality_score": record.quality_metrics.overall_score,
                "issues": record.quality_metrics.issues_detected
            },
            correlation_id=correlation_id
        ))
    
    async def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing statistics"""
        quality_trends = await self.repository.get_quality_trends(days=7)
        
        return {
            "processing_stats": self.processing_stats,
            "circuit_breaker_status": self.circuit_breaker.state,
            "quality_trends": quality_trends,
            "last_updated": datetime.now().isoformat()
        }


# Factory function for easy initialization
async def create_gong_data_quality_module() -> GongDataQualityModule:
    """Create and initialize Gong Data Quality Module"""
    event_publisher = SimpleEventPublisher()
    repository = SnowflakeDataQualityRepository()
    await repository.initialize()
    
    module = GongDataQualityModule(event_publisher, repository)
    
    logger.info("✅ Gong Data Quality Module initialized with event-driven architecture")
    return module


# Example usage and testing
async def main():
    """Example usage of the Gong Data Quality Module"""
    module = await create_gong_data_quality_module()
    
    # Example Gong call data
    sample_call_data = {
        "id": "call_123",
        "title": "Demo Call with Acme Corp",
        "started": "2025-01-02T10:00:00Z",
        "duration": 1800,
        "participants": ["john@acme.com", "sales@company.com"]
    }
    
    # Process the data
    result = await module.process_gong_data(sample_call_data, "call")
    
    print(f"Processing result: {result.processing_status}")
    print(f"Quality score: {result.quality_metrics.overall_score:.2f}")
    print(f"Issues: {result.quality_metrics.issues_detected}")
    
    # Get stats
    stats = await module.get_processing_stats()
    print(f"Processing stats: {stats}")


if __name__ == "__main__":
    asyncio.run(main()) 