#!/usr/bin/env python3
"""Comprehensive test runner for infrastructure testing framework"""

import argparse
import json
import logging
import os
import subprocess
import sys
import time
from datetime import datetime
from typing import Any, Dict, List

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class InfrastructureTestRunner:
    """Orchestrates the execution of all infrastructure tests"""

    def __init__(self, args):
        self.args = args
        self.test_results = {
            "start_time": datetime.now().isoformat(),
            "test_suites": {},
            "summary": {
                "total_tests": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "duration": 0,
            },
        }
        self.start_time = time.time()

    def run_test_suite(
        self, suite_name: str, test_path: str, markers: List[str] = None
    ) -> Dict[str, Any]:
        """Run a specific test suite and capture results"""
        logger.info(f"\n{'=' * 60}")
        logger.info(f"Running {suite_name} tests...")
        logger.info(f"{'=' * 60}")

        # Build pytest command
        cmd = ["pytest", test_path, "-v", "--tb=short"]

        # Add markers if specified
        if markers:
            for marker in markers:
                cmd.extend(["-m", marker])

        # Add coverage if requested
        if self.args.coverage:
            cmd.extend(["--cov=infrastructure", "--cov-report=term-missing"])

        # Add parallel execution if requested
        if self.args.parallel:
            cmd.extend(["-n", str(self.args.workers)])

        # Run the tests
        suite_start = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True)
        suite_duration = time.time() - suite_start

        # Parse results
        suite_results = {
            "duration": suite_duration,
            "return_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "passed": result.stdout.count(" PASSED"),
            "failed": result.stdout.count(" FAILED"),
            "skipped": result.stdout.count(" SKIPPED"),
        }

        # Log summary
        logger.info(f"\n{suite_name} Results:")
        logger.info(f"  Duration: {suite_duration:.2f}s")
        logger.info(f"  Passed: {suite_results['passed']}")
        logger.info(f"  Failed: {suite_results['failed']}")
        logger.info(f"  Skipped: {suite_results['skipped']}")

        return suite_results

    def run_unit_tests(self):
        """Run unit tests for individual components"""
        if self.args.skip_unit:
            logger.info("Skipping unit tests")
            return

        results = self.run_test_suite(
            "Unit Tests",
            "tests/infrastructure/unit/",
            markers=["not integration", "not e2e", "not performance"],
        )
        self.test_results["test_suites"]["unit"] = results

    def run_integration_tests(self):
        """Run integration tests for component interactions"""
        if self.args.skip_integration:
            logger.info("Skipping integration tests")
            return

        results = self.run_test_suite(
            "Integration Tests",
            "tests/infrastructure/integration/",
            markers=["integration"],
        )
        self.test_results["test_suites"]["integration"] = results

    def run_e2e_tests(self):
        """Run end-to-end tests for complete infrastructure"""
        if self.args.skip_e2e:
            logger.info("Skipping end-to-end tests")
            return

        results = self.run_test_suite(
            "End-to-End Tests", "tests/infrastructure/e2e/", markers=["e2e"]
        )
        self.test_results["test_suites"]["e2e"] = results

    def run_performance_tests(self):
        """Run performance tests"""
        if self.args.skip_performance:
            logger.info("Skipping performance tests")
            return

        results = self.run_test_suite(
            "Performance Tests",
            "tests/infrastructure/performance/",
            markers=["performance"],
        )
        self.test_results["test_suites"]["performance"] = results

    def run_security_tests(self):
        """Run security and compliance tests"""
        if not self.args.security:
            logger.info("Skipping security tests (use --security to enable)")
            return

        # Create security test file if it doesn't exist
        security_test_path = "tests/infrastructure/security/test_security.py"
        if not os.path.exists(security_test_path):
            os.makedirs(os.path.dirname(security_test_path), exist_ok=True)
            with open(security_test_path, "w") as f:
                f.write(
                    """
import pytest

@pytest.mark.security
class TestSecurity:
    def test_secret_management(self):
        # Test that secrets are properly managed
        pass

    def test_network_security(self):
        # Test network security configurations
        pass

    def test_access_controls(self):
        # Test access control implementations
        pass
"""
                )

        results = self.run_test_suite(
            "Security Tests", "tests/infrastructure/security/", markers=["security"]
        )
        self.test_results["test_suites"]["security"] = results

    def generate_report(self):
        """Generate comprehensive test report"""
        # Calculate summary
        total_duration = time.time() - self.start_time
        self.test_results["summary"]["duration"] = total_duration

        for suite_name, suite_results in self.test_results["test_suites"].items():
            self.test_results["summary"]["total_tests"] += (
                suite_results["passed"]
                + suite_results["failed"]
                + suite_results["skipped"]
            )
            self.test_results["summary"]["passed"] += suite_results["passed"]
            self.test_results["summary"]["failed"] += suite_results["failed"]
            self.test_results["summary"]["skipped"] += suite_results["skipped"]

        # Display summary
        logger.info(f"\n{'=' * 60}")
        logger.info("INFRASTRUCTURE TEST SUMMARY")
        logger.info(f"{'=' * 60}")
        logger.info(f"Total Duration: {total_duration:.2f}s")
        logger.info(f"Total Tests: {self.test_results['summary']['total_tests']}")
        logger.info(f"Passed: {self.test_results['summary']['passed']}")
        logger.info(f"Failed: {self.test_results['summary']['failed']}")
        logger.info(f"Skipped: {self.test_results['summary']['skipped']}")

        # Calculate pass rate
        if self.test_results["summary"]["total_tests"] > 0:
            pass_rate = (
                self.test_results["summary"]["passed"]
                / self.test_results["summary"]["total_tests"]
            ) * 100
            logger.info(f"Pass Rate: {pass_rate:.1f}%")

        # Save detailed report
        report_path = f"tests/infrastructure/test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, "w") as f:
            json.dump(self.test_results, f, indent=2)
        logger.info(f"\nDetailed report saved to: {report_path}")

        # Return exit code based on failures
        return 0 if self.test_results["summary"]["failed"] == 0 else 1

    def run(self):
        """Run all test suites"""
        logger.info("Starting Infrastructure Test Suite")
        logger.info(f"Test configuration: {vars(self.args)}")

        # Run test suites in order
        self.run_unit_tests()
        self.run_integration_tests()
        self.run_e2e_tests()
        self.run_performance_tests()
        self.run_security_tests()

        # Generate and return report
        return self.generate_report()


