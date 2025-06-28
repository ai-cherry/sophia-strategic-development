#!/usr/bin/env python3
"""
Enhanced Asana Integration Test Suite

Comprehensive testing framework for Asana integration including:
- Estuary connectivity and data ingestion
- Snowflake transformation and AI enrichment
- Project intelligence and analytics
- Chat service integration
- Performance and quality validation
"""

import argparse
import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from backend.agents.specialized.asana_project_intelligence_agent import (
    AsanaProjectIntelligenceAgent,
)
from backend.etl.estuary.estuary_configuration_manager import EnhancedEstuaryManager
from backend.mcp_servers.enhanced_ai_memory_mcp_server import EnhancedAiMemoryMCPServer
from backend.services.enhanced_unified_chat_service import (
    EnhancedUnifiedChatService,
    QueryContext,
)
from backend.utils.snowflake_cortex_service import SnowflakeCortexService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestCategory(Enum):
    """Test categories for Asana integration"""

    CONNECTIVITY = "connectivity"
    DATA_INGESTION = "data_ingestion"
    TRANSFORMATION = "transformation"
    AI_ENRICHMENT = "ai_enrichment"
    INTELLIGENCE = "intelligence"
    CHAT_INTEGRATION = "chat_integration"
    PERFORMANCE = "performance"
    SECURITY = "security"
    DATA_QUALITY = "data_quality"


@dataclass
class TestResult:
    """Individual test result"""

    test_name: str
    category: TestCategory
    status: str  # PASS, FAIL, SKIP
    execution_time: float
    message: str
    details: dict[str, Any] = field(default_factory=dict)
    metrics: dict[str, float] = field(default_factory=dict)


@dataclass
class TestSuite:
    """Test suite configuration and results"""

    environment: str
    include_data_validation: bool
    performance_thresholds: dict[str, float]
    results: list[TestResult] = field(default_factory=list)
    start_time: datetime | None = None
    end_time: datetime | None = None


