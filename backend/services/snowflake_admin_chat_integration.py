"""
Snowflake Admin Chat Integration
Integration layer between Enhanced Unified Chat Service and Snowflake Admin Agent
"""

import asyncio
import json
import logging
import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

from backend.agents.specialized.snowflake_admin_agent import (
    SnowflakeAdminAgent,
    AdminTaskRequest,
    AdminTaskResponse,
    SnowflakeEnvironment,
    confirm_snowflake_admin_task,
)

logger = logging.getLogger(__name__)


class SnowflakeAdminIntent(Enum):
    """Snowflake admin-specific intents"""

    SCHEMA_MANAGEMENT = "schema_management"
    WAREHOUSE_MANAGEMENT = "warehouse_management"
    ROLE_MANAGEMENT = "role_management"
    USER_MANAGEMENT = "user_management"
    GRANTS_MANAGEMENT = "grants_management"
    OBJECT_INSPECTION = "object_inspection"
    CONFIGURATION = "configuration"
    CONFIRMATION = "confirmation"


@dataclass
class SnowflakeAdminQuery:
    """Parsed Snowflake admin query"""

    original_query: str
    intent: SnowflakeAdminIntent
    environment: SnowflakeEnvironment
    entities: Dict[str, Any]
    confidence: float
    requires_confirmation: bool = False
    confirmation_id: Optional[str] = None


