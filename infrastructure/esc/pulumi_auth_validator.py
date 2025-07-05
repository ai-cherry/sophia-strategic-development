#!/usr/bin/env python3
"""
Comprehensive Pulumi ESC Authentication Validator for Sophia AI

This script validates the complete authentication chain for Pulumi ESC:
1. Environment variables (PULUMI_ACCESS_TOKEN, PULUMI_ORG)
2. Pulumi CLI installation and version
3. Authentication status
4. ESC environment access
5. Secret retrieval test

Usage:
    python infrastructure/esc/pulumi_auth_validator.py

Returns:
    JSON report with validation results and overall status
"""

import json
import logging
import os
import subprocess
import sys
from datetime import datetime
from typing import Any

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class PulumiAuthValidator:
    """Comprehensive Pulumi ESC authentication validator"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.required_env_vars = ["PULUMI_ACCESS_TOKEN", "PULUMI_ORG"]
        self.default_org = "default"
        self.default_env = "sophia-ai-production"

    def validate_complete_auth_chain(self) -> dict[str, Any]:
        """
        Run comprehensive authentication validation

        Returns:
            Dictionary with validation results and overall status
        """
        self.logger.info(
            "🔐 Starting comprehensive Pulumi ESC authentication validation..."
        )

        results = {
            "timestamp": datetime.now().isoformat(),
            "validator_version": "1.0",
            "checks": {},
            "overall_status": "UNKNOWN",
            "recommendations": [],
        }

        # Check 1: Environment variables
        self.logger.info("📋 Checking environment variables...")
        results["checks"]["env_vars"] = self._check_env_variables()

        # Check 2: Pulumi CLI installation and version
        self.logger.info("🔧 Checking Pulumi CLI installation...")
        results["checks"]["cli_install"] = self._check_cli_installation()

        # Check 3: Authentication status
        self.logger.info("🔑 Checking authentication status...")
        results["checks"]["auth_status"] = self._check_auth_status()

        # Check 4: ESC environment access
        self.logger.info("🌍 Checking ESC environment access...")
        results["checks"]["esc_access"] = self._check_esc_access()

        # Check 5: Secret retrieval test
        self.logger.info("🔒 Testing secret retrieval...")
        results["checks"]["secret_retrieval"] = self._test_secret_retrieval()

        # Determine overall status and recommendations
        overall_status, recommendations = self._analyze_results(results["checks"])
        results["overall_status"] = overall_status
        results["recommendations"] = recommendations

        # Log summary
        self._log_summary(results)

        return results

    def _check_env_variables(self) -> dict[str, Any]:
        """Check required environment variables"""
        missing = []
        present = []

        for var in self.required_env_vars:
            value = os.getenv(var)
            if not value:
                missing.append(var)
            else:
                present.append(
                    {
                        "name": var,
                        "length": len(value),
                        "masked": f"{value[:4]}...{value[-4:]}"
                        if len(value) > 8
                        else "***",
                    }
                )

        return {
            "status": "PASS" if not missing else "FAIL",
            "missing_vars": missing,
            "present_vars": present,
            "message": "All required environment variables present"
            if not missing
            else f"Missing: {missing}",
            "details": {
                "required_count": len(self.required_env_vars),
                "present_count": len(present),
                "missing_count": len(missing),
            },
        }

    def _check_cli_installation(self) -> dict[str, Any]:
        """Check Pulumi CLI installation and version"""
        try:
            result = subprocess.run(
                ["pulumi", "version"], capture_output=True, text=True, timeout=10
            )

            if result.returncode == 0:
                version_info = result.stdout.strip()
                return {
                    "status": "PASS",
                    "version": version_info,
                    "message": "Pulumi CLI installed and accessible",
                    "details": {
                        "command_executed": "pulumi version",
                        "exit_code": result.returncode,
                        "execution_time": "< 10 seconds",
                    },
                }
            else:
                return {
                    "status": "FAIL",
                    "error": result.stderr,
                    "message": "Pulumi CLI execution failed",
                    "details": {
                        "command_executed": "pulumi version",
                        "exit_code": result.returncode,
                        "stdout": result.stdout,
                        "stderr": result.stderr,
                    },
                }
        except subprocess.TimeoutExpired:
            return {
                "status": "FAIL",
                "message": "Pulumi CLI command timed out",
                "details": {"timeout_seconds": 10},
            }
        except FileNotFoundError:
            return {
                "status": "FAIL",
                "message": "Pulumi CLI not found in PATH",
                "details": {
                    "suggestion": "Install Pulumi CLI from https://www.pulumi.com/docs/get-started/install/"
                },
            }
        except Exception as e:
            return {
                "status": "FAIL",
                "message": f"Unexpected error checking CLI: {str(e)}",
                "details": {"exception_type": type(e).__name__},
            }

    def _check_auth_status(self) -> dict[str, Any]:
        """Check Pulumi authentication status"""
        try:
            result = subprocess.run(
                ["pulumi", "whoami"], capture_output=True, text=True, timeout=10
            )

            if result.returncode == 0:
                user_info = result.stdout.strip()
                return {
                    "status": "PASS",
                    "user": user_info,
                    "message": "Successfully authenticated with Pulumi",
                    "details": {
                        "command_executed": "pulumi whoami",
                        "authenticated_user": user_info,
                    },
                }
            else:
                return {
                    "status": "FAIL",
                    "error": result.stderr,
                    "message": "Pulumi authentication failed",
                    "details": {
                        "command_executed": "pulumi whoami",
                        "exit_code": result.returncode,
                        "suggestion": "Run 'pulumi login' or check PULUMI_ACCESS_TOKEN",
                    },
                }
        except subprocess.TimeoutExpired:
            return {"status": "FAIL", "message": "Authentication check timed out"}
        except Exception as e:
            return {"status": "FAIL", "message": f"Auth check failed: {str(e)}"}

    def _check_esc_access(self) -> dict[str, Any]:
        """Check ESC environment access"""
        try:
            # Use pulumi env ls without --org flag (modern CLI approach)
            result = subprocess.run(
                ["pulumi", "env", "ls"], capture_output=True, text=True, timeout=15
            )

            if result.returncode == 0:
                environments = [
                    env.strip()
                    for env in result.stdout.strip().split("\n")
                    if env.strip()
                ]
                return {
                    "status": "PASS",
                    "environments": environments,
                    "message": f"ESC environments accessible (found {len(environments)} environments)",
                    "details": {
                        "environment_count": len(environments),
                        "command_executed": "pulumi env ls",
                        "environments_list": environments,
                    },
                }
            else:
                return {
                    "status": "FAIL",
                    "error": result.stderr,
                    "message": "Cannot access ESC environments",
                    "details": {
                        "exit_code": result.returncode,
                        "command_executed": "pulumi env ls",
                        "suggestion": "Check authentication and permissions",
                    },
                }
        except subprocess.TimeoutExpired:
            return {"status": "FAIL", "message": "ESC access check timed out"}
        except Exception as e:
            return {"status": "FAIL", "message": f"ESC access check failed: {str(e)}"}

    def _test_secret_retrieval(self) -> dict[str, Any]:
        """Test secret retrieval from ESC environment"""
        try:
            org = os.getenv("PULUMI_ORG", self.default_org)
            env_name = os.getenv("PULUMI_ENV", self.default_env)
            env_path = f"{org}/{env_name}"

            result = subprocess.run(
                ["pulumi", "env", "get", env_path, "--show-secrets"],
                capture_output=True,
                text=True,
                timeout=20,
            )

            if result.returncode == 0:
                try:
                    # Try to extract JSON from the output (it may have extra formatting)
                    output = result.stdout.strip()

                    # Look for JSON data - it should start with { and end with }
                    json_start = output.find("{")
                    json_end = output.rfind("}") + 1

                    if json_start >= 0 and json_end > json_start:
                        json_data = output[json_start:json_end]
                        data = json.loads(json_data)
                        values = data if isinstance(data, dict) else {}

                        # Count secret-like keys
                        secret_indicators = [
                            "secret",
                            "key",
                            "token",
                            "password",
                            "credential",
                            "api",
                        ]
                        secret_count = 0
                        total_values = len(values)

                        def count_secrets_recursive(obj, path=""):
                            nonlocal secret_count
                            if isinstance(obj, dict):
                                for key, value in obj.items():
                                    current_path = f"{path}.{key}" if path else key
                                    if any(
                                        indicator in key.lower()
                                        for indicator in secret_indicators
                                    ):
                                        secret_count += 1
                                    if isinstance(value, dict):
                                        count_secrets_recursive(value, current_path)
                            elif isinstance(obj, list):
                                for i, item in enumerate(obj):
                                    count_secrets_recursive(item, f"{path}[{i}]")

                        count_secrets_recursive(values)

                        return {
                            "status": "PASS",
                            "secret_count": secret_count,
                            "total_values": total_values,
                            "message": f"Successfully retrieved {secret_count} secrets from ESC environment '{env_name}'",
                            "details": {
                                "environment_path": env_path,
                                "command_executed": f"pulumi env get {env_path} --show-secrets",
                                "data_structure_valid": True,
                                "values_found": total_values > 0,
                                "sample_keys": list(values.keys())[:5]
                                if values
                                else [],
                            },
                        }
                    else:
                        # No JSON found, but command succeeded - check for expected output patterns
                        if "values:" in output.lower() or "secret" in output.lower():
                            return {
                                "status": "PASS",
                                "message": f"ESC environment '{env_name}' accessible with values (non-JSON format)",
                                "details": {
                                    "environment_path": env_path,
                                    "command_executed": f"pulumi env get {env_path} --show-secrets",
                                    "output_format": "text",
                                    "output_length": len(output),
                                },
                            }
                        else:
                            return {
                                "status": "FAIL",
                                "message": "ESC environment returned unexpected format",
                                "details": {
                                    "output_preview": output[:200] + "..."
                                    if len(output) > 200
                                    else output
                                },
                            }

                except json.JSONDecodeError as e:
                    # Fallback: check if output contains expected content
                    if (
                        "[secret]" in result.stdout
                        or "values:" in result.stdout.lower()
                    ):
                        return {
                            "status": "PASS",
                            "message": f"ESC environment '{env_name}' accessible (format not JSON but contains secrets)",
                            "details": {
                                "environment_path": env_path,
                                "command_executed": f"pulumi env get {env_path} --show-secrets",
                                "json_parse_error": str(e),
                                "output_contains_secrets": True,
                            },
                        }
                    else:
                        return {
                            "status": "FAIL",
                            "message": "Invalid response format from ESC",
                            "details": {
                                "json_error": str(e),
                                "output_preview": result.stdout[:200] + "..."
                                if len(result.stdout) > 200
                                else result.stdout,
                            },
                        }
            else:
                return {
                    "status": "FAIL",
                    "error": result.stderr,
                    "message": f"Failed to retrieve secrets from ESC environment '{env_name}'",
                    "details": {
                        "environment_path": env_path,
                        "exit_code": result.returncode,
                        "suggestion": "Check environment name and permissions",
                    },
                }
        except subprocess.TimeoutExpired:
            return {
                "status": "FAIL",
                "message": "Secret retrieval test timed out",
                "details": {"timeout_seconds": 20},
            }
        except Exception as e:
            return {
                "status": "FAIL",
                "message": f"Secret retrieval test failed: {str(e)}",
            }

    def _analyze_results(self, checks: dict[str, Any]) -> tuple[str, list[str]]:
        """Analyze check results and generate recommendations"""
        passed_checks = sum(
            1 for check in checks.values() if check.get("status") == "PASS"
        )
        total_checks = len(checks)

        recommendations = []

        # Determine overall status
        if passed_checks == total_checks:
            overall_status = "PASS"
            recommendations.append(
                "✅ All authentication checks passed - Pulumi ESC is fully functional"
            )
        elif passed_checks >= total_checks * 0.8:
            overall_status = "WARNING"
            recommendations.append(
                "⚠️ Most checks passed but some issues detected - review failed checks"
            )
        else:
            overall_status = "FAIL"
            recommendations.append(
                "❌ Critical authentication issues detected - immediate attention required"
            )

        # Generate specific recommendations
        for check_name, check_result in checks.items():
            if check_result.get("status") == "FAIL":
                if check_name == "env_vars":
                    missing_vars = check_result.get("missing_vars", [])
                    for var in missing_vars:
                        recommendations.append(
                            f"🔧 Set environment variable: export {var}=<value>"
                        )
                elif check_name == "cli_install":
                    recommendations.append(
                        "🔧 Install Pulumi CLI: curl -fsSL https://get.pulumi.com | sh"
                    )
                elif check_name == "auth_status":
                    recommendations.append("🔧 Authenticate with Pulumi: pulumi login")
                elif check_name == "esc_access":
                    recommendations.append(
                        "🔧 Check organization permissions and PULUMI_ORG variable"
                    )
                elif check_name == "secret_retrieval":
                    recommendations.append(
                        "🔧 Verify ESC environment exists and contains secrets"
                    )

        return overall_status, recommendations

    def _log_summary(self, results: dict[str, Any]):
        """Log validation summary"""
        status = results["overall_status"]
        checks = results["checks"]

        if status == "PASS":
            self.logger.info("✅ VALIDATION COMPLETE: All checks passed!")
        elif status == "WARNING":
            self.logger.warning("⚠️ VALIDATION COMPLETE: Some issues detected")
        else:
            self.logger.error("❌ VALIDATION COMPLETE: Critical issues found")

        # Log individual check results
        for check_name, check_result in checks.items():
            status_icon = "✅" if check_result.get("status") == "PASS" else "❌"
            message = check_result.get("message", "No message")
            self.logger.info(f"  {status_icon} {check_name}: {message}")

        # Log recommendations
        if results["recommendations"]:
            self.logger.info("\n📋 RECOMMENDATIONS:")
            for rec in results["recommendations"]:
                self.logger.info(f"  {rec}")


def main():
    """Main function for CLI usage"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate Pulumi ESC authentication for Sophia AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python infrastructure/esc/pulumi_auth_validator.py
    python infrastructure/esc/pulumi_auth_validator.py --output json
    python infrastructure/esc/pulumi_auth_validator.py --quiet
        """,
    )

    parser.add_argument(
        "--output",
        choices=["json", "summary"],
        default="summary",
        help="Output format (default: summary)",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress log output, only show final result",
    )

    args = parser.parse_args()

    # Adjust logging level if quiet
    if args.quiet:
        logging.getLogger().setLevel(logging.WARNING)

    try:
        validator = PulumiAuthValidator()
        results = validator.validate_complete_auth_chain()

        if args.output == "json":
            print(json.dumps(results, indent=2))
        else:
            # Summary output
            status = results["overall_status"]
            passed_checks = sum(
                1
                for check in results["checks"].values()
                if check.get("status") == "PASS"
            )
            total_checks = len(results["checks"])

            print("\n🔐 Pulumi ESC Authentication Validation Summary")
            print(f"Status: {status}")
            print(f"Checks Passed: {passed_checks}/{total_checks}")
            print(f"Timestamp: {results['timestamp']}")

            if results["recommendations"]:
                print("\n📋 Recommendations:")
                for rec in results["recommendations"]:
                    print(f"  {rec}")

        # Exit with appropriate code
        sys.exit(0 if results["overall_status"] == "PASS" else 1)

    except Exception as e:
        logger.error(f"Validation failed with error: {e}")
        if args.output == "json":
            error_result = {
                "timestamp": datetime.now().isoformat(),
                "overall_status": "ERROR",
                "error": str(e),
                "message": "Validation script encountered an error",
            }
            print(json.dumps(error_result, indent=2))
        else:
            print(f"❌ Validation Error: {e}")

        sys.exit(2)


if __name__ == "__main__":
    main()
