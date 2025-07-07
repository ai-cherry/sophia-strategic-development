# File: backend/services/snowflake_intelligence_service.py

import json
import logging
from dataclasses import dataclass
from typing import Any

from infrastructure.mcp_servers.mcp_client import MCPClient
from infrastructure.services.semantic_layer_service import SemanticLayerService
from infrastructure.services.vector_indexing_service import VectorIndexingService

logger = logging.getLogger(__name__)


@dataclass
class IntelligenceQuery:
    """Structure for Snowflake Intelligence queries"""

    query_text: str
    user_context: dict[str, Any]
    required_sources: list[str]
    response_format: str = "comprehensive"
    include_visualizations: bool = True


@dataclass
class IntelligenceResponse:
    """Structure for Snowflake Intelligence responses"""

    answer: str
    sources_used: list[str]
    confidence_score: float
    sql_queries: list[str]
    visualizations: list[dict[str, Any]]
    follow_up_suggestions: list[str]


class SnowflakeIntelligenceService:
    """
    Snowflake Intelligence integration service.
    Provides natural language query capabilities with cross-source reasoning.
    """

    def __init__(self):
        self.semantic_service = SemanticLayerService()
        self.vector_service = VectorIndexingService()
        self.mcp_client = MCPClient()

    async def process_natural_language_query(
        self, query: IntelligenceQuery
    ) -> IntelligenceResponse:
        """Process natural language query using Snowflake Intelligence"""
        try:
            query_analysis = await self._analyze_query_intent(query.query_text)
            structured_data = await self._retrieve_structured_data(
                query_analysis, query.query_text
            )
            unstructured_data = await self._retrieve_unstructured_data(
                query_analysis, query.query_text
            )

            synthesis_result = await self._synthesize_response(
                query.query_text, structured_data, unstructured_data, query.user_context
            )

            visualizations = await self._generate_visualizations(synthesis_result)
            follow_ups = await self._generate_follow_up_suggestions(
                query.query_text, synthesis_result
            )

            return IntelligenceResponse(
                answer=synthesis_result.get("answer", "No answer found."),
                sources_used=synthesis_result.get("sources", []),
                confidence_score=synthesis_result.get("confidence", 0.0),
                sql_queries=synthesis_result.get("sql_queries", []),
                visualizations=visualizations,
                follow_up_suggestions=follow_ups,
            )

        except Exception as e:
            logger.error(
                f"Failed to process natural language query: {e}", exc_info=True
            )
            return IntelligenceResponse(
                answer=f"I encountered an error processing your query: {str(e)}",
                sources_used=[],
                confidence_score=0.0,
                sql_queries=[],
                visualizations=[],
                follow_up_suggestions=[],
            )

    async def _analyze_query_intent(self, query_text: str) -> dict[str, Any]:
        """Analyze query intent using Snowflake Cortex"""
        analysis_prompt = f"""
        Analyze this business intelligence query and determine:
        1. Primary intent (metrics, trends, comparisons, insights, etc.)
        2. Business entities mentioned (customers, employees, products, projects)
        3. Time periods referenced
        4. Data sources likely needed (CRM, calls, slack, projects, etc.)
        5. Analysis type (descriptive, diagnostic, predictive, prescriptive)

        Query: {query_text}

        Return as JSON with keys: intent, entities, time_period, sources, analysis_type
        """

        cortex_query = (
            "SELECT SNOWFLAKE.CORTEX.COMPLETE('mixtral-8x7b', %s) as analysis"
        )

        try:
            result = await self.semantic_service._execute_query(
                cortex_query, [analysis_prompt]
            )
            if result and result[0].get("ANALYSIS"):
                analysis = json.loads(result[0]["ANALYSIS"])
                logger.info(f"Query intent analysis for '{query_text}': {analysis}")
                return analysis
        except Exception as e:
            logger.error(f"Cortex query intent analysis failed: {e}")

        # Fallback to basic analysis
        return {
            "intent": "general_inquiry",
            "entities": [],
            "time_period": "recent",
            "sources": ["all"],
            "analysis_type": "descriptive",
        }

    async def _retrieve_structured_data(
        self, query_analysis: dict[str, Any], query_text: str
    ) -> dict[str, Any]:
        """Retrieve relevant structured data based on query analysis"""
        structured_results = {}
        sql_queries_executed = []

        # This is a simplified logic. A more advanced version would use a query builder.
        if "customer" in query_analysis.get("entities", []):
            customer_query = "SELECT * FROM SOPHIA_SEMANTIC.CUSTOMER_360 ORDER BY last_activity DESC LIMIT 20;"
            structured_results[
                "customers"
            ] = await self.semantic_service._execute_query(customer_query)
            sql_queries_executed.append(customer_query)

        if "employee" in query_analysis.get("entities", []):
            employee_query = "SELECT * FROM SOPHIA_SEMANTIC.EMPLOYEE_360 ORDER BY calls_participated DESC LIMIT 20;"
            structured_results[
                "employees"
            ] = await self.semantic_service._execute_query(employee_query)
            sql_queries_executed.append(employee_query)

        if query_analysis.get("intent") == "metrics":
            metrics_query = "SELECT * FROM SOPHIA_SEMANTIC.BUSINESS_METRICS ORDER BY month DESC LIMIT 12;"
            structured_results["metrics"] = await self.semantic_service._execute_query(
                metrics_query
            )
            sql_queries_executed.append(metrics_query)

        structured_results["_sql_queries"] = sql_queries_executed
        logger.info(f"Retrieved structured data for query: '{query_text}'")
        return structured_results

    async def _retrieve_unstructured_data(
        self, query_analysis: dict[str, Any], query_text: str
    ) -> dict[str, Any]:
        """Retrieve relevant unstructured data using vector search"""
        unstructured_results = {}

        search_terms = query_analysis.get("entities", []) + [
            query_analysis.get("intent", "")
        ]
        search_query = " ".join(filter(None, search_terms)) or query_text

        # Search Slack messages
        slack_search_sql = """
        SELECT message_text, channel_name, timestamp, user_id,
               VECTOR_COSINE_SIMILARITY(embedding, SNOWFLAKE.CORTEX.EMBED_TEXT_768('e5-base-v2', %s)) as similarity
        FROM SLACK_DATA.MESSAGES_VECTORIZED
        ORDER BY similarity DESC
        LIMIT 10;
        """
        unstructured_results["slack"] = await self.semantic_service._execute_query(
            slack_search_sql, [search_query]
        )

        # Search Gong transcripts
        gong_search_sql = """
        SELECT transcript_segment, call_id, call_date, participants, sentiment_score,
               VECTOR_COSINE_SIMILARITY(embedding, SNOWFLAKE.CORTEX.EMBED_TEXT_768('e5-base-v2', %s)) as similarity
        FROM GONG_DATA.CALL_TRANSCRIPTS_VECTORIZED
        ORDER BY similarity DESC
        LIMIT 10;
        """
        unstructured_results["gong"] = await self.semantic_service._execute_query(
            gong_search_sql, [search_query]
        )
        logger.info(f"Retrieved unstructured data for query: '{query_text}'")
        return unstructured_results

    async def _synthesize_response(
        self, query: str, structured: dict, unstructured: dict, context: dict
    ) -> dict[str, Any]:
        """Synthesize comprehensive response using Snowflake Cortex"""

        synthesis_context = {
            "query": query,
            "user_role": context.get("role", "user"),
            "structured_data_summary": self._summarize_structured_data(structured),
            "unstructured_insights": self._summarize_unstructured_data(unstructured),
        }

        synthesis_prompt = f"""
        You are an expert business intelligence analyst. Based on the following data, provide a comprehensive answer to the user's query.

        Query: {query}
        User Role: {context.get("role", "Executive")}

        Structured Data Summary:
        {synthesis_context["structured_data_summary"]}

        Unstructured Insights:
        {synthesis_context["unstructured_insights"]}

        Provide a comprehensive response that:
        1. Directly answers the question
        2. Includes relevant metrics and trends
        3. Provides actionable insights
        4. Cites specific data sources
        5. Suggests next steps if appropriate

        Format as JSON with keys: answer, sources, confidence, insights, recommendations
        """

        cortex_query = (
            "SELECT SNOWFLAKE.CORTEX.COMPLETE('mixtral-8x7b', %s) as synthesis"
        )

        try:
            result = await self.semantic_service._execute_query(
                cortex_query, [synthesis_prompt]
            )
            if result and result[0].get("SYNTHESIS"):
                synthesis = json.loads(result[0]["SYNTHESIS"])
                synthesis["sql_queries"] = structured.get("_sql_queries", [])
                logger.info(f"Successfully synthesized response for query: '{query}'")
                return synthesis
        except Exception as e:
            logger.error(f"Cortex response synthesis failed: {e}")

        return {
            "answer": "I found relevant information but had difficulty synthesizing a complete response.",
            "sources": list(structured.keys()) + list(unstructured.keys()),
            "confidence": 0.5,
            "sql_queries": structured.get("_sql_queries", []),
            "insights": [],
            "recommendations": [],
        }

    def _summarize_structured_data(self, data: dict) -> str:
        """Placeholder for summarizing structured data."""
        summary_parts = []
        for key, value in data.items():
            if key.startswith("_"):
                continue
            if isinstance(value, list) and len(value) > 0:
                summary_parts.append(f"- Found {len(value)} records for '{key}'.")
        return "\n".join(summary_parts) or "No structured data found."

    def _summarize_unstructured_data(self, data: dict) -> str:
        """Placeholder for summarizing unstructured data."""
        summary_parts = []
        for key, value in data.items():
            if isinstance(value, list) and len(value) > 0:
                summary_parts.append(
                    f"- Found {len(value)} relevant documents from '{key}'."
                )
        return "\n".join(summary_parts) or "No unstructured data found."

    async def _generate_visualizations(self, synthesis_result: dict) -> list:
        """Placeholder for generating visualizations."""
        logger.info("Placeholder: Generating visualizations.")
        return []

    async def _generate_follow_up_suggestions(
        self, query: str, synthesis_result: dict
    ) -> list:
        """Placeholder for generating follow-up suggestions."""
        logger.info("Placeholder: Generating follow-up suggestions.")
        return []

    async def health_check(self) -> dict[str, Any]:
        """Performs a health check on the intelligence service."""
        semantic_health = await self.semantic_service.health_check()
        vector_health = await self.vector_service.health_check()

        healthy = (
            semantic_health["status"] == "healthy"
            and vector_health["status"] == "healthy"
        )

        return {
            "status": "healthy" if healthy else "unhealthy",
            "dependencies": {
                "semantic_layer_service": semantic_health,
                "vector_indexing_service": vector_health,
            },
        }
