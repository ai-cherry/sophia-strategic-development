"""
Extensible Data Quality Validation Rules for Gong Integration.

Provides additional validation rules and business logic checks
beyond the core rules in gong_data_quality.py.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from enum import Enum

import structlog
from pydantic import BaseModel

from .gong_data_quality import ValidationResult, AlertSeverity

logger = structlog.get_logger()


class RuleCategory(str, Enum):
    """Categories of validation rules."""

    REQUIRED = "required"
    FORMAT = "format"
    BUSINESS = "business"
    CONSISTENCY = "consistency"
    ENRICHMENT = "enrichment"
    ANALYTICS = "analytics"


class ValidationRule(BaseModel):
    """Base validation rule definition."""

    name: str
    category: RuleCategory
    severity: AlertSeverity
    description: str
    enabled: bool = True

    async def validate(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate data against this rule."""
        raise NotImplementedError


class TranscriptQualityRule(ValidationRule):
    """Validate transcript quality and completeness."""

    def __init__(self):
        super().__init__(
            name="transcript_quality",
            category=RuleCategory.ENRICHMENT,
            severity=AlertSeverity.MEDIUM,
            description="Validates transcript quality metrics",
        )

    async def validate(self, data: Dict[str, Any]) -> ValidationResult:
        """Check transcript quality."""
        transcript = data.get("transcript", {})

        if not transcript:
            return ValidationResult(
                rule_name=self.name,
                passed=False,
                severity=self.severity,
                message="No transcript data available",
            )

        issues = []

        # Check confidence score
        confidence = transcript.get("confidence_score", 0)
        if confidence < 0.7:
            issues.append(f"Low confidence score: {confidence:.2f}")

        # Check segment coverage
        segments = transcript.get("transcript_segments", [])
        if not segments:
            issues.append("No transcript segments found")
        else:
            # Check for gaps
            total_duration = data.get("duration_seconds", 0)
            if total_duration > 0:
                segment_duration = sum(
                    s.get("end_time", 0) - s.get("start_time", 0) for s in segments
                )
                coverage = segment_duration / total_duration
                if coverage < 0.8:
                    issues.append(f"Low transcript coverage: {coverage:.2%}")

            # Check speaker attribution
            unattributed = sum(1 for s in segments if not s.get("speaker_id"))
            if unattributed > len(segments) * 0.2:
                issues.append(
                    f"High unattributed segments: {unattributed}/{len(segments)}"
                )

        if issues:
            return ValidationResult(
                rule_name=self.name,
                passed=False,
                severity=self.severity,
                message="; ".join(issues),
            )

        return ValidationResult(
            rule_name=self.name, passed=True, severity=self.severity
        )


class ParticipantEnrichmentRule(ValidationRule):
    """Validate participant data enrichment quality."""

    def __init__(self):
        super().__init__(
            name="participant_enrichment",
            category=RuleCategory.ENRICHMENT,
            severity=AlertSeverity.HIGH,
            description="Validates participant data enrichment",
        )

    async def validate(self, data: Dict[str, Any]) -> ValidationResult:
        """Check participant enrichment quality."""
        participants = data.get("participants", [])

        if not participants:
            return ValidationResult(
                rule_name=self.name,
                passed=False,
                severity=self.severity,
                message="No participants found",
            )

        issues = []
        poorly_enriched = 0

        for participant in participants:
            enrichment_score = 0
            total_checks = 0

            # Check email domain extraction
            email = participant.get("email", "")
            company_domain = participant.get("company_domain", "")
            if email and "@" in email:
                total_checks += 1
                expected_domain = email.split("@")[1]
                if company_domain == expected_domain:
                    enrichment_score += 1

            # Check role identification
            if participant.get("role"):
                enrichment_score += 1
            total_checks += 1

            # Check engagement metrics
            if participant.get("engagement_score") is not None:
                enrichment_score += 1
            total_checks += 1

            # Check talk time metrics
            if participant.get("talk_time_seconds") is not None:
                enrichment_score += 1
            total_checks += 1

            # Calculate participant enrichment percentage
            if total_checks > 0:
                enrichment_pct = enrichment_score / total_checks
                if enrichment_pct < 0.5:
                    poorly_enriched += 1

        if poorly_enriched > 0:
            issues.append(
                f"{poorly_enriched}/{len(participants)} participants poorly enriched"
            )

        # Check for duplicate participants
        emails = [p.get("email") for p in participants if p.get("email")]
        if len(emails) != len(set(emails)):
            issues.append("Duplicate participant emails detected")

        if issues:
            return ValidationResult(
                rule_name=self.name,
                passed=False,
                severity=self.severity,
                message="; ".join(issues),
            )

        return ValidationResult(
            rule_name=self.name, passed=True, severity=self.severity
        )


