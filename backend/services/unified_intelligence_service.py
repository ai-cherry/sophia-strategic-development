"""
Sophia AI Unified Intelligence Service
======================================
This service unifies all AI capabilities into a single intelligent interface
with constitutional AI constraints and self-optimization.
"""

import logging
from typing import Any, Optional

import pandas as pd

# Setup logging first
logger = logging.getLogger(__name__)

# Optional Snowflake import
try:
    from backend.utils.snowflake_cortex_service import SnowflakeCortexService

    SNOWFLAKE_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Snowflake Cortex service not available: {e}")
    SnowflakeCortexService = None
    SNOWFLAKE_AVAILABLE = False

from backend.services.advanced_llm_service import AdvancedLLMService
from backend.services.data_source_manager import (
    DataError,
    DataSourceManager,
    DataSourceType,
)
from backend.services.data_transformer import DataTransformer


class UnifiedIntelligenceService:
    """
    Orchestrates data fetching, processing, and AI synthesis to answer user queries.
    """

    def __init__(self, config: Optional[dict] = None):
        self.config = config or {}
        self.data_manager = DataSourceManager()
        self.llm_service = AdvancedLLMService()
        self.transformer = DataTransformer()
        logger.info("UnifiedIntelligenceService initialized.")

    async def process_query(
        self, query: str, context: Optional[dict] = None
    ) -> dict[str, Any]:
        """
        Main entry point for processing a user query.
        Determines intent, fetches data, and synthesizes a response.
        """
        context = context or {}
        try:
            intent = self._determine_intent(query)
            logger.info(f"Determined intent: {intent}")

            handler = self._get_intent_handler(intent)
            results, insights = await handler(query, context)

            response = await self.llm_service.synthesize_response(
                query, context, results
            )

            return {
                "type": intent,
                "query": query,
                "results": results,
                "insights": insights,
                "response": response,
            }

        except DataError as e:
            logger.error(f"DataError while processing query '{query}': {e}")
            return {"error": str(e), "type": "data_error"}
        except Exception:
            logger.exception(f"Unexpected error processing query: '{query}'")
            return {
                "error": "An unexpected internal error occurred.",
                "type": "system_error",
            }

    def _determine_intent(self, query: str) -> str:
        """Determines the user's intent from the query. (Placeholder)"""
        query_lower = query.lower()
        if "deal" in query_lower or "sale" in query_lower or "pipeline" in query_lower:
            return "sales"
        if "marketing" in query_lower or "campaign" in query_lower:
            return "marketing"
        # Add more intent detection logic...
        return "general"

    def _get_intent_handler(self, intent: str):
        """Returns the appropriate handler function for a given intent."""
        if intent == "sales":
            return self._handle_sales_query
        # Add other handlers...
        return self._handle_general_query

    async def _handle_sales_query(
        self, query: str, context: dict
    ) -> (list[dict], list[str]):
        """Handles sales-related queries."""
        # This is where we replace the mock logic
        logger.info("Handling sales query...")

        # In a real scenario, the query to the data manager would be more specific
        sales_data_raw = await self.data_manager.fetch_data(
            DataSourceType.SNOWFLAKE, "get_top_deals"
        )

        if not sales_data_raw:
            return [], ["No sales data could be retrieved."]

        sales_df = self.transformer.transform_snowflake_results(sales_data_raw)
        self.transformer.validate_sales_data(sales_df)

        insights = self._generate_sales_insights(sales_df)

        return sales_df.to_dict("records"), insights

    async def _handle_general_query(
        self, query: str, context: dict
    ) -> (list[dict], list[str]):
        """Handles general queries."""
        logger.info("Handling general query...")
        # For general queries, we might search multiple sources.
        # This is a simplified example.
        return [], ["This is a general query. No specific data fetched."]

    def _generate_sales_insights(self, data: pd.DataFrame) -> list[str]:
        """Generates analytical insights from sales data."""
        if data.empty:
            return ["No data to analyze."]

        total_value = data["amount"].sum()
        deal_count = len(data)
        avg_deal_size = total_value / deal_count if deal_count > 0 else 0

        insights = [
            f"Total pipeline value in view: ${total_value:,.2f} across {deal_count} deals.",
            f"Average deal size: ${avg_deal_size:,.2f}.",
            f"Highest probability deal is '{data.loc[data['probability'].idxmax()]['deal_name']}' at {data['probability'].max()}%.",
        ]
        return insights


# Singleton instance getter
_unified_intelligence_instance = None


def get_unified_intelligence_service() -> UnifiedIntelligenceService:
    """Get or create the singleton unified intelligence service instance"""
    global _unified_intelligence_instance
    if _unified_intelligence_instance is None:
        _unified_intelligence_instance = UnifiedIntelligenceService()
    return _unified_intelligence_instance
