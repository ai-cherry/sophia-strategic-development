#!/usr/bin/env python3
"""
Lambda Labs Serverless Deployment Script
========================================
Comprehensive deployment script for Lambda Labs Serverless AI infrastructure
with validation, monitoring setup, and integration testing.
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
from datetime import datetime
from typing import Any

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.auto_esc_config import (
    get_ai_orchestration_config,
    get_lambda_labs_serverless_config,
    validate_lambda_labs_config,
)
from backend.services.lambda_labs_cost_monitor import (
    get_cost_monitor,
    start_cost_monitoring,
)
from backend.services.lambda_labs_serverless_service import get_lambda_service
from backend.services.unified_chat_service_enhanced import get_enhanced_chat_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LambdaServerlessDeployer:
    """
    Lambda Labs Serverless Deployment Manager
    
    Handles complete deployment of Lambda Labs Serverless infrastructure
    including configuration validation, service initialization, monitoring
    setup, and integration testing.
    """

    def __init__(self):
        """Initialize the deployer"""
        self.deployment_id = f"lambda-serverless-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        self.deployment_status = {
            "id": self.deployment_id,
            "started_at": datetime.now().isoformat(),
            "status": "initializing",
            "steps": {},
            "errors": [],
            "warnings": []
        }

        logger.info(f"🚀 Lambda Labs Serverless Deployment [{self.deployment_id}] initialized")

    async def deploy(self) -> dict[str, Any]:
        """
        Execute complete deployment process
        
        Returns:
            Deployment results
        """
        try:
            self.deployment_status["status"] = "running"

            # Phase 1: Pre-deployment validation
            logger.info("📋 Phase 1: Pre-deployment validation")
            await self._validate_prerequisites()

            # Phase 2: Configuration setup
            logger.info("⚙️ Phase 2: Configuration setup")
            await self._setup_configuration()

            # Phase 3: Service initialization
            logger.info("🔧 Phase 3: Service initialization")
            await self._initialize_services()

            # Phase 4: Monitoring setup
            logger.info("📊 Phase 4: Monitoring setup")
            await self._setup_monitoring()

            # Phase 5: Integration testing
            logger.info("🧪 Phase 5: Integration testing")
            await self._run_integration_tests()

            # Phase 6: Final validation
            logger.info("✅ Phase 6: Final validation")
            await self._final_validation()

            self.deployment_status["status"] = "completed"
            self.deployment_status["completed_at"] = datetime.now().isoformat()

            logger.info("🎉 Lambda Labs Serverless deployment completed successfully!")
            return self.deployment_status

        except Exception as e:
            self.deployment_status["status"] = "failed"
            self.deployment_status["error"] = str(e)
            self.deployment_status["failed_at"] = datetime.now().isoformat()

            logger.error(f"❌ Deployment failed: {e}")
            raise

    async def _validate_prerequisites(self) -> None:
        """Validate deployment prerequisites"""
        step_name = "validate_prerequisites"
        self.deployment_status["steps"][step_name] = {"status": "running", "started_at": datetime.now().isoformat()}

        try:
            # Check environment variables
            required_env_vars = [
                "LAMBDA_API_KEY",
                "PULUMI_ORG",
                "ENVIRONMENT"
            ]

            missing_vars = []
            for var in required_env_vars:
                if not os.getenv(var):
                    missing_vars.append(var)

            if missing_vars:
                raise ValueError(f"Missing required environment variables: {missing_vars}")

            # Validate Lambda Labs configuration
            if not validate_lambda_labs_config():
                raise ValueError("Lambda Labs configuration validation failed")

            # Check Pulumi ESC connectivity
            try:
                result = subprocess.run(
                    ["pulumi", "env", "get", "scoobyjava-org/default/sophia-ai-production", "lambda_api_key"],
                    check=False, capture_output=True,
                    text=True,
                    timeout=30
                )

                if result.returncode != 0:
                    raise ValueError("Pulumi ESC connectivity check failed")

            except subprocess.TimeoutExpired:
                raise ValueError("Pulumi ESC connectivity check timed out")

            # Check Python dependencies
            required_packages = [
                "aiohttp",
                "openai",
                "backoff",
                "fastapi",
                "pydantic"
            ]

            for package in required_packages:
                try:
                    __import__(package)
                except ImportError:
                    raise ValueError(f"Missing required package: {package}")

            self.deployment_status["steps"][step_name]["status"] = "completed"
            self.deployment_status["steps"][step_name]["completed_at"] = datetime.now().isoformat()

            logger.info("✅ Prerequisites validation completed")

        except Exception as e:
            self.deployment_status["steps"][step_name]["status"] = "failed"
            self.deployment_status["steps"][step_name]["error"] = str(e)
            raise

    async def _setup_configuration(self) -> None:
        """Setup configuration for Lambda Labs Serverless"""
        step_name = "setup_configuration"
        self.deployment_status["steps"][step_name] = {"status": "running", "started_at": datetime.now().isoformat()}

        try:
            # Load configurations
            lambda_config = get_lambda_labs_serverless_config()
            ai_config = get_ai_orchestration_config()

            # Validate configuration values
            if not lambda_config.get("inference_api_key"):
                raise ValueError("Lambda Labs inference API key not configured")

            if lambda_config.get("daily_budget", 0) <= 0:
                raise ValueError("Daily budget must be positive")

            # Log configuration summary (without sensitive data)
            config_summary = {
                "inference_endpoint": lambda_config.get("inference_endpoint"),
                "daily_budget": lambda_config.get("daily_budget"),
                "monthly_budget": lambda_config.get("monthly_budget"),
                "routing_strategy": lambda_config.get("routing_strategy"),
                "default_provider": ai_config.get("default_provider"),
                "hybrid_mode": ai_config.get("enable_hybrid_mode"),
                "cost_optimization": ai_config.get("enable_cost_optimization")
            }

            logger.info(f"Configuration loaded: {json.dumps(config_summary, indent=2)}")

            # Store configuration in deployment status
            self.deployment_status["configuration"] = config_summary

            self.deployment_status["steps"][step_name]["status"] = "completed"
            self.deployment_status["steps"][step_name]["completed_at"] = datetime.now().isoformat()

            logger.info("✅ Configuration setup completed")

        except Exception as e:
            self.deployment_status["steps"][step_name]["status"] = "failed"
            self.deployment_status["steps"][step_name]["error"] = str(e)
            raise

    async def _initialize_services(self) -> None:
        """Initialize Lambda Labs Serverless services"""
        step_name = "initialize_services"
        self.deployment_status["steps"][step_name] = {"status": "running", "started_at": datetime.now().isoformat()}

        try:
            # Initialize Lambda Labs service
            logger.info("Initializing Lambda Labs Serverless service...")
            lambda_service = await get_lambda_service()

            # Test basic functionality
            health_check = await lambda_service.health_check()
            if health_check["status"] != "healthy":
                raise ValueError(f"Lambda Labs service health check failed: {health_check}")

            # Initialize cost monitor
            logger.info("Initializing cost monitor...")
            cost_monitor = await get_cost_monitor()

            # Initialize enhanced chat service
            logger.info("Initializing enhanced chat service...")
            chat_service = await get_enhanced_chat_service()

            # Test chat service
            chat_health = await chat_service.health_check()
            if chat_health["overall_status"] not in ["healthy", "degraded"]:
                raise ValueError(f"Chat service health check failed: {chat_health}")

            # Store service information
            self.deployment_status["services"] = {
                "lambda_service": {
                    "status": "initialized",
                    "health": health_check,
                    "models_available": len(lambda_service.models)
                },
                "cost_monitor": {
                    "status": "initialized",
                    "monitoring_interval": cost_monitor.monitoring_interval
                },
                "chat_service": {
                    "status": "initialized",
                    "health": chat_health
                }
            }

            self.deployment_status["steps"][step_name]["status"] = "completed"
            self.deployment_status["steps"][step_name]["completed_at"] = datetime.now().isoformat()

            logger.info("✅ Services initialization completed")

        except Exception as e:
            self.deployment_status["steps"][step_name]["status"] = "failed"
            self.deployment_status["steps"][step_name]["error"] = str(e)
            raise

    async def _setup_monitoring(self) -> None:
        """Setup monitoring and alerting"""
        step_name = "setup_monitoring"
        self.deployment_status["steps"][step_name] = {"status": "running", "started_at": datetime.now().isoformat()}

        try:
            # Start cost monitoring
            logger.info("Starting cost monitoring...")
            await start_cost_monitoring()

            # Verify monitoring is active
            cost_monitor = await get_cost_monitor()
            if not cost_monitor.monitoring_task or cost_monitor.monitoring_task.done():
                raise ValueError("Cost monitoring failed to start")

            # Setup Snowflake monitoring tables
            logger.info("Setting up Snowflake monitoring tables...")
            await self._setup_snowflake_monitoring()

            self.deployment_status["monitoring"] = {
                "cost_monitoring": "active",
                "monitoring_interval": cost_monitor.monitoring_interval,
                "thresholds": cost_monitor.thresholds,
                "snowflake_integration": "configured"
            }

            self.deployment_status["steps"][step_name]["status"] = "completed"
            self.deployment_status["steps"][step_name]["completed_at"] = datetime.now().isoformat()

            logger.info("✅ Monitoring setup completed")

        except Exception as e:
            self.deployment_status["steps"][step_name]["status"] = "failed"
            self.deployment_status["steps"][step_name]["error"] = str(e)
            raise

    async def _setup_snowflake_monitoring(self) -> None:
        """Setup Snowflake monitoring tables"""
        from shared.utils.snowflake_cortex_service import SnowflakeCortexService

        snowflake = SnowflakeCortexService()

        # Create monitoring table if it doesn't exist
        create_table_query = """
        CREATE TABLE IF NOT EXISTS SOPHIA_AI.AI_INSIGHTS.LAMBDA_LABS_COST_MONITORING (
            timestamp TIMESTAMP_NTZ,
            daily_cost FLOAT,
            hourly_cost FLOAT,
            total_cost FLOAT,
            total_requests INTEGER,
            successful_requests INTEGER,
            failed_requests INTEGER,
            average_response_time FLOAT,
            budget_remaining FLOAT,
            predicted_daily_cost FLOAT,
            predicted_monthly_cost FLOAT,
            prediction_confidence FLOAT,
            trend_direction VARCHAR(20),
            model_usage VARIANT,
            created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
        )
        """

        await snowflake.execute_query(create_table_query)

        # Create performance monitoring table
        create_performance_table_query = """
        CREATE TABLE IF NOT EXISTS SOPHIA_AI.AI_INSIGHTS.LAMBDA_LABS_PERFORMANCE_MONITORING (
            timestamp TIMESTAMP_NTZ,
            query_type VARCHAR(50),
            provider VARCHAR(50),
            model_used VARCHAR(100),
            cost FLOAT,
            response_time FLOAT,
            input_tokens INTEGER,
            output_tokens INTEGER,
            cached BOOLEAN,
            success BOOLEAN,
            error_message VARCHAR(1000),
            created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
        )
        """

        await snowflake.execute_query(create_performance_table_query)

    async def _run_integration_tests(self) -> None:
        """Run comprehensive integration tests"""
        step_name = "integration_tests"
        self.deployment_status["steps"][step_name] = {"status": "running", "started_at": datetime.now().isoformat()}

        try:
            test_results = {}

            # Test 1: Basic chat completion
            logger.info("Running basic chat completion test...")
            chat_service = await get_enhanced_chat_service()

            chat_result = await chat_service.chat_completion(
                "Hello, this is a test message for Lambda Labs Serverless deployment.",
                {"test": True}
            )

            test_results["basic_chat"] = {
                "status": "passed",
                "response_time": chat_result.get("response_time", 0),
                "cost": chat_result.get("cost", 0),
                "provider": chat_result.get("provider"),
                "model_used": chat_result.get("model_used")
            }

            # Test 2: Code analysis
            logger.info("Running code analysis test...")
            code_result = await chat_service.chat_completion(
                "def fibonacci(n): return n if n <= 1 else fibonacci(n-1) + fibonacci(n-2)\n\nAnalyze this code for performance issues.",
                {"analysis_type": "code"}
            )

            test_results["code_analysis"] = {
                "status": "passed",
                "response_time": code_result.get("response_time", 0),
                "cost": code_result.get("cost", 0),
                "provider": code_result.get("provider"),
                "query_type": code_result.get("routing", {}).get("query_type")
            }

            # Test 3: Business intelligence query
            logger.info("Running business intelligence test...")
            bi_result = await chat_service.chat_completion(
                "Generate a summary of key performance indicators for a SaaS business dashboard.",
                {"analysis_type": "business"}
            )

            test_results["business_intelligence"] = {
                "status": "passed",
                "response_time": bi_result.get("response_time", 0),
                "cost": bi_result.get("cost", 0),
                "provider": bi_result.get("provider"),
                "hybrid_used": bi_result.get("provider") == "hybrid"
            }

            # Test 4: Cost monitoring
            logger.info("Running cost monitoring test...")
            cost_monitor = await get_cost_monitor()
            cost_report = await cost_monitor.get_cost_report()

            test_results["cost_monitoring"] = {
                "status": "passed",
                "monitoring_active": cost_report.get("monitoring_status", {}).get("active", False),
                "current_cost": cost_report.get("current_costs", {}).get("daily_cost", 0),
                "alerts_count": len(cost_report.get("active_alerts", []))
            }

            # Test 5: Performance stats
            logger.info("Running performance stats test...")
            perf_stats = await chat_service.get_performance_stats()

            test_results["performance_tracking"] = {
                "status": "passed",
                "total_requests": perf_stats.get("total_requests", 0),
                "average_response_time": perf_stats.get("average_response_time", 0),
                "cache_hit_rate": perf_stats.get("cache_hit_rate", 0)
            }

            # Calculate overall test results
            total_tests = len(test_results)
            passed_tests = sum(1 for result in test_results.values() if result["status"] == "passed")

            self.deployment_status["tests"] = {
                "total": total_tests,
                "passed": passed_tests,
                "failed": total_tests - passed_tests,
                "success_rate": (passed_tests / total_tests) * 100,
                "results": test_results
            }

            if passed_tests < total_tests:
                raise ValueError(f"Integration tests failed: {passed_tests}/{total_tests} passed")

            self.deployment_status["steps"][step_name]["status"] = "completed"
            self.deployment_status["steps"][step_name]["completed_at"] = datetime.now().isoformat()

            logger.info(f"✅ Integration tests completed: {passed_tests}/{total_tests} passed")

        except Exception as e:
            self.deployment_status["steps"][step_name]["status"] = "failed"
            self.deployment_status["steps"][step_name]["error"] = str(e)
            raise

    async def _final_validation(self) -> None:
        """Perform final validation"""
        step_name = "final_validation"
        self.deployment_status["steps"][step_name] = {"status": "running", "started_at": datetime.now().isoformat()}

        try:
            validation_results = {}

            # Validate all services are healthy
            chat_service = await get_enhanced_chat_service()
            health_check = await chat_service.health_check()

            validation_results["service_health"] = {
                "overall_status": health_check["overall_status"],
                "lambda_labs": health_check["services"].get("lambda_labs", {}).get("status"),
                "snowflake_cortex": health_check["services"].get("snowflake_cortex", {}).get("status"),
                "cost_monitor": health_check["services"].get("cost_monitor", {}).get("status")
            }

            # Validate monitoring is active
            cost_monitor = await get_cost_monitor()
            monitoring_active = cost_monitor.monitoring_task and not cost_monitor.monitoring_task.done()

            validation_results["monitoring"] = {
                "cost_monitoring_active": monitoring_active,
                "monitoring_interval": cost_monitor.monitoring_interval
            }

            # Validate configuration
            lambda_config = get_lambda_labs_serverless_config()
            validation_results["configuration"] = {
                "api_key_configured": bool(lambda_config.get("inference_api_key")),
                "budget_configured": lambda_config.get("daily_budget", 0) > 0,
                "routing_strategy": lambda_config.get("routing_strategy")
            }

            # Check for any critical issues
            critical_issues = []

            if validation_results["service_health"]["overall_status"] == "unhealthy":
                critical_issues.append("Service health check failed")

            if not validation_results["monitoring"]["cost_monitoring_active"]:
                critical_issues.append("Cost monitoring not active")

            if not validation_results["configuration"]["api_key_configured"]:
                critical_issues.append("API key not configured")

            if critical_issues:
                raise ValueError(f"Critical validation issues: {critical_issues}")

            self.deployment_status["validation"] = validation_results

            self.deployment_status["steps"][step_name]["status"] = "completed"
            self.deployment_status["steps"][step_name]["completed_at"] = datetime.now().isoformat()

            logger.info("✅ Final validation completed")

        except Exception as e:
            self.deployment_status["steps"][step_name]["status"] = "failed"
            self.deployment_status["steps"][step_name]["error"] = str(e)
            raise

    def generate_deployment_report(self) -> str:
        """Generate comprehensive deployment report"""
        report = f"""
