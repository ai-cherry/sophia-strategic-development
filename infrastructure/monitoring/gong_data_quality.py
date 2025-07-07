from __future__ import annotations

"""
Gong Data Quality Monitoring and Real-Time Metrics.

This module provides comprehensive data quality monitoring for Gong webhook data,
including real-time metrics, quality scoring, and alerting capabilities.

Key Features:
- Real-time quality assessment of webhook data
- API enhancement success tracking
- Data completeness validation
- Participant mapping accuracy
- Automated quality alerts
- Prometheus metrics integration

TODO: Implement file decomposition
"""

import time
from collections import defaultdict, deque
from datetime import UTC, datetime
from enum import Enum
from typing import Any

import structlog
from prometheus_client import Counter, Gauge, Histogram
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings

logger = structlog.get_logger()

# Real-time Data Quality Metrics
webhook_calls_received_total = Counter(
    "gong_webhook_calls_received_total",
    "Total number of webhook calls received",
    ["webhook_type", "status"],
)

api_enhancement_success_rate = Gauge(
    "gong_api_enhancement_success_rate",
    "API call success percentage for data enhancement",
)

transcript_completeness_rate = Gauge(
    "gong_transcript_completeness_rate",
    "Percentage of calls with complete transcript data",
)

participant_mapping_accuracy = Gauge(
    "gong_participant_mapping_accuracy",
    "Accuracy of participant identification and mapping",
)

data_processing_latency = Histogram(
    "gong_data_processing_latency_seconds",
    "End-to-end processing time for webhook data",
    buckets=[0.1, 0.5, 1, 2, 5, 10, 30, 60],
)

error_rate_by_type = Counter(
    "gong_error_rate_by_type_total",
    "Categorized error tracking",
    ["error_type", "severity"],
)

# Advanced Quality Metrics
data_freshness_score = Gauge(
    "gong_data_freshness_score", "Data recency assessment (0-1 scale)"
)

field_coverage_percentage = Gauge(
    "gong_field_coverage_percentage",
    "Percentage of required fields completed",
    ["field_category"],
)

enrichment_success_rate = Gauge(
    "gong_enrichment_success_rate", "Data enhancement effectiveness percentage"
)

validation_rule_violations = Counter(
    "gong_validation_rule_violations_total",
    "Specific validation rule failures",
    ["rule_name", "severity"],
)