class SnowflakeAdminIntentClassifier:
    """Intent classifier for Snowflake admin queries"""

    def __init__(self):
        self.admin_patterns = {
            SnowflakeAdminIntent.SCHEMA_MANAGEMENT: {
                "keywords": ["schema", "create schema", "drop schema", "alter schema"],
                "phrases": [
                    "create schema",
                    "show schemas",
                    "describe schema",
                    "grant on schema",
                ],
                "patterns": [
                    r"create\s+schema",
                    r"show\s+schemas",
                    r"describe\s+schema",
                ],
            },
            SnowflakeAdminIntent.WAREHOUSE_MANAGEMENT: {
                "keywords": [
                    "warehouse",
                    "compute",
                    "create warehouse",
                    "alter warehouse",
                ],
                "phrases": [
                    "create warehouse",
                    "show warehouses",
                    "alter warehouse",
                    "suspend warehouse",
                ],
                "patterns": [
                    r"create\s+warehouse",
                    r"show\s+warehouses",
                    r"alter\s+warehouse",
                ],
            },
            SnowflakeAdminIntent.ROLE_MANAGEMENT: {
                "keywords": ["role", "create role", "grant role", "show roles"],
                "phrases": ["create role", "grant role", "show roles", "drop role"],
                "patterns": [r"create\s+role", r"grant\s+role", r"show\s+roles"],
            },
            SnowflakeAdminIntent.USER_MANAGEMENT: {
                "keywords": ["user", "create user", "alter user", "show users"],
                "phrases": ["create user", "show users", "alter user", "drop user"],
                "patterns": [r"create\s+user", r"show\s+users", r"alter\s+user"],
            },
            SnowflakeAdminIntent.GRANTS_MANAGEMENT: {
                "keywords": ["grant", "revoke", "privilege", "permission"],
                "phrases": [
                    "grant usage",
                    "revoke access",
                    "show grants",
                    "grant select",
                ],
                "patterns": [r"grant\s+\w+", r"revoke\s+\w+", r"show\s+grants"],
            },
            SnowflakeAdminIntent.OBJECT_INSPECTION: {
                "keywords": ["show", "describe", "list", "inspect"],
                "phrases": [
                    "show tables",
                    "describe table",
                    "show columns",
                    "list objects",
                ],
                "patterns": [r"show\s+\w+", r"describe\s+\w+", r"list\s+\w+"],
            },
            SnowflakeAdminIntent.CONFIRMATION: {
                "keywords": ["confirm", "yes", "proceed", "execute"],
                "phrases": [
                    "yes confirm",
                    "proceed with",
                    "execute sql",
                    "confirm operation",
                ],
                "patterns": [r"confirm\s+\w+", r"yes\s*,?\s*confirm", r"proceed"],
            },
        }

        self.environment_patterns = {
            "dev": [r"\bdev\b", r"\bdevelopment\b", r"\bdev[_-]env\b"],
            "stg": [r"\bstg\b", r"\bstaging\b", r"\bstage\b", r"\bstg[_-]env\b"],
            "prod": [r"\bprod\b", r"\bproduction\b", r"\bprod[_-]env\b"],
        }

    def is_snowflake_admin_query(self, query: str) -> bool:
        """Check if query is related to Snowflake administration"""
        query_lower = query.lower()

        # Check for Snowflake-specific keywords
        snowflake_keywords = [
            "snowflake",
            "schema",
            "warehouse",
            "role",
            "grant",
            "revoke",
            "create",
            "drop",
            "alter",
            "show",
            "describe",
            "sql",
        ]

        admin_keywords = ["admin", "administration", "manage", "configure", "setup"]

        # Must have at least one Snowflake keyword
        has_snowflake = any(keyword in query_lower for keyword in snowflake_keywords)

        # Check for admin patterns
        for intent_patterns in self.admin_patterns.values():
            if any(keyword in query_lower for keyword in intent_patterns["keywords"]):
                return True
            if any(phrase in query_lower for phrase in intent_patterns["phrases"]):
                return True
            if any(
                re.search(pattern, query_lower)
                for pattern in intent_patterns["patterns"]
            ):
                return True

        return has_snowflake and any(
            keyword in query_lower for keyword in admin_keywords
        )

    def classify_admin_intent(self, query: str) -> Tuple[SnowflakeAdminIntent, float]:
        """Classify Snowflake admin intent"""
        query_lower = query.lower()
        intent_scores = {}

        for intent, patterns in self.admin_patterns.items():
            score = 0.0

            # Check keywords
            for keyword in patterns["keywords"]:
                if keyword in query_lower:
                    score += 0.2

            # Check phrases (higher weight)
            for phrase in patterns["phrases"]:
                if phrase in query_lower:
                    score += 0.4

            # Check regex patterns (highest weight)
            for pattern in patterns["patterns"]:
                if re.search(pattern, query_lower):
                    score += 0.5

            intent_scores[intent] = score

        if intent_scores:
            best_intent = max(intent_scores.items(), key=lambda x: x[1])
            return best_intent[0], min(best_intent[1], 1.0)

        return SnowflakeAdminIntent.OBJECT_INSPECTION, 0.3

    def extract_environment(self, query: str) -> SnowflakeEnvironment:
        """Extract target environment from query"""
        query_lower = query.lower()

        for env, patterns in self.environment_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    return SnowflakeEnvironment(env)

        # Default to dev for safety
        return SnowflakeEnvironment.DEV

    def extract_entities(
        self, query: str, intent: SnowflakeAdminIntent
    ) -> Dict[str, Any]:
        """Extract entities based on intent"""
        entities = {}
        query.lower()

        # Extract common entities
        schema_match = re.search(
            r"schema\s+([A-Za-z_][A-Za-z0-9_]*)", query, re.IGNORECASE
        )
        if schema_match:
            entities["schema_name"] = schema_match.group(1)

        warehouse_match = re.search(
            r"warehouse\s+([A-Za-z_][A-Za-z0-9_]*)", query, re.IGNORECASE
        )
        if warehouse_match:
            entities["warehouse_name"] = warehouse_match.group(1)

        role_match = re.search(r"role\s+([A-Za-z_][A-Za-z0-9_]*)", query, re.IGNORECASE)
        if role_match:
            entities["role_name"] = role_match.group(1)

        user_match = re.search(r"user\s+([A-Za-z0-9._@-]+)", query, re.IGNORECASE)
        if user_match:
            entities["user_name"] = user_match.group(1)

        table_match = re.search(
            r"table\s+([A-Za-z_][A-Za-z0-9_.]*)", query, re.IGNORECASE
        )
        if table_match:
            entities["table_name"] = table_match.group(1)

        # Extract confirmation ID for confirmation intents
        if intent == SnowflakeAdminIntent.CONFIRMATION:
            confirm_match = re.search(
                r"confirm[_\s]+([A-Za-z0-9_]+)", query, re.IGNORECASE
            )
            if confirm_match:
                entities["confirmation_id"] = confirm_match.group(1)

        return entities

    def parse_admin_query(self, query: str) -> SnowflakeAdminQuery:
        """Parse complete admin query"""
        intent, confidence = self.classify_admin_intent(query)
        environment = self.extract_environment(query)
        entities = self.extract_entities(query, intent)

        return SnowflakeAdminQuery(
            original_query=query,
            intent=intent,
            environment=environment,
            entities=entities,
            confidence=confidence,
        )