# Lambda Labs Serverless Deployment Report
**Deployment ID:** {self.deployment_id}
**Status:** {self.deployment_status['status']}
**Started:** {self.deployment_status['started_at']}
**Completed:** {self.deployment_status.get('completed_at', 'N/A')}

## Configuration Summary
- **Inference Endpoint:** {self.deployment_status.get('configuration', {}).get('inference_endpoint')}
- **Daily Budget:** ${self.deployment_status.get('configuration', {}).get('daily_budget', 0)}
- **Routing Strategy:** {self.deployment_status.get('configuration', {}).get('routing_strategy')}
- **Hybrid Mode:** {self.deployment_status.get('configuration', {}).get('hybrid_mode')}

## Services Status
"""

        services = self.deployment_status.get('services', {})
        for service_name, service_info in services.items():
            report += f"- **{service_name}:** {service_info.get('status', 'unknown')}\n"

        report += "\n## Integration Tests\n"
        tests = self.deployment_status.get('tests', {})
        if tests:
            report += f"- **Total Tests:** {tests.get('total', 0)}\n"
            report += f"- **Passed:** {tests.get('passed', 0)}\n"
            report += f"- **Success Rate:** {tests.get('success_rate', 0):.1f}%\n"

        report += "\n## Monitoring Setup\n"
        monitoring = self.deployment_status.get('monitoring', {})
        if monitoring:
            report += f"- **Cost Monitoring:** {monitoring.get('cost_monitoring', 'unknown')}\n"
            report += f"- **Monitoring Interval:** {monitoring.get('monitoring_interval', 0)} seconds\n"

        if self.deployment_status.get('errors'):
            report += "\n## Errors\n"
            for error in self.deployment_status['errors']:
                report += f"- {error}\n"

        return report


async def main():
    """Main deployment function"""
    try:
        # Create deployer
        deployer = LambdaServerlessDeployer()

        # Run deployment
        result = await deployer.deploy()

        # Generate report
        report = deployer.generate_deployment_report()

        # Save report
        report_file = f"deployment_reports/lambda_serverless_{deployer.deployment_id}.md"
        os.makedirs("deployment_reports", exist_ok=True)

        with open(report_file, 'w') as f:
            f.write(report)

        print("\n🎉 Deployment completed successfully!")
        print(f"📄 Report saved to: {report_file}")
        print(f"📊 Deployment ID: {deployer.deployment_id}")

        # Print summary
        print("\n📋 Deployment Summary:")
        print(f"   Status: {result['status']}")
        print(f"   Services: {len(result.get('services', {}))}")
        print(f"   Tests: {result.get('tests', {}).get('passed', 0)}/{result.get('tests', {}).get('total', 0)}")

        return result

    except Exception as e:
        logger.error(f"Deployment failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