class CallMetadataRule(ValidationRule):
    """Validate call metadata completeness."""

    def __init__(self):
        super().__init__(
            name="call_metadata",
            category=RuleCategory.BUSINESS,
            severity=AlertSeverity.MEDIUM,
            description="Validates call metadata quality",
        )

    async def validate(self, data: Dict[str, Any]) -> ValidationResult:
        """Check call metadata quality."""
        issues = []

        # Check title quality
        title = data.get("title", "")
        if not title or len(title.strip()) < 5:
            issues.append("Missing or inadequate call title")
        elif title.lower() in ["untitled", "call", "meeting", "n/a"]:
            issues.append("Generic call title detected")

        # Check purpose/description
        purpose = data.get("purpose", "")
        if not purpose or len(purpose.strip()) < 10:
            issues.append("Missing or inadequate call purpose")

        # Check topics
        topics = data.get("topics", [])
        if not topics:
            issues.append("No topics identified")
        elif len(topics) < 2:
            issues.append("Insufficient topic extraction")

        # Check action items
        action_items = data.get("action_items", [])
        if isinstance(action_items, list):
            # Validate action item structure
            invalid_items = 0
            for item in action_items:
                if not isinstance(item, dict):
                    invalid_items += 1
                elif not item.get("description") or not item.get("assignee"):
                    invalid_items += 1
            if invalid_items > 0:
                issues.append(f"{invalid_items} invalid action items")

        # Check call outcome
        outcome = data.get("outcome", "")
        if not outcome and data.get("duration_seconds", 0) > 600:  # Calls > 10 min
            issues.append("No outcome recorded for significant call")

        if issues:
            return ValidationResult(
                rule_name=self.name,
                passed=False,
                severity=self.severity,
                message="; ".join(issues),
            )

        return ValidationResult(
            rule_name=self.name, passed=True, severity=self.severity
        )


class TimeConsistencyRule(ValidationRule):
    """Validate temporal consistency across fields."""

    def __init__(self):
        super().__init__(
            name="time_consistency",
            category=RuleCategory.CONSISTENCY,
            severity=AlertSeverity.HIGH,
            description="Validates temporal data consistency",
        )

    async def validate(self, data: Dict[str, Any]) -> ValidationResult:
        """Check time-related consistency."""
        issues = []

        # Parse timestamps
        try:
            started = data.get("started")
            ended = data.get("ended")
            scheduled_start = data.get("scheduled_start")

            if started and ended:
                start_dt = datetime.fromisoformat(started.replace("Z", "+00:00"))
                end_dt = datetime.fromisoformat(ended.replace("Z", "+00:00"))

                # Check chronological order
                if end_dt <= start_dt:
                    issues.append("End time before or equal to start time")

                # Check duration consistency
                calculated_duration = (end_dt - start_dt).total_seconds()
                reported_duration = data.get("duration_seconds", 0)

                if (
                    abs(calculated_duration - reported_duration) > 60
                ):  # 1 minute tolerance
                    issues.append(
                        f"Duration mismatch: calculated={calculated_duration:.0f}s, "
                        f"reported={reported_duration:.0f}s"
                    )

                # Check for future dates
                now = datetime.now(timezone.utc)
                if start_dt > now:
                    issues.append("Start time in the future")
                if end_dt > now:
                    issues.append("End time in the future")

            # Check scheduled vs actual start
            if scheduled_start and started:
                scheduled_dt = datetime.fromisoformat(
                    scheduled_start.replace("Z", "+00:00")
                )
                start_dt = datetime.fromisoformat(started.replace("Z", "+00:00"))

                # Check for significant delays (>30 minutes)
                delay = (start_dt - scheduled_dt).total_seconds()
                if delay > 1800:
                    issues.append(f"Call started {delay/60:.0f} minutes late")
                elif delay < -300:  # Started >5 min early
                    issues.append(f"Call started {abs(delay)/60:.0f} minutes early")

        except Exception as e:
            issues.append(f"Timestamp parsing error: {str(e)}")

        if issues:
            return ValidationResult(
                rule_name=self.name,
                passed=False,
                severity=self.severity,
                message="; ".join(issues),
            )

        return ValidationResult(
            rule_name=self.name, passed=True, severity=self.severity
        )


class AnalyticsQualityRule(ValidationRule):
    """Validate analytics data quality."""

    def __init__(self):
        super().__init__(
            name="analytics_quality",
            category=RuleCategory.ANALYTICS,
            severity=AlertSeverity.LOW,
            description="Validates analytics data extraction",
        )

    async def validate(self, data: Dict[str, Any]) -> ValidationResult:
        """Check analytics data quality."""
        analytics = data.get("analytics", {})

        if not analytics:
            return ValidationResult(
                rule_name=self.name,
                passed=False,
                severity=self.severity,
                message="No analytics data available",
            )

        issues = []

        # Check sentiment analysis
        sentiment = analytics.get("sentiment")
        if sentiment:
            if not isinstance(sentiment, dict):
                issues.append("Invalid sentiment data structure")
            elif not sentiment.get("overall_score"):
                issues.append("Missing overall sentiment score")

        # Check talk ratio
        talk_ratio = analytics.get("talk_ratio")
        if talk_ratio:
            # Validate talk ratio adds up to ~100%
            total_ratio = sum(talk_ratio.values())
            if abs(total_ratio - 1.0) > 0.05:  # 5% tolerance
                issues.append(f"Talk ratios don't sum to 100%: {total_ratio:.2%}")

        # Check interaction metrics
        interactions = analytics.get("interactions", {})
        if interactions:
            # Validate interaction counts are reasonable
            total_interactions = interactions.get("total", 0)
            duration_minutes = data.get("duration_seconds", 0) / 60

            if duration_minutes > 0:
                interactions_per_minute = total_interactions / duration_minutes
                if interactions_per_minute > 10:  # Unusually high
                    issues.append(
                        f"Unusually high interaction rate: {interactions_per_minute:.1f}/min"
                    )

        # Check key moments
        key_moments = analytics.get("key_moments", [])
        if isinstance(key_moments, list) and len(key_moments) > 0:
            # Validate key moment structure
            invalid_moments = 0
            for moment in key_moments:
                if not isinstance(moment, dict):
                    invalid_moments += 1
                elif not moment.get("timestamp") or not moment.get("description"):
                    invalid_moments += 1
            if invalid_moments > 0:
                issues.append(f"{invalid_moments} invalid key moments")

        if issues:
            return ValidationResult(
                rule_name=self.name,
                passed=False,
                severity=self.severity,
                message="; ".join(issues),
            )

        return ValidationResult(
            rule_name=self.name, passed=True, severity=self.severity
        )