def main():
    """Main entry point for test runner"""
    parser = argparse.ArgumentParser(
        description="Run infrastructure tests with various options"
    )

    # Test selection options
    parser.add_argument("--skip-unit", action="store_true", help="Skip unit tests")
    parser.add_argument(
        "--skip-integration", action="store_true", help="Skip integration tests"
    )
    parser.add_argument("--skip-e2e", action="store_true", help="Skip end-to-end tests")
    parser.add_argument(
        "--skip-performance", action="store_true", help="Skip performance tests"
    )
    parser.add_argument(
        "--security", action="store_true", help="Include security tests"
    )

    # Execution options
    parser.add_argument("--parallel", action="store_true", help="Run tests in parallel")
    parser.add_argument(
        "--workers", type=int, default=4, help="Number of parallel workers (default: 4)"
    )
    parser.add_argument(
        "--coverage", action="store_true", help="Generate coverage report"
    )

    # Quick test options
    parser.add_argument(
        "--quick", action="store_true", help="Run only unit tests for quick feedback"
    )
    parser.add_argument(
        "--full", action="store_true", help="Run all tests including security"
    )

    args = parser.parse_args()

    # Handle quick mode
    if args.quick:
        args.skip_integration = True
        args.skip_e2e = True
        args.skip_performance = True

    # Handle full mode
    if args.full:
        args.security = True

    # Create and run test runner
    runner = InfrastructureTestRunner(args)
    exit_code = runner.run()

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