class SnowflakeAdminChatIntegration:
    """Integration layer for Snowflake admin functionality in chat"""

    def __init__(self):
        self.intent_classifier = SnowflakeAdminIntentClassifier()
        self.admin_agent = SnowflakeAdminAgent()
        self.pending_confirmations = {}  # In production, use Redis
        self.initialized = False

    async def initialize(self):
        """Initialize the integration"""
        if self.initialized:
            return

        try:
            await self.admin_agent.initialize()
            self.initialized = True
            logger.info("✅ Snowflake Admin Chat Integration initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Snowflake Admin Chat Integration: {e}")
            raise

    def is_admin_query(self, query: str) -> bool:
        """Check if query is a Snowflake admin query"""
        return self.intent_classifier.is_snowflake_admin_query(query)

    async def process_admin_query(
        self,
        query: str,
        user_id: str = "system",
        user_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Process a Snowflake admin query

        Args:
            query: User query
            user_id: User identifier
            user_context: Additional user context

        Returns:
            Formatted response for chat interface
        """
        if not self.initialized:
            await self.initialize()

        try:
            # Parse the admin query
            parsed_query = self.intent_classifier.parse_admin_query(query)

            # Handle confirmation queries
            if parsed_query.intent == SnowflakeAdminIntent.CONFIRMATION:
                return await self._handle_confirmation(parsed_query, user_id)

            # Execute admin task
            request = AdminTaskRequest(
                natural_language_request=query,
                target_environment=parsed_query.environment,
                user_id=user_id,
            )

            response = await self.admin_agent.execute_admin_task(request)

            # Format response for chat
            return self._format_admin_response(response, parsed_query)

        except Exception as e:
            logger.error(f"Error processing admin query: {e}")
            return {
                "success": False,
                "message": f"Error processing Snowflake admin query: {str(e)}",
                "type": "error",
            }

    async def _handle_confirmation(
        self, parsed_query: SnowflakeAdminQuery, user_id: str
    ) -> Dict[str, Any]:
        """Handle confirmation queries"""
        confirmation_id = parsed_query.entities.get("confirmation_id")

        if not confirmation_id:
            return {
                "success": False,
                "message": "Please specify the confirmation ID (e.g., 'confirm confirm_123')",
                "type": "error",
            }

        if confirmation_id not in self.pending_confirmations:
            return {
                "success": False,
                "message": f"Confirmation ID {confirmation_id} not found or expired",
                "type": "error",
            }

        # Get confirmation data
        confirmation_data = self.pending_confirmations[confirmation_id]

        # Execute confirmed SQL
        response = await confirm_snowflake_admin_task(
            natural_language_request=confirmation_data["original_request"],
            confirmed_sql=confirmation_data["sql"],
            target_environment=confirmation_data["environment"],
            user_id=user_id,
        )

        # Remove from pending
        del self.pending_confirmations[confirmation_id]

        return {
            "success": response.success,
            "message": response.message,
            "type": "confirmation_executed",
            "sql_executed": response.sql_executed,
            "environment": confirmation_data["environment"],
            "execution_time": f"{response.execution_time:.2f}s",
            "results": response.results[:5] if response.results else None,
        }

    def _format_admin_response(
        self, response: AdminTaskResponse, parsed_query: SnowflakeAdminQuery
    ) -> Dict[str, Any]:
        """Format admin response for chat interface"""

        if response.requires_confirmation:
            # Generate confirmation ID
            confirmation_id = f"confirm_{len(self.pending_confirmations)}_{int(asyncio.get_event_loop().time())}"

            # Store pending confirmation
            self.pending_confirmations[confirmation_id] = {
                "original_request": parsed_query.original_query,
                "sql": response.confirmation_sql,
                "environment": response.environment.value,
                "timestamp": asyncio.get_event_loop().time(),
            }

            return {
                "success": False,
                "message": response.message,
                "type": "confirmation_required",
                "confirmation_id": confirmation_id,
                "proposed_sql": response.confirmation_sql,
                "environment": response.environment.value,
                "warning": "⚠️ This operation contains potentially destructive SQL commands.",
                "instructions": f"To proceed, type: 'confirm {confirmation_id}'",
            }

        # Regular response
        result = {
            "success": response.success,
            "message": response.message,
            "type": "admin_task_completed",
            "environment": (
                response.environment.value if response.environment else "unknown"
            ),
            "execution_time": f"{response.execution_time:.2f}s",
        }

        if response.sql_executed:
            result["sql_executed"] = response.sql_executed

        if response.results:
            result["results"] = response.results[:10]  # Limit for chat display
            if len(response.results) > 10:
                result["results_note"] = (
                    f"Showing 10 of {len(response.results)} results"
                )

        return result

    async def get_admin_suggestions(self, partial_query: str) -> List[str]:
        """Get suggestions for admin queries"""
        suggestions = []

        # Common admin tasks
        common_tasks = [
            "Show all schemas in the current database",
            "Create a new schema called MARKETING_STAGE",
            "Show all warehouses and their status",
            "Create a warehouse called DEV_WH with size XSMALL",
            "Show all roles in the account",
            "Grant USAGE on schema ANALYTICS to role DATA_ANALYST",
            "Describe table CUSTOMERS",
            "Show all tables in schema SALES_DATA",
        ]

        # Filter suggestions based on partial query
        partial_lower = partial_query.lower()
        for task in common_tasks:
            if any(word in task.lower() for word in partial_lower.split()):
                suggestions.append(task)

        return suggestions[:5]  # Return top 5 suggestions

    async def health_check(self) -> Dict[str, Any]:
        """Health check for admin integration"""
        health = await self.admin_agent.health_check()

        return {
            "integration_initialized": self.initialized,
            "admin_agent_health": health,
            "pending_confirmations": len(self.pending_confirmations),
        }


# Global integration instance
snowflake_admin_integration = SnowflakeAdminChatIntegration()


# Convenience functions
async def process_snowflake_admin_query(
    query: str, user_id: str = "system", user_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Convenience function for processing Snowflake admin queries

    Args:
        query: User query
        user_id: User identifier
        user_context: Additional context

    Returns:
        Formatted response
    """
    return await snowflake_admin_integration.process_admin_query(
        query, user_id, user_context
    )


def is_snowflake_admin_query(query: str) -> bool:
    """
    Check if query is related to Snowflake administration

    Args:
        query: User query

    Returns:
        True if it's a Snowflake admin query
    """
    return snowflake_admin_integration.is_admin_query(query)


# Example usage
if __name__ == "__main__":

    async def test_admin_integration():
        """Test the admin integration"""

        test_queries = [
            "Create a new schema called MARKETING_STAGE in dev environment",
            "Show all warehouses in production",
            "Grant USAGE on warehouse ANALYTICS_WH to role DATA_ANALYST",
            "Drop schema OLD_DATA",  # Should require confirmation
            "confirm confirm_123",  # Confirmation example
        ]

        for query in test_queries:
            print(f"\n--- Query: {query} ---")

            if is_snowflake_admin_query(query):
                response = await process_snowflake_admin_query(query, "test_user")
                print(f"Response: {json.dumps(response, indent=2, default=str)}")
            else:
                print("Not a Snowflake admin query")

    asyncio.run(test_admin_integration())
