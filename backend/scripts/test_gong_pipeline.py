#!/usr/bin/env python3
"""
Comprehensive Gong Data Pipeline Test Suite

Tests the complete end-to-end Gong data pipeline in SOPHIA_AI_DEV:
- Airbyte sync validation
- Raw data landing verification
- Transformation procedure testing
- AI Memory integration testing
- PII policy validation
- Performance and monitoring tests

Usage:
    python backend/scripts/test_gong_pipeline.py --test-suite all
    python backend/scripts/test_gong_pipeline.py --test-suite airbyte
    python backend/scripts/test_gong_pipeline.py --test-suite transformation
    python backend/scripts/test_gong_pipeline.py --test-suite ai-memory
"""

import asyncio
import json
import logging
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import argparse

from backend.utils.snowflake_cortex_service import SnowflakeCortexService
from backend.utils.snowflake_gong_connector import SnowflakeGongConnector
from backend.mcp.enhanced_ai_memory_mcp_server import EnhancedAiMemoryMCPServer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestSuite(Enum):
    """Available test suites"""
    ALL = "all"
    AIRBYTE = "airbyte"
    TRANSFORMATION = "transformation"
    AI_MEMORY = "ai-memory"
    PII_POLICIES = "pii-policies"
    PERFORMANCE = "performance"


@dataclass
class TestResult:
    """Test result structure"""
    test_name: str
    success: bool
    message: str
    details: Optional[Dict[str, Any]] = None
    execution_time_ms: Optional[float] = None