class AlertSeverity(str, Enum):
    """Alert severity levels."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class AlertType(str, Enum):
    """Types of quality alerts."""

    QUALITY_DEGRADATION = "quality_degradation"
    API_FAILURE = "api_failure"
    PROCESSING_DELAY = "processing_delay"
    DATA_INCOMPLETE = "data_incomplete"
    VALIDATION_FAILURE = "validation_failure"
    SYSTEM_ERROR = "system_error"


class QualityDimension(str, Enum):
    """Data quality dimensions."""

    COMPLETENESS = "completeness"
    ACCURACY = "accuracy"
    TIMELINESS = "timeliness"
    CONSISTENCY = "consistency"
    VALIDITY = "validity"


class DataQualityConfig(BaseSettings):
    """Configuration for data quality monitoring."""

    # Monitoring thresholds
    MIN_QUALITY_SCORE: float = Field(default=0.8, alias="MIN_QUALITY_SCORE")
    MAX_PROCESSING_LATENCY: float = Field(default=30.0, alias="MAX_PROCESSING_LATENCY")
    ALERT_WEBHOOK_URL: str = Field(default="", alias="ALERT_WEBHOOK_URL")

    # Data validation rules
    REQUIRED_FIELDS: list[str] = [
        "call_id",
        "title",
        "started",
        "duration_seconds",
        "primary_user_id",
        "participants",
    ]
    COMPLETENESS_THRESHOLD: float = Field(default=0.95, alias="COMPLETENESS_THRESHOLD")

    # Alert configuration
    ALERT_COOLDOWN_MINUTES: int = Field(default=15, alias="ALERT_COOLDOWN_MINUTES")
    MAX_ALERTS_PER_HOUR: int = Field(default=10, alias="MAX_ALERTS_PER_HOUR")

    # Performance settings
    METRIC_UPDATE_INTERVAL: float = Field(default=5.0, alias="METRIC_UPDATE_INTERVAL")
    QUALITY_HISTORY_SIZE: int = Field(default=1000, alias="QUALITY_HISTORY_SIZE")

    class Config:
        env_file = ".env"
        case_sensitive = True


class QualityReport(BaseModel):
    """Comprehensive quality assessment report."""

    webhook_id: str
    call_id: str
    timestamp: datetime
    overall_score: float = Field(ge=0.0, le=1.0)
    dimensions: dict[QualityDimension, float]
    validation_results: list[ValidationResult]
    processing_metrics: ProcessingMetrics
    issues: list[QualityIssue] = Field(default_factory=list)


class ValidationResult(BaseModel):
    """Individual validation rule result."""

    rule_name: str
    passed: bool
    severity: AlertSeverity
    message: str | None = None
    field_name: str | None = None
    expected_value: Any | None = None
    actual_value: Any | None = None


class ProcessingMetrics(BaseModel):
    """Processing performance metrics."""

    total_duration_ms: float
    api_call_duration_ms: float | None = None
    validation_duration_ms: float
    storage_duration_ms: float | None = None
    api_calls_made: int = 0
    api_calls_failed: int = 0


class QualityIssue(BaseModel):
    """Identified quality issue."""

    dimension: QualityDimension
    severity: AlertSeverity
    description: str
    impact: str
    recommendation: str | None = None


class EnhancementReport(BaseModel):
    """API enhancement tracking report."""

    call_id: str
    enhancement_timestamp: datetime
    api_calls_attempted: int
    api_calls_successful: int
    data_points_enriched: int
    enhancement_duration_ms: float
    failures: list[dict[str, Any]] = Field(default_factory=list)


class CompletenessReport(BaseModel):
    """Data completeness assessment."""

    call_id: str
    total_fields: int
    populated_fields: int
    required_fields_missing: list[str] = Field(default_factory=list)
    optional_fields_missing: list[str] = Field(default_factory=list)
    completeness_percentage: float = Field(ge=0.0, le=100.0)
    field_quality_scores: dict[str, float] = Field(default_factory=dict)


class MappingReport(BaseModel):
    """Participant mapping accuracy report."""

    call_id: str
    total_participants: int
    successfully_mapped: int
    mapping_failures: list[dict[str, Any]] = Field(default_factory=list)
    accuracy_percentage: float = Field(ge=0.0, le=100.0)
    confidence_scores: dict[str, float] = Field(default_factory=dict)


class GongDataQualityMonitor:
    """
    Central data quality monitoring orchestrator.
    Integrates with existing webhook processing pipeline.
    """

    def __init__(self, config: DataQualityConfig | None = None):
        self.config = config or DataQualityConfig()
        self.logger = logger.bind(component="gong_data_quality_monitor")

        # Quality tracking
        self.quality_history = deque(maxlen=self.config.QUALITY_HISTORY_SIZE)
        self.alert_history = defaultdict(list)
        self.last_metrics_update = time.time()

        # Rule engine
        self.rule_engine = QualityRuleEngine(self.config)

        # Metrics collector
        self.metrics_collector = QualityMetricsCollector()

        # Moving averages for rates
        self.api_success_window = deque(maxlen=100)
        self.transcript_completeness_window = deque(maxlen=100)
        self.participant_accuracy_window = deque(maxlen=100)
        self.enrichment_success_window = deque(maxlen=100)

    async def monitor_webhook_quality(
        self, webhook_data: dict[str, Any]
    ) -> QualityReport:
        """
        Real-time quality assessment of webhook data.

        Args:
            webhook_data: Raw webhook data received

        Returns:
            Comprehensive quality report
        """
        start_time = time.time()
        call_id = webhook_data.get("call_id", "unknown")
        webhook_id = webhook_data.get("webhook_id", f"webhook_{int(time.time())}")

        self.logger.info(
            "Starting quality monitoring", call_id=call_id, webhook_id=webhook_id
        )

        # Track webhook reception
        webhook_calls_received_total.labels(
            webhook_type=webhook_data.get("event_type", "unknown"), status="received"
        ).inc()

        # Initialize report
        report = QualityReport(
            webhook_id=webhook_id,
            call_id=call_id,
            timestamp=datetime.now(UTC),
            overall_score=0.0,
            dimensions={},
            validation_results=[],
            processing_metrics=ProcessingMetrics(
                total_duration_ms=0, validation_duration_ms=0
            ),
        )

        # Validate data
        validation_start = time.time()
        validation_results = await self.rule_engine.validate_webhook_data(webhook_data)
        report.validation_results = validation_results
        report.processing_metrics.validation_duration_ms = (
            time.time() - validation_start
        ) * 1000

        # Assess quality dimensions
        dimensions = await self._assess_quality_dimensions(
            webhook_data, validation_results
        )
        report.dimensions = dimensions

        # Calculate overall score
        report.overall_score = self._calculate_overall_score(dimensions)

        # Identify issues
        report.issues = self._identify_quality_issues(
            webhook_data, dimensions, validation_results
        )

        # Update processing metrics
        report.processing_metrics.total_duration_ms = (time.time() - start_time) * 1000

        # Update metrics
        self.metrics_collector.update_quality_metrics(report)

        # Store in history
        self.quality_history.append(report)

        # Check for alerts
        await self._check_quality_alerts(report)

        # Update data freshness
        self._update_data_freshness(webhook_data)

        self.logger.info(
            "Quality monitoring completed",
            call_id=call_id,
            webhook_id=webhook_id,
            overall_score=report.overall_score,
            duration_ms=report.processing_metrics.total_duration_ms,
        )

        return report

    async def track_api_enhancement(
        self,
        call_id: str,
        api_response: dict[str, Any] | None,
        api_calls_made: int,
        duration_ms: float,
        errors: list[dict[str, Any]] = None,
    ) -> EnhancementReport:
        """
        Monitor API call success and data enrichment.

        Args:
            call_id: Call identifier
            api_response: Response from API enhancement
            api_calls_made: Number of API calls attempted
            duration_ms: Total enhancement duration
            errors: List of any errors encountered

        Returns:
            Enhancement tracking report
        """
        errors = errors or []
        api_calls_successful = api_calls_made - len(errors)

        # Track success rate
        success_rate = (
            api_calls_successful / api_calls_made if api_calls_made > 0 else 0
        )
        self.api_success_window.append(success_rate)

        # Count enriched data points
        data_points_enriched = 0
        if api_response:
            data_points_enriched = self._count_enriched_fields(api_response)

        report = EnhancementReport(
            call_id=call_id,
            enhancement_timestamp=datetime.now(UTC),
            api_calls_attempted=api_calls_made,
            api_calls_successful=api_calls_successful,
            data_points_enriched=data_points_enriched,
            enhancement_duration_ms=duration_ms,
            failures=[{"error": str(e)} for e in errors],
        )

        # Update metrics
        if len(self.api_success_window) > 0:
            api_enhancement_success_rate.set(
                sum(self.api_success_window) / len(self.api_success_window) * 100
            )

        # Track errors
        for error in errors:
            error_rate_by_type.labels(
                error_type=error.get("type", "unknown"),
                severity=error.get("severity", "medium"),
            ).inc()

        self.logger.info(
            "API enhancement tracked",
            call_id=call_id,
            success_rate=success_rate,
            data_points_enriched=data_points_enriched,
        )

        return report

    async def validate_data_completeness(
        self, processed_data: dict[str, Any]
    ) -> CompletenessReport:
        """
        Comprehensive field validation and completeness assessment.

        Args:
            processed_data: Processed webhook data with enhancements

        Returns:
            Data completeness report
        """
        call_id = processed_data.get("call_id", "unknown")

        # Analyze field completeness
        all_fields = self._extract_all_fields(processed_data)
        populated_fields = self._count_populated_fields(processed_data, all_fields)

        # Check required fields
        required_missing = []
        for field in self.config.REQUIRED_FIELDS:
            if not self._is_field_populated(processed_data, field):
                required_missing.append(field)

        # Calculate completeness
        completeness_pct = (
            (populated_fields / len(all_fields) * 100) if all_fields else 0
        )

        # Assess field quality
        field_quality = await self._assess_field_quality(processed_data)

        report = CompletenessReport(
            call_id=call_id,
            total_fields=len(all_fields),
            populated_fields=populated_fields,
            required_fields_missing=required_missing,
            optional_fields_missing=self._find_optional_missing(
                processed_data, all_fields
            ),
            completeness_percentage=completeness_pct,
            field_quality_scores=field_quality,
        )

        # Update metrics
        self.transcript_completeness_window.append(
            1.0 if self._has_complete_transcript(processed_data) else 0.0
        )

        if len(self.transcript_completeness_window) > 0:
            transcript_completeness_rate.set(
                sum(self.transcript_completeness_window)
                / len(self.transcript_completeness_window)
                * 100
            )

        field_coverage_percentage.labels(field_category="required").set(
            (len(self.config.REQUIRED_FIELDS) - len(required_missing))
            / len(self.config.REQUIRED_FIELDS)
            * 100
        )

        field_coverage_percentage.labels(field_category="all").set(completeness_pct)

        self.logger.info(
            "Data completeness validated",
            call_id=call_id,
            completeness_percentage=completeness_pct,
            required_missing=len(required_missing),
        )

        return report

    async def assess_participant_mapping(
        self, participants: list[dict[str, Any]], call_id: str
    ) -> MappingReport:
        """
        Participant identification accuracy assessment.

        Args:
            participants: List of participant data
            call_id: Call identifier

        Returns:
            Participant mapping accuracy report
        """
        total_participants = len(participants)
        successfully_mapped = 0
        mapping_failures = []
        confidence_scores = {}

        for participant in participants:
            participant_id = participant.get(
                "user_id", participant.get("email", "unknown")
            )

            # Check mapping quality
            mapping_quality = self._assess_participant_mapping_quality(participant)
            confidence_scores[participant_id] = mapping_quality["confidence"]

            if mapping_quality["success"]:
                successfully_mapped += 1
            else:
                mapping_failures.append(
                    {
                        "participant_id": participant_id,
                        "reason": mapping_quality["reason"],
                        "missing_fields": mapping_quality.get("missing_fields", []),
                    }
                )

        accuracy_pct = (
            (successfully_mapped / total_participants * 100)
            if total_participants > 0
            else 0
        )

        report = MappingReport(
            call_id=call_id,
            total_participants=total_participants,
            successfully_mapped=successfully_mapped,
            mapping_failures=mapping_failures,
            accuracy_percentage=accuracy_pct,
            confidence_scores=confidence_scores,
        )

        # Update metrics
        self.participant_accuracy_window.append(accuracy_pct / 100)

        if len(self.participant_accuracy_window) > 0:
            participant_mapping_accuracy.set(
                sum(self.participant_accuracy_window)
                / len(self.participant_accuracy_window)
                * 100
            )

        self.logger.info(
            "Participant mapping assessed",
            call_id=call_id,
            total_participants=total_participants,
            accuracy_percentage=accuracy_pct,
        )

        return report

    async def _assess_quality_dimensions(
        self, webhook_data: dict[str, Any], validation_results: list[ValidationResult]
    ) -> dict[QualityDimension, float]:
        """Assess all quality dimensions."""
        dimensions = {}

        # Completeness
        completeness_score = self._calculate_completeness_score(webhook_data)
        dimensions[QualityDimension.COMPLETENESS] = completeness_score

        # Accuracy
        accuracy_score = self._calculate_accuracy_score(validation_results)
        dimensions[QualityDimension.ACCURACY] = accuracy_score

        # Timeliness
        timeliness_score = self._calculate_timeliness_score(webhook_data)
        dimensions[QualityDimension.TIMELINESS] = timeliness_score

        # Consistency
        consistency_score = self._calculate_consistency_score(webhook_data)
        dimensions[QualityDimension.CONSISTENCY] = consistency_score

        # Validity
        validity_score = self._calculate_validity_score(validation_results)
        dimensions[QualityDimension.VALIDITY] = validity_score

        return dimensions

    def _calculate_overall_score(
        self, dimensions: dict[QualityDimension, float]
    ) -> float:
        """Calculate weighted overall quality score."""
        weights = {
            QualityDimension.COMPLETENESS: 0.3,
            QualityDimension.ACCURACY: 0.25,
            QualityDimension.TIMELINESS: 0.15,
            QualityDimension.CONSISTENCY: 0.15,
            QualityDimension.VALIDITY: 0.15,
        }

        score = 0.0
        for dimension, weight in weights.items():
            score += dimensions.get(dimension, 0.0) * weight

        return min(max(score, 0.0), 1.0)

    def _calculate_completeness_score(self, data: dict[str, Any]) -> float:
        """Calculate data completeness score."""
        required_present = sum(
            1
            for field in self.config.REQUIRED_FIELDS
            if self._is_field_populated(data, field)
        )
        return required_present / len(self.config.REQUIRED_FIELDS)

    def _calculate_accuracy_score(
        self, validation_results: list[ValidationResult]
    ) -> float:
        """Calculate accuracy score from validation results."""
        if not validation_results:
            return 1.0

        passed = sum(1 for result in validation_results if result.passed)
        return passed / len(validation_results)

    def _calculate_timeliness_score(self, data: dict[str, Any]) -> float:
        """Calculate timeliness score based on data freshness."""
        # Check webhook received time vs event time
        event_time = data.get("started", data.get("timestamp"))
        if not event_time:
            return 0.5

        try:
            if isinstance(event_time, str):
                event_dt = datetime.fromisoformat(event_time.replace("Z", "+00:00"))
            else:
                event_dt = event_time

            delay = (datetime.now(UTC) - event_dt).total_seconds()

            # Score based on delay (1.0 for <5min, 0.0 for >1hour)
            if delay < 300:  # 5 minutes
                return 1.0
            elif delay < 3600:  # 1 hour
                return 1.0 - (delay - 300) / 3300
            else:
                return 0.0
        except Exception:
            return 0.5

    def _calculate_consistency_score(self, data: dict[str, Any]) -> float:
        """Calculate data consistency score."""
        inconsistencies = 0
        checks = 0

        # Check duration consistency
        if "duration_seconds" in data and "started" in data and "ended" in data:
            checks += 1
            try:
                start = datetime.fromisoformat(data["started"].replace("Z", "+00:00"))
                end = datetime.fromisoformat(data["ended"].replace("Z", "+00:00"))
                calculated_duration = (end - start).total_seconds()
                if abs(calculated_duration - data["duration_seconds"]) > 60:
                    inconsistencies += 1
            except Exception:
                inconsistencies += 1

        # Check participant count consistency
        if "participants" in data and "participant_count" in data:
            checks += 1
            if len(data["participants"]) != data["participant_count"]:
                inconsistencies += 1

        if checks == 0:
            return 1.0

        return 1.0 - (inconsistencies / checks)

    def _calculate_validity_score(
        self, validation_results: list[ValidationResult]
    ) -> float:
        """Calculate validity score from validation results."""
        if not validation_results:
            return 1.0

        # Weight by severity
        severity_weights = {
            AlertSeverity.CRITICAL: 1.0,
            AlertSeverity.HIGH: 0.8,
            AlertSeverity.MEDIUM: 0.5,
            AlertSeverity.LOW: 0.3,
            AlertSeverity.INFO: 0.1,
        }

        total_weight = 0.0
        passed_weight = 0.0

        for result in validation_results:
            weight = severity_weights.get(result.severity, 0.5)
            total_weight += weight
            if result.passed:
                passed_weight += weight

        return passed_weight / total_weight if total_weight > 0 else 1.0

    def _identify_quality_issues(
        self,
        data: dict[str, Any],
        dimensions: dict[QualityDimension, float],
        validation_results: list[ValidationResult],
    ) -> list[QualityIssue]:
        """Identify specific quality issues."""
        issues = []

        # Check each dimension
        for dimension, score in dimensions.items():
            if score < 0.8:  # Below threshold
                issue = self._create_quality_issue(
                    dimension, score, data, validation_results
                )
                if issue:
                    issues.append(issue)

        return issues

    def _create_quality_issue(
        self,
        dimension: QualityDimension,
        score: float,
        data: dict[str, Any],
        validation_results: list[ValidationResult],
    ) -> QualityIssue | None:
        """Create quality issue for a dimension."""
        if dimension == QualityDimension.COMPLETENESS:
            missing_fields = [
                f
                for f in self.config.REQUIRED_FIELDS
                if not self._is_field_populated(data, f)
            ]
            if missing_fields:
                return QualityIssue(
                    dimension=dimension,
                    severity=(
                        AlertSeverity.HIGH if score < 0.5 else AlertSeverity.MEDIUM
                    ),
                    description=f"Data completeness below threshold: {score:.2%}",
                    impact=f"Missing required fields: {', '.join(missing_fields)}",
                    recommendation="Ensure all required fields are populated before processing",
                )

        elif dimension == QualityDimension.ACCURACY:
            failed_validations = [r for r in validation_results if not r.passed]
            if failed_validations:
                return QualityIssue(
                    dimension=dimension,
                    severity=AlertSeverity.HIGH,
                    description=f"Data accuracy issues detected: {score:.2%}",
                    impact=f"{len(failed_validations)} validation rules failed",
                    recommendation="Review and correct data validation failures",
                )

        elif dimension == QualityDimension.TIMELINESS:
            return QualityIssue(
                dimension=dimension,
                severity=AlertSeverity.MEDIUM,
                description=f"Data freshness below optimal: {score:.2%}",
                impact="Delayed data may impact real-time analytics",
                recommendation="Investigate webhook delivery delays",
            )

        return None

    async def _check_quality_alerts(self, report: QualityReport):
        """Check if quality alerts should be triggered."""
        # Check overall quality score
        if report.overall_score < self.config.MIN_QUALITY_SCORE:
            await self._trigger_alert(
                AlertType.QUALITY_DEGRADATION,
                AlertSeverity.HIGH,
                f"Overall quality score {report.overall_score:.2%} below threshold",
                report,
            )

        # Check for critical validation failures
        critical_failures = [
            r
            for r in report.validation_results
            if not r.passed and r.severity == AlertSeverity.CRITICAL
        ]
        if critical_failures:
            await self._trigger_alert(
                AlertType.VALIDATION_FAILURE,
                AlertSeverity.CRITICAL,
                f"{len(critical_failures)} critical validation failures",
                report,
            )

        # Check processing latency
        if (
            report.processing_metrics.total_duration_ms
            > self.config.MAX_PROCESSING_LATENCY * 1000
        ):
            await self._trigger_alert(
                AlertType.PROCESSING_DELAY,
                AlertSeverity.MEDIUM,
                f"Processing latency {report.processing_metrics.total_duration_ms}ms exceeds threshold",
                report,
            )

    async def _trigger_alert(
        self,
        alert_type: AlertType,
        severity: AlertSeverity,
        message: str,
        report: QualityReport,
    ):
        """Trigger quality alert with cooldown."""
        alert_key = f"{alert_type}:{report.call_id}"

        # Check cooldown
        if alert_key in self.alert_history:
            last_alert = self.alert_history[alert_key][-1]
            if (
                datetime.now(UTC) - last_alert["timestamp"]
            ).total_seconds() < self.config.ALERT_COOLDOWN_MINUTES * 60:
                return

        # Record alert
        alert_data = {
            "timestamp": datetime.now(UTC),
            "type": alert_type,
            "severity": severity,
            "message": message,
            "call_id": report.call_id,
            "quality_score": report.overall_score,
        }

        self.alert_history[alert_key].append(alert_data)

        # Log alert
        self.logger.warning(
            "Quality alert triggered",
            alert_type=alert_type.value,
            severity=severity.value,
            message=message,
            call_id=report.call_id,
        )

        # TODO: Send to alert manager for routing

    def _update_data_freshness(self, webhook_data: dict[str, Any]):
        """Update data freshness metric."""
        event_time = webhook_data.get("started", webhook_data.get("timestamp"))
        if not event_time:
            data_freshness_score.set(0.5)
            return

        try:
            if isinstance(event_time, str):
                event_dt = datetime.fromisoformat(event_time.replace("Z", "+00:00"))
            else:
                event_dt = event_time

            delay_seconds = (datetime.now(UTC) - event_dt).total_seconds()

            # Calculate freshness score (1.0 for immediate, 0.0 for >1 hour old)
            if delay_seconds < 60:  # Less than 1 minute
                freshness = 1.0
            elif delay_seconds < 3600:  # Less than 1 hour
                freshness = 1.0 - (delay_seconds - 60) / 3540
            else:
                freshness = 0.0

            data_freshness_score.set(freshness)
        except Exception as e:
            self.logger.error("Error calculating data freshness", error=str(e))
            data_freshness_score.set(0.5)

    def _is_field_populated(self, data: dict[str, Any], field_path: str) -> bool:
        """Check if a field is populated (handles nested fields)."""
        parts = field_path.split(".")
        current = data

        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return False

        # Check if value is meaningful
        if current is None:
            return False
        if isinstance(current, str) and not current.strip():
            return False
        return not (isinstance(current, list | dict) and not current)

    def _extract_all_fields(self, data: dict[str, Any], prefix: str = "") -> set[str]:
        """Extract all field paths from nested data structure."""
        fields = set()

        for key, value in data.items():
            field_path = f"{prefix}.{key}" if prefix else key
            fields.add(field_path)

            if isinstance(value, dict):
                fields.update(self._extract_all_fields(value, field_path))
            elif isinstance(value, list) and value and isinstance(value[0], dict):
                # Sample first item for structure
                fields.update(self._extract_all_fields(value[0], f"{field_path}[0]"))

        return fields

    def _count_populated_fields(
        self, data: dict[str, Any], all_fields: set[str]
    ) -> int:
        """Count populated fields."""
        return sum(1 for field in all_fields if self._is_field_populated(data, field))

    def _find_optional_missing(
        self, data: dict[str, Any], all_fields: set[str]
    ) -> list[str]:
        """Find optional fields that are missing."""
        optional_missing = []

        for field in all_fields:
            if (
                field not in self.config.REQUIRED_FIELDS
                and not self._is_field_populated(data, field)
            ):
                optional_missing.append(field)

        return optional_missing

    def _has_complete_transcript(self, data: dict[str, Any]) -> bool:
        """Check if transcript data is complete."""
        transcript = data.get("transcript")
        if not transcript:
            return False

        # Check for transcript segments
        segments = transcript.get("transcript_segments", [])
        if not segments:
            return False

        # Check segment quality
        total_duration = data.get("duration_seconds", 0)
        transcript_duration = sum(
            s.get("end_time", 0) - s.get("start_time", 0) for s in segments
        )

        # Transcript should cover at least 80% of call duration
        if total_duration > 0:
            coverage = transcript_duration / total_duration
            return coverage >= 0.8

        return False

    async def _assess_field_quality(self, data: dict[str, Any]) -> dict[str, float]:
        """Assess quality scores for individual fields."""
        field_quality = {}

        # Assess transcript quality
        if "transcript" in data:
            transcript_score = self._calculate_transcript_quality(data["transcript"])
            field_quality["transcript"] = transcript_score

        # Assess participant data quality
        if "participants" in data:
            participant_score = self._calculate_participant_quality(
                data["participants"]
            )
            field_quality["participants"] = participant_score

        # Assess metadata quality
        metadata_fields = ["title", "purpose", "topics", "action_items"]
        for field in metadata_fields:
            if field in data:
                field_quality[field] = self._calculate_metadata_quality(data[field])

        return field_quality

    def _calculate_transcript_quality(self, transcript: dict[str, Any]) -> float:
        """Calculate transcript quality score."""
        if not transcript:
            return 0.0

        score = 0.0
        factors = 0

        # Check for segments
        segments = transcript.get("transcript_segments", [])
        if segments:
            factors += 1
            # More segments generally mean better coverage
            score += min(len(segments) / 100, 1.0)

        # Check confidence score
        if "confidence_score" in transcript:
            factors += 1
            score += transcript["confidence_score"]

        # Check for speaker attribution
        if segments:
            factors += 1
            attributed = sum(1 for s in segments if s.get("speaker_id"))
            score += attributed / len(segments)

        return score / factors if factors > 0 else 0.0

    def _calculate_participant_quality(
        self, participants: list[dict[str, Any]]
    ) -> float:
        """Calculate participant data quality score."""
        if not participants:
            return 0.0

        total_score = 0.0

        for participant in participants:
            p_score = 0.0
            factors = 0

            # Check required fields
            required_fields = ["user_id", "email", "name"]
            for field in required_fields:
                if participant.get(field):
                    p_score += 1
                factors += 1

            # Check optional but valuable fields
            optional_fields = ["role", "company_domain", "engagement_score"]
            for field in optional_fields:
                if participant.get(field):
                    p_score += 0.5
                factors += 0.5

            participant_score = p_score / factors if factors > 0 else 0.0
            total_score += participant_score

        return total_score / len(participants)

    def _calculate_metadata_quality(self, field_value: Any) -> float:
        """Calculate metadata field quality score."""
        if not field_value:
            return 0.0

        if isinstance(field_value, str):
            # Check for meaningful content
            if len(field_value.strip()) < 3:
                return 0.3
            elif len(field_value.strip()) < 10:
                return 0.6
            else:
                return 1.0

        elif isinstance(field_value, list):
            # Check list content
            if not field_value:
                return 0.0
            elif len(field_value) == 1:
                return 0.5
            else:
                return min(len(field_value) / 5, 1.0)

        elif isinstance(field_value, dict):
            # Check dict completeness
            if not field_value:
                return 0.0
            else:
                populated = sum(1 for v in field_value.values() if v)
                return populated / len(field_value)

        return 0.5

    def _count_enriched_fields(self, api_response: dict[str, Any]) -> int:
        """Count number of fields enriched by API."""
        enriched_count = 0

        # Check transcript enrichment
        if api_response.get("transcript"):
            transcript = api_response["transcript"]
            if transcript.get("transcript_segments"):
                enriched_count += len(transcript["transcript_segments"])
            if transcript.get("key_phrases"):
                enriched_count += len(transcript["key_phrases"])

        # Check participant enrichment
        if api_response.get("participants"):
            enriched_count += (
                len(api_response["participants"]) * 5
            )  # Avg fields per participant

        # Check analytics enrichment
        if api_response.get("analytics"):
            analytics = api_response["analytics"]
            enriched_count += sum(1 for v in analytics.values() if v is not None)

        return enriched_count

    def _assess_participant_mapping_quality(
        self, participant: dict[str, Any]
    ) -> dict[str, Any]:
        """Assess quality of participant mapping."""
        required_fields = ["user_id", "email", "name"]
        missing_fields = [f for f in required_fields if not participant.get(f)]

        # Calculate confidence based on available data
        confidence = 1.0

        if missing_fields:
            confidence -= len(missing_fields) * 0.3

        # Check email validity
        email = participant.get("email", "")
        if email and "@" not in email:
            confidence -= 0.2

        # Check for company domain
        if not participant.get("company_domain"):
            confidence -= 0.1

        success = confidence >= 0.7 and not missing_fields

        return {
            "success": success,
            "confidence": max(confidence, 0.0),
            "reason": (
                "Missing required fields"
                if missing_fields
                else "Low data quality"
                if not success
                else "OK"
            ),
            "missing_fields": missing_fields,
        }


class QualityRuleEngine:
    """
    Configurable data quality validation rules.
    """

    def __init__(self, config: DataQualityConfig):
        self.config = config
        self.logger = logger.bind(component="quality_rule_engine")

    async def validate_webhook_data(
        self, webhook_data: dict[str, Any]
    ) -> list[ValidationResult]:
        """Validate webhook data against all rules."""
        results = []

        # Required field validation
        results.extend(self._validate_required_fields(webhook_data))

        # Data type validation
        results.extend(self._validate_data_types(webhook_data))

        # Business rule validation
        results.extend(self._validate_business_rules(webhook_data))

        # Format validation
        results.extend(self._validate_formats(webhook_data))

        # Track violations
        for result in results:
            if not result.passed:
                validation_rule_violations.labels(
                    rule_name=result.rule_name, severity=result.severity.value
                ).inc()

        return results

    def _validate_required_fields(self, data: dict[str, Any]) -> list[ValidationResult]:
        """Validate presence of required fields."""
        results = []

        for field in self.config.REQUIRED_FIELDS:
            if not self._get_field_value(data, field):
                results.append(
                    ValidationResult(
                        rule_name=f"required_field_{field}",
                        passed=False,
                        severity=AlertSeverity.HIGH,
                        message=f"Required field '{field}' is missing or empty",
                        field_name=field,
                    )
                )
            else:
                results.append(
                    ValidationResult(
                        rule_name=f"required_field_{field}",
                        passed=True,
                        severity=AlertSeverity.HIGH,
                        field_name=field,
                    )
                )

        return results

    def _validate_data_types(self, data: dict[str, Any]) -> list[ValidationResult]:
        """Validate data types of fields."""
        results = []

        # Define expected types
        type_expectations = {
            "call_id": str,
            "duration_seconds": (int, float),
            "started": str,
            "participants": list,
            "is_video": bool,
        }

        for field, expected_type in type_expectations.items():
            value = self._get_field_value(data, field)
            if value is not None:
                if not isinstance(value, expected_type):
                    results.append(
                        ValidationResult(
                            rule_name=f"data_type_{field}",
                            passed=False,
                            severity=AlertSeverity.MEDIUM,
                            message=f"Field '{field}' has incorrect type",
                            field_name=field,
                            expected_value=str(expected_type),
                            actual_value=str(type(value)),
                        )
                    )
                else:
                    results.append(
                        ValidationResult(
                            rule_name=f"data_type_{field}",
                            passed=True,
                            severity=AlertSeverity.MEDIUM,
                            field_name=field,
                        )
                    )

        return results

    def _validate_business_rules(self, data: dict[str, Any]) -> list[ValidationResult]:
        """Validate business logic rules."""
        results = []

        # Duration must be positive
        duration = data.get("duration_seconds", 0)
        if duration <= 0:
            results.append(
                ValidationResult(
                    rule_name="positive_duration",
                    passed=False,
                    severity=AlertSeverity.HIGH,
                    message="Call duration must be positive",
                    field_name="duration_seconds",
                    actual_value=duration,
                )
            )

        # Must have at least one participant
        participants = data.get("participants", [])
        if not participants:
            results.append(
                ValidationResult(
                    rule_name="minimum_participants",
                    passed=False,
                    severity=AlertSeverity.HIGH,
                    message="Call must have at least one participant",
                    field_name="participants",
                )
            )

        # Start time must be before current time
        started = data.get("started")
        if started:
            try:
                start_dt = datetime.fromisoformat(started.replace("Z", "+00:00"))
                if start_dt > datetime.now(UTC):
                    results.append(
                        ValidationResult(
                            rule_name="valid_start_time",
                            passed=False,
                            severity=AlertSeverity.MEDIUM,
                            message="Start time cannot be in the future",
                            field_name="started",
                            actual_value=started,
                        )
                    )
            except Exception:
                pass

        return results

    def _validate_formats(self, data: dict[str, Any]) -> list[ValidationResult]:
        """Validate field formats."""
        results = []

        # Validate email formats
        participants = data.get("participants", [])
        for i, participant in enumerate(participants):
            email = participant.get("email")
            if email and "@" not in email:
                results.append(
                    ValidationResult(
                        rule_name=f"email_format_participant_{i}",
                        passed=False,
                        severity=AlertSeverity.LOW,
                        message=f"Invalid email format for participant {i}",
                        field_name=f"participants[{i}].email",
                        actual_value=email,
                    )
                )

        # Validate datetime formats
        datetime_fields = ["started", "ended", "scheduled_start"]
        for field in datetime_fields:
            value = data.get(field)
            if value and isinstance(value, str):
                try:
                    datetime.fromisoformat(value.replace("Z", "+00:00"))
                    results.append(
                        ValidationResult(
                            rule_name=f"datetime_format_{field}",
                            passed=True,
                            severity=AlertSeverity.MEDIUM,
                            field_name=field,
                        )
                    )
                except Exception:
                    results.append(
                        ValidationResult(
                            rule_name=f"datetime_format_{field}",
                            passed=False,
                            severity=AlertSeverity.MEDIUM,
                            message=f"Invalid datetime format for field '{field}'",
                            field_name=field,
                            actual_value=value,
                        )
                    )

        return results

    def _get_field_value(self, data: dict[str, Any], field_path: str) -> Any:
        """Get field value from nested path."""
        parts = field_path.split(".")
        current = data

        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None

        return current

    async def validate_transcript_quality(self, transcript: str) -> ValidationResult:
        """Transcript completeness and quality checks."""
        if not transcript:
            return ValidationResult(
                rule_name="transcript_quality",
                passed=False,
                severity=AlertSeverity.MEDIUM,
                message="Transcript is empty",
            )

        # Check minimum length
        if len(transcript) < 100:
            return ValidationResult(
                rule_name="transcript_quality",
                passed=False,
                severity=AlertSeverity.LOW,
                message="Transcript is too short",
                actual_value=f"{len(transcript)} characters",
            )

        return ValidationResult(
            rule_name="transcript_quality", passed=True, severity=AlertSeverity.MEDIUM
        )

    async def check_participant_data(
        self, participants: list[dict[str, Any]]
    ) -> ValidationResult:
        """Participant information validation."""
        if not participants:
            return ValidationResult(
                rule_name="participant_data",
                passed=False,
                severity=AlertSeverity.HIGH,
                message="No participants found",
            )

        # Check each participant
        invalid_count = 0
        for participant in participants:
            if not participant.get("email") and not participant.get("user_id"):
                invalid_count += 1

        if invalid_count > 0:
            return ValidationResult(
                rule_name="participant_data",
                passed=False,
                severity=AlertSeverity.MEDIUM,
                message=f"{invalid_count} participants missing identification",
                actual_value=f"{invalid_count}/{len(participants)} invalid",
            )

        return ValidationResult(
            rule_name="participant_data", passed=True, severity=AlertSeverity.HIGH
        )

    async def assess_metadata_completeness(
        self, metadata: dict[str, Any]
    ) -> ValidationResult:
        """Required metadata field validation."""
        required_metadata = ["title", "purpose", "topics"]
        missing = [f for f in required_metadata if not metadata.get(f)]

        if missing:
            return ValidationResult(
                rule_name="metadata_completeness",
                passed=False,
                severity=AlertSeverity.LOW,
                message=f"Missing metadata fields: {', '.join(missing)}",
                actual_value=missing,
            )

        return ValidationResult(
            rule_name="metadata_completeness", passed=True, severity=AlertSeverity.LOW
        )


class QualityMetricsCollector:
    """
    Prometheus metrics collection and export.
    EXTENDS existing metrics in gong_webhook_server.py
    """

    def __init__(self):
        self.logger = logger.bind(component="quality_metrics_collector")

    def update_quality_metrics(self, quality_report: QualityReport):
        """Update Prometheus counters and gauges."""
        # Update processing latency
        data_processing_latency.observe(
            quality_report.processing_metrics.total_duration_ms / 1000
        )

        # Update enrichment success rate (moving average)
        if hasattr(self, "_enrichment_window"):
            self._enrichment_window.append(quality_report.overall_score)
            if len(self._enrichment_window) > 100:
                self._enrichment_window.pop(0)
            enrichment_success_rate.set(
                sum(self._enrichment_window) / len(self._enrichment_window) * 100
            )
        else:
            self._enrichment_window = [quality_report.overall_score]

        # Log quality dimensions
        for dimension, score in quality_report.dimensions.items():
            self.logger.info(
                "Quality dimension update",
                dimension=dimension.value,
                score=score,
                call_id=quality_report.call_id,
            )

    def track_processing_performance(self, latency_ms: float, success: bool):
        """Performance and reliability metrics."""
        # Track in appropriate bucket
        data_processing_latency.observe(latency_ms / 1000)

        # Track success/failure
        if success:
            webhook_calls_received_total.labels(
                webhook_type="call", status="processed"
            ).inc()
        else:
            webhook_calls_received_total.labels(
                webhook_type="call", status="failed"
            ).inc()

    def export_dashboard_data(self) -> dict[str, Any]:
        """Generate data for Grafana dashboards."""
        # This would typically integrate with Prometheus
        # For now, return structured data
        return {
            "timestamp": datetime.now(UTC).isoformat(),
            "metrics": {
                "api_enhancement_success_rate": api_enhancement_success_rate._value.get(),
                "transcript_completeness_rate": transcript_completeness_rate._value.get(),
                "participant_mapping_accuracy": participant_mapping_accuracy._value.get(),
                "data_freshness_score": data_freshness_score._value.get(),
                "enrichment_success_rate": enrichment_success_rate._value.get(),
            },
        }
