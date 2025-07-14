"""
Memory Governance Framework for Sophia AI

Implements governance policies for data quality, security, compliance,
and performance in the memory ecosystem.
"""

import logging
import hashlib
import re
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

from backend.services.unified_memory_service_v2 import get_unified_memory_service
from backend.services.document_chunking_service import DocumentChunk
from backend.services.redis_helper import RedisHelper
from shared.utils.monitoring import log_execution_time

logger = logging.getLogger(__name__)


class PolicyType(Enum):
    """Types of governance policies"""

    DATA_QUALITY = "data_quality"
    SECURITY = "security"
    COMPLIANCE = "compliance"
    PERFORMANCE = "performance"
    RETENTION = "retention"


class PolicyViolationSeverity(Enum):
    """Severity levels for policy violations"""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class PolicyViolation:
    """Represents a policy violation"""

    violation_id: str
    policy_type: PolicyType
    severity: PolicyViolationSeverity
    description: str
    affected_item: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class GovernancePolicy:
    """Defines a governance policy"""

    policy_id: str
    policy_type: PolicyType
    name: str
    description: str
    rules: Dict[str, Any]
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class DataQualityMetrics:
    """Metrics for data quality assessment"""

    embedding_quality: float
    chunk_coherence: float
    information_density: float
    duplicate_ratio: float
    completeness_score: float
    overall_quality: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class DataQualityAssessor:
    """Assesses data quality for embeddings and chunks"""

    def __init__(self):
        self.memory_service = get_unified_memory_service()
        self.quality_thresholds = {
            "min_embedding_similarity": 0.7,
            "min_chunk_coherence": 0.8,
            "min_information_density": 0.6,
            "max_duplicate_ratio": 0.1,
            "min_completeness": 0.85,
        }

    async def assess_chunk_quality(self, chunk: DocumentChunk) -> DataQualityMetrics:
        """Assess quality of a document chunk"""
        # Calculate embedding quality
        embedding_quality = await self._assess_embedding_quality(chunk)

        # Calculate chunk coherence
        chunk_coherence = self._assess_chunk_coherence(chunk.content)

        # Calculate information density
        info_density = self._calculate_information_density(chunk.content)

        # Check for duplicates
        duplicate_ratio = await self._check_duplicate_ratio(chunk)

        # Calculate completeness
        completeness = self._assess_completeness(chunk)

        # Calculate overall quality
        overall_quality = (
            0.3 * embedding_quality
            + 0.2 * chunk_coherence
            + 0.2 * info_density
            + 0.1 * (1 - duplicate_ratio)
            + 0.2 * completeness
        )

        return DataQualityMetrics(
            embedding_quality=embedding_quality,
            chunk_coherence=chunk_coherence,
            information_density=info_density,
            duplicate_ratio=duplicate_ratio,
            completeness_score=completeness,
            overall_quality=overall_quality,
            metadata={
                "chunk_id": chunk.chunk_id,
                "word_count": len(chunk.content.split()),
                "assessed_at": datetime.now().isoformat(),
            },
        )

    async def _assess_embedding_quality(self, chunk: DocumentChunk) -> float:
        """Assess quality of embeddings"""
        if not chunk.embeddings:
            # Generate embeddings if missing
            try:
                chunk.embeddings = await self.memory_service.generate_embedding(
                    chunk.content
                )
            except Exception as e:
                logger.warning(f"Failed to generate embedding: {e}")
                return 0.0

        # Check embedding dimensionality
        expected_dims = 768  # Lambda GPU default
        if len(chunk.embeddings) != expected_dims:
            return 0.5

        # Check for zero or near-zero embeddings (indicates poor quality)
        import numpy as np

        embedding_array = np.array(chunk.embeddings)

        # Calculate statistics
        magnitude = np.linalg.norm(embedding_array)
        if magnitude < 0.1:  # Near-zero embedding
            return 0.0

        # Check for reasonable variance
        variance = np.var(embedding_array)
        if variance < 0.01:  # Low variance indicates poor representation
            return 0.5

        return 1.0

    def _assess_chunk_coherence(self, content: str) -> float:
        """Assess semantic coherence of chunk content"""
        sentences = content.split(". ")

        if len(sentences) < 2:
            return 1.0

        # Check for topic consistency
        # Simple approach: check for common words across sentences
        word_sets = [set(sent.lower().split()) for sent in sentences]

        # Remove stop words
        stop_words = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
        }
        word_sets = [ws - stop_words for ws in word_sets]

        # Calculate overlap between consecutive sentences
        overlaps = []
        for i in range(len(word_sets) - 1):
            if word_sets[i] and word_sets[i + 1]:
                overlap = len(word_sets[i] & word_sets[i + 1]) / min(
                    len(word_sets[i]), len(word_sets[i + 1])
                )
                overlaps.append(overlap)

        if overlaps:
            avg_overlap = sum(overlaps) / len(overlaps)
            # Map to 0-1 scale with reasonable thresholds
            return min(1.0, avg_overlap * 2)

        return 0.8  # Default coherence

    def _calculate_information_density(self, content: str) -> float:
        """Calculate information density of content"""
        words = content.lower().split()

        if not words:
            return 0.0

        # Unique word ratio
        unique_ratio = len(set(words)) / len(words)

        # Average word length (longer words often carry more information)
        avg_word_length = sum(len(w) for w in words) / len(words)
        word_length_score = min(1.0, avg_word_length / 8)  # Normalize to 8 chars

        # Check for meaningful content patterns
        # Numbers, proper nouns, technical terms indicate high information
        import re

        # Count information-rich patterns
        numbers = len(re.findall(r"\b\d+\b", content))
        capitalized = len(re.findall(r"\b[A-Z][a-z]+\b", content))
        technical_terms = len(
            re.findall(r"\b\w+(?:tion|ment|ity|ance|ence)\b", content)
        )

        pattern_score = min(
            1.0, (numbers + capitalized + technical_terms) / (len(words) / 10)
        )

        # Combined score
        return (unique_ratio + word_length_score + pattern_score) / 3

    async def _check_duplicate_ratio(self, chunk: DocumentChunk) -> float:
        """Check for duplicate content"""
        # Generate content hash
        content_hash = hashlib.md5(chunk.content.encode()).hexdigest()

        # Check cache for similar hashes
        cache_key = f"content_hash:{chunk.document_id}"
        existing_hashes = (
            await self.memory_service.redis_helper.get_json(cache_key) or []
        )

        # Calculate similarity with existing content
        duplicate_count = existing_hashes.count(content_hash)

        # Add current hash to cache
        existing_hashes.append(content_hash)
        await self.memory_service.redis_helper.set_json(
            cache_key,
            existing_hashes[-100:],  # Keep last 100 hashes
            ttl=86400,  # 24 hours
        )

        # Return ratio
        return duplicate_count / max(1, len(existing_hashes))

    def _assess_completeness(self, chunk: DocumentChunk) -> float:
        """Assess completeness of chunk"""
        content = chunk.content

        # Check for incomplete sentences
        sentences = content.split(". ")
        complete_sentences = sum(
            1 for s in sentences if s.strip().endswith((".", "!", "?"))
        )
        sentence_completeness = complete_sentences / len(sentences) if sentences else 0

        # Check for required metadata
        required_metadata = ["source", "created_at", "document_id"]
        metadata_completeness = sum(
            1 for key in required_metadata if key in chunk.metadata
        ) / len(required_metadata)

        # Check for truncation indicators
        truncation_indicators = ["...", "[truncated]", "[continued]", "etc."]
        has_truncation = any(
            indicator in content for indicator in truncation_indicators
        )
        truncation_score = 0.5 if has_truncation else 1.0

        # Combined completeness
        return (sentence_completeness + metadata_completeness + truncation_score) / 3


