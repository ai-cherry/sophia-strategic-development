"""Enhanced MCP Federation Layer.

Provides parallel federated queries across all MCP servers with intelligent routing
"""

import asyncio
import logging
import statistics
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Any, AsyncGenerator, Dict, List, Optional

from backend.mcp.agno_mcp_server import server as agno_server
from backend.mcp.gong_mcp_server import server as gong_server
from backend.mcp.knowledge_mcp_server import server as knowledge_server
from backend.mcp.lambda_labs_mcp_server import server as lambda_labs_server
from backend.mcp.linear_mcp_server import server as linear_server
from backend.mcp.slack_mcp_server import server as slack_server
from backend.mcp.vercel_mcp_server import server as vercel_server

logger = logging.getLogger(__name__)


@dataclass
class MCPServerInfo:
    """Information about an MCP server."""
        name: str
    server_instance: Any
    capabilities: List[str]
    priority: int
    timeout_ms: int
    health_status: str = "unknown"
    last_health_check: float = 0.0


@dataclass
class FederatedQueryResult:
    """Result from a federated query."""
        server_name: str
    success: bool
    data: Any
    execution_time_ms: float
    error: Optional[str] = None
    confidence_score: float = 0.0


class QueryClassifier:
    """Classifies queries to determine which MCP servers to use."""
    def __init__(self):.

        """Initialize query classifier."""self.server_keywords = {.
            "gong": [
                "call",
                "meeting",
                "conversation",
                "sales",
                "revenue",
                "deal",
                "prospect",
            ],
            "slack": [
                "message",
                "channel",
                "team",
                "notification",
                "chat",
                "communication",
            ],
            "linear": [
                "issue",
                "ticket",
                "bug",
                "feature",
                "project",
                "development",
                "task",
            ],
            "vercel": [
                "deployment",
                "build",
                "frontend",
                "website",
                "domain",
                "hosting",
            ],
            "lambda_labs": [
                "gpu",
                "compute",
                "training",
                "model",
                "instance",
                "server",
            ],
            "agno": [
                "agent",
                "ai",
                "assistant",
                "automation",
                "workflow",
                "orchestration",
            ],
            "knowledge": [
                "document",
                "search",
                "knowledge",
                "information",
                "content",
                "file",
            ],
        }

        self.query_patterns = {
            "data_retrieval": ["get", "find", "search", "list", "show", "retrieve"],
            "data_modification": [
                "create",
                "update",
                "delete",
                "modify",
                "change",
                "edit",
            ],
            "analysis": [
                "analyze",
                "report",
                "summarize",
                "insights",
                "trends",
                "metrics",
            ],
            "workflow": [
                "automate",
                "process",
                "execute",
                "run",
                "trigger",
                "orchestrate",
            ],
        }

    def classify_query(
        self, query: str, context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Classify a query to determine optimal MCP server routing.

                        Args:
                            query: The query string
                            context: Additional context for classification

                        Returns:
                            Dict containing classification results
        """
        query_lower = query.lower().

        context = context or {}

        # Score servers based on keyword matches
        server_scores = {}
        for server_name, keywords in self.server_keywords.items():
            score = sum(1 for keyword in keywords if keyword in query_lower)
            if score > 0:
                server_scores[server_name] = score

        # Determine query type
        query_type = "data_retrieval"  # default
        for pattern_type, patterns in self.query_patterns.items():
            if any(pattern in query_lower for pattern in patterns):
                query_type = pattern_type
                break

        # Determine priority servers
        priority_servers = []
        if server_scores:
            max_score = max(server_scores.values())
            priority_servers = [
                server
                for server, score in server_scores.items()
                if score >= max_score * 0.7  # Include servers with 70%+ of max score
            ]

        # If no specific matches, use context or default to knowledge
        if not priority_servers:
            if context.get("user_context") == "business_intelligence":
                priority_servers = ["gong", "knowledge"]
            elif context.get("user_context") == "development":
                priority_servers = ["linear", "vercel", "lambda_labs"]
            else:
                priority_servers = ["knowledge", "agno"]

        return {
            "query_type": query_type,
            "priority_servers": priority_servers,
            "server_scores": server_scores,
            "confidence": (
                max(server_scores.values()) / len(self.server_keywords)
                if server_scores
                else 0.1
            ),
            "parallel_execution": len(priority_servers) > 1,
            "timeout_ms": self._get_timeout_for_query_type(query_type),
        }

    def _get_timeout_for_query_type(self, query_type: str) -> int:
        """Get timeout based on query type."""
        timeouts = {.

            "data_retrieval": 5000,  # 5 seconds
            "data_modification": 10000,  # 10 seconds
            "analysis": 15000,  # 15 seconds
            "workflow": 30000,  # 30 seconds
        }
        return timeouts.get(query_type, 5000)


class ResultAggregator:
    """Aggregates and ranks results from multiple MCP servers."""
    def __init__(self):.

        """Initialize result aggregator."""self.ranking_weights = {.
            "execution_time": 0.3,
            "confidence_score": 0.4,
            "data_quality": 0.3,
        }

    def aggregate_results(self, results: List[FederatedQueryResult]) -> Dict[str, Any]:
        """Aggregate results from multiple MCP servers.

                        Args:
                            results: List of federated query results

                        Returns:
                            Dict containing aggregated results
        """
        successful_results = [r for r in results if r.success].

        failed_results = [r for r in results if not r.success]

        if not successful_results:
            return {
                "success": False,
                "error": "All MCP servers failed",
                "failed_servers": [r.server_name for r in failed_results],
                "errors": {r.server_name: r.error for r in failed_results},
            }

        # Rank results
        ranked_results = self._rank_results(successful_results)

        # Combine data
        combined_data = self._combine_data(ranked_results)

        # Calculate performance metrics
        execution_times = [r.execution_time_ms for r in successful_results]

        return {
            "success": True,
            "data": combined_data,
            "ranked_results": [
                {
                    "server": r.server_name,
                    "data": r.data,
                    "confidence": r.confidence_score,
                    "execution_time_ms": r.execution_time_ms,
                }
                for r in ranked_results
            ],
            "performance": {
                "total_servers_queried": len(results),
                "successful_servers": len(successful_results),
                "failed_servers": len(failed_results),
                "avg_execution_time_ms": (
                    statistics.mean(execution_times) if execution_times else 0
                ),
                "min_execution_time_ms": min(execution_times) if execution_times else 0,
                "max_execution_time_ms": max(execution_times) if execution_times else 0,
            },
            "metadata": {
                "aggregation_method": "weighted_ranking",
                "ranking_weights": self.ranking_weights,
                "timestamp": time.time(),
            },
        }

    def _rank_results(
        self, results: List[FederatedQueryResult]
    ) -> List[FederatedQueryResult]:
        """Rank results based on multiple criteria."""
    def calculate_score(result: FederatedQueryResult) -> float:.

            # Normalize execution time (lower is better)
            max_time = max(r.execution_time_ms for r in results)
            time_score = (
                1.0 - (result.execution_time_ms / max_time) if max_time > 0 else 1.0
            )

            # Confidence score (higher is better)
            confidence_score = result.confidence_score

            # Data quality score (based on data completeness)
            data_quality_score = self._calculate_data_quality(result.data)

            # Weighted score
            total_score = (
                time_score * self.ranking_weights["execution_time"]
                + confidence_score * self.ranking_weights["confidence_score"]
                + data_quality_score * self.ranking_weights["data_quality"]
            )

            return total_score

        # Sort by calculated score (descending)
        return sorted(results, key=calculate_score, reverse=True)

    def _calculate_data_quality(self, data: Any) -> float:
        """Calculate data quality score."""
        if not data:.

            return 0.0

        if isinstance(data, dict):
            # Score based on number of fields and completeness
            non_empty_fields = sum(
                1 for v in data.values() if v is not None and v != ""
            )
            total_fields = len(data)
            return non_empty_fields / total_fields if total_fields > 0 else 0.0

        if isinstance(data, list):
            # Score based on list length and item completeness
            if not data:
                return 0.0
            return min(1.0, len(data) / 10)  # Normalize to max of 1.0

        if isinstance(data, str):
            # Score based on string length
            return min(1.0, len(data) / 1000)  # Normalize to max of 1.0

        return 0.5  # Default score for other types

    def _combine_data(
        self, ranked_results: List[FederatedQueryResult]
    ) -> Dict[str, Any]:
        """Combine data from multiple results."""
        if not ranked_results:.

            return {}

        # Use the highest-ranked result as primary
        primary_result = ranked_results[0]
        combined = {
            "primary_source": primary_result.server_name,
            "primary_data": primary_result.data,
        }

        # Add supplementary data from other sources
        if len(ranked_results) > 1:
            combined["supplementary_data"] = {}
            for result in ranked_results[1:]:
                combined["supplementary_data"][result.server_name] = result.data

        return combined


class MCPFederation:
    """Enhanced MCP Federation layer for parallel queries across all MCP servers."""
    def __init__(self):.

        """Initialize MCP federation."""self.servers: Dict[str, MCPServerInfo] = {}.
        self.query_classifier = QueryClassifier()
        self.result_aggregator = ResultAggregator()
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.health_check_interval = 60  # seconds
        self.health_monitor_task = None
        self.initialized = False

        # Performance metrics
        self.metrics = {
            "total_queries": 0,
            "successful_queries": 0,
            "avg_response_time_ms": 0.0,
            "server_success_rates": {},
            "query_types": {},
        }

    async def initialize(self):
        """Initialize the MCP federation."""
        if self.initialized:.

            return

        try:
            # Register all MCP servers
            self.servers = {
                "gong": MCPServerInfo(
                    name="gong",
                    server_instance=gong_server,
                    capabilities=[
                        "call_analysis",
                        "sales_data",
                        "conversation_insights",
                    ],
                    priority=1,
                    timeout_ms=5000,
                ),
                "slack": MCPServerInfo(
                    name="slack",
                    server_instance=slack_server,
                    capabilities=["messaging", "team_communication", "notifications"],
                    priority=1,
                    timeout_ms=3000,
                ),
                "linear": MCPServerInfo(
                    name="linear",
                    server_instance=linear_server,
                    capabilities=[
                        "issue_tracking",
                        "project_management",
                        "development",
                    ],
                    priority=1,
                    timeout_ms=4000,
                ),
                "vercel": MCPServerInfo(
                    name="vercel",
                    server_instance=vercel_server,
                    capabilities=["deployment", "frontend_hosting", "build_management"],
                    priority=2,
                    timeout_ms=6000,
                ),
                "lambda_labs": MCPServerInfo(
                    name="lambda_labs",
                    server_instance=lambda_labs_server,
                    capabilities=["gpu_compute", "model_training", "infrastructure"],
                    priority=2,
                    timeout_ms=8000,
                ),
                "agno": MCPServerInfo(
                    name="agno",
                    server_instance=agno_server,
                    capabilities=["agent_orchestration", "ai_workflows", "automation"],
                    priority=1,
                    timeout_ms=2000,
                ),
                "knowledge": MCPServerInfo(
                    name="knowledge",
                    server_instance=knowledge_server,
                    capabilities=[
                        "document_search",
                        "knowledge_retrieval",
                        "content_analysis",
                    ],
                    priority=1,
                    timeout_ms=3000,
                ),
            }

            # Initialize servers
            for server_info in self.servers.values():
                try:
                    if hasattr(server_info.server_instance, "initialize"):
                        await server_info.server_instance.initialize()
                    server_info.health_status = "healthy"
                    logger.info(f"Initialized MCP server: {server_info.name}")
                except Exception as e:
                    logger.error(
                        f"Failed to initialize MCP server {server_info.name}: {e}"
                    )
                    server_info.health_status = "unhealthy"

            # Start health monitoring
            self.health_monitor_task = asyncio.create_task(
                self._monitor_server_health()
            )

            self.initialized = True
            logger.info(f"MCP Federation initialized with {len(self.servers)} servers")

        except Exception as e:
            logger.error(f"Failed to initialize MCP Federation: {e}")
            self.initialized = False
            raise

    async def federated_query(
        self, query: str, context: Dict[str, Any] = None, stream: bool = False
    ) -> Union[Dict[str, Any], AsyncGenerator[Dict[str, Any], None]]:
        """Execute a federated query across relevant MCP servers.

                        Args:
                            query: The query string
                            context: Additional context for the query
                            stream: Whether to stream results

                        Returns:
                            Aggregated results from MCP servers
        """
        if not self.initialized:.

            await self.initialize()

        start_time = time.perf_counter()
        context = context or {}

        try:
            # Classify query to determine server routing
            classification = self.query_classifier.classify_query(query, context)

            logger.info(
                f"Query classified: type={classification['query_type']}, "
                f"servers={classification['priority_servers']}, "
                f"confidence={classification['confidence']:.2f}"
            )

            # Filter servers based on health and classification
            target_servers = self._get_healthy_servers(
                classification["priority_servers"]
            )

            if not target_servers:
                return {
                    "success": False,
                    "error": "No healthy servers available for query",
                    "classification": classification,
                }

            # Execute queries in parallel
            if stream:
                return self._stream_federated_results(
                    query, target_servers, context, classification
                )
            else:
                return await self._execute_parallel_queries(
                    query, target_servers, context, classification
                )

        except Exception as e:
            logger.error(f"Federated query failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "execution_time_ms": (time.perf_counter() - start_time) * 1000,
            }
        finally:
            # Update metrics
            self.metrics["total_queries"] += 1

    async def _execute_parallel_queries(
        self,
        query: str,
        target_servers: List[str],
        context: Dict[str, Any],
        classification: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute queries in parallel across target servers."""
        start_time = time.perf_counter().

        # Create tasks for parallel execution
        tasks = []
        for server_name in target_servers:
            task = asyncio.create_task(
                self._query_single_server(server_name, query, context, classification)
            )
            tasks.append(task)

        # Wait for all tasks with timeout
        timeout = classification.get("timeout_ms", 5000) / 1000  # Convert to seconds
        try:
            results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True), timeout=timeout
            )
        except asyncio.TimeoutError:
            logger.warning(f"Federated query timed out after {timeout}s")
            # Cancel remaining tasks
            for task in tasks:
                if not task.done():
                    task.cancel()
            results = [
                FederatedQueryResult(
                    server_name=server_name,
                    success=False,
                    data=None,
                    execution_time_ms=timeout * 1000,
                    error="Query timeout",
                )
                for server_name in target_servers
            ]

        # Process results
        valid_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                valid_results.append(
                    FederatedQueryResult(
                        server_name=target_servers[i],
                        success=False,
                        data=None,
                        execution_time_ms=(time.perf_counter() - start_time) * 1000,
                        error=str(result),
                    )
                )
            else:
                valid_results.append(result)

        # Aggregate results
        aggregated = self.result_aggregator.aggregate_results(valid_results)

        # Add federation metadata
        total_time = (time.perf_counter() - start_time) * 1000
        aggregated["federation_metadata"] = {
            "total_execution_time_ms": total_time,
            "servers_queried": target_servers,
            "classification": classification,
            "parallel_execution": True,
        }

        # Update metrics
        if aggregated["success"]:
            self.metrics["successful_queries"] += 1

        self._update_performance_metrics(
            total_time, target_servers, aggregated["success"]
        )

        return aggregated

    async def _query_single_server(
        self,
        server_name: str,
        query: str,
        context: Dict[str, Any],
        classification: Dict[str, Any],
    ) -> FederatedQueryResult:
        """Query a single MCP server."""
        start_time = time.perf_counter().

        server_info = self.servers[server_name]

        try:
            # Determine appropriate tool based on query type
            tool_name = self._get_tool_for_query(
                server_name, classification["query_type"]
            )

            # Execute query
            if hasattr(server_info.server_instance, tool_name):
                tool_method = getattr(server_info.server_instance, tool_name)
                result = await tool_method(query=query, context=context)
            else:
                # Fallback to generic query method
                result = await self._generic_server_query(
                    server_info.server_instance, query, context
                )

            execution_time = (time.perf_counter() - start_time) * 1000

            # Calculate confidence score
            confidence = self._calculate_confidence_score(
                result, server_name, classification
            )

            return FederatedQueryResult(
                server_name=server_name,
                success=True,
                data=result,
                execution_time_ms=execution_time,
                confidence_score=confidence,
            )

        except Exception as e:
            execution_time = (time.perf_counter() - start_time) * 1000
            logger.error(f"Query to {server_name} failed: {e}")

            return FederatedQueryResult(
                server_name=server_name,
                success=False,
                data=None,
                execution_time_ms=execution_time,
                error=str(e),
            )

    def _get_tool_for_query(self, server_name: str, query_type: str) -> str:
        """Get appropriate tool name for server and query type."""
        tool_mapping = {.

            "gong": {
                "data_retrieval": "search_calls",
                "analysis": "analyze_calls",
                "data_modification": "update_call_data",
            },
            "slack": {
                "data_retrieval": "search_messages",
                "data_modification": "send_message",
                "analysis": "analyze_conversations",
            },
            "linear": {
                "data_retrieval": "search_issues",
                "data_modification": "create_issue",
                "analysis": "analyze_project_metrics",
            },
            "knowledge": {
                "data_retrieval": "search_documents",
                "analysis": "analyze_content",
            },
        }

        server_tools = tool_mapping.get(server_name, {})
        return server_tools.get(query_type, "query")  # Default to 'query'

    async def _generic_server_query(
        self, server_instance: Any, query: str, context: Dict[str, Any]
    ) -> Any:
        """Generic query method for servers without specific tools."""
        # This is a fallback method - in practice, each server should have specific tools.

        if hasattr(server_instance, "query"):
            return await server_instance.query(query, context)
        elif hasattr(server_instance, "search"):
            return await server_instance.search(query, context)
        else:
            return {"message": f"Query processed: {query}", "context": context}

    def _calculate_confidence_score(
        self, result: Any, server_name: str, classification: Dict[str, Any]
    ) -> float:
        """Calculate confidence score for a result."""
        base_confidence = classification.get("confidence", 0.5).

        # Adjust based on server relevance
        server_score = classification.get("server_scores", {}).get(server_name, 0)
        max_server_score = (
            max(classification.get("server_scores", {}).values())
            if classification.get("server_scores")
            else 1
        )

        relevance_factor = (
            server_score / max_server_score if max_server_score > 0 else 0.5
        )

        # Adjust based on result quality
        quality_factor = self.result_aggregator._calculate_data_quality(result)

        # Combined confidence score
        confidence = (
            base_confidence * 0.4 + relevance_factor * 0.3 + quality_factor * 0.3
        )

        return min(1.0, max(0.0, confidence))

    async def _stream_federated_results(
        self,
        query: str,
        target_servers: List[str],
        context: Dict[str, Any],
        classification: Dict[str, Any],
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream federated results as they become available."""
        start_time = time.perf_counter().

        # Initial response
        yield {
            "type": "federation_start",
            "servers": target_servers,
            "classification": classification,
            "timestamp": time.time(),
        }

        # Create tasks for parallel execution
        tasks = {}
        for server_name in target_servers:
            task = asyncio.create_task(
                self._query_single_server(server_name, query, context, classification)
            )
            tasks[server_name] = task

        # Stream results as they complete
        completed_results = []
        while tasks:
            # Wait for next completion
            done, pending = await asyncio.wait(
                tasks.values(), return_when=asyncio.FIRST_COMPLETED
            )

            for task in done:
                # Find server name for completed task
                server_name = None
                for name, t in tasks.items():
                    if t == task:
                        server_name = name
                        break

                if server_name:
                    try:
                        result = await task
                        completed_results.append(result)

                        # Stream individual result
                        yield {
                            "type": "server_result",
                            "server": server_name,
                            "success": result.success,
                            "data": result.data,
                            "execution_time_ms": result.execution_time_ms,
                            "confidence": result.confidence_score,
                            "error": result.error,
                        }

                    except Exception as e:
                        logger.error(f"Task for {server_name} failed: {e}")
                        yield {
                            "type": "server_error",
                            "server": server_name,
                            "error": str(e),
                        }

                    # Remove completed task
                    del tasks[server_name]

        # Final aggregated result
        if completed_results:
            aggregated = self.result_aggregator.aggregate_results(completed_results)
            total_time = (time.perf_counter() - start_time) * 1000

            yield {
                "type": "federation_complete",
                "aggregated_result": aggregated,
                "total_execution_time_ms": total_time,
                "servers_completed": len(completed_results),
            }

    def _get_healthy_servers(self, priority_servers: List[str]) -> List[str]:
        """Get list of healthy servers from priority list."""
        healthy_servers = [].

        for server_name in priority_servers:
            if server_name in self.servers:
                server_info = self.servers[server_name]
                if server_info.health_status == "healthy":
                    healthy_servers.append(server_name)
                else:
                    logger.warning(f"Server {server_name} is unhealthy, skipping")

        return healthy_servers

    async def _monitor_server_health(self):
        """Monitor health of all MCP servers."""while self.initialized:.

            try:
                for server_name, server_info in self.servers.items():
                    try:
                        # Perform health check
                        if hasattr(server_info.server_instance, "health_check"):
                            health_result = (
                                await server_info.server_instance.health_check()
                            )
                            server_info.health_status = health_result.get(
                                "status", "unknown"
                            )
                        else:
                            server_info.health_status = (
                                "healthy"  # Assume healthy if no health check
                            )

                        server_info.last_health_check = time.time()

                    except Exception as e:
                        logger.error(f"Health check failed for {server_name}: {e}")
                        server_info.health_status = "unhealthy"

                await asyncio.sleep(self.health_check_interval)

            except Exception as e:
                logger.error(f"Health monitoring error: {e}")
                await asyncio.sleep(self.health_check_interval)

    def _update_performance_metrics(
        self, execution_time_ms: float, servers: List[str], success: bool
    ):
        """Update performance metrics."""
        # Update average response time.

        total_queries = self.metrics["total_queries"]
        current_avg = self.metrics["avg_response_time_ms"]
        self.metrics["avg_response_time_ms"] = (
            current_avg * (total_queries - 1) + execution_time_ms
        ) / total_queries

        # Update server success rates
        for server in servers:
            if server not in self.metrics["server_success_rates"]:
                self.metrics["server_success_rates"][server] = {
                    "total": 0,
                    "successful": 0,
                }

            self.metrics["server_success_rates"][server]["total"] += 1
            if success:
                self.metrics["server_success_rates"][server]["successful"] += 1

    def get_federation_stats(self) -> Dict[str, Any]:
        """Get comprehensive federation statistics."""
        server_stats = {}.

        for server_name, server_info in self.servers.items():
            success_data = self.metrics["server_success_rates"].get(
                server_name, {"total": 0, "successful": 0}
            )
            success_rate = (
                success_data["successful"] / success_data["total"]
                if success_data["total"] > 0
                else 0.0
            )

            server_stats[server_name] = {
                "health_status": server_info.health_status,
                "last_health_check": server_info.last_health_check,
                "capabilities": server_info.capabilities,
                "priority": server_info.priority,
                "timeout_ms": server_info.timeout_ms,
                "success_rate": success_rate,
                "total_queries": success_data["total"],
            }

        return {
            "overall_metrics": self.metrics,
            "server_stats": server_stats,
            "federation_health": {
                "healthy_servers": sum(
                    1 for s in self.servers.values() if s.health_status == "healthy"
                ),
                "total_servers": len(self.servers),
                "overall_success_rate": (
                    self.metrics["successful_queries"] / self.metrics["total_queries"]
                    if self.metrics["total_queries"] > 0
                    else 0.0
                ),
            },
        }

    async def close(self):
        """Close the MCP federation."""
        self.initialized = False

        if self.health_monitor_task:
            self.health_monitor_task.cancel()

        self.executor.shutdown(wait=True)
        logger.info("MCP Federation closed")


# Global instance
mcp_federation = MCPFederation()
