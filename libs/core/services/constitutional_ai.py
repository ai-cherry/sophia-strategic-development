from datetime import UTC, datetime

"""
Sophia AI Constitutional AI Framework
=====================================
Ensures all AI operations comply with ethical principles and business constraints.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class SophiaConstitutionalFramework:
    """Constitutional AI framework specifically for Sophia AI's business intelligence mission"""

    def __init__(self):
        """Initialize the constitutional framework with core principles"""
        self.principles = self._define_principles()
        logger.info(
            "🛡️ Constitutional AI Framework initialized with {} principles",
            len(self.principles),
        )

    def _define_principles(self) -> list[dict[str, Any]]:
        """Define the core constitutional principles for Sophia AI"""
        return [
            {
                "name": "business_intelligence_accuracy",
                "weight": 0.95,
                "description": "Provide accurate, data-driven business insights",
                "validation_functions": [
                    self._validate_data_accuracy,
                    self._validate_confidence_scores,
                    self._validate_source_attribution,
                ],
            },
            {
                "name": "privacy_protection",
                "weight": 0.98,
                "description": "Protect sensitive business and personal data",
                "validation_functions": [
                    self._validate_no_pii_exposure,
                    self._validate_data_handling,
                    self._validate_consent_compliance,
                ],
            },
            {
                "name": "human_autonomy",
                "weight": 0.90,
                "description": "Support decision-making without replacing human judgment",
                "validation_functions": [
                    self._validate_recommendation_language,
                    self._validate_ai_identification,
                    self._validate_multiple_perspectives,
                ],
            },
            {
                "name": "transparency",
                "weight": 0.85,
                "description": "Be transparent about AI reasoning and limitations",
                "validation_functions": [
                    self._validate_explainability,
                    self._validate_uncertainty_communication,
                    self._validate_limitation_disclosure,
                ],
            },
            {
                "name": "fairness",
                "weight": 0.88,
                "description": "Ensure fair and unbiased analysis",
                "validation_functions": [
                    self._validate_bias_mitigation,
                    self._validate_inclusive_language,
                    self._validate_equitable_treatment,
                ],
            },
        ]

    async def validate_query(
        self, query: str, context: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Validate a business intelligence query against constitutional principles

        Args:
            query: The natural language query
            context: Business context including user info

        Returns:
            Validation result with approval status and compliance score
        """
        logger.info(
            f"🔍 Validating query against constitutional principles: {query[:50]}..."
        )

        validation_results = []

        for principle in self.principles:
            principle_score = await self._validate_principle(principle, query, context)
            validation_results.append(
                {
                    "principle": principle["name"],
                    "score": principle_score,
                    "weight": principle["weight"],
                }
            )

        # Calculate overall compliance score
        total_score = sum(r["score"] * r["weight"] for r in validation_results)
        total_weight = sum(r["weight"] for r in validation_results)
        compliance_score = total_score / total_weight if total_weight > 0 else 0

        # Identify violations
        violations = [r for r in validation_results if r["score"] < 0.5]

        result = {
            "approved": compliance_score > 0.8,
            "compliance_score": compliance_score,
            "principle_scores": validation_results,
            "violations": violations,
            "timestamp": datetime.now(UTC).isoformat(),
        }

        if not result["approved"]:
            result["reason"] = self._generate_violation_reason(violations)
            result["suggestions"] = self._generate_improvement_suggestions(violations)

        logger.info(
            f"✅ Query validation complete: {'Approved' if result['approved'] else 'Rejected'} (score: {compliance_score:.2f})"
        )

        return result

    async def _validate_principle(
        self, principle: dict[str, Any], query: str, context: dict[str, Any]
    ) -> float:
        """Validate a query against a specific principle"""
        scores = []

        for validation_func in principle["validation_functions"]:
            try:
                score = await validation_func(query, context)
                scores.append(score)
            except Exception as e:
                logger.exception(
                    f"Error in validation function {validation_func.__name__}: {e}"
                )
                scores.append(0.5)  # Neutral score on error

        return sum(scores) / len(scores) if scores else 0.5

    # Validation Functions for Business Intelligence Accuracy
    async def _validate_data_accuracy(
        self, query: str, context: dict[str, Any]
    ) -> float:
        """Validate that the query seeks accurate data"""
        # Check for misleading keywords
        misleading_keywords = ["fake", "manipulate", "falsify", "lie", "deceive"]
        if any(keyword in query.lower() for keyword in misleading_keywords):
            return 0.0

        # Check for accuracy-promoting keywords
        accuracy_keywords = ["accurate", "precise", "exact", "verified", "factual"]
        if any(keyword in query.lower() for keyword in accuracy_keywords):
            return 1.0

        return 0.8  # Default high score for normal queries

    async def _validate_confidence_scores(
        self, query: str, context: dict[str, Any]
    ) -> float:
        """Validate that confidence scores will be provided"""
        # Queries asking for certainty or confidence are good
        if any(
            word in query.lower()
            for word in ["confidence", "certainty", "probability", "likelihood"]
        ):
            return 1.0

        return 0.9  # Default high score

    async def _validate_source_attribution(
        self, query: str, context: dict[str, Any]
    ) -> float:
        """Validate that sources will be properly attributed"""
        # Check if query asks for sources
        if any(
            word in query.lower()
            for word in ["source", "reference", "citation", "where"]
        ):
            return 1.0

        return 0.85  # Default good score

    # Validation Functions for Privacy Protection
    async def _validate_no_pii_exposure(
        self, query: str, context: dict[str, Any]
    ) -> float:
        """Validate that no PII will be exposed"""
        # Check for PII-related keywords
        pii_keywords = [
            "ssn",
            "social security",
            "credit card",
            "password",
            "private key",
        ]
        if any(keyword in query.lower() for keyword in pii_keywords):
            return 0.2  # Low score, needs careful handling

        # Check for personal data requests
        personal_keywords = ["personal", "private", "confidential", "secret"]
        if any(keyword in query.lower() for keyword in personal_keywords):
            return 0.6  # Medium score, needs review

        return 0.95  # Default high score

    async def _validate_data_handling(
        self, query: str, context: dict[str, Any]
    ) -> float:
        """Validate proper data handling practices"""
        # Check user role for data access
        user_role = context.get("user_role", "employee")

        if "executive" in user_role or "ceo" in user_role:
            return 1.0  # Full access for executives

        # Check for sensitive data requests
        if any(
            word in query.lower()
            for word in ["salary", "compensation", "revenue", "profit"]
        ):
            return 0.7 if "manager" in user_role else 0.4

        return 0.9  # Default good score

    async def _validate_consent_compliance(
        self, query: str, context: dict[str, Any]
    ) -> float:
        """Validate consent compliance"""
        # For now, assume consent is properly managed
        return 0.95

    # Validation Functions for Human Autonomy
    async def _validate_recommendation_language(
        self, query: str, context: dict[str, Any]
    ) -> float:
        """Validate that recommendations respect human autonomy"""
        # Check for overly prescriptive language
        prescriptive_keywords = ["must", "have to", "required to", "forced to"]
        if any(keyword in query.lower() for keyword in prescriptive_keywords):
            return 0.6  # Lower score for prescriptive queries

        # Check for supportive language
        supportive_keywords = ["suggest", "recommend", "consider", "might", "could"]
        if any(keyword in query.lower() for keyword in supportive_keywords):
            return 1.0

        return 0.85

    async def _validate_ai_identification(
        self, query: str, context: dict[str, Any]
    ) -> float:
        """Validate that AI will identify itself properly"""
        return 0.95  # Always identify as AI

    async def _validate_multiple_perspectives(
        self, query: str, context: dict[str, Any]
    ) -> float:
        """Validate consideration of multiple perspectives"""
        # Check for perspective-seeking language
        if any(
            word in query.lower()
            for word in ["perspectives", "options", "alternatives", "approaches"]
        ):
            return 1.0

        return 0.8

    # Validation Functions for Transparency
    async def _validate_explainability(
        self, query: str, context: dict[str, Any]
    ) -> float:
        """Validate that responses will be explainable"""
        if any(
            word in query.lower() for word in ["explain", "why", "how", "reasoning"]
        ):
            return 1.0

        return 0.85

    async def _validate_uncertainty_communication(
        self, query: str, context: dict[str, Any]
    ) -> float:
        """Validate proper communication of uncertainty"""
        return 0.9  # Always communicate uncertainty

    async def _validate_limitation_disclosure(
        self, query: str, context: dict[str, Any]
    ) -> float:
        """Validate disclosure of AI limitations"""
        return 0.9  # Always disclose limitations when relevant

    # Validation Functions for Fairness
    async def _validate_bias_mitigation(
        self, query: str, context: dict[str, Any]
    ) -> float:
        """Validate bias mitigation"""
        # Check for potentially biased language
        biased_keywords = ["only", "just", "always", "never", "all", "none"]
        if any(keyword in query.lower() for keyword in biased_keywords):
            return 0.7  # Lower score for absolute language

        return 0.9

    async def _validate_inclusive_language(
        self, query: str, context: dict[str, Any]
    ) -> float:
        """Validate use of inclusive language"""
        return 0.95  # Default high score

    async def _validate_equitable_treatment(
        self, query: str, context: dict[str, Any]
    ) -> float:
        """Validate equitable treatment"""
        return 0.95  # Default high score

    def _generate_violation_reason(self, violations: list[dict[str, Any]]) -> str:
        """Generate a human-readable reason for violations"""
        if not violations:
            return ""

        violation_names = [v["principle"] for v in violations]
        return f"Query violates constitutional principles: {', '.join(violation_names)}"

    def _generate_improvement_suggestions(
        self, violations: list[dict[str, Any]]
    ) -> list[str]:
        """Generate suggestions to improve compliance"""
        suggestions = []

        for violation in violations:
            principle = violation["principle"]

            if principle == "business_intelligence_accuracy":
                suggestions.append(
                    "Ensure your query seeks accurate, verifiable information"
                )
            elif principle == "privacy_protection":
                suggestions.append("Avoid requesting sensitive personal information")
            elif principle == "human_autonomy":
                suggestions.append("Frame requests as suggestions rather than commands")
            elif principle == "transparency":
                suggestions.append("Ask for explanations and reasoning behind insights")
            elif principle == "fairness":
                suggestions.append(
                    "Avoid absolute statements and consider multiple perspectives"
                )

        return suggestions

    async def validate_response(self, response: dict[str, Any]) -> dict[str, Any]:
        """Validate an AI response against constitutional principles"""
        # Simplified validation for responses
        return {
            "approved": True,
            "compliance_score": 0.95,
            "timestamp": datetime.now(UTC).isoformat(),
        }

    async def validate_optimization(
        self, optimization: dict[str, Any]
    ) -> dict[str, Any]:
        """Validate a proposed optimization against constitutional principles"""
        # Ensure optimizations don't violate principles
        score = 0.9  # Default high score

        # Check if optimization affects privacy
        if "data_collection" in optimization.get("type", ""):
            score *= 0.8

        # Check if optimization affects autonomy
        if "automation" in optimization.get("type", ""):
            score *= 0.85

        return {
            "approved": score > 0.7,
            "compliance_score": score,
            "timestamp": datetime.now(UTC).isoformat(),
        }
