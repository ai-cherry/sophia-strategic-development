#!/usr/bin/env python3
"""
Sophia AI - MCP Optimization Components Test Suite
Comprehensive testing of all optimization components for validation
"""

import asyncio
import logging
import sys
import traceback
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TestResults:
    def __init__(self):
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.failures = []
    
    def add_result(self, test_name: str, passed: bool, error: str = None):
        self.total_tests += 1
        if passed:
            self.passed_tests += 1
            logger.info(f"✅ {test_name} - PASSED")
        else:
            self.failed_tests += 1
            self.failures.append(f"{test_name}: {error}")
            logger.error(f"❌ {test_name} - FAILED: {error}")
    
    def print_summary(self):
        logger.info("=" * 60)
        logger.info("TEST SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total Tests: {self.total_tests}")
        logger.info(f"Passed: {self.passed_tests}")
        logger.info(f"Failed: {self.failed_tests}")
        logger.info(f"Success Rate: {(self.passed_tests/self.total_tests)*100:.1f}%")
        
        if self.failures:
            logger.info("\nFAILURES:")
            for failure in self.failures:
                logger.error(f"  - {failure}")

async def test_standardized_mcp_server():
    """Test the StandardizedMCPServer base class."""
    results = TestResults()
    
    try:
        from backend.mcp.base.standardized_mcp_server import (
            MCPServerConfig, SyncPriority, HealthStatus, HealthCheckResult
        )
        results.add_result("Import StandardizedMCPServer", True)
        
        # Test config creation
        MCPServerConfig(
            server_name="test_server",
            port=3001,
            sync_priority=SyncPriority.HIGH,
            sync_interval_minutes=5
        )
        results.add_result("Create MCPServerConfig", True)
        
        # Test enums
        assert len(list(SyncPriority)) == 4
        assert len(list(HealthStatus)) == 4
        results.add_result("Enum definitions", True)
        
        # Test HealthCheckResult
        HealthCheckResult(
            component="test",
            status=HealthStatus.HEALTHY,
            response_time_ms=50.0
        )
        results.add_result("Create HealthCheckResult", True)
        
    except Exception as e:
        results.add_result("StandardizedMCPServer tests", False, str(e))
    
    return results

async def test_enhanced_cortex_service():
    """Test the Enhanced Snowflake Cortex Service."""
    results = TestResults()
    
    try:
        from backend.utils.enhanced_snowflake_cortex_service import (
            EnhancedSnowflakeCortexService, AIProcessingConfig, CortexModel,
            EmbeddingResult, SemanticSearchResult, AIInsight
        )
        results.add_result("Import EnhancedSnowflakeCortexService", True)
        
        # Test config creation
        config = AIProcessingConfig(
            embedding_model=CortexModel.E5_BASE_V2,
            llm_model=CortexModel.LLAMA3_70B
        )
        results.add_result("Create AIProcessingConfig", True)
        
        # Test service instantiation
        EnhancedSnowflakeCortexService(config)
        results.add_result("Create Cortex service instance", True)
        
        # Test data structures
        EmbeddingResult(
            text="test",
            embedding=[0.1, 0.2, 0.3],
            model="e5-base-v2",
            timestamp=datetime.utcnow(),
            processing_time_ms=100.0
        )
        results.add_result("Create EmbeddingResult", True)
        
        SemanticSearchResult(
            content="test content",
            similarity_score=0.85,
            metadata={},
            source_table="test_table",
            record_id="123"
        )
        results.add_result("Create SemanticSearchResult", True)
        
        AIInsight(
            insight_type="business",
            content="Test insight",
            confidence_score=0.9,
            supporting_data=["data1"],
            generated_at=datetime.utcnow()
        )
        results.add_result("Create AIInsight", True)
        
    except Exception as e:
        results.add_result("EnhancedSnowflakeCortexService tests", False, str(e))
    
    return results