class PIIDetectionRule(ValidationRule):
    """Detect potential PII in transcript data."""

    def __init__(self):
        super().__init__(
            name="pii_detection",
            category=RuleCategory.BUSINESS,
            severity=AlertSeverity.CRITICAL,
            description="Detects potential PII in data",
        )

        # Simple PII patterns (extend as needed)
        self.ssn_pattern = re.compile(r"\b\d{3}-?\d{2}-?\d{4}\b")
        self.cc_pattern = re.compile(r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b")
        self.phone_pattern = re.compile(
            r"\b(?:\+?1[-.]?)?\(?([0-9]{3})\)?[-.]?([0-9]{3})[-.]?([0-9]{4})\b"
        )

    async def validate(self, data: Dict[str, Any]) -> ValidationResult:
        """Check for potential PII."""
        pii_found = []

        # Check transcript
        transcript = data.get("transcript", {})
        if transcript:
            segments = transcript.get("transcript_segments", [])
            for i, segment in enumerate(segments):
                text = segment.get("text", "")

                # Check for SSN
                if self.ssn_pattern.search(text):
                    pii_found.append(f"Potential SSN in segment {i}")

                # Check for credit card
                if self.cc_pattern.search(text):
                    pii_found.append(f"Potential credit card in segment {i}")

                # Check for phone numbers (this is less critical)
                phone_matches = self.phone_pattern.findall(text)
                if (
                    len(phone_matches) > 3
                ):  # Multiple phone numbers might indicate PII dump
                    pii_found.append(f"Multiple phone numbers in segment {i}")

        # Check notes and action items
        notes = data.get("notes", "")
        if notes and (self.ssn_pattern.search(notes) or self.cc_pattern.search(notes)):
            pii_found.append("Potential PII in notes")

        action_items = data.get("action_items", [])
        for i, item in enumerate(action_items):
            if isinstance(item, dict):
                desc = item.get("description", "")
                if self.ssn_pattern.search(desc) or self.cc_pattern.search(desc):
                    pii_found.append(f"Potential PII in action item {i}")

        if pii_found:
            return ValidationResult(
                rule_name=self.name,
                passed=False,
                severity=self.severity,
                message=f"PII detected: {'; '.join(pii_found[:3])}",  # Limit to first 3
            )

        return ValidationResult(
            rule_name=self.name, passed=True, severity=self.severity
        )


class CustomRuleRegistry:
    """Registry for managing custom validation rules."""

    def __init__(self):
        self.rules: Dict[str, ValidationRule] = {}
        self.logger = logger.bind(component="custom_rule_registry")

        # Register default rules
        self._register_default_rules()

    def _register_default_rules(self):
        """Register default validation rules."""
        default_rules = [
            TranscriptQualityRule(),
            ParticipantEnrichmentRule(),
            CallMetadataRule(),
            TimeConsistencyRule(),
            AnalyticsQualityRule(),
            PIIDetectionRule(),
        ]

        for rule in default_rules:
            self.register_rule(rule)

    def register_rule(self, rule: ValidationRule):
        """Register a custom validation rule."""
        self.rules[rule.name] = rule
        self.logger.info(f"Registered rule: {rule.name}")

    def unregister_rule(self, rule_name: str):
        """Unregister a validation rule."""
        if rule_name in self.rules:
            del self.rules[rule_name]
            self.logger.info(f"Unregistered rule: {rule_name}")

    def get_rule(self, rule_name: str) -> Optional[ValidationRule]:
        """Get a specific rule by name."""
        return self.rules.get(rule_name)

    def get_rules_by_category(self, category: RuleCategory) -> List[ValidationRule]:
        """Get all rules in a category."""
        return [r for r in self.rules.values() if r.category == category]

    def get_enabled_rules(self) -> List[ValidationRule]:
        """Get all enabled rules."""
        return [r for r in self.rules.values() if r.enabled]

    async def validate_all(self, data: Dict[str, Any]) -> List[ValidationResult]:
        """Run all enabled rules against data."""
        results = []

        for rule in self.get_enabled_rules():
            try:
                result = await rule.validate(data)
                results.append(result)
            except Exception as e:
                self.logger.error(f"Error in rule {rule.name}: {str(e)}")
                results.append(
                    ValidationResult(
                        rule_name=rule.name,
                        passed=False,
                        severity=AlertSeverity.MEDIUM,
                        message=f"Rule execution error: {str(e)}",
                    )
                )

        return results

    async def validate_by_category(
        self, data: Dict[str, Any], category: RuleCategory
    ) -> List[ValidationResult]:
        """Run all rules in a specific category."""
        results = []

        for rule in self.get_rules_by_category(category):
            if rule.enabled:
                try:
                    result = await rule.validate(data)
                    results.append(result)
                except Exception as e:
                    self.logger.error(f"Error in rule {rule.name}: {str(e)}")

        return results


# Singleton instance
rule_registry = CustomRuleRegistry()