class EnhancedAsanaIntegrationTestSuite:
    """Comprehensive Asana integration test suite"""

    def __init__(self, environment: str = "dev", include_data_validation: bool = True):
        self.environment = environment
        self.include_data_validation = include_data_validation
        self.test_suite = TestSuite(
            environment=environment,
            include_data_validation=include_data_validation,
            performance_thresholds={
                "estuary_setup_max_time": 300.0,  # 5 minutes
                "data_transformation_max_time": 120.0,  # 2 minutes
                "ai_enrichment_max_time": 180.0,  # 3 minutes
                "query_response_max_time": 5.0,  # 5 seconds
                "intelligence_report_max_time": 30.0,  # 30 seconds
                "min_data_quality_score": 0.90,  # 90%
                "min_ai_embedding_coverage": 0.80,  # 80%
            },
        )

        # Service instances
        self.estuary_manager = None
        self.cortex_service = None
        self.intelligence_agent = None
        self.chat_service = None
        self.ai_memory_service = None

    async def initialize_services(self) -> None:
        """Initialize all required services for testing"""
        try:
            logger.info("🔧 Initializing test services")

            self.estuary_manager = EnhancedEstuaryManager(self.environment)
            await self.estuary_manager.initialize()

            self.cortex_service = SnowflakeCortexService()
            await self.cortex_service.initialize()

            self.intelligence_agent = AsanaProjectIntelligenceAgent(
                {"agent_id": "test_asana_intelligence", "performance_target_ms": 200}
            )
            await self.intelligence_agent.initialize()

            self.chat_service = EnhancedUnifiedChatService()
            await self.chat_service.initialize()

            self.ai_memory_service = EnhancedAiMemoryMCPServer()
            await self.ai_memory_service.initialize()

            logger.info("✅ All test services initialized")

        except Exception as e:
            logger.error(f"❌ Failed to initialize test services: {e}")
            raise

    async def run_connectivity_tests(self) -> list[TestResult]:
        """Test connectivity to all required services"""
        logger.info("🔗 Running connectivity tests")
        results = []

        # Test Asana API connectivity
        start_time = time.time()
        try:
            result = await self.estuary_manager.test_source_connection("asana")
            execution_time = time.time() - start_time

            if result.status.value == "success":
                results.append(
                    TestResult(
                        test_name="asana_api_connectivity",
                        category=TestCategory.CONNECTIVITY,
                        status="PASS",
                        execution_time=execution_time,
                        message="Asana API connectivity successful",
                        metrics={"response_time": execution_time},
                    )
                )
            else:
                results.append(
                    TestResult(
                        test_name="asana_api_connectivity",
                        category=TestCategory.CONNECTIVITY,
                        status="FAIL",
                        execution_time=execution_time,
                        message=f"Asana API connectivity failed: {result.error_message}",
                        details={"error": result.error_message},
                    )
                )

        except Exception as e:
            execution_time = time.time() - start_time
            results.append(
                TestResult(
                    test_name="asana_api_connectivity",
                    category=TestCategory.CONNECTIVITY,
                    status="FAIL",
                    execution_time=execution_time,
                    message=f"Asana API test error: {str(e)}",
                    details={"exception": str(e)},
                )
            )

        # Test Snowflake connectivity
        start_time = time.time()
        try:
            await self.cortex_service.execute_query("SELECT 1 as connectivity_test")
            execution_time = time.time() - start_time

            results.append(
                TestResult(
                    test_name="snowflake_connectivity",
                    category=TestCategory.CONNECTIVITY,
                    status="PASS",
                    execution_time=execution_time,
                    message="Snowflake connectivity successful",
                    metrics={"response_time": execution_time},
                )
            )

        except Exception as e:
            execution_time = time.time() - start_time
            results.append(
                TestResult(
                    test_name="snowflake_connectivity",
                    category=TestCategory.CONNECTIVITY,
                    status="FAIL",
                    execution_time=execution_time,
                    message=f"Snowflake connectivity failed: {str(e)}",
                    details={"exception": str(e)},
                )
            )

        # Test Estuary server connectivity
        start_time = time.time()
        try:
            health_status = await self.estuary_manager.perform_health_check()
            execution_time = time.time() - start_time

            if health_status.get("overall_status") in ["healthy", "degraded"]:
                results.append(
                    TestResult(
                        test_name="estuary_server_connectivity",
                        category=TestCategory.CONNECTIVITY,
                        status="PASS",
                        execution_time=execution_time,
                        message="Estuary server connectivity successful",
                        details={"health_status": health_status},
                    )
                )
            else:
                results.append(
                    TestResult(
                        test_name="estuary_server_connectivity",
                        category=TestCategory.CONNECTIVITY,
                        status="FAIL",
                        execution_time=execution_time,
                        message="Estuary server unhealthy",
                        details={"health_status": health_status},
                    )
                )

        except Exception as e:
            execution_time = time.time() - start_time
            results.append(
                TestResult(
                    test_name="estuary_server_connectivity",
                    category=TestCategory.CONNECTIVITY,
                    status="FAIL",
                    execution_time=execution_time,
                    message=f"Estuary server test error: {str(e)}",
                    details={"exception": str(e)},
                )
            )

        return results

    async def run_data_ingestion_tests(self) -> list[TestResult]:
        """Test Asana data ingestion pipeline"""
        logger.info("📥 Running data ingestion tests")
        results = []

        # Test Estuary pipeline setup
        start_time = time.time()
        try:
            pipeline_results = (
                await self.estuary_manager.setup_complete_asana_pipeline()
            )
            execution_time = time.time() - start_time

            # Check if all pipeline components were successful
            all_successful = all(
                result.status.value == "success" for result in pipeline_results.values()
            )

            if all_successful:
                results.append(
                    TestResult(
                        test_name="asana_pipeline_setup",
                        category=TestCategory.DATA_INGESTION,
                        status="PASS",
                        execution_time=execution_time,
                        message="Asana Estuary pipeline setup successful",
                        details={
                            "pipeline_results": {
                                k: v.status.value for k, v in pipeline_results.items()
                            }
                        },
                        metrics={"setup_time": execution_time},
                    )
                )
            else:
                failed_components = [
                    k
                    for k, v in pipeline_results.items()
                    if v.status.value != "success"
                ]
                results.append(
                    TestResult(
                        test_name="asana_pipeline_setup",
                        category=TestCategory.DATA_INGESTION,
                        status="FAIL",
                        execution_time=execution_time,
                        message=f"Pipeline setup failed for components: {failed_components}",
                        details={"failed_components": failed_components},
                    )
                )

        except Exception as e:
            execution_time = time.time() - start_time
            results.append(
                TestResult(
                    test_name="asana_pipeline_setup",
                    category=TestCategory.DATA_INGESTION,
                    status="FAIL",
                    execution_time=execution_time,
                    message=f"Pipeline setup error: {str(e)}",
                    details={"exception": str(e)},
                )
            )

        # Test data ingestion validation
        if self.include_data_validation:
            start_time = time.time()
            try:
                # Wait for some data to be ingested (in real scenario, this would be more sophisticated)
                await asyncio.sleep(60)  # Wait 1 minute for data ingestion

                # Validate raw data exists
                raw_data_query = """
                SELECT
                    COUNT(*) as total_records,
                    COUNT(DISTINCT _estuary_data:gid) as unique_gids
                FROM RAW_ESTUARY._ESTUARY_RAW_ASANA_PROJECTS
                WHERE _estuary_emitted_at >= CURRENT_TIMESTAMP - INTERVAL '1 hour'
                """

                result = await self.cortex_service.execute_query(raw_data_query)
                execution_time = time.time() - start_time

                if not result.empty:
                    total_records = result.iloc[0]["TOTAL_RECORDS"]
                    unique_gids = result.iloc[0]["UNIQUE_GIDS"]

                    if total_records > 0:
                        results.append(
                            TestResult(
                                test_name="raw_data_ingestion",
                                category=TestCategory.DATA_INGESTION,
                                status="PASS",
                                execution_time=execution_time,
                                message=f"Raw data ingestion successful: {total_records} records, {unique_gids} unique projects",
                                metrics={
                                    "total_records": total_records,
                                    "unique_gids": unique_gids,
                                    "data_quality": unique_gids / max(total_records, 1),
                                },
                            )
                        )
                    else:
                        results.append(
                            TestResult(
                                test_name="raw_data_ingestion",
                                category=TestCategory.DATA_INGESTION,
                                status="FAIL",
                                execution_time=execution_time,
                                message="No raw data found in ingestion tables",
                            )
                        )
                else:
                    results.append(
                        TestResult(
                            test_name="raw_data_ingestion",
                            category=TestCategory.DATA_INGESTION,
                            status="FAIL",
                            execution_time=execution_time,
                            message="Unable to query raw data tables",
                        )
                    )

            except Exception as e:
                execution_time = time.time() - start_time
                results.append(
                    TestResult(
                        test_name="raw_data_ingestion",
                        category=TestCategory.DATA_INGESTION,
                        status="FAIL",
                        execution_time=execution_time,
                        message=f"Data validation error: {str(e)}",
                        details={"exception": str(e)},
                    )
                )

        return results

    async def run_transformation_tests(self) -> list[TestResult]:
        """Test data transformation procedures"""
        logger.info("🔄 Running transformation tests")
        results = []

        # Test project transformation
        start_time = time.time()
        try:
            # Execute transformation procedure
            await self.cortex_service.execute_query("CALL TRANSFORM_ASANA_PROJECTS()")
            execution_time = time.time() - start_time

            # Validate transformed data
            validation_query = """
            SELECT
                COUNT(*) as transformed_records,
                COUNT(CASE WHEN AI_MEMORY_METADATA IS NOT NULL THEN 1 END) as records_with_metadata,
                AVG(CONFIDENCE_SCORE) as avg_confidence_score
            FROM STG_TRANSFORMED.STG_ASANA_PROJECTS
            """

            validation_result = await self.cortex_service.execute_query(
                validation_query
            )

            if not validation_result.empty:
                row = validation_result.iloc[0]
                transformed_records = row["TRANSFORMED_RECORDS"]
                records_with_metadata = row["RECORDS_WITH_METADATA"]
                avg_confidence = row["AVG_CONFIDENCE_SCORE"]

                if transformed_records > 0:
                    results.append(
                        TestResult(
                            test_name="project_transformation",
                            category=TestCategory.TRANSFORMATION,
                            status="PASS",
                            execution_time=execution_time,
                            message=f"Project transformation successful: {transformed_records} records",
                            metrics={
                                "transformed_records": transformed_records,
                                "metadata_coverage": records_with_metadata
                                / max(transformed_records, 1),
                                "avg_confidence_score": avg_confidence or 0.0,
                            },
                        )
                    )
                else:
                    results.append(
                        TestResult(
                            test_name="project_transformation",
                            category=TestCategory.TRANSFORMATION,
                            status="FAIL",
                            execution_time=execution_time,
                            message="No records transformed",
                        )
                    )
            else:
                results.append(
                    TestResult(
                        test_name="project_transformation",
                        category=TestCategory.TRANSFORMATION,
                        status="FAIL",
                        execution_time=execution_time,
                        message="Unable to validate transformation results",
                    )
                )

        except Exception as e:
            execution_time = time.time() - start_time
            results.append(
                TestResult(
                    test_name="project_transformation",
                    category=TestCategory.TRANSFORMATION,
                    status="FAIL",
                    execution_time=execution_time,
                    message=f"Project transformation error: {str(e)}",
                    details={"exception": str(e)},
                )
            )

        # Test task transformation
        start_time = time.time()
        try:
            # Execute task transformation procedure
            await self.cortex_service.execute_query("CALL TRANSFORM_ASANA_TASKS()")
            execution_time = time.time() - start_time

            # Validate task transformation
            task_validation_query = """
            SELECT
                COUNT(*) as transformed_tasks,
                COUNT(CASE WHEN ASSIGNEE_GID IS NOT NULL THEN 1 END) as assigned_tasks,
                COUNT(CASE WHEN TASK_STATUS = 'OVERDUE' THEN 1 END) as overdue_tasks
            FROM STG_TRANSFORMED.STG_ASANA_TASKS
            """

            task_result = await self.cortex_service.execute_query(task_validation_query)

            if not task_result.empty:
                row = task_result.iloc[0]
                transformed_tasks = row["TRANSFORMED_TASKS"]
                assigned_tasks = row["ASSIGNED_TASKS"]
                overdue_tasks = row["OVERDUE_TASKS"]

                results.append(
                    TestResult(
                        test_name="task_transformation",
                        category=TestCategory.TRANSFORMATION,
                        status="PASS",
                        execution_time=execution_time,
                        message=f"Task transformation successful: {transformed_tasks} tasks",
                        metrics={
                            "transformed_tasks": transformed_tasks,
                            "assignment_rate": assigned_tasks
                            / max(transformed_tasks, 1),
                            "overdue_rate": overdue_tasks / max(transformed_tasks, 1),
                        },
                    )
                )
            else:
                results.append(
                    TestResult(
                        test_name="task_transformation",
                        category=TestCategory.TRANSFORMATION,
                        status="FAIL",
                        execution_time=execution_time,
                        message="Unable to validate task transformation",
                    )
                )

        except Exception as e:
            execution_time = time.time() - start_time
            results.append(
                TestResult(
                    test_name="task_transformation",
                    category=TestCategory.TRANSFORMATION,
                    status="FAIL",
                    execution_time=execution_time,
                    message=f"Task transformation error: {str(e)}",
                    details={"exception": str(e)},
                )
            )

        return results

    async def run_ai_enrichment_tests(self) -> list[TestResult]:
        """Test AI enrichment procedures"""
        logger.info("🤖 Running AI enrichment tests")
        results = []

        # Test project AI enrichment
        start_time = time.time()
        try:
            # Execute AI enrichment procedure
            await self.cortex_service.execute_query(
                "CALL GENERATE_ASANA_PROJECT_AI_EMBEDDINGS()"
            )
            execution_time = time.time() - start_time

            # Validate AI enrichment
            enrichment_query = """
            SELECT
                COUNT(*) as total_projects,
                COUNT(CASE WHEN AI_MEMORY_EMBEDDING IS NOT NULL THEN 1 END) as projects_with_embeddings,
                COUNT(CASE WHEN AI_PROJECT_SUMMARY IS NOT NULL THEN 1 END) as projects_with_summaries,
                AVG(AI_HEALTH_SCORE) as avg_health_score
            FROM STG_TRANSFORMED.STG_ASANA_PROJECTS
            """

            enrichment_result = await self.cortex_service.execute_query(
                enrichment_query
            )

            if not enrichment_result.empty:
                row = enrichment_result.iloc[0]
                total_projects = row["TOTAL_PROJECTS"]
                projects_with_embeddings = row["PROJECTS_WITH_EMBEDDINGS"]
                projects_with_summaries = row["PROJECTS_WITH_SUMMARIES"]
                avg_health_score = row["AVG_HEALTH_SCORE"]

                embedding_coverage = projects_with_embeddings / max(total_projects, 1)

                if (
                    embedding_coverage
                    >= self.test_suite.performance_thresholds[
                        "min_ai_embedding_coverage"
                    ]
                ):
                    results.append(
                        TestResult(
                            test_name="project_ai_enrichment",
                            category=TestCategory.AI_ENRICHMENT,
                            status="PASS",
                            execution_time=execution_time,
                            message=f"Project AI enrichment successful: {embedding_coverage:.1%} coverage",
                            metrics={
                                "embedding_coverage": embedding_coverage,
                                "summary_coverage": projects_with_summaries
                                / max(total_projects, 1),
                                "avg_health_score": avg_health_score or 0.0,
                            },
                        )
                    )
                else:
                    results.append(
                        TestResult(
                            test_name="project_ai_enrichment",
                            category=TestCategory.AI_ENRICHMENT,
                            status="FAIL",
                            execution_time=execution_time,
                            message=f"AI enrichment coverage below threshold: {embedding_coverage:.1%}",
                            metrics={"embedding_coverage": embedding_coverage},
                        )
                    )
            else:
                results.append(
                    TestResult(
                        test_name="project_ai_enrichment",
                        category=TestCategory.AI_ENRICHMENT,
                        status="FAIL",
                        execution_time=execution_time,
                        message="Unable to validate AI enrichment",
                    )
                )

        except Exception as e:
            execution_time = time.time() - start_time
            results.append(
                TestResult(
                    test_name="project_ai_enrichment",
                    category=TestCategory.AI_ENRICHMENT,
                    status="FAIL",
                    execution_time=execution_time,
                    message=f"AI enrichment error: {str(e)}",
                    details={"exception": str(e)},
                )
            )

        # Test semantic search capability
        start_time = time.time()
        try:
            # Test semantic search on enriched data
            search_query = """
            SELECT
                PROJECT_NAME,
                VECTOR_COSINE_SIMILARITY(
                    AI_MEMORY_EMBEDDING,
                    SNOWFLAKE.CORTEX.EMBED_TEXT_768('e5-base-v2', 'software development project')
                ) as similarity_score
            FROM STG_TRANSFORMED.STG_ASANA_PROJECTS
            WHERE AI_MEMORY_EMBEDDING IS NOT NULL
            ORDER BY similarity_score DESC
            LIMIT 5
            """

            search_result = await self.cortex_service.execute_query(search_query)
            execution_time = time.time() - start_time

            if not search_result.empty and len(search_result) > 0:
                max_similarity = search_result.iloc[0]["SIMILARITY_SCORE"]
                results.append(
                    TestResult(
                        test_name="semantic_search",
                        category=TestCategory.AI_ENRICHMENT,
                        status="PASS",
                        execution_time=execution_time,
                        message=f"Semantic search successful: max similarity {max_similarity:.3f}",
                        metrics={
                            "max_similarity": max_similarity,
                            "results_count": len(search_result),
                        },
                    )
                )
            else:
                results.append(
                    TestResult(
                        test_name="semantic_search",
                        category=TestCategory.AI_ENRICHMENT,
                        status="FAIL",
                        execution_time=execution_time,
                        message="Semantic search returned no results",
                    )
                )

        except Exception as e:
            execution_time = time.time() - start_time
            results.append(
                TestResult(
                    test_name="semantic_search",
                    category=TestCategory.AI_ENRICHMENT,
                    status="FAIL",
                    execution_time=execution_time,
                    message=f"Semantic search error: {str(e)}",
                    details={"exception": str(e)},
                )
            )

        return results

    async def run_intelligence_tests(self) -> list[TestResult]:
        """Test project intelligence and analytics"""
        logger.info("🧠 Running intelligence tests")
        results = []

        # Test project intelligence report generation
        start_time = time.time()
        try:
            report = (
                await self.intelligence_agent.generate_project_intelligence_report()
            )
            execution_time = time.time() - start_time

            if report and "error" not in report:
                project_count = len(report.get("project_metrics", []))
                team_count = len(report.get("team_productivity", []))

                results.append(
                    TestResult(
                        test_name="intelligence_report_generation",
                        category=TestCategory.INTELLIGENCE,
                        status="PASS",
                        execution_time=execution_time,
                        message=f"Intelligence report generated: {project_count} projects, {team_count} teams",
                        metrics={
                            "project_count": project_count,
                            "team_count": team_count,
                            "generation_time": execution_time,
                        },
                    )
                )
            else:
                results.append(
                    TestResult(
                        test_name="intelligence_report_generation",
                        category=TestCategory.INTELLIGENCE,
                        status="FAIL",
                        execution_time=execution_time,
                        message=f"Intelligence report generation failed: {report.get('error', 'Unknown error')}",
                        details={"report": report},
                    )
                )

        except Exception as e:
            execution_time = time.time() - start_time
            results.append(
                TestResult(
                    test_name="intelligence_report_generation",
                    category=TestCategory.INTELLIGENCE,
                    status="FAIL",
                    execution_time=execution_time,
                    message=f"Intelligence report error: {str(e)}",
                    details={"exception": str(e)},
                )
            )

        # Test risk assessment
        start_time = time.time()
        try:
            risk_assessments = await self.intelligence_agent.perform_risk_assessment()
            execution_time = time.time() - start_time

            if risk_assessments:
                high_risk_count = sum(
                    1
                    for r in risk_assessments
                    if r.overall_risk.value in ["high", "critical"]
                )

                results.append(
                    TestResult(
                        test_name="risk_assessment",
                        category=TestCategory.INTELLIGENCE,
                        status="PASS",
                        execution_time=execution_time,
                        message=f"Risk assessment completed: {len(risk_assessments)} projects, {high_risk_count} high-risk",
                        metrics={
                            "assessed_projects": len(risk_assessments),
                            "high_risk_projects": high_risk_count,
                            "assessment_time": execution_time,
                        },
                    )
                )
            else:
                results.append(
                    TestResult(
                        test_name="risk_assessment",
                        category=TestCategory.INTELLIGENCE,
                        status="FAIL",
                        execution_time=execution_time,
                        message="No risk assessments generated",
                    )
                )

        except Exception as e:
            execution_time = time.time() - start_time
            results.append(
                TestResult(
                    test_name="risk_assessment",
                    category=TestCategory.INTELLIGENCE,
                    status="FAIL",
                    execution_time=execution_time,
                    message=f"Risk assessment error: {str(e)}",
                    details={"exception": str(e)},
                )
            )

        return results

    async def run_chat_integration_tests(self) -> list[TestResult]:
        """Test chat service integration with Asana data"""
        logger.info("💬 Running chat integration tests")
        results = []

        # Test Asana project query
        start_time = time.time()
        try:
            context = QueryContext(
                user_id="test_user",
                user_role="manager",
                dashboard_type="project",
                security_level="EXECUTIVE",
            )

            query_result = await self.chat_service.process_unified_query(
                "Show me the status of all active Asana projects", context
            )
            execution_time = time.time() - start_time

            if query_result and query_result.confidence_score > 0.5:
                results.append(
                    TestResult(
                        test_name="asana_project_query",
                        category=TestCategory.CHAT_INTEGRATION,
                        status="PASS",
                        execution_time=execution_time,
                        message=f"Asana project query successful: {query_result.records_analyzed} records",
                        metrics={
                            "confidence_score": query_result.confidence_score,
                            "records_analyzed": query_result.records_analyzed,
                            "response_time": execution_time,
                        },
                    )
                )
            else:
                results.append(
                    TestResult(
                        test_name="asana_project_query",
                        category=TestCategory.CHAT_INTEGRATION,
                        status="FAIL",
                        execution_time=execution_time,
                        message="Asana project query failed or low confidence",
                        details={
                            "query_result": (
                                query_result.__dict__ if query_result else None
                            )
                        },
                    )
                )

        except Exception as e:
            execution_time = time.time() - start_time
            results.append(
                TestResult(
                    test_name="asana_project_query",
                    category=TestCategory.CHAT_INTEGRATION,
                    status="FAIL",
                    execution_time=execution_time,
                    message=f"Chat integration error: {str(e)}",
                    details={"exception": str(e)},
                )
            )

        return results

    async def run_performance_tests(self) -> list[TestResult]:
        """Test performance benchmarks"""
        logger.info("⚡ Running performance tests")
        results = []

        # Test query response time
        start_time = time.time()
        try:
            # Execute multiple queries and measure average response time
            query_times = []

            for _i in range(5):
                query_start = time.time()
                await self.cortex_service.execute_query(
                    "SELECT COUNT(*) FROM STG_TRANSFORMED.STG_ASANA_PROJECTS LIMIT 100"
                )
                query_times.append(time.time() - query_start)

            avg_query_time = sum(query_times) / len(query_times)
            execution_time = time.time() - start_time

            if (
                avg_query_time
                <= self.test_suite.performance_thresholds["query_response_max_time"]
            ):
                results.append(
                    TestResult(
                        test_name="query_performance",
                        category=TestCategory.PERFORMANCE,
                        status="PASS",
                        execution_time=execution_time,
                        message=f"Query performance within threshold: {avg_query_time:.3f}s avg",
                        metrics={
                            "avg_query_time": avg_query_time,
                            "max_query_time": max(query_times),
                            "min_query_time": min(query_times),
                        },
                    )
                )
            else:
                results.append(
                    TestResult(
                        test_name="query_performance",
                        category=TestCategory.PERFORMANCE,
                        status="FAIL",
                        execution_time=execution_time,
                        message=f"Query performance above threshold: {avg_query_time:.3f}s avg",
                        metrics={"avg_query_time": avg_query_time},
                    )
                )

        except Exception as e:
            execution_time = time.time() - start_time
            results.append(
                TestResult(
                    test_name="query_performance",
                    category=TestCategory.PERFORMANCE,
                    status="FAIL",
                    execution_time=execution_time,
                    message=f"Performance test error: {str(e)}",
                    details={"exception": str(e)},
                )
            )

        return results

    async def run_data_quality_tests(self) -> list[TestResult]:
        """Test data quality metrics"""
        logger.info("📊 Running data quality tests")
        results = []

        # Test overall data quality
        start_time = time.time()
        try:
            quality_metrics = await self.estuary_manager.validate_asana_data_quality()
            execution_time = time.time() - start_time

            if (
                quality_metrics.quality_score
                >= self.test_suite.performance_thresholds["min_data_quality_score"]
            ):
                results.append(
                    TestResult(
                        test_name="data_quality_validation",
                        category=TestCategory.DATA_QUALITY,
                        status="PASS",
                        execution_time=execution_time,
                        message=f"Data quality within threshold: {quality_metrics.quality_score:.1%}",
                        metrics={
                            "quality_score": quality_metrics.quality_score,
                            "total_records": quality_metrics.total_records,
                            "valid_records": quality_metrics.valid_records,
                            "invalid_records": quality_metrics.invalid_records,
                        },
                    )
                )
            else:
                results.append(
                    TestResult(
                        test_name="data_quality_validation",
                        category=TestCategory.DATA_QUALITY,
                        status="FAIL",
                        execution_time=execution_time,
                        message=f"Data quality below threshold: {quality_metrics.quality_score:.1%}",
                        details={"issues": quality_metrics.issues},
                    )
                )

        except Exception as e:
            execution_time = time.time() - start_time
            results.append(
                TestResult(
                    test_name="data_quality_validation",
                    category=TestCategory.DATA_QUALITY,
                    status="FAIL",
                    execution_time=execution_time,
                    message=f"Data quality test error: {str(e)}",
                    details={"exception": str(e)},
                )
            )

        return results

    async def run_all_tests(self) -> TestSuite:
        """Run complete test suite"""
        logger.info("🚀 Starting comprehensive Asana integration test suite")
        self.test_suite.start_time = datetime.now()

        try:
            await self.initialize_services()

            # Run all test categories
            test_functions = [
                self.run_connectivity_tests,
                self.run_data_ingestion_tests,
                self.run_transformation_tests,
                self.run_ai_enrichment_tests,
                self.run_intelligence_tests,
                self.run_chat_integration_tests,
                self.run_performance_tests,
                self.run_data_quality_tests,
            ]

            for test_function in test_functions:
                try:
                    category_results = await test_function()
                    self.test_suite.results.extend(category_results)
                except Exception as e:
                    logger.error(
                        f"❌ Test category failed: {test_function.__name__}: {e}"
                    )
                    # Add a failure result for the entire category
                    self.test_suite.results.append(
                        TestResult(
                            test_name=test_function.__name__,
                            category=TestCategory.CONNECTIVITY,  # Default category
                            status="FAIL",
                            execution_time=0.0,
                            message=f"Test category failed: {str(e)}",
                            details={"exception": str(e)},
                        )
                    )

        except Exception as e:
            logger.error(f"❌ Test suite initialization failed: {e}")
        finally:
            self.test_suite.end_time = datetime.now()
            await self.cleanup_services()

        return self.test_suite

    async def cleanup_services(self) -> None:
        """Clean up test services"""
        try:
            if self.estuary_manager:
                await self.estuary_manager.cleanup()
            if self.cortex_service:
                await self.cortex_service.close()
            if self.intelligence_agent:
                await self.intelligence_agent.close()
            if self.chat_service:
                await self.chat_service.close()
            if self.ai_memory_service:
                await self.ai_memory_service.close()
        except Exception as e:
            logger.error(f"❌ Error cleaning up services: {e}")

    def generate_test_report(self) -> dict[str, Any]:
        """Generate comprehensive test report"""
        total_tests = len(self.test_suite.results)
        passed_tests = sum(1 for r in self.test_suite.results if r.status == "PASS")
        failed_tests = sum(1 for r in self.test_suite.results if r.status == "FAIL")
        skipped_tests = sum(1 for r in self.test_suite.results if r.status == "SKIP")

        # Calculate success rate by category
        category_stats = {}
        for category in TestCategory:
            category_results = [
                r for r in self.test_suite.results if r.category == category
            ]
            if category_results:
                category_passed = sum(1 for r in category_results if r.status == "PASS")
                category_stats[category.value] = {
                    "total": len(category_results),
                    "passed": category_passed,
                    "success_rate": category_passed / len(category_results),
                }

        # Calculate overall execution time
        total_execution_time = 0.0
        if self.test_suite.start_time and self.test_suite.end_time:
            total_execution_time = (
                self.test_suite.end_time - self.test_suite.start_time
            ).total_seconds()

        return {
            "test_suite_summary": {
                "environment": self.test_suite.environment,
                "start_time": (
                    self.test_suite.start_time.isoformat()
                    if self.test_suite.start_time
                    else None
                ),
                "end_time": (
                    self.test_suite.end_time.isoformat()
                    if self.test_suite.end_time
                    else None
                ),
                "total_execution_time": total_execution_time,
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "skipped_tests": skipped_tests,
                "success_rate": passed_tests / max(total_tests, 1),
                "include_data_validation": self.test_suite.include_data_validation,
            },
            "category_statistics": category_stats,
            "performance_thresholds": self.test_suite.performance_thresholds,
            "detailed_results": [
                {
                    "test_name": r.test_name,
                    "category": r.category.value,
                    "status": r.status,
                    "execution_time": r.execution_time,
                    "message": r.message,
                    "metrics": r.metrics,
                    "details": r.details,
                }
                for r in self.test_suite.results
            ],
            "failed_tests": [
                {
                    "test_name": r.test_name,
                    "category": r.category.value,
                    "message": r.message,
                    "details": r.details,
                }
                for r in self.test_suite.results
                if r.status == "FAIL"
            ],
        }