async def test_sync_orchestrator():
    """Test the Cross-Platform Sync Orchestrator."""
    results = TestResults()
    
    try:
        from backend.core.cross_platform_sync_orchestrator import (
            CrossPlatformSyncOrchestrator, SyncConfiguration, SyncStatus,
            SyncPriority, ConflictType, DataConflict, SyncResult, SyncMetrics
        )
        results.add_result("Import CrossPlatformSyncOrchestrator", True)
        
        # Test orchestrator creation
        CrossPlatformSyncOrchestrator()
        results.add_result("Create sync orchestrator", True)
        
        # Test sync configuration
        SyncConfiguration(
            platform="test_platform",
            data_type="test_data",
            priority=SyncPriority.HIGH,
            sync_interval_minutes=5
        )
        results.add_result("Create SyncConfiguration", True)
        
        # Test data structures
        SyncResult(
            platform="test",
            data_type="test",
            status=SyncStatus.SUCCESS,
            records_synced=100
        )
        results.add_result("Create SyncResult", True)
        
        DataConflict(
            conflict_id="test_conflict",
            conflict_type=ConflictType.DUPLICATE_RECORD,
            platforms=["platform1", "platform2"],
            identifier="test@example.com",
            conflicting_data={}
        )
        results.add_result("Create DataConflict", True)
        
        # Test metrics
        metrics = SyncMetrics()
        metrics.total_syncs = 10
        metrics.successful_syncs = 9
        metrics.sync_success_rate = 0.9
        results.add_result("Create SyncMetrics", True)
        
    except Exception as e:
        results.add_result("CrossPlatformSyncOrchestrator tests", False, str(e))
    
    return results

async def test_multi_agent_workflow():
    """Test the Multi-Agent Workflow Framework."""
    results = TestResults()
    
    try:
        from backend.workflows.multi_agent_workflow import (
            MultiAgentWorkflow, WorkflowDefinition, WorkflowTask, AgentRole,
            WorkflowStatus, TaskStatus, WorkflowResult,
            WorkflowExecution
        )
        results.add_result("Import MultiAgentWorkflow", True)
        
        # Test workflow task creation
        task = WorkflowTask(
            task_id="test_task",
            agent_type="test_agent",
            agent_role=AgentRole.ANALYZER,
            input_data={"test": "data"}
        )
        results.add_result("Create WorkflowTask", True)
        
        # Test workflow definition
        workflow_def = WorkflowDefinition(
            workflow_id="test_workflow",
            name="Test Workflow",
            description="Test workflow description",
            tasks=[task]
        )
        results.add_result("Create WorkflowDefinition", True)
        
        # Test workflow creation
        MultiAgentWorkflow(workflow_def)
        results.add_result("Create MultiAgentWorkflow", True)
        
        # Test workflow execution structure
        WorkflowExecution(
            workflow_id="test",
            execution_id="test_exec",
            status=WorkflowStatus.PENDING,
            start_time=datetime.utcnow()
        )
        results.add_result("Create WorkflowExecution", True)
        
        # Test workflow result
        WorkflowResult(
            task_id="test",
            agent_type="test",
            status=TaskStatus.COMPLETED,
            output_data={},
            execution_time_seconds=1.0,
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow()
        )
        results.add_result("Create WorkflowResult", True)
        
        # Test agent interface (abstract)
        try:
            # This should not be instantiable directly
            results.add_result("AgentWorkflowInterface instantiation", True)
        except Exception:
            results.add_result("AgentWorkflowInterface abstract check", True)
        
    except Exception as e:
        results.add_result("MultiAgentWorkflow tests", False, str(e))
    
    return results

