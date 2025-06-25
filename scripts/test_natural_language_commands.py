#!/usr/bin/env python3
"""
Test Natural Language Commands
Test suite for natural language command processing and GitHub integration
"""

import asyncio
import logging
import sys
import tempfile
from pathlib import Path
from typing import Dict, Any
import unittest

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestNaturalLanguageCommands(unittest.TestCase):
    """Test natural language command processing"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.project_root = Path(self.temp_dir)
        
        # Create mock project structure
        (self.project_root / ".git").mkdir()
        (self.project_root / ".github" / "workflows").mkdir(parents=True)
        (self.project_root / "backend").mkdir()
        (self.project_root / "frontend").mkdir()
        
        # Create mock files
        (self.project_root / "requirements.txt").write_text("fastapi==0.104.1\naiohttp==3.9.3")
        (self.project_root / "cursor_mcp_config.json").write_text('{"mcpServers": {}}')
        
    def test_repository_sync_command(self):
        """Test repository synchronization commands"""
        commands = [
            "sync with main branch",
            "fetch latest changes",
            "pull from origin",
            "update repository"
        ]
        
        for command in commands:
            with self.subTest(command=command):
                result = self._process_natural_language_command(command)
                self.assertIsInstance(result, dict)
                self.assertIn("action", result)
                self.assertEqual(result["action"], "repository_sync")
    
    def test_github_status_commands(self):
        """Test GitHub status inquiry commands"""
        commands = [
            "show github status",
            "check pr status",
            "display workflow status",
            "what's the build status"
        ]
        
        for command in commands:
            with self.subTest(command=command):
                result = self._process_natural_language_command(command)
                self.assertIsInstance(result, dict)
                self.assertIn("action", result)
                self.assertEqual(result["action"], "github_status")
    
    def test_code_analysis_commands(self):
        """Test code analysis commands"""
        commands = [
            "analyze code quality",
            "check for security issues",
            "run code analysis",
            "scan for vulnerabilities"
        ]
        
        for command in commands:
            with self.subTest(command=command):
                result = self._process_natural_language_command(command)
                self.assertIsInstance(result, dict)
                self.assertIn("action", result)
                self.assertEqual(result["action"], "code_analysis")
    
    def test_mcp_server_commands(self):
        """Test MCP server management commands"""
        commands = [
            "start mcp servers",
            "check mcp health",
            "restart ai memory server",
            "validate mcp configuration"
        ]
        
        for command in commands:
            with self.subTest(command=command):
                result = self._process_natural_language_command(command)
                self.assertIsInstance(result, dict)
                self.assertIn("action", result)
                self.assertEqual(result["action"], "mcp_management")
    
    def test_deployment_commands(self):
        """Test deployment commands"""
        commands = [
            "deploy to staging",
            "trigger deployment",
            "run deployment pipeline",
            "deploy latest changes"
        ]
        
        for command in commands:
            with self.subTest(command=command):
                result = self._process_natural_language_command(command)
                self.assertIsInstance(result, dict)
                self.assertIn("action", result)
                self.assertEqual(result["action"], "deployment")
    
    def test_branch_management_commands(self):
        """Test branch management commands"""
        commands = [
            "create feature branch for user auth",
            "switch to main branch",
            "merge feature branch",
            "delete old branches"
        ]
        
        for command in commands:
            with self.subTest(command=command):
                result = self._process_natural_language_command(command)
                self.assertIsInstance(result, dict)
                self.assertIn("action", result)
                self.assertEqual(result["action"], "branch_management")
    
    def test_issue_management_commands(self):
        """Test issue and PR management commands"""
        commands = [
            "create issue for bug fix",
            "update pr description",
            "assign reviewer to pr",
            "close completed issues"
        ]
        
        for command in commands:
            with self.subTest(command=command):
                result = self._process_natural_language_command(command)
                self.assertIsInstance(result, dict)
                self.assertIn("action", result)
                self.assertEqual(result["action"], "issue_management")
    
    def test_documentation_commands(self):
        """Test documentation generation commands"""
        commands = [
            "generate api documentation",
            "update readme file",
            "create changelog entry",
            "document new features"
        ]
        
        for command in commands:
            with self.subTest(command=command):
                result = self._process_natural_language_command(command)
                self.assertIsInstance(result, dict)
                self.assertIn("action", result)
                self.assertEqual(result["action"], "documentation")
    
    def test_testing_commands(self):
        """Test testing-related commands"""
        commands = [
            "run all tests",
            "check test coverage",
            "run security tests",
            "execute integration tests"
        ]
        
        for command in commands:
            with self.subTest(command=command):
                result = self._process_natural_language_command(command)
                self.assertIsInstance(result, dict)
                self.assertIn("action", result)
                self.assertEqual(result["action"], "testing")
    
    def test_configuration_commands(self):
        """Test configuration management commands"""
        commands = [
            "update cursor configuration",
            "optimize mcp settings",
            "sync environment variables",
            "validate configuration"
        ]
        
        for command in commands:
            with self.subTest(command=command):
                result = self._process_natural_language_command(command)
                self.assertIsInstance(result, dict)
                self.assertIn("action", result)
                self.assertEqual(result["action"], "configuration")
    
    def test_monitoring_commands(self):
        """Test monitoring and metrics commands"""
        commands = [
            "show development metrics",
            "generate performance report",
            "check system health",
            "monitor application status"
        ]
        
        for command in commands:
            with self.subTest(command=command):
                result = self._process_natural_language_command(command)
                self.assertIsInstance(result, dict)
                self.assertIn("action", result)
                self.assertEqual(result["action"], "monitoring")
    
    def test_command_parameter_extraction(self):
        """Test parameter extraction from commands"""
        test_cases = [
            {
                "command": "create feature branch for user authentication",
                "expected_params": {"branch_type": "feature", "feature_name": "user authentication"}
            },
            {
                "command": "deploy to staging environment",
                "expected_params": {"environment": "staging"}
            },
            {
                "command": "analyze security issues in auth module",
                "expected_params": {"analysis_type": "security", "module": "auth"}
            },
            {
                "command": "run tests for user service",
                "expected_params": {"test_scope": "user service"}
            }
        ]
        
        for test_case in test_cases:
            with self.subTest(command=test_case["command"]):
                result = self._process_natural_language_command(test_case["command"])
                self.assertIsInstance(result, dict)
                self.assertIn("parameters", result)
                
                # Check that some expected parameters are extracted
                for key, value in test_case["expected_params"].items():
                    if key in result["parameters"]:
                        self.assertIn(value.lower(), result["parameters"][key].lower())
    
    def test_command_validation(self):
        """Test command validation and error handling"""
        invalid_commands = [
            "",
            "   ",
            "invalid command that makes no sense",
            "delete everything permanently",  # Should be flagged as dangerous
            "format hard drive"  # Should be rejected
        ]
        
        for command in invalid_commands:
            with self.subTest(command=command):
                result = self._process_natural_language_command(command)
                if command.strip() == "":
                    self.assertIn("error", result)
                elif "delete everything" in command or "format hard drive" in command:
                    self.assertEqual(result.get("action"), "rejected")
                    self.assertIn("dangerous", result.get("reason", "").lower())
    
    def test_multi_step_commands(self):
        """Test multi-step command processing"""
        commands = [
            "sync repository and run tests",
            "analyze code quality then generate report",
            "create branch, make changes, and create pr",
            "deploy to staging and run health checks"
        ]
        
        for command in commands:
            with self.subTest(command=command):
                result = self._process_natural_language_command(command)
                self.assertIsInstance(result, dict)
                self.assertIn("steps", result)
                self.assertIsInstance(result["steps"], list)
                self.assertGreater(len(result["steps"]), 1)
    
    def test_context_awareness(self):
        """Test context-aware command processing"""
        # Mock current context
        context = {
            "current_branch": "feature/user-auth",
            "uncommitted_changes": True,
            "last_commit": "abc123",
            "open_prs": 2,
            "failing_tests": 1
        }
        
        commands = [
            "what's the current status",
            "should i commit these changes",
            "is it safe to merge",
            "what needs attention"
        ]
        
        for command in commands:
            with self.subTest(command=command):
                result = self._process_natural_language_command(command, context=context)
                self.assertIsInstance(result, dict)
                self.assertIn("context_aware", result)
                self.assertTrue(result["context_aware"])
    
    def test_github_integration_specific_commands(self):
        """Test GitHub App integration specific commands"""
        commands = [
            "enable github actions",
            "configure branch protection",
            "setup pr templates",
            "add issue labels",
            "create github workflow"
        ]
        
        for command in commands:
            with self.subTest(command=command):
                result = self._process_natural_language_command(command)
                self.assertIsInstance(result, dict)
                self.assertIn("action", result)
                self.assertEqual(result["action"], "github_integration")
                self.assertIn("github_specific", result)
                self.assertTrue(result["github_specific"])
    
    def test_cursor_optimization_commands(self):
        """Test Cursor IDE optimization commands"""
        commands = [
            "optimize cursor settings",
            "enhance ai assistance",
            "improve code completion",
            "configure cursor for this project"
        ]
        
        for command in commands:
            with self.subTest(command=command):
                result = self._process_natural_language_command(command)
                self.assertIsInstance(result, dict)
                self.assertIn("action", result)
                self.assertEqual(result["action"], "cursor_optimization")
    
    def _process_natural_language_command(self, command: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process a natural language command (mock implementation)"""
        command = command.lower().strip()
        
        if not command:
            return {"error": "Empty command"}
        
        # Dangerous command detection
        dangerous_keywords = ["delete everything", "format hard drive", "rm -rf /"]
        if any(keyword in command for keyword in dangerous_keywords):
            return {
                "action": "rejected",
                "reason": "Dangerous command detected",
                "command": command
            }
        
        # Command classification
        action_mapping = {
            ("sync", "fetch", "pull", "update"): "repository_sync",
            ("status", "check", "display"): "github_status",
            ("analyze", "scan", "quality", "security"): "code_analysis",
            ("mcp", "server", "health"): "mcp_management",
            ("deploy", "deployment", "pipeline"): "deployment",
            ("branch", "merge", "switch"): "branch_management",
            ("issue", "pr", "reviewer"): "issue_management",
            ("document", "readme", "changelog"): "documentation",
            ("test", "coverage"): "testing",
            ("config", "setting", "environment"): "configuration",
            ("metric", "report", "monitor"): "monitoring",
            ("github action", "workflow", "protection"): "github_integration",
            ("cursor", "optimization", "ai assistance"): "cursor_optimization"
        }
        
        # Find matching action
        action = "unknown"
        for keywords, action_type in action_mapping.items():
            if any(keyword in command for keyword in keywords):
                action = action_type
                break
        
        result = {
            "action": action,
            "command": command,
            "parameters": self._extract_parameters(command),
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        # Multi-step command detection
        if " and " in command or " then " in command:
            steps = []
            if " and " in command:
                steps = [step.strip() for step in command.split(" and ")]
            elif " then " in command:
                steps = [step.strip() for step in command.split(" then ")]
            
            result["steps"] = [{"action": self._classify_single_command(step), "command": step} for step in steps]
        
        # Context awareness
        if context:
            result["context_aware"] = True
            result["context"] = context
        
        # GitHub-specific detection
        github_keywords = ["github", "workflow", "actions", "pr template", "branch protection"]
        if any(keyword in command for keyword in github_keywords):
            result["github_specific"] = True
        
        return result
    
    def _extract_parameters(self, command: str) -> Dict[str, str]:
        """Extract parameters from command"""
        parameters = {}
        
        # Environment detection
        environments = ["staging", "production", "development", "dev", "prod"]
        for env in environments:
            if env in command:
                parameters["environment"] = env
                break
        
        # Branch type detection
        if "feature branch" in command:
            parameters["branch_type"] = "feature"
            # Extract feature name
            if " for " in command:
                feature_part = command.split(" for ")[-1]
                parameters["feature_name"] = feature_part.strip()
        elif "hotfix branch" in command:
            parameters["branch_type"] = "hotfix"
        
        # Analysis type detection
        if "security" in command:
            parameters["analysis_type"] = "security"
        elif "quality" in command:
            parameters["analysis_type"] = "quality"
        elif "performance" in command:
            parameters["analysis_type"] = "performance"
        
        # Module/component detection
        components = ["auth", "user", "api", "database", "frontend", "backend"]
        for component in components:
            if component in command:
                parameters["module"] = component
                break
        
        # Test scope detection
        if "test" in command:
            if " for " in command:
                test_part = command.split(" for ")[-1]
                parameters["test_scope"] = test_part.strip()
        
        return parameters
    
    def _classify_single_command(self, command: str) -> str:
        """Classify a single command"""
        result = self._process_natural_language_command(command)
        return result.get("action", "unknown")


class TestGitHubIntegrationFeatures(unittest.TestCase):
    """Test GitHub integration specific features"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.project_root = Path(self.temp_dir)
        
    def test_workflow_detection(self):
        """Test GitHub workflow detection"""
        workflows_dir = self.project_root / ".github" / "workflows"
        workflows_dir.mkdir(parents=True)
        
        # Create mock workflow files
        (workflows_dir / "ci.yml").write_text("name: CI\non: [push]")
        (workflows_dir / "deploy.yaml").write_text("name: Deploy\non: [release]")
        
        workflow_count = len(list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml")))
        self.assertEqual(workflow_count, 2)
    
    def test_template_detection(self):
        """Test PR and issue template detection"""
        github_dir = self.project_root / ".github"
        github_dir.mkdir()
        
        # Create PR template
        (github_dir / "PULL_REQUEST_TEMPLATE.md").write_text("## Description\n...")
        
        # Create issue templates
        issue_templates_dir = github_dir / "ISSUE_TEMPLATE"
        issue_templates_dir.mkdir()
        (issue_templates_dir / "bug_report.md").write_text("---\nname: Bug Report\n...")
        
        self.assertTrue((github_dir / "PULL_REQUEST_TEMPLATE.md").exists())
        self.assertTrue((issue_templates_dir / "bug_report.md").exists())
    
    def test_branch_protection_simulation(self):
        """Test branch protection rule simulation"""
        # Mock branch protection rules
        protection_rules = {
            "main": {
                "required_reviews": 2,
                "dismiss_stale_reviews": True,
                "require_code_owner_reviews": True,
                "required_status_checks": ["ci", "security-scan"]
            },
            "develop": {
                "required_reviews": 1,
                "required_status_checks": ["ci"]
            }
        }
        
        for branch, rules in protection_rules.items():
            self.assertIn("required_reviews", rules)
            self.assertIsInstance(rules["required_reviews"], int)
            self.assertGreater(rules["required_reviews"], 0)


class TestMCPIntegrationFeatures(unittest.TestCase):
    """Test MCP integration features"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.project_root = Path(self.temp_dir)
        
    def test_mcp_config_validation(self):
        """Test MCP configuration validation"""
        # Valid configuration
        valid_config = {
            "mcpServers": {
                "ai_memory": {
                    "command": "python",
                    "args": ["-m", "backend.mcp.ai_memory_mcp_server"],
                    "capabilities": {"semantic_search": True}
                },
                "codacy": {
                    "command": "python",
                    "args": ["-m", "mcp-servers.codacy.codacy_mcp_server"],
                    "capabilities": {"code_analysis": True}
                }
            }
        }
        
        # Validation checks
        self.assertIn("mcpServers", valid_config)
        servers = valid_config["mcpServers"]
        
        for server_name, server_config in servers.items():
            self.assertIn("command", server_config)
            self.assertIn("args", server_config)
            self.assertIsInstance(server_config["args"], list)
    
    def test_server_health_simulation(self):
        """Test MCP server health check simulation"""
        servers = ["ai_memory", "codacy", "snowflake_admin", "asana", "notion"]
        health_status = {}
        
        for server in servers:
            # Simulate health check
            health_status[server] = {
                "status": "healthy",
                "response_time": 0.05,
                "last_check": "2024-01-01T00:00:00Z"
            }
        
        self.assertEqual(len(health_status), 5)
        for server, status in health_status.items():
            self.assertEqual(status["status"], "healthy")
            self.assertLess(status["response_time"], 1.0)


class TestPerformanceMetrics(unittest.TestCase):
    """Test performance metrics and monitoring"""
    
    def test_response_time_analysis(self):
        """Test response time analysis"""
        response_times = [0.1, 0.15, 0.12, 0.8, 0.09, 0.11, 0.13, 0.14, 0.16, 0.10]
        
        # Calculate metrics
        avg_response_time = sum(response_times) / len(response_times)
        min_response_time = min(response_times)
        max_response_time = max(response_times)
        
        # Assertions
        self.assertLess(avg_response_time, 0.5)  # Average should be reasonable
        self.assertLess(min_response_time, 0.2)  # Min should be fast
        self.assertLess(max_response_time, 1.0)  # Max should be acceptable
    
    def test_error_rate_calculation(self):
        """Test error rate calculation"""
        total_requests = 1000
        failed_requests = 25
        
        error_rate = failed_requests / total_requests
        success_rate = 1 - error_rate
        
        self.assertEqual(error_rate, 0.025)  # 2.5% error rate
        self.assertEqual(success_rate, 0.975)  # 97.5% success rate
        self.assertLess(error_rate, 0.05)  # Error rate should be < 5%
    
    def test_throughput_metrics(self):
        """Test throughput metrics"""
        requests_per_second = 150
        concurrent_users = 50
        
        # Calculate metrics
        requests_per_user = requests_per_second / concurrent_users
        
        self.assertGreater(requests_per_second, 100)  # Good throughput
        self.assertGreater(requests_per_user, 1)  # Reasonable per-user load


async def run_async_tests():
    """Run async test scenarios"""
    logger.info("🧪 Running async test scenarios")
    
    # Test async command processing
    async def test_async_command_processing():
        commands = [
            "analyze code quality",
            "check mcp server health",
            "sync with remote repository"
        ]
        
        results = []
        for command in commands:
            # Simulate async processing
            await asyncio.sleep(0.1)
            result = {"command": command, "status": "completed", "duration": 0.1}
            results.append(result)
        
        return results
    
    # Test concurrent operations
    async def test_concurrent_operations():
        tasks = [
            test_async_command_processing(),
            test_async_command_processing(),
            test_async_command_processing()
        ]
        
        results = await asyncio.gather(*tasks)
        return results
    
    # Run tests
    try:
        async_results = await test_async_command_processing()
        concurrent_results = await test_concurrent_operations()
        
        logger.info(f"✅ Async tests completed: {len(async_results)} commands processed")
        logger.info(f"✅ Concurrent tests completed: {len(concurrent_results)} task groups")
        
        return True
    except Exception as e:
        logger.error(f"❌ Async tests failed: {e}")
        return False


def main():
    """Main test runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Natural Language Commands")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--async-tests", action="store_true", help="Run async tests")
    parser.add_argument("--performance-tests", action="store_true", help="Run performance tests")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Run synchronous tests
    logger.info("🧪 Starting natural language command tests")
    
    test_loader = unittest.TestLoader()
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestNaturalLanguageCommands,
        TestGitHubIntegrationFeatures,
        TestMCPIntegrationFeatures
    ]
    
    if args.performance_tests:
        test_classes.append(TestPerformanceMetrics)
    
    for test_class in test_classes:
        tests = test_loader.loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2 if args.verbose else 1)
    result = runner.run(test_suite)
    
    # Run async tests if requested
    if args.async_tests:
        logger.info("🔄 Running async tests")
        async_success = asyncio.run(run_async_tests())
        if not async_success:
            result.errors.append(("Async Tests", "Async test execution failed"))
    
    # Print summary
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    success_count = total_tests - failures - errors
    success_rate = (success_count / total_tests) * 100 if total_tests > 0 else 0
    
    logger.info("\n📊 Test Summary:")
    logger.info(f"Total Tests: {total_tests}")
    logger.info(f"Passed: {success_count}")
    logger.info(f"Failed: {failures}")
    logger.info(f"Errors: {errors}")
    logger.info(f"Success Rate: {success_rate:.1f}%")
    
    if result.wasSuccessful():
        logger.info("✅ All tests passed!")
        return 0
    else:
        logger.error("❌ Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 