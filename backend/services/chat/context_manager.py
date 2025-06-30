"""
Context Manager - Phase 2B Implementation
Manages conversation context and business intelligence integration
"""

import logging
from typing import Any

from ...models.chat_models import ChatContext

logger = logging.getLogger(__name__)

class ContextManager:
    """
    Manages conversation context and business intelligence
    Handles context persistence, enrichment, and retrieval
    """

    def __init__(self):
        self.logger = logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")

        # In-memory context storage (replace with database in production)
        self._contexts: dict[str, ChatContext] = {}

        self.logger.info("Context manager initialized")

    async def get_context(self, session_id: str) -> ChatContext | None:
        """Get context for a session"""
        return self._contexts.get(session_id)

    async def update_context(self, session_id: str, context: ChatContext) -> bool:
        """Update context for a session"""
        try:
            # Merge with existing context if present
            existing_context = self._contexts.get(session_id)

            if existing_context:
                # Merge contexts intelligently
                merged_context = self._merge_contexts(existing_context, context)
                self._contexts[session_id] = merged_context
            else:
                self._contexts[session_id] = context

            self.logger.debug(f"Updated context for session: {session_id}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to update context for session {session_id}: {str(e)}")
            return False

    def _merge_contexts(self, existing: ChatContext, new: ChatContext) -> ChatContext:
        """Intelligently merge two contexts"""
        merged = ChatContext(
            user_id=new.user_id or existing.user_id,
            user_role=new.user_role or existing.user_role,
            organization=new.organization or existing.organization,
            department=new.department or existing.department
        )

        # Merge preferences
        merged.preferences = existing.preferences or {}
        if new.preferences:
            merged.preferences.update(new.preferences)

        # Merge business context
        merged.business_context = existing.business_context or {}
        if new.business_context:
            merged.business_context.update(new.business_context)

        return merged

    async def enrich_context(self, session_id: str, enrichment_data: dict[str, Any]) -> bool:
        """Enrich context with additional business intelligence"""
        try:
            context = self._contexts.get(session_id)

            if not context:
                # Create new context with enrichment data
                context = ChatContext(business_context=enrichment_data)
                self._contexts[session_id] = context
            else:
                # Add enrichment to existing context
                if not context.business_context:
                    context.business_context = {}
                context.business_context.update(enrichment_data)

            self.logger.debug(f"Enriched context for session: {session_id}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to enrich context for session {session_id}: {str(e)}")
            return False

    async def get_business_insights(self, session_id: str) -> dict[str, Any]:
        """Get business insights from context"""
        context = self._contexts.get(session_id)

        if not context or not context.business_context:
            return {}

        # Extract relevant business insights
        insights = {
            "user_profile": {
                "role": context.user_role,
                "department": context.department,
                "organization": context.organization
            },
            "business_metrics": context.business_context.get("metrics", {}),
            "recent_activities": context.business_context.get("activities", []),
            "preferences": context.preferences or {}
        }

        return insights

    async def get_contextual_suggestions(self, session_id: str, mode: str) -> list[str]:
        """Get contextual suggestions based on user context and mode"""
        context = self._contexts.get(session_id)

        if not context:
            return self._get_default_suggestions(mode)

        suggestions = []

        # Role-based suggestions
        if context.user_role:
            suggestions.extend(self._get_role_based_suggestions(context.user_role, mode))

        # Department-based suggestions
        if context.department:
            suggestions.extend(self._get_department_suggestions(context.department, mode))

        # Business context suggestions
        if context.business_context:
            suggestions.extend(self._get_business_context_suggestions(context.business_context, mode))

        # Remove duplicates and limit
        unique_suggestions = list(dict.fromkeys(suggestions))
        return unique_suggestions[:5]

    def _get_default_suggestions(self, mode: str) -> list[str]:
        """Get default suggestions for a mode"""
        defaults = {
            "universal": [
                "How can I help you today?",
                "What would you like to know?",
                "Tell me more about your needs"
            ],
            "sophia": [
                "Analyze our business performance",
                "What are the key trends?",
                "Generate strategic insights"
            ],
            "executive": [
                "Summarize key metrics",
                "What are our priorities?",
                "Prepare board summary"
            ]
        }

        return defaults.get(mode, defaults["universal"])

    def _get_role_based_suggestions(self, role: str, mode: str) -> list[str]:
        """Get suggestions based on user role"""
        role_suggestions = {
            "ceo": [
                "Review quarterly performance",
                "Analyze competitive positioning",
                "Strategic planning insights"
            ],
            "cfo": [
                "Financial performance analysis",
                "Cost optimization opportunities",
                "Revenue forecasting"
            ],
            "cto": [
                "Technology roadmap review",
                "Infrastructure optimization",
                "Innovation opportunities"
            ],
            "manager": [
                "Team performance metrics",
                "Resource allocation",
                "Process improvements"
            ]
        }

        return role_suggestions.get(role.lower(), [])

    def _get_department_suggestions(self, department: str, mode: str) -> list[str]:
        """Get suggestions based on department"""
        dept_suggestions = {
            "sales": [
                "Sales pipeline analysis",
                "Customer acquisition metrics",
                "Revenue forecasting"
            ],
            "marketing": [
                "Campaign performance",
                "Lead generation analysis",
                "Brand metrics"
            ],
            "engineering": [
                "Development velocity",
                "Code quality metrics",
                "Technical debt analysis"
            ],
            "finance": [
                "Budget analysis",
                "Cost center performance",
                "Financial projections"
            ]
        }

        return dept_suggestions.get(department.lower(), [])

    def _get_business_context_suggestions(self, business_context: dict[str, Any], mode: str) -> list[str]:
        """Get suggestions based on business context"""
        suggestions = []

        # Check for recent metrics
        if "metrics" in business_context:
            suggestions.append("Explain recent metric changes")

        # Check for activities
        if "activities" in business_context:
            suggestions.append("Summarize recent activities")

        # Check for alerts or issues
        if "alerts" in business_context:
            suggestions.append("Review current alerts")

        return suggestions

    async def delete_context(self, session_id: str) -> bool:
        """Delete context for a session"""
        if session_id in self._contexts:
            del self._contexts[session_id]
            self.logger.debug(f"Deleted context for session: {session_id}")
            return True

        return False

    async def get_context_summary(self, session_id: str) -> dict[str, Any]:
        """Get a summary of the context"""
        context = self._contexts.get(session_id)

        if not context:
            return {"exists": False}

        return {
            "exists": True,
            "user_id": context.user_id,
            "user_role": context.user_role,
            "organization": context.organization,
            "department": context.department,
            "has_preferences": bool(context.preferences),
            "has_business_context": bool(context.business_context),
            "business_context_keys": list(context.business_context.keys()) if context.business_context else []
        }

    async def close(self):
        """Close context manager and cleanup resources"""
        self._contexts.clear()
        self.logger.info("Context manager closed")

    def __len__(self) -> int:
        """Get number of contexts"""
        return len(self._contexts)