async def main():
    """Main test execution function"""
    parser = argparse.ArgumentParser(
        description="Enhanced Asana Integration Test Suite"
    )
    parser.add_argument(
        "--environment", default="dev", choices=["dev", "staging", "prod"]
    )
    parser.add_argument("--output", help="Output file for test results (JSON)")
    parser.add_argument("--include-data-validation", action="store_true", default=True)
    parser.add_argument(
        "--skip-data-validation", action="store_false", dest="include_data_validation"
    )

    args = parser.parse_args()

    # Create and run test suite
    test_suite = EnhancedAsanaIntegrationTestSuite(
        environment=args.environment,
        include_data_validation=args.include_data_validation,
    )

    try:
        await test_suite.run_all_tests()
        report = test_suite.generate_test_report()

        # Print summary
        summary = report["test_suite_summary"]
        print("\n🧪 Asana Integration Test Suite Results")
        print("=" * 50)
        print(f"Environment: {summary['environment']}")
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Passed: {summary['passed_tests']}")
        print(f"Failed: {summary['failed_tests']}")
        print(f"Success Rate: {summary['success_rate']:.1%}")
        print(f"Execution Time: {summary['total_execution_time']:.1f}s")

        # Print category breakdown
        print("\n📊 Category Breakdown:")
        for category, stats in report["category_statistics"].items():
            print(
                f"  {category}: {stats['passed']}/{stats['total']} ({stats['success_rate']:.1%})"
            )

        # Print failed tests
        if report["failed_tests"]:
            print("\n❌ Failed Tests:")
            for failed_test in report["failed_tests"]:
                print(
                    f"  - {failed_test['test_name']} ({failed_test['category']}): {failed_test['message']}"
                )

        # Save to file if specified
        if args.output:
            with open(args.output, "w") as f:
                json.dump(report, f, indent=2, default=str)
            print(f"\n💾 Detailed results saved to: {args.output}")

        # Return appropriate exit code
        return 0 if summary["failed_tests"] == 0 else 1

    except Exception as e:
        print(f"❌ Test suite execution failed: {e}")
        return 1


if __name__ == "__main__":
    exit(asyncio.run(main()))