class SecurityPolicyEnforcer:
    """Enforces security policies for memory operations"""

    def __init__(self):
        self.pii_patterns = self._compile_pii_patterns()
        self.access_control_enabled = True

    def _compile_pii_patterns(self) -> Dict[str, re.Pattern]:
        """Compile regex patterns for PII detection"""
        return {
            "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
            "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
            "phone": re.compile(
                r"\b(?:\+?1[-.]?)?\(?[0-9]{3}\)?[-.]?[0-9]{3}[-.]?[0-9]{4}\b"
            ),
            "credit_card": re.compile(r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b"),
            "ip_address": re.compile(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b"),
            "date_of_birth": re.compile(
                r"\b(0[1-9]|1[0-2])/(0[1-9]|[12][0-9]|3[01])/\d{4}\b"
            ),
        }

    async def check_content_security(self, content: str) -> List[PolicyViolation]:
        """Check content for security violations"""
        violations = []

        # Check for PII
        pii_violations = self._detect_pii(content)
        violations.extend(pii_violations)

        # Check for sensitive keywords
        sensitive_violations = self._check_sensitive_keywords(content)
        violations.extend(sensitive_violations)

        # Check for potential injection attacks
        injection_violations = self._check_injection_patterns(content)
        violations.extend(injection_violations)

        return violations

    def _detect_pii(self, content: str) -> List[PolicyViolation]:
        """Detect PII in content"""
        violations = []

        for pii_type, pattern in self.pii_patterns.items():
            matches = pattern.findall(content)
            if matches:
                # Mask the actual values in the violation report
                masked_matches = [
                    self._mask_pii(match, pii_type) for match in matches[:3]
                ]  # Show max 3 examples

                violations.append(
                    PolicyViolation(
                        violation_id=f"pii_{pii_type}_{hashlib.md5(content.encode()).hexdigest()[:8]}",
                        policy_type=PolicyType.SECURITY,
                        severity=PolicyViolationSeverity.ERROR,
                        description=f"Detected {pii_type} PII in content",
                        affected_item="content",
                        metadata={
                            "pii_type": pii_type,
                            "count": len(matches),
                            "examples": masked_matches,
                        },
                    )
                )

        return violations

    def _mask_pii(self, value: str, pii_type: str) -> str:
        """Mask PII value for reporting"""
        if pii_type == "email":
            parts = value.split("@")
            if len(parts) == 2:
                masked = parts[0][:2] + "***@" + parts[1]
                return masked
        elif pii_type == "phone":
            return value[:3] + "***" + value[-4:]
        elif pii_type == "ssn":
            return "***-**-" + value[-4:]
        elif pii_type == "credit_card":
            return value[:4] + " **** **** " + value[-4:]
        else:
            return value[:3] + "***"

    def _check_sensitive_keywords(self, content: str) -> List[PolicyViolation]:
        """Check for sensitive business keywords"""
        violations = []

        # Define sensitive keywords
        sensitive_keywords = {
            "high": ["confidential", "secret", "proprietary", "restricted"],
            "medium": ["internal only", "private", "sensitive"],
            "low": ["draft", "preliminary", "not for distribution"],
        }

        content_lower = content.lower()

        for severity, keywords in sensitive_keywords.items():
            for keyword in keywords:
                if keyword in content_lower:
                    violations.append(
                        PolicyViolation(
                            violation_id=f"sensitive_{keyword.replace(' ', '_')}_{hashlib.md5(content.encode()).hexdigest()[:8]}",
                            policy_type=PolicyType.SECURITY,
                            severity=(
                                PolicyViolationSeverity.WARNING
                                if severity == "medium"
                                else (
                                    PolicyViolationSeverity.ERROR
                                    if severity == "high"
                                    else PolicyViolationSeverity.INFO
                                )
                            ),
                            description=f"Content contains sensitive keyword: {keyword}",
                            affected_item="content",
                            metadata={
                                "keyword": keyword,
                                "sensitivity_level": severity,
                            },
                        )
                    )

        return violations

    def _check_injection_patterns(self, content: str) -> List[PolicyViolation]:
        """Check for potential injection attack patterns"""
        violations = []

        # SQL injection patterns
        sql_patterns = [
            r"('\s*OR\s*'1'\s*=\s*'1)",
            r"(;\s*DROP\s+TABLE)",
            r"(UNION\s+SELECT)",
            r"(INSERT\s+INTO.*VALUES)",
        ]

        # Script injection patterns
        script_patterns = [
            r"(<script[^>]*>)",
            r"(javascript:)",
            r"(onerror\s*=)",
            r"(onclick\s*=)",
        ]

        # Check SQL patterns
        for pattern in sql_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                violations.append(
                    PolicyViolation(
                        violation_id=f"sql_injection_{hashlib.md5(pattern.encode()).hexdigest()[:8]}",
                        policy_type=PolicyType.SECURITY,
                        severity=PolicyViolationSeverity.CRITICAL,
                        description="Potential SQL injection pattern detected",
                        affected_item="content",
                        metadata={"pattern": pattern},
                    )
                )

        # Check script patterns
        for pattern in script_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                violations.append(
                    PolicyViolation(
                        violation_id=f"script_injection_{hashlib.md5(pattern.encode()).hexdigest()[:8]}",
                        policy_type=PolicyType.SECURITY,
                        severity=PolicyViolationSeverity.CRITICAL,
                        description="Potential script injection pattern detected",
                        affected_item="content",
                        metadata={"pattern": pattern},
                    )
                )

        return violations

    async def check_access_permissions(
        self, user_id: str, resource_id: str, action: str
    ) -> Tuple[bool, Optional[PolicyViolation]]:
        """Check if user has permission to perform action on resource"""
        if not self.access_control_enabled:
            return True, None

        # Get user role and permissions
        user_role = await self._get_user_role(user_id)
        resource_metadata = await self._get_resource_metadata(resource_id)

        # Define permission matrix
        permission_matrix = {
            "admin": ["read", "write", "delete", "share"],
            "user": ["read", "write"],
            "viewer": ["read"],
            "guest": [],
        }

        allowed_actions = permission_matrix.get(user_role, [])

        # Check resource-specific restrictions
        if resource_metadata:
            security_level = resource_metadata.get("security_level", "public")

            if security_level == "confidential" and user_role not in ["admin", "user"]:
                return False, PolicyViolation(
                    violation_id=f"access_denied_{user_id}_{resource_id}",
                    policy_type=PolicyType.SECURITY,
                    severity=PolicyViolationSeverity.ERROR,
                    description="Access denied to confidential resource",
                    affected_item=resource_id,
                    metadata={
                        "user_id": user_id,
                        "user_role": user_role,
                        "resource_security_level": security_level,
                        "attempted_action": action,
                    },
                )

        if action not in allowed_actions:
            return False, PolicyViolation(
                violation_id=f"permission_denied_{user_id}_{action}",
                policy_type=PolicyType.SECURITY,
                severity=PolicyViolationSeverity.WARNING,
                description=f"User lacks permission for action: {action}",
                affected_item=resource_id,
                metadata={
                    "user_id": user_id,
                    "user_role": user_role,
                    "attempted_action": action,
                    "allowed_actions": allowed_actions,
                },
            )

        return True, None

    async def _get_user_role(self, user_id: str) -> str:
        """Get user role from database or cache"""
        # Simplified implementation - in production, query user database
        # For now, return default role
        return "user"

    async def _get_resource_metadata(
        self, resource_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get resource metadata"""
        # Simplified implementation - in production, query resource database
        return {
            "security_level": "public",
            "owner": "system",
            "created_at": datetime.now().isoformat(),
        }


class CompliancePolicyManager:
    """Manages compliance policies for data retention and regulations"""

    def __init__(self):
        self.retention_policies = self._load_retention_policies()
        self.compliance_rules = self._load_compliance_rules()

    def _load_retention_policies(self) -> Dict[str, timedelta]:
        """Load data retention policies"""
        return {
            "pii_data": timedelta(days=90),  # 90 days for PII
            "financial_data": timedelta(days=2555),  # 7 years for financial
            "communication": timedelta(days=365),  # 1 year for communications
            "analytics": timedelta(days=730),  # 2 years for analytics
            "temporary": timedelta(days=7),  # 7 days for temporary data
            "default": timedelta(days=365),  # 1 year default
        }

    def _load_compliance_rules(self) -> Dict[str, Dict[str, Any]]:
        """Load compliance rules (GDPR, CCPA, etc.)"""
        return {
            "gdpr": {
                "requires_consent": True,
                "right_to_deletion": True,
                "data_portability": True,
                "breach_notification": timedelta(hours=72),
            },
            "ccpa": {
                "requires_disclosure": True,
                "right_to_opt_out": True,
                "non_discrimination": True,
            },
            "hipaa": {
                "requires_encryption": True,
                "access_logging": True,
                "minimum_necessary": True,
            },
        }

    async def check_retention_compliance(
        self, data_type: str, created_at: datetime
    ) -> Optional[PolicyViolation]:
        """Check if data has exceeded retention period"""
        retention_period = self.retention_policies.get(
            data_type, self.retention_policies["default"]
        )

        age = datetime.now() - created_at

        if age > retention_period:
            return PolicyViolation(
                violation_id=f"retention_{data_type}_{created_at.isoformat()}",
                policy_type=PolicyType.RETENTION,
                severity=PolicyViolationSeverity.WARNING,
                description=f"Data has exceeded retention period of {retention_period.days} days",
                affected_item=data_type,
                metadata={
                    "data_type": data_type,
                    "created_at": created_at.isoformat(),
                    "age_days": age.days,
                    "retention_days": retention_period.days,
                },
            )

        return None

    async def check_gdpr_compliance(
        self, user_data: Dict[str, Any]
    ) -> List[PolicyViolation]:
        """Check GDPR compliance for user data"""
        violations = []

        # Check for consent
        if not user_data.get("consent_given"):
            violations.append(
                PolicyViolation(
                    violation_id=f"gdpr_consent_{user_data.get('user_id', 'unknown')}",
                    policy_type=PolicyType.COMPLIANCE,
                    severity=PolicyViolationSeverity.ERROR,
                    description="User consent not recorded (GDPR requirement)",
                    affected_item=user_data.get("user_id", "unknown"),
                    metadata={"regulation": "gdpr", "requirement": "consent"},
                )
            )

        # Check for data minimization
        unnecessary_fields = ["ssn", "full_address", "birth_date"]
        collected_unnecessary = [
            field for field in unnecessary_fields if field in user_data
        ]

        if collected_unnecessary:
            violations.append(
                PolicyViolation(
                    violation_id=f"gdpr_minimization_{user_data.get('user_id', 'unknown')}",
                    policy_type=PolicyType.COMPLIANCE,
                    severity=PolicyViolationSeverity.WARNING,
                    description="Collecting potentially unnecessary personal data",
                    affected_item=user_data.get("user_id", "unknown"),
                    metadata={
                        "regulation": "gdpr",
                        "unnecessary_fields": collected_unnecessary,
                    },
                )
            )

        return violations


class MemoryGovernanceService:
    """Main governance service orchestrating all policy enforcement"""

    def __init__(self):
        self.quality_assessor = DataQualityAssessor()
        self.security_enforcer = SecurityPolicyEnforcer()
        self.compliance_manager = CompliancePolicyManager()
        self.redis_helper = RedisHelper()
        self.audit_enabled = True

    @log_execution_time
    async def validate_chunk(
        self, chunk: DocumentChunk, user_id: Optional[str] = None
    ) -> Tuple[bool, List[PolicyViolation]]:
        """
        Validate a chunk against all governance policies

        Returns:
            Tuple of (is_valid, violations)
        """
        violations = []

        # Check data quality
        quality_metrics = await self.quality_assessor.assess_chunk_quality(chunk)

        if (
            quality_metrics.overall_quality
            < self.quality_assessor.quality_thresholds["min_chunk_coherence"]
        ):
            violations.append(
                PolicyViolation(
                    violation_id=f"quality_{chunk.chunk_id}",
                    policy_type=PolicyType.DATA_QUALITY,
                    severity=PolicyViolationSeverity.WARNING,
                    description=f"Chunk quality below threshold: {quality_metrics.overall_quality:.2f}",
                    affected_item=chunk.chunk_id,
                    metadata=quality_metrics.__dict__,
                )
            )

        # Check security
        security_violations = await self.security_enforcer.check_content_security(
            chunk.content
        )
        violations.extend(security_violations)

        # Check access permissions if user provided
        if user_id:
            (
                has_access,
                access_violation,
            ) = await self.security_enforcer.check_access_permissions(
                user_id, chunk.chunk_id, "write"
            )
            if not has_access and access_violation:
                violations.append(access_violation)

        # Check retention compliance
        retention_violation = await self.compliance_manager.check_retention_compliance(
            chunk.metadata.get("data_type", "default"), chunk.created_at
        )
        if retention_violation:
            violations.append(retention_violation)

        # Audit the validation
        if self.audit_enabled:
            await self._audit_validation(chunk.chunk_id, violations)

        # Determine if chunk is valid
        critical_violations = [
            v for v in violations if v.severity == PolicyViolationSeverity.CRITICAL
        ]
        is_valid = len(critical_violations) == 0

        return is_valid, violations

    async def apply_security_policies(self, content: str) -> str:
        """Apply security policies to content (e.g., PII masking)"""
        # Detect PII
        for pii_type, pattern in self.security_enforcer.pii_patterns.items():
            matches = pattern.findall(content)
            for match in matches:
                masked = self.security_enforcer._mask_pii(match, pii_type)
                content = content.replace(match, masked)

        return content

    async def generate_governance_report(
        self, start_date: datetime, end_date: datetime
    ) -> Dict[str, Any]:
        """Generate governance compliance report"""
        # Get audit logs
        audit_logs = await self._get_audit_logs(start_date, end_date)

        # Aggregate violations by type
        violations_by_type = {}
        violations_by_severity = {}

        for log in audit_logs:
            for violation in log.get("violations", []):
                # By type
                policy_type = violation["policy_type"]
                violations_by_type[policy_type] = (
                    violations_by_type.get(policy_type, 0) + 1
                )

                # By severity
                severity = violation["severity"]
                violations_by_severity[severity] = (
                    violations_by_severity.get(severity, 0) + 1
                )

        # Calculate compliance rate
        total_validations = len(audit_logs)
        validations_with_violations = sum(
            1 for log in audit_logs if log.get("violations")
        )
        compliance_rate = (
            (total_validations - validations_with_violations) / total_validations
            if total_validations > 0
            else 1.0
        )

        return {
            "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
            "summary": {
                "total_validations": total_validations,
                "compliance_rate": compliance_rate,
                "total_violations": sum(violations_by_type.values()),
            },
            "violations_by_type": violations_by_type,
            "violations_by_severity": violations_by_severity,
            "recommendations": self._generate_recommendations(
                violations_by_type, violations_by_severity
            ),
        }

    def _generate_recommendations(
        self, violations_by_type: Dict[str, int], violations_by_severity: Dict[str, int]
    ) -> List[str]:
        """Generate recommendations based on violations"""
        recommendations = []

        # Data quality recommendations
        if violations_by_type.get(PolicyType.DATA_QUALITY.value, 0) > 10:
            recommendations.append(
                "High number of data quality violations. Consider improving chunking strategies and content validation."
            )

        # Security recommendations
        if violations_by_type.get(PolicyType.SECURITY.value, 0) > 0:
            recommendations.append(
                "Security violations detected. Implement automated PII detection and masking in the ingestion pipeline."
            )

        # Critical violations
        if violations_by_severity.get(PolicyViolationSeverity.CRITICAL.value, 0) > 0:
            recommendations.append(
                "Critical violations require immediate attention. Review security policies and access controls."
            )

        return recommendations

    async def _audit_validation(self, item_id: str, violations: List[PolicyViolation]):
        """Audit validation results"""
        audit_entry = {
            "item_id": item_id,
            "timestamp": datetime.now().isoformat(),
            "violations": [
                {
                    "violation_id": v.violation_id,
                    "policy_type": v.policy_type.value,
                    "severity": v.severity.value,
                    "description": v.description,
                }
                for v in violations
            ],
        }

        # Store in Redis with expiration
        audit_key = f"audit:{datetime.now().strftime('%Y%m%d')}:{item_id}"
        await self.redis_helper.set_json(
            audit_key, audit_entry, ttl=86400 * 30
        )  # 30 days

    async def _get_audit_logs(
        self, start_date: datetime, end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Retrieve audit logs for date range"""
        logs = []

        # Iterate through dates
        current_date = start_date
        while current_date <= end_date:
            current_date.strftime("%Y%m%d")

            # Get all audit entries for this date
            # Note: In production, use SCAN for large datasets
            keys = []  # Would get from Redis SCAN

            for key in keys:
                log = await self.redis_helper.get_json(key)
                if log:
                    logs.append(log)

            current_date += timedelta(days=1)

        return logs