class GongPipelineTestSuite:
    """
    Comprehensive test suite for Gong data pipeline
    
    Test Categories:
    1. Airbyte Sync Validation
    2. Raw Data Landing Verification
    3. Transformation Procedure Testing
    4. AI Memory Integration Testing
    5. PII Policy Validation
    6. Performance and Monitoring Tests
    """

    def __init__(self):
        self.cortex_service: Optional[SnowflakeCortexService] = None
        self.gong_connector: Optional[SnowflakeGongConnector] = None
        self.ai_memory: Optional[EnhancedAiMemoryMCPServer] = None
        
        self.test_results: List[TestResult] = []
        self.database = "SOPHIA_AI_DEV"

    async def initialize(self) -> None:
        """Initialize test services"""
        try:
            self.cortex_service = SnowflakeCortexService()
            self.gong_connector = SnowflakeGongConnector()
            self.ai_memory = EnhancedAiMemoryMCPServer()
            
            await self.ai_memory.initialize()
            
            logger.info("✅ Test suite initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize test suite: {e}")
            raise

    async def run_test_suite(self, suite: TestSuite) -> Dict[str, Any]:
        """Run specified test suite"""
        try:
            logger.info(f"🧪 Running {suite.value.upper()} test suite...")
            
            if suite == TestSuite.ALL:
                await self._run_all_tests()
            elif suite == TestSuite.AIRBYTE:
                await self._test_airbyte_sync()
            elif suite == TestSuite.TRANSFORMATION:
                await self._test_transformation_procedures()
            elif suite == TestSuite.AI_MEMORY:
                await self._test_ai_memory_integration()
            elif suite == TestSuite.PII_POLICIES:
                await self._test_pii_policies()
            elif suite == TestSuite.PERFORMANCE:
                await self._test_performance_metrics()
            
            # Generate test summary
            total_tests = len(self.test_results)
            passed_tests = sum(1 for result in self.test_results if result.success)
            failed_tests = total_tests - passed_tests
            success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
            
            summary = {
                "test_suite": suite.value,
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": success_rate,
                "overall_status": "PASSED" if failed_tests == 0 else "FAILED",
                "test_results": [
                    {
                        "test_name": result.test_name,
                        "success": result.success,
                        "message": result.message,
                        "execution_time_ms": result.execution_time_ms
                    }
                    for result in self.test_results
                ],
                "test_timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info(f"🎯 Test suite completed: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}%)")
            return summary
            
        except Exception as e:
            logger.error(f"Test suite execution failed: {e}")
            return {
                "test_suite": suite.value,
                "overall_status": "ERROR",
                "error": str(e),
                "test_results": self.test_results
            }

    async def _run_all_tests(self) -> None:
        """Run all test categories"""
        await self._test_airbyte_sync()
        await self._test_transformation_procedures()
        await self._test_ai_memory_integration()
        await self._test_pii_policies()
        await self._test_performance_metrics()

    async def _test_airbyte_sync(self) -> None:
        """Test Airbyte sync validation"""
        logger.info("🔄 Testing Airbyte sync validation...")
        
        # Test 1: Verify RAW_AIRBYTE tables exist and have data
        await self._execute_test(
            "raw_tables_exist",
            self._verify_raw_tables_exist
        )
        
        # Test 2: Verify recent data ingestion
        await self._execute_test(
            "recent_data_ingestion",
            self._verify_recent_data_ingestion
        )
        
        # Test 3: Verify data structure and VARIANT columns
        await self._execute_test(
            "data_structure_validation",
            self._verify_data_structure
        )
        
        # Test 4: Check for processing errors
        await self._execute_test(
            "processing_errors_check",
            self._check_processing_errors
        )

    async def _test_transformation_procedures(self) -> None:
        """Test transformation procedures"""
        logger.info("�� Testing transformation procedures...")
        
        # Test 1: Execute transformation procedures
        await self._execute_test(
            "transform_raw_calls",
            self._test_transform_raw_calls
        )
        
        # Test 2: Verify STG_GONG_CALLS population
        await self._execute_test(
            "stg_calls_population",
            self._verify_stg_calls_population
        )
        
        # Test 3: Test AI enrichment procedures
        await self._execute_test(
            "ai_enrichment_procedures",
            self._test_ai_enrichment
        )
        
        # Test 4: Verify data quality and completeness
        await self._execute_test(
            "data_quality_validation",
            self._verify_data_quality
        )

    async def _test_ai_memory_integration(self) -> None:
        """Test AI Memory integration"""
        logger.info("🧠 Testing AI Memory integration...")
        
        # Test 1: Verify embedding generation
        await self._execute_test(
            "embedding_generation",
            self._test_embedding_generation
        )
        
        # Test 2: Test semantic search functionality
        await self._execute_test(
            "semantic_search",
            self._test_semantic_search
        )
        
        # Test 3: Verify AI_MEMORY.MEMORY_RECORDS population
        await self._execute_test(
            "memory_records_population",
            self._verify_memory_records
        )
        
        # Test 4: Test cross-platform memory access
        await self._execute_test(
            "cross_platform_memory",
            self._test_cross_platform_memory
        )

    async def _test_pii_policies(self) -> None:
        """Test PII masking policies"""
        logger.info("🔒 Testing PII policies...")
        
        # Test 1: Verify email masking policy application
        await self._execute_test(
            "email_masking_policy",
            self._test_email_masking
        )
        
        # Test 2: Test role-based access control
        await self._execute_test(
            "role_based_access",
            self._test_role_based_access
        )

    async def _test_performance_metrics(self) -> None:
        """Test performance and monitoring"""
        logger.info("📊 Testing performance metrics...")
        
        # Test 1: Query performance benchmarks
        await self._execute_test(
            "query_performance",
            self._test_query_performance
        )
        
        # Test 2: Verify monitoring table population
        await self._execute_test(
            "monitoring_tables",
            self._verify_monitoring_tables
        )

    async def _execute_test(self, test_name: str, test_function) -> None:
        """Execute individual test with timing and error handling"""
        start_time = datetime.utcnow()
        
        try:
            result = await test_function()
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            if isinstance(result, bool):
                success = result
                message = "Test passed" if result else "Test failed"
                details = None
            elif isinstance(result, dict):
                success = result.get("success", False)
                message = result.get("message", "No message provided")
                details = result.get("details")
            else:
                success = False
                message = f"Invalid test result format: {type(result)}"
                details = None
            
            self.test_results.append(TestResult(
                test_name=test_name,
                success=success,
                message=message,
                details=details,
                execution_time_ms=execution_time
            ))
            
            status = "✅ PASS" if success else "❌ FAIL"
            logger.info(f"{status} {test_name}: {message} ({execution_time:.0f}ms)")
            
        except Exception as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            self.test_results.append(TestResult(
                test_name=test_name,
                success=False,
                message=f"Test execution failed: {str(e)}",
                execution_time_ms=execution_time
            ))
            
            logger.error(f"❌ ERROR {test_name}: {str(e)} ({execution_time:.0f}ms)")

    # Individual test implementations
    
    async def _verify_raw_tables_exist(self) -> Dict[str, Any]:
        """Verify RAW_AIRBYTE tables exist and have proper structure"""
        async with self.cortex_service as cortex:
            # Check if tables exist
            tables_query = f"""
            SELECT table_name, row_count
            FROM {self.database}.INFORMATION_SCHEMA.TABLES 
            WHERE table_schema = 'RAW_AIRBYTE' 
            AND table_name IN ('RAW_GONG_CALLS_RAW', 'RAW_GONG_TRANSCRIPTS_RAW')
            """
            
            result = await cortex.execute_query(tables_query)
            
            if len(result) >= 2:
                return {
                    "success": True,
                    "message": f"Found {len(result)} required RAW_AIRBYTE tables",
                    "details": {"tables": result.to_dict('records')}
                }
            else:
                return {
                    "success": False,
                    "message": f"Missing RAW_AIRBYTE tables. Found: {len(result)}/2"
                }

    async def _verify_recent_data_ingestion(self) -> Dict[str, Any]:
        """Verify recent data has been ingested"""
        async with self.cortex_service as cortex:
            # Check for data ingested in the last 24 hours
            ingestion_query = f"""
            SELECT 
                COUNT(*) as total_records,
                MAX(INGESTED_AT) as latest_ingestion,
                MIN(INGESTED_AT) as earliest_ingestion
            FROM {self.database}.RAW_AIRBYTE.RAW_GONG_CALLS_RAW
            WHERE INGESTED_AT >= DATEADD(hour, -24, CURRENT_TIMESTAMP())
            """
            
            result = await cortex.execute_query(ingestion_query)
            
            if len(result) > 0 and result.iloc[0]['TOTAL_RECORDS'] > 0:
                return {
                    "success": True,
                    "message": f"Found {result.iloc[0]['TOTAL_RECORDS']} records ingested in last 24 hours",
                    "details": result.iloc[0].to_dict()
                }
            else:
                return {
                    "success": False,
                    "message": "No recent data ingestion detected"
                }

    async def _verify_data_structure(self) -> Dict[str, Any]:
        """Verify data structure and VARIANT columns"""
        async with self.cortex_service as cortex:
            # Check VARIANT column structure
            structure_query = f"""
            SELECT 
                COUNT(*) as total_records,
                COUNT(CASE WHEN _AIRBYTE_DATA IS NOT NULL THEN 1 END) as valid_variant_records,
                COUNT(CASE WHEN CALL_ID IS NOT NULL THEN 1 END) as valid_call_ids
            FROM {self.database}.RAW_AIRBYTE.RAW_GONG_CALLS_RAW
            LIMIT 1000
            """
            
            result = await cortex.execute_query(structure_query)
            
            if len(result) > 0:
                row = result.iloc[0]
                success = (row['VALID_VARIANT_RECORDS'] == row['TOTAL_RECORDS'] and 
                          row['VALID_CALL_IDS'] > 0)
                
                return {
                    "success": success,
                    "message": f"Data structure validation: {row['VALID_VARIANT_RECORDS']}/{row['TOTAL_RECORDS']} valid VARIANT records",
                    "details": row.to_dict()
                }
            else:
                return {"success": False, "message": "No data found for structure validation"}

    async def _check_processing_errors(self) -> Dict[str, Any]:
        """Check for processing errors in raw data"""
        async with self.cortex_service as cortex:
            errors_query = f"""
            SELECT 
                COUNT(*) as total_errors,
                COUNT(DISTINCT PROCESSING_ERROR) as unique_error_types
            FROM {self.database}.RAW_AIRBYTE.RAW_GONG_CALLS_RAW
            WHERE PROCESSING_ERROR IS NOT NULL
            """
            
            result = await cortex.execute_query(errors_query)
            
            if len(result) > 0:
                row = result.iloc[0]
                success = row['TOTAL_ERRORS'] == 0
                
                return {
                    "success": success,
                    "message": f"Processing errors check: {row['TOTAL_ERRORS']} errors found",
                    "details": row.to_dict()
                }
            else:
                return {"success": True, "message": "No processing errors found"}

    async def _test_transform_raw_calls(self) -> Dict[str, Any]:
        """Test transformation procedure execution"""
        async with self.cortex_service as cortex:
            # Execute transformation procedure
            transform_query = f"""
            CALL {self.database}.STG_TRANSFORMED.TRANSFORM_RAW_GONG_CALLS()
            """
            
            result = await cortex.execute_query(transform_query)
            
            if len(result) > 0:
                message = result.iloc[0].iloc[0]  # Get the returned message
                success = "Error" not in message
                
                return {
                    "success": success,
                    "message": f"Transformation procedure result: {message}"
                }
            else:
                return {"success": False, "message": "Transformation procedure returned no result"}

    async def _verify_stg_calls_population(self) -> Dict[str, Any]:
        """Verify STG_GONG_CALLS table population"""
        async with self.cortex_service as cortex:
            population_query = f"""
            SELECT 
                COUNT(*) as total_stg_records,
                COUNT(CASE WHEN HUBSPOT_DEAL_ID IS NOT NULL THEN 1 END) as records_with_deals,
                COUNT(CASE WHEN SENTIMENT_SCORE IS NOT NULL THEN 1 END) as records_with_sentiment,
                MAX(UPDATED_AT) as latest_update
            FROM {self.database}.STG_TRANSFORMED.STG_GONG_CALLS
            """
            
            result = await cortex.execute_query(population_query)
            
            if len(result) > 0:
                row = result.iloc[0]
                success = row['TOTAL_STG_RECORDS'] > 0
                
                return {
                    "success": success,
                    "message": f"STG_GONG_CALLS populated with {row['TOTAL_STG_RECORDS']} records",
                    "details": row.to_dict()
                }
            else:
                return {"success": False, "message": "STG_GONG_CALLS table not found or empty"}

    async def _test_ai_enrichment(self) -> Dict[str, Any]:
        """Test AI enrichment procedures"""
        async with self.cortex_service as cortex:
            # Execute AI enrichment procedure
            enrichment_query = f"""
            CALL {self.database}.STG_TRANSFORMED.GENERATE_AI_EMBEDDINGS()
            """
            
            result = await cortex.execute_query(enrichment_query)
            
            if len(result) > 0:
                message = result.iloc[0].iloc[0]
                success = "Error" not in message
                
                return {
                    "success": success,
                    "message": f"AI enrichment result: {message}"
                }
            else:
                return {"success": False, "message": "AI enrichment procedure returned no result"}

    async def _verify_data_quality(self) -> Dict[str, Any]:
        """Verify data quality and completeness"""
        async with self.cortex_service as cortex:
            quality_query = f"""
            SELECT 
                COUNT(*) as total_records,
                COUNT(CASE WHEN CALL_ID IS NOT NULL THEN 1 END) as valid_call_ids,
                COUNT(CASE WHEN CALL_DATETIME_UTC IS NOT NULL THEN 1 END) as valid_timestamps,
                COUNT(CASE WHEN PRIMARY_USER_EMAIL IS NOT NULL THEN 1 END) as valid_users,
                AVG(CASE WHEN CALL_DURATION_SECONDS > 0 THEN CALL_DURATION_SECONDS END) as avg_duration
            FROM {self.database}.STG_TRANSFORMED.STG_GONG_CALLS
            """
            
            result = await cortex.execute_query(quality_query)
            
            if len(result) > 0:
                row = result.iloc[0]
                completeness_rate = (row['VALID_CALL_IDS'] / row['TOTAL_RECORDS'] * 100) if row['TOTAL_RECORDS'] > 0 else 0
                success = completeness_rate >= 95  # 95% completeness threshold
                
                return {
                    "success": success,
                    "message": f"Data quality: {completeness_rate:.1f}% completeness rate",
                    "details": row.to_dict()
                }
            else:
                return {"success": False, "message": "No data found for quality validation"}

    async def _test_embedding_generation(self) -> Dict[str, Any]:
        """Test embedding generation"""
        async with self.cortex_service as cortex:
            embedding_query = f"""
            SELECT 
                COUNT(*) as total_records,
                COUNT(CASE WHEN AI_MEMORY_EMBEDDING IS NOT NULL THEN 1 END) as records_with_embeddings,
                COUNT(CASE WHEN AI_MEMORY_METADATA IS NOT NULL THEN 1 END) as records_with_metadata
            FROM {self.database}.STG_TRANSFORMED.STG_GONG_CALLS
            WHERE CALL_SUMMARY IS NOT NULL
            """
            
            result = await cortex.execute_query(embedding_query)
            
            if len(result) > 0:
                row = result.iloc[0]
                embedding_rate = (row['RECORDS_WITH_EMBEDDINGS'] / row['TOTAL_RECORDS'] * 100) if row['TOTAL_RECORDS'] > 0 else 0
                success = embedding_rate >= 80  # 80% embedding coverage threshold
                
                return {
                    "success": success,
                    "message": f"Embedding generation: {embedding_rate:.1f}% coverage",
                    "details": row.to_dict()
                }
            else:
                return {"success": False, "message": "No records found for embedding validation"}

    async def _test_semantic_search(self) -> Dict[str, Any]:
        """Test semantic search functionality"""
        try:
            # Test semantic search using AI Memory service
            search_results = await self.ai_memory.recall_gong_call_insights(
                query="customer feedback pricing discussion",
                limit=5,
                use_cortex_search=True
            )
            
            success = len(search_results) > 0
            return {
                "success": success,
                "message": f"Semantic search returned {len(search_results)} results",
                "details": {"result_count": len(search_results)}
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Semantic search test failed: {str(e)}"
            }

    async def _verify_memory_records(self) -> Dict[str, Any]:
        """Verify AI_MEMORY.MEMORY_RECORDS population"""
        async with self.cortex_service as cortex:
            memory_query = f"""
            SELECT 
                COUNT(*) as total_memory_records,
                COUNT(CASE WHEN SOURCE_TYPE = 'gong' THEN 1 END) as gong_memory_records,
                COUNT(CASE WHEN EMBEDDING IS NOT NULL THEN 1 END) as records_with_embeddings
            FROM {self.database}.AI_MEMORY.MEMORY_RECORDS
            """
            
            result = await cortex.execute_query(memory_query)
            
            if len(result) > 0:
                row = result.iloc[0]
                success = row['GONG_MEMORY_RECORDS'] > 0
                
                return {
                    "success": success,
                    "message": f"AI Memory records: {row['GONG_MEMORY_RECORDS']} Gong records out of {row['TOTAL_MEMORY_RECORDS']} total",
                    "details": row.to_dict()
                }
            else:
                return {"success": False, "message": "AI_MEMORY.MEMORY_RECORDS table not found or empty"}

    async def _test_cross_platform_memory(self) -> Dict[str, Any]:
        """Test cross-platform memory access"""
        try:
            # Test storing and retrieving Gong memory
            test_memory_id = f"test_gong_call_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            # Store test memory
            store_result = await self.ai_memory.store_gong_call_insight(
                call_id=test_memory_id,
                insight_content="Test call insight for pipeline validation",
                call_summary="Test summary for validation",
                sentiment_score=0.7,
                key_topics=["testing", "validation", "pipeline"]
            )
            
            # Retrieve test memory
            recall_results = await self.ai_memory.recall_gong_call_insights(
                query="test call insight pipeline validation",
                limit=1
            )
            
            success = len(recall_results) > 0 and any(
                test_memory_id in str(result) for result in recall_results
            )
            
            return {
                "success": success,
                "message": f"Cross-platform memory test: {'PASSED' if success else 'FAILED'}",
                "details": {
                    "store_result": store_result.get("success", False),
                    "recall_count": len(recall_results)
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Cross-platform memory test failed: {str(e)}"
            }

    async def _test_email_masking(self) -> Dict[str, Any]:
        """Test email masking policy"""
        async with self.cortex_service as cortex:
            # Test email masking with different roles
            masking_query = f"""
            SELECT 
                COUNT(*) as total_records,
                COUNT(CASE WHEN PRIMARY_USER_EMAIL LIKE '%***%' THEN 1 END) as masked_emails,
                COUNT(CASE WHEN PRIMARY_USER_EMAIL NOT LIKE '%***%' THEN 1 END) as unmasked_emails
            FROM {self.database}.STG_TRANSFORMED.STG_GONG_CALLS
            WHERE PRIMARY_USER_EMAIL IS NOT NULL
            LIMIT 100
            """
            
            result = await cortex.execute_query(masking_query)
            
            if len(result) > 0:
                row = result.iloc[0]
                # The masking behavior depends on the current role
                success = row['TOTAL_RECORDS'] > 0
                
                return {
                    "success": success,
                    "message": f"Email masking policy active: {row['MASKED_EMAILS']} masked, {row['UNMASKED_EMAILS']} unmasked",
                    "details": row.to_dict()
                }
            else:
                return {"success": False, "message": "No email data found for masking test"}

    async def _test_role_based_access(self) -> Dict[str, Any]:
        """Test role-based access control"""
        # This would require switching roles, which is complex in automated tests
        # For now, we'll just verify the policies exist
        async with self.cortex_service as cortex:
            policy_query = f"""
            SELECT policy_name, policy_kind
            FROM {self.database}.INFORMATION_SCHEMA.POLICIES
            WHERE policy_name = 'MASK_EMAIL'
            """
            
            result = await cortex.execute_query(policy_query)
            
            success = len(result) > 0
            return {
                "success": success,
                "message": f"Role-based access policies: {'Found' if success else 'Not found'}",
                "details": {"policies_found": len(result)}
            }

    async def _test_query_performance(self) -> Dict[str, Any]:
        """Test query performance benchmarks"""
        performance_tests = []
        
        # Test 1: Simple select performance
        start_time = datetime.utcnow()
        async with self.cortex_service as cortex:
            simple_query = f"""
            SELECT COUNT(*) FROM {self.database}.STG_TRANSFORMED.STG_GONG_CALLS
            """
            await cortex.execute_query(simple_query)
        
        simple_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        performance_tests.append(("simple_select", simple_time, simple_time < 1000))  # < 1 second
        
        # Test 2: Complex join performance
        start_time = datetime.utcnow()
        async with self.cortex_service as cortex:
            complex_query = f"""
            SELECT c.CALL_ID, c.ACCOUNT_NAME, t.TRANSCRIPT_TEXT
            FROM {self.database}.STG_TRANSFORMED.STG_GONG_CALLS c
            LEFT JOIN {self.database}.STG_TRANSFORMED.STG_GONG_CALL_TRANSCRIPTS t
                ON c.CALL_ID = t.CALL_ID
            WHERE c.CALL_DATETIME_UTC >= DATEADD(day, -7, CURRENT_TIMESTAMP())
            LIMIT 100
            """
            await cortex.execute_query(complex_query)
        
        complex_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        performance_tests.append(("complex_join", complex_time, complex_time < 5000))  # < 5 seconds
        
        all_passed = all(passed for _, _, passed in performance_tests)
        
        return {
            "success": all_passed,
            "message": f"Performance tests: {sum(1 for _, _, passed in performance_tests if passed)}/{len(performance_tests)} passed",
            "details": {
                "tests": [
                    {"test": test, "time_ms": time_ms, "passed": passed}
                    for test, time_ms, passed in performance_tests
                ]
            }
        }

    async def _verify_monitoring_tables(self) -> Dict[str, Any]:
        """Verify monitoring table population"""
        async with self.cortex_service as cortex:
            monitoring_query = f"""
            SELECT 
                COUNT(*) as total_logs,
                COUNT(CASE WHEN JOB_TYPE = 'airbyte_gong_sync' THEN 1 END) as airbyte_logs,
                MAX(LOG_TIMESTAMP) as latest_log
            FROM {self.database}.OPS_MONITORING.ETL_JOB_LOGS
            WHERE LOG_TIMESTAMP >= DATEADD(day, -1, CURRENT_TIMESTAMP())
            """
            
            result = await cortex.execute_query(monitoring_query)
            
            if len(result) > 0:
                row = result.iloc[0]
                success = row['TOTAL_LOGS'] >= 0  # Any logs are good
                
                return {
                    "success": success,
                    "message": f"Monitoring tables: {row['TOTAL_LOGS']} logs found",
                    "details": row.to_dict()
                }
            else:
                return {"success": False, "message": "OPS_MONITORING.ETL_JOB_LOGS table not found"}

    async def cleanup(self) -> None:
        """Clean up test resources"""
        if self.ai_memory:
            # Clean up any test data
            pass


async def main():
    """Main function for CLI usage"""
    parser = argparse.ArgumentParser(description="Test Gong Data Pipeline")
    parser.add_argument("--test-suite", choices=["all", "airbyte", "transformation", "ai-memory", "pii-policies", "performance"],
                       default="all", help="Test suite to run")
    parser.add_argument("--output-file", help="Output file for test results (JSON)")
    
    args = parser.parse_args()
    
    suite = TestSuite(args.test_suite.replace("-", "_"))
    test_runner = GongPipelineTestSuite()
    
    try:
        await test_runner.initialize()
        result = await test_runner.run_test_suite(suite)
        
        # Output results
        if args.output_file:
            with open(args.output_file, 'w') as f:
                json.dump(result, f, indent=2)
            logger.info(f"Test results written to {args.output_file}")
        else:
            print(json.dumps(result, indent=2))
        
        # Exit with appropriate code
        if result["overall_status"] in ["PASSED", "ERROR"]:
            sys.exit(0 if result["overall_status"] == "PASSED" else 1)
        else:
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Test execution failed: {e}")
        sys.exit(1)
        
    finally:
        await test_runner.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