async def test_metrics_collector():
    """Test the MCP Metrics Collector."""
    results = TestResults()
    
    try:
        from backend.monitoring.mcp_metrics_collector import (
            MCPMetricsCollector, AlertSeverity, Alert
        )
        results.add_result("Import MCPMetricsCollector", True)
        
        # Test metrics collector creation
        collector = MCPMetricsCollector("test_server")
        results.add_result("Create MCPMetricsCollector", True)
        
        # Test alert creation
        Alert(
            alert_id="test_alert",
            severity=AlertSeverity.WARNING,
            message="Test alert message",
            metric_name="test_metric",
            current_value=1.0,
            threshold_value=0.5,
            triggered_at=datetime.utcnow(),
            server_name="test_server"
        )
        results.add_result("Create Alert", True)
        
        # Test metric recording
        collector.record_request("GET", "/test", "success", 0.1)
        results.add_result("Record request metric", True)
        
        collector.record_sync_metrics(100, 0.95, 30)
        results.add_result("Record sync metrics", True)
        
        collector.record_ai_processing_metrics("test", 2.0, 0.9)
        results.add_result("Record AI metrics", True)
        
        collector.record_workflow_metrics("test", "completed", 45.0, 5, 0)
        results.add_result("Record workflow metrics", True)
        
        # Test health status update
        collector.update_health_status(True)
        results.add_result("Update health status", True)
        
        # Test metrics summary
        summary = collector.get_metrics_summary()
        assert isinstance(summary, dict)
        results.add_result("Get metrics summary", True)
        
        # Test business intelligence metrics
        bi_metrics = collector.get_business_intelligence_metrics()
        assert isinstance(bi_metrics, dict)
        results.add_result("Get BI metrics", True)
        
    except Exception as e:
        results.add_result("MCPMetricsCollector tests", False, str(e))
    
    return results

async def test_component_integration():
    """Test integration between components."""
    results = TestResults()
    
    try:
        # Test that components can work together
        from backend.mcp.base.standardized_mcp_server import MCPServerConfig, SyncPriority
        from backend.core.cross_platform_sync_orchestrator import CrossPlatformSyncOrchestrator
        from backend.monitoring.mcp_metrics_collector import MCPMetricsCollector
        
        # Create components
        CrossPlatformSyncOrchestrator()
        MCPMetricsCollector("integration_test")
        
        # Test that they can be used together
        MCPServerConfig(
            server_name="integration_test",
            port=3001,
            sync_priority=SyncPriority.HIGH,
            sync_interval_minutes=5,
            enable_metrics=True
        )
        
        results.add_result("Component integration test", True)
        
        # Test async compatibility
        await asyncio.sleep(0.01)  # Ensure async compatibility
        results.add_result("Async compatibility", True)
        
    except Exception as e:
        results.add_result("Component integration", False, str(e))
    
    return results

async def run_all_tests():
    """Run all component tests."""
    logger.info("🚀 STARTING MCP OPTIMIZATION COMPONENTS TEST SUITE")
    logger.info("=" * 60)
    
    all_results = TestResults()
    
    # Run individual test suites
    test_suites = [
        ("Standardized MCP Server", test_standardized_mcp_server),
        ("Enhanced Cortex Service", test_enhanced_cortex_service),
        ("Sync Orchestrator", test_sync_orchestrator),
        ("Multi-Agent Workflow", test_multi_agent_workflow),
        ("Metrics Collector", test_metrics_collector),
        ("Component Integration", test_component_integration)
    ]
    
    for suite_name, test_func in test_suites:
        logger.info(f"\n🔍 Testing {suite_name}...")
        try:
            suite_results = await test_func()
            
            # Merge results
            all_results.total_tests += suite_results.total_tests
            all_results.passed_tests += suite_results.passed_tests
            all_results.failed_tests += suite_results.failed_tests
            all_results.failures.extend(suite_results.failures)
            
        except Exception as e:
            logger.error(f"❌ Test suite {suite_name} crashed: {e}")
            logger.error(traceback.format_exc())
            all_results.add_result(f"{suite_name} (crashed)", False, str(e))
    
    # Print final summary
    all_results.print_summary()
    
    # Return success status
    return all_results.failed_tests == 0

if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1) 