"""
Enhanced Snowflake Cortex Service
Deep integration with Snowflake AI Cortex functions for advanced search and analysis
"""

import json
import logging
from datetime import datetime
from typing import Any, Union

from backend.services.snowflake_cortex_service import SnowflakeCortexService

logger = logging.getLogger(__name__)


class EnhancedSnowflakeCortexService(SnowflakeCortexService):
    """Enhanced Snowflake Cortex service with advanced AI functions"""

    def __init__(self):
        super().__init__()
        self.ai_functions = {
            "filter": "AI_FILTER",
            "classify": "AI_CLASSIFY",
            "aggregate": "AI_AGG",
            "similarity": "AI_SIMILARITY",
            "complete": "AI_COMPLETE",
            "translate": "AI_TRANSLATE",
            "extract": "AI_EXTRACT",
            "summarize": "AI_SUMMARIZE",
            "sentiment": "AI_SENTIMENT",
        }
        self.model_mappings = {
            "fast": "llama3.1-8b",
            "balanced": "llama3.1-70b",
            "powerful": "llama3.1-405b",
            "code": "codellama-70b",
            "embedding": "snowflake-arctic-embed-l",
        }

    async def enhanced_search_with_cortex(
        self,
        query: str,
        search_context: dict[str, Any] = None,
        use_ai_filter: bool = True,
        use_ai_classify: bool = True,
        max_results: int = 10,
    ) -> dict[str, Any]:
        """Enhanced search using Snowflake Cortex AI functions"""

        try:
            # Build search query with AI functions
            search_sql = self._build_enhanced_search_query(
                query, search_context, use_ai_filter, use_ai_classify, max_results
            )

            # Execute search
            results = await self.execute_query(search_sql)

            # Post-process results with AI analysis
            enhanced_results = await self._enhance_search_results(results, query)

            return {
                "query": query,
                "results": enhanced_results,
                "metadata": {
                    "total_results": len(enhanced_results),
                    "ai_filter_used": use_ai_filter,
                    "ai_classify_used": use_ai_classify,
                    "search_context": search_context,
                    "timestamp": datetime.utcnow().isoformat(),
                },
            }

        except Exception as e:
            logger.error(f"Enhanced search failed: {e}")
            return {
                "query": query,
                "results": [],
                "error": str(e),
                "metadata": {
                    "total_results": 0,
                    "timestamp": datetime.utcnow().isoformat(),
                },
            }

    def _build_enhanced_search_query(
        self,
        query: str,
        context: dict[str, Any] = None,
        use_ai_filter: bool = True,
        use_ai_classify: bool = True,
        max_results: int = 10,
    ) -> str:
        """Build enhanced search query with AI functions"""

        # Base search across knowledge tables
        base_query = """
        WITH knowledge_search AS (
            SELECT
                'ai_memory' as source,
                id,
                content,
                metadata,
                timestamp,
                AI_SIMILARITY(content, %(query)s) as similarity_score
            FROM ai_memory.memory_records
            WHERE content IS NOT NULL

            UNION ALL

            SELECT
                'knowledge_base' as source,
                id::string as id,
                content,
                metadata,
                created_at as timestamp,
                AI_SIMILARITY(content, %(query)s) as similarity_score
            FROM knowledge_base.documents
            WHERE content IS NOT NULL
        )
        """

        # Add AI filtering if enabled
        if use_ai_filter:
            filter_condition = f"""
            AI_FILTER(
                content,
                'Content is relevant to: {query}'
            ) = TRUE
            """
        else:
            filter_condition = "similarity_score > 0.7"

        # Add AI classification if enabled
        if use_ai_classify:
            classify_field = """
            AI_CLASSIFY(
                content,
                ARRAY_CONSTRUCT(
                    'technical_documentation',
                    'business_analysis',
                    'meeting_notes',
                    'project_planning',
                    'customer_feedback',
                    'competitive_intelligence'
                )
            ) as content_category,
            """
        else:
            classify_field = "'general' as content_category,"

        # Build final query
        final_query = f"""
        SELECT
            source,
            id,
            content,
            metadata,
            timestamp,
            similarity_score,
            {classify_field}
            AI_SENTIMENT(content) as sentiment_score,
            AI_EXTRACT(content, 'key_topics') as key_topics,
            AI_SUMMARIZE(content, 100) as summary
        FROM knowledge_search
        WHERE {filter_condition}
        ORDER BY similarity_score DESC
        LIMIT {max_results}
        """

        return final_query

    async def _enhance_search_results(
        self, results: list[dict[str, Any]], query: str
    ) -> list[dict[str, Any]]:
        """Enhance search results with additional AI analysis"""

        if not results:
            return []

        enhanced_results = []

        for result in results:
            try:
                # Enhanced result structure
                enhanced_result = {
                    "id": result.get("id"),
                    "source": result.get("source"),
                    "content": result.get("content", ""),
                    "summary": result.get("summary", ""),
                    "metadata": result.get("metadata", {}),
                    "timestamp": result.get("timestamp"),
                    "relevance": {
                        "similarity_score": float(result.get("similarity_score", 0)),
                        "content_category": result.get("content_category", "general"),
                        "sentiment_score": float(result.get("sentiment_score", 0)),
                        "key_topics": result.get("key_topics", []),
                    },
                    "ai_analysis": await self._generate_ai_analysis(result, query),
                }

                enhanced_results.append(enhanced_result)

            except Exception as e:
                logger.warning(f"Failed to enhance result {result.get('id')}: {e}")
                # Add basic result if enhancement fails
                enhanced_results.append(
                    {
                        "id": result.get("id"),
                        "source": result.get("source"),
                        "content": result.get("content", ""),
                        "error": str(e),
                    }
                )

        return enhanced_results

    async def _generate_ai_analysis(
        self, result: dict[str, Any], query: str
    ) -> dict[str, Any]:
        """Generate AI analysis for a search result"""

        content = result.get("content", "")
        if not content:
            return {}

        try:
            # Generate contextual analysis
            analysis_query = f"""
            SELECT
                AI_COMPLETE(
                    'Analyze this content in relation to the query "{query}".
                    Provide key insights, relevance explanation, and actionable points.',
                    %(content)s
                ) as analysis,
                AI_EXTRACT(
                    %(content)s,
                    'action_items'
                ) as action_items,
                AI_CLASSIFY(
                    %(content)s,
                    ARRAY_CONSTRUCT('high_priority', 'medium_priority', 'low_priority')
                ) as priority_level
            """

            analysis_results = await self.execute_query(
                analysis_query, {"content": content}
            )

            if analysis_results:
                return {
                    "analysis": analysis_results[0].get("analysis", ""),
                    "action_items": analysis_results[0].get("action_items", []),
                    "priority_level": analysis_results[0].get(
                        "priority_level", "medium_priority"
                    ),
                }
            else:
                return {}

        except Exception as e:
            logger.warning(f"AI analysis failed: {e}")
            return {}

    async def intelligent_aggregation(
        self,
        data_source: str,
        aggregation_type: str,
        filters: dict[str, Any] = None,
        ai_model: str = "balanced",
    ) -> dict[str, Any]:
        """Intelligent aggregation using AI_AGG function"""

        try:
            # Map aggregation types to AI prompts
            aggregation_prompts = {
                "sentiment_analysis": "Analyze the sentiment trends and provide insights",
                "topic_clustering": "Identify main topics and cluster related content",
                "trend_analysis": "Identify trends and patterns over time",
                "priority_ranking": "Rank items by priority and importance",
                "risk_assessment": "Assess risks and provide mitigation strategies",
                "opportunity_identification": "Identify opportunities and recommendations",
            }

            prompt = aggregation_prompts.get(
                aggregation_type, "Analyze and summarize the data"
            )
            model = self.model_mappings.get(ai_model, "llama3.1-70b")

            # Build aggregation query
            aggregation_query = f"""
            WITH data_subset AS (
                SELECT * FROM {data_source}
                WHERE 1=1
                {self._build_filter_conditions(filters) if filters else ""}
            )
            SELECT
                AI_AGG(
                    content,
                    '{prompt}',
                    '{model}'
                ) as aggregated_insights,
                COUNT(*) as total_records,
                MIN(timestamp) as earliest_record,
                MAX(timestamp) as latest_record
            FROM data_subset
            """

            results = await self.execute_query(aggregation_query)

            if results:
                return {
                    "aggregation_type": aggregation_type,
                    "insights": results[0].get("aggregated_insights", ""),
                    "metadata": {
                        "total_records": results[0].get("total_records", 0),
                        "time_range": {
                            "start": results[0].get("earliest_record"),
                            "end": results[0].get("latest_record"),
                        },
                        "model_used": model,
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                }
            else:
                return {
                    "aggregation_type": aggregation_type,
                    "insights": "",
                    "error": "No results returned",
                }

        except Exception as e:
            logger.error(f"Intelligent aggregation failed: {e}")
            return {
                "aggregation_type": aggregation_type,
                "insights": "",
                "error": str(e),
            }

    def _build_filter_conditions(self, filters: dict[str, Any]) -> str:
        """Build SQL filter conditions from filter dictionary"""

        conditions = []

        for key, value in filters.items():
            if isinstance(value, str):
                conditions.append(f"AND {key} = '{value}'")
            elif isinstance(value, (int, float)):
                conditions.append(f"AND {key} = {value}")
            elif isinstance(value, list):
                value_str = "', '".join(str(v) for v in value)
                conditions.append(f"AND {key} IN ('{value_str}')")
            elif isinstance(value, dict):
                if "start" in value and "end" in value:
                    conditions.append(
                        f"AND {key} BETWEEN '{value['start']}' AND '{value['end']}'"
                    )

        return " ".join(conditions)

    async def semantic_similarity_search(
        self,
        query: str,
        data_sources: list[str],
        similarity_threshold: float = 0.7,
        max_results: int = 50,
        include_metadata: bool = True,
    ) -> dict[str, Any]:
        """Advanced semantic similarity search across multiple data sources"""

        try:
            # Build unified similarity search
            union_queries = []

            for source in data_sources:
                source_query = f"""
                SELECT
                    '{source}' as source,
                    id,
                    content,
                    {'metadata,' if include_metadata else ''}
                    timestamp,
                    AI_SIMILARITY(content, %(query)s) as similarity_score
                FROM {source}
                WHERE content IS NOT NULL
                """
                union_queries.append(source_query)

            # Combine all sources
            combined_query = f"""
            WITH combined_search AS (
                {' UNION ALL '.join(union_queries)}
            )
            SELECT
                source,
                id,
                content,
                {'metadata,' if include_metadata else ''}
                timestamp,
                similarity_score,
                AI_CLASSIFY(
                    content,
                    ARRAY_CONSTRUCT(
                        'highly_relevant',
                        'moderately_relevant',
                        'partially_relevant',
                        'not_relevant'
                    )
                ) as relevance_category
            FROM combined_search
            WHERE similarity_score >= {similarity_threshold}
            ORDER BY similarity_score DESC
            LIMIT {max_results}
            """

            results = await self.execute_query(combined_query, {"query": query})

            # Group results by source
            grouped_results = {}
            for result in results:
                source = result["source"]
                if source not in grouped_results:
                    grouped_results[source] = []
                grouped_results[source].append(result)

            return {
                "query": query,
                "results": results,
                "grouped_results": grouped_results,
                "metadata": {
                    "total_results": len(results),
                    "sources_searched": len(data_sources),
                    "similarity_threshold": similarity_threshold,
                    "max_results": max_results,
                    "timestamp": datetime.utcnow().isoformat(),
                },
            }

        except Exception as e:
            logger.error(f"Semantic similarity search failed: {e}")
            return {"query": query, "results": [], "error": str(e)}

    async def ai_powered_classification(
        self,
        content: Union[str, list[str]],
        categories: list[str],
        model: str = "balanced",
        confidence_threshold: float = 0.8,
    ) -> dict[str, Any]:
        """AI-powered content classification with confidence scoring"""

        try:
            model_name = self.model_mappings.get(model, "llama3.1-70b")

            if isinstance(content, str):
                content_list = [content]
            else:
                content_list = content

            # Build classification query
            categories_array = "', '".join(categories)

            classification_query = f"""
            WITH content_data AS (
                SELECT
                    ROW_NUMBER() OVER (ORDER BY 1) as idx,
                    value as content_text
                FROM TABLE(FLATTEN(ARRAY_CONSTRUCT(
                    {', '.join(f"'{c}'" for c in content_list)}
                )))
            )
            SELECT
                idx,
                content_text,
                AI_CLASSIFY(
                    content_text,
                    ARRAY_CONSTRUCT('{categories_array}'),
                    '{model_name}'
                ) as predicted_category,
                AI_COMPLETE(
                    'Provide a confidence score (0-1) for this classification and explain why.',
                    content_text || ' Category: ' || AI_CLASSIFY(content_text, ARRAY_CONSTRUCT('{categories_array}'))
                ) as confidence_analysis
            FROM content_data
            """

            results = await self.execute_query(classification_query)

            # Process results
            classifications = []
            for result in results:
                classifications.append(
                    {
                        "content": result["content_text"],
                        "predicted_category": result["predicted_category"],
                        "confidence_analysis": result["confidence_analysis"],
                        "meets_threshold": True,  # Would need to parse confidence from analysis
                    }
                )

            return {
                "classifications": classifications,
                "categories": categories,
                "model_used": model_name,
                "confidence_threshold": confidence_threshold,
                "metadata": {
                    "total_items": len(content_list),
                    "timestamp": datetime.utcnow().isoformat(),
                },
            }

        except Exception as e:
            logger.error(f"AI classification failed: {e}")
            return {"classifications": [], "error": str(e)}

    async def contextual_ai_completion(
        self,
        prompt: str,
        context_data: dict[str, Any] = None,
        model: str = "balanced",
        max_tokens: int = 1000,
    ) -> dict[str, Any]:
        """Contextual AI completion with business data integration"""

        try:
            model_name = self.model_mappings.get(model, "llama3.1-70b")

            # Build context if provided
            context_string = ""
            if context_data:
                context_string = f"Context: {json.dumps(context_data, indent=2)}\n\n"

            # Build completion query
            completion_query = f"""
            SELECT
                AI_COMPLETE(
                    %(full_prompt)s,
                    '{model_name}'
                ) as completion,
                AI_SENTIMENT(%(full_prompt)s) as prompt_sentiment,
                AI_EXTRACT(%(full_prompt)s, 'key_concepts') as key_concepts
            """

            full_prompt = f"{context_string}{prompt}"

            results = await self.execute_query(
                completion_query, {"full_prompt": full_prompt}
            )

            if results:
                return {
                    "prompt": prompt,
                    "completion": results[0].get("completion", ""),
                    "analysis": {
                        "prompt_sentiment": results[0].get("prompt_sentiment", 0),
                        "key_concepts": results[0].get("key_concepts", []),
                        "context_used": context_data is not None,
                    },
                    "metadata": {
                        "model_used": model_name,
                        "max_tokens": max_tokens,
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                }
            else:
                return {
                    "prompt": prompt,
                    "completion": "",
                    "error": "No completion generated",
                }

        except Exception as e:
            logger.error(f"Contextual AI completion failed: {e}")
            return {"prompt": prompt, "completion": "", "error": str(e)}

    async def hybrid_search_fusion(
        self,
        query: str,
        internal_weight: float = 0.6,
        external_weight: float = 0.4,
        fusion_method: str = "weighted_average",
    ) -> dict[str, Any]:
        """Hybrid search fusion combining internal and external results"""

        try:
            # Internal search using Snowflake Cortex
            internal_results = await self.enhanced_search_with_cortex(
                query=query, max_results=20
            )

            # External search would be integrated here
            # For now, we'll simulate external results
            external_results = {
                "results": [],
                "metadata": {"source": "external", "total_results": 0},
            }

            # Fusion algorithm
            if fusion_method == "weighted_average":
                fused_results = self._weighted_average_fusion(
                    internal_results["results"],
                    external_results["results"],
                    internal_weight,
                    external_weight,
                )
            elif fusion_method == "rank_fusion":
                fused_results = self._rank_fusion(
                    internal_results["results"], external_results["results"]
                )
            else:
                fused_results = internal_results["results"]

            return {
                "query": query,
                "fused_results": fused_results,
                "metadata": {
                    "fusion_method": fusion_method,
                    "internal_weight": internal_weight,
                    "external_weight": external_weight,
                    "internal_results_count": len(internal_results["results"]),
                    "external_results_count": len(external_results["results"]),
                    "fused_results_count": len(fused_results),
                    "timestamp": datetime.utcnow().isoformat(),
                },
            }

        except Exception as e:
            logger.error(f"Hybrid search fusion failed: {e}")
            return {"query": query, "fused_results": [], "error": str(e)}

    def _weighted_average_fusion(
        self,
        internal_results: list[dict[str, Any]],
        external_results: list[dict[str, Any]],
        internal_weight: float,
        external_weight: float,
    ) -> list[dict[str, Any]]:
        """Weighted average fusion of search results"""

        # Create combined results with fusion scores
        combined_results = []

        # Add internal results
        for result in internal_results:
            similarity_score = result.get("relevance", {}).get("similarity_score", 0)
            fusion_score = similarity_score * internal_weight

            combined_results.append(
                {**result, "fusion_score": fusion_score, "result_source": "internal"}
            )

        # Add external results (when available)
        for result in external_results:
            similarity_score = result.get("score", 0)
            fusion_score = similarity_score * external_weight

            combined_results.append(
                {**result, "fusion_score": fusion_score, "result_source": "external"}
            )

        # Sort by fusion score
        combined_results.sort(key=lambda x: x.get("fusion_score", 0), reverse=True)

        return combined_results

    def _rank_fusion(
        self,
        internal_results: list[dict[str, Any]],
        external_results: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Rank-based fusion of search results"""

        # Simple rank fusion - combine ranks from both sources
        combined_results = []

        # Add internal results with ranks
        for i, result in enumerate(internal_results):
            combined_results.append(
                {
                    **result,
                    "internal_rank": i + 1,
                    "external_rank": float("inf"),
                    "result_source": "internal",
                }
            )

        # Add external results with ranks
        for i, result in enumerate(external_results):
            combined_results.append(
                {
                    **result,
                    "internal_rank": float("inf"),
                    "external_rank": i + 1,
                    "result_source": "external",
                }
            )

        # Calculate combined rank (harmonic mean)
        for result in combined_results:
            internal_rank = result.get("internal_rank", float("inf"))
            external_rank = result.get("external_rank", float("inf"))

            if internal_rank == float("inf"):
                result["fusion_score"] = 1.0 / external_rank
            elif external_rank == float("inf"):
                result["fusion_score"] = 1.0 / internal_rank
            else:
                result["fusion_score"] = 2.0 / (internal_rank + external_rank)

        # Sort by fusion score
        combined_results.sort(key=lambda x: x.get("fusion_score", 0), reverse=True)

        return combined_results

    async def get_cortex_health_status(self) -> dict[str, Any]:
        """Get health status of Snowflake Cortex functions"""

        try:
            # Test each AI function
            test_queries = {
                "AI_SIMILARITY": "SELECT AI_SIMILARITY('test', 'test') as result",
                "AI_CLASSIFY": "SELECT AI_CLASSIFY('test content', ARRAY_CONSTRUCT('positive', 'negative')) as result",
                "AI_COMPLETE": "SELECT AI_COMPLETE('Complete this: Hello', 'llama3.1-8b') as result",
                "AI_SENTIMENT": "SELECT AI_SENTIMENT('This is great!') as result",
                "AI_EXTRACT": "SELECT AI_EXTRACT('Key points: 1. Important', 'key_points') as result",
                "AI_SUMMARIZE": "SELECT AI_SUMMARIZE('This is a long text that needs summarization.', 50) as result",
            }

            function_status = {}

            for function_name, test_query in test_queries.items():
                try:
                    await self.execute_query(test_query)
                    function_status[function_name] = "healthy"
                except Exception as e:
                    function_status[function_name] = f"error: {e!s}"

            # Calculate overall health
            healthy_functions = sum(
                1 for status in function_status.values() if status == "healthy"
            )
            total_functions = len(function_status)
            health_percentage = (healthy_functions / total_functions) * 100

            return {
                "overall_health": "healthy" if health_percentage >= 80 else "degraded",
                "health_percentage": health_percentage,
                "function_status": function_status,
                "available_models": list(self.model_mappings.keys()),
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Cortex health check failed: {e}")
            return {
                "overall_health": "unhealthy",
                "health_percentage": 0,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }
