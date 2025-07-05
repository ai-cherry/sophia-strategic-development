#!/usr/bin/env python3
"""
Lambda Labs Deployment & Testing Script
=======================================

Comprehensive deployment and testing of Sophia AI on Lambda Labs infrastructure.
Tests all components: Docker, Kubernetes, MCP servers, health checks, and performance.

Date: July 5, 2025
"""

import asyncio
import json
import logging
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LambdaLabsDeploymentTester:
    """Comprehensive Lambda Labs deployment and testing"""

    def __init__(self):
        self.project_root = Path.cwd()
        self.lambda_labs_ip = "146.235.200.1"  # Primary Lambda Labs instance
        self.results = {
            "deployment_start": datetime.now().isoformat(),
            "phases": {},
            "tests": {},
            "performance": {},
            "errors": [],
            "final_status": "pending"
        }

        # Test endpoints and expected responses
        self.test_endpoints = {
            "health": {"path": "/health", "expected_status": 200},
            "api_docs": {"path": "/docs", "expected_status": 200},
            "chat": {"path": "/api/v1/chat", "method": "POST", "expected_status": 200},
            "dashboard": {"path": "/api/v1/dashboard/metrics", "expected_status": 200}
        }

        # MCP servers to test
        self.mcp_servers = {
            "ai_memory": {"port": 9000, "health": "/health"},
            "codacy": {"port": 3008, "health": "/health"},
            "github": {"port": 9003, "health": "/health"},
            "linear": {"port": 9004, "health": "/health"},
            "snowflake_admin": {"port": 9020, "health": "/health"}
        }

    async def run_full_deployment_test(self) -> dict[str, Any]:
        """Run complete deployment and testing workflow"""
        logger.info("🚀 STARTING LAMBDA LABS COMPREHENSIVE DEPLOYMENT & TESTING")
        logger.info("=" * 80)
        logger.info("📅 Date: July 5, 2025")
        logger.info(f"🏭 Target: Lambda Labs ({self.lambda_labs_ip})")
        logger.info("🎯 Scope: Full deployment validation + performance testing")
        logger.info("")

        try:
            # Phase 1: Pre-deployment validation
            await self._phase_1_pre_deployment()

            # Phase 2: Docker deployment
            await self._phase_2_docker_deployment()

            # Phase 3: Kubernetes validation
            await self._phase_3_kubernetes_validation()

            # Phase 4: MCP servers testing
            await self._phase_4_mcp_testing()

            # Phase 5: Performance testing
            await self._phase_5_performance_testing()

            # Phase 6: Integration testing
            await self._phase_6_integration_testing()

            # Final assessment
            self._final_assessment()

        except Exception as e:
            logger.error(f"❌ Deployment test failed: {e}")
            self.results["errors"].append(str(e))
            self.results["final_status"] = "failed"

        return self.results

    async def _phase_1_pre_deployment(self):
        """Phase 1: Pre-deployment validation"""
        logger.info("📋 PHASE 1: Pre-deployment Validation")
        logger.info("-" * 50)

        phase_results = {"status": "running", "checks": {}}

        # Check Docker availability
        try:
            result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                phase_results["checks"]["docker"] = {"status": "✅", "version": result.stdout.strip()}
                logger.info(f"✅ Docker available: {result.stdout.strip()}")
            else:
                phase_results["checks"]["docker"] = {"status": "❌", "error": "Docker not available"}
                logger.error("❌ Docker not available")
        except Exception as e:
            phase_results["checks"]["docker"] = {"status": "❌", "error": str(e)}
            logger.error(f"❌ Docker check failed: {e}")

        # Check Pulumi access
        try:
            result = subprocess.run(["pulumi", "whoami"], capture_output=True, text=True)
            if result.returncode == 0:
                phase_results["checks"]["pulumi"] = {"status": "✅", "user": result.stdout.strip()}
                logger.info(f"✅ Pulumi authenticated: {result.stdout.strip()}")
            else:
                phase_results["checks"]["pulumi"] = {"status": "❌", "error": "Pulumi auth failed"}
                logger.error("❌ Pulumi authentication failed")
        except Exception as e:
            phase_results["checks"]["pulumi"] = {"status": "❌", "error": str(e)}
            logger.error(f"❌ Pulumi check failed: {e}")

        # Check kubectl access
        try:
            result = subprocess.run(["kubectl", "version", "--client"], capture_output=True, text=True)
            if result.returncode == 0:
                phase_results["checks"]["kubectl"] = {"status": "✅", "version": "available"}
                logger.info("✅ kubectl available")
            else:
                phase_results["checks"]["kubectl"] = {"status": "❌", "error": "kubectl not available"}
                logger.error("❌ kubectl not available")
        except Exception as e:
            phase_results["checks"]["kubectl"] = {"status": "❌", "error": str(e)}
            logger.error(f"❌ kubectl check failed: {e}")

        # Check Dockerfile.production exists
        dockerfile = self.project_root / "Dockerfile.production"
        if dockerfile.exists():
            phase_results["checks"]["dockerfile"] = {"status": "✅", "path": str(dockerfile)}
            logger.info("✅ Dockerfile.production found")
        else:
            phase_results["checks"]["dockerfile"] = {"status": "❌", "error": "Dockerfile.production missing"}
            logger.error("❌ Dockerfile.production missing")

        # Validate environment
        try:
            result = subprocess.run([sys.executable, "scripts/validate_deployment_env.py"],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                phase_results["checks"]["environment"] = {"status": "✅", "message": "All variables validated"}
                logger.info("✅ Environment variables validated")
            else:
                phase_results["checks"]["environment"] = {"status": "⚠️", "warning": result.stderr}
                logger.warning(f"⚠️ Environment validation warnings: {result.stderr}")
        except Exception as e:
            phase_results["checks"]["environment"] = {"status": "❌", "error": str(e)}
            logger.error(f"❌ Environment validation failed: {e}")

        phase_results["status"] = "completed"
        phase_results["success_rate"] = len([c for c in phase_results["checks"].values() if c["status"] == "✅"]) / len(phase_results["checks"])
        self.results["phases"]["phase_1_validation"] = phase_results

        logger.info(f"📊 Phase 1 Complete: {phase_results['success_rate']:.1%} success rate")
        logger.info("")

    async def _phase_2_docker_deployment(self):
        """Phase 2: Docker build and deployment"""
        logger.info("🐳 PHASE 2: Docker Build & Deployment")
        logger.info("-" * 50)

        phase_results = {"status": "running", "steps": {}}

        # Step 1: Build Docker image
        logger.info("🔨 Building Docker image...")
        try:
            start_time = time.time()
            result = subprocess.run([
                "docker", "build",
                "-t", "scoobyjava15/sophia-ai:test-july5",
                "-f", "Dockerfile.production",
                "."
            ], capture_output=True, text=True, timeout=600)  # 10 minute timeout

            build_time = time.time() - start_time

            if result.returncode == 0:
                phase_results["steps"]["docker_build"] = {
                    "status": "✅",
                    "build_time": f"{build_time:.1f}s",
                    "image": "scoobyjava15/sophia-ai:test-july5"
                }
                logger.info(f"✅ Docker build successful ({build_time:.1f}s)")
            else:
                phase_results["steps"]["docker_build"] = {
                    "status": "❌",
                    "error": result.stderr[-500:]  # Last 500 chars of error
                }
                logger.error(f"❌ Docker build failed: {result.stderr[-200:]}")

        except subprocess.TimeoutExpired:
            phase_results["steps"]["docker_build"] = {"status": "❌", "error": "Build timeout (10 minutes)"}
            logger.error("❌ Docker build timed out")
        except Exception as e:
            phase_results["steps"]["docker_build"] = {"status": "❌", "error": str(e)}
            logger.error(f"❌ Docker build error: {e}")

        # Step 2: Test local container run
        if phase_results["steps"]["docker_build"]["status"] == "✅":
            logger.info("🧪 Testing local container...")
            try:
                # Start container in background
                result = subprocess.run([
                    "docker", "run", "-d",
                    "--name", "sophia-test-local",
                    "-p", "8001:8000",
                    "-e", "ENVIRONMENT=test",
                    "scoobyjava15/sophia-ai:test-july5"
                ], capture_output=True, text=True)

                if result.returncode == 0:
                    container_id = result.stdout.strip()
                    logger.info(f"✅ Container started: {container_id[:12]}")

                    # Wait for startup
                    await asyncio.sleep(10)

                    # Test health endpoint
                    health_result = subprocess.run([
                        "curl", "-f", "-s", "http://localhost:8001/health"
                    ], capture_output=True, text=True)

                    if health_result.returncode == 0:
                        phase_results["steps"]["local_test"] = {
                            "status": "✅",
                            "container_id": container_id[:12],
                            "health_response": health_result.stdout
                        }
                        logger.info("✅ Local container health check passed")
                    else:
                        phase_results["steps"]["local_test"] = {
                            "status": "⚠️",
                            "container_id": container_id[:12],
                            "warning": "Health check failed but container running"
                        }
                        logger.warning("⚠️ Container running but health check failed")

                    # Cleanup
                    subprocess.run(["docker", "stop", "sophia-test-local"], capture_output=True)
                    subprocess.run(["docker", "rm", "sophia-test-local"], capture_output=True)

                else:
                    phase_results["steps"]["local_test"] = {"status": "❌", "error": result.stderr}
                    logger.error(f"❌ Container start failed: {result.stderr}")

            except Exception as e:
                phase_results["steps"]["local_test"] = {"status": "❌", "error": str(e)}
                logger.error(f"❌ Local container test error: {e}")
        else:
            phase_results["steps"]["local_test"] = {"status": "⏭️", "reason": "Skipped due to build failure"}

        phase_results["status"] = "completed"
        self.results["phases"]["phase_2_docker"] = phase_results
        logger.info("📊 Phase 2 Complete")
        logger.info("")

    async def _phase_3_kubernetes_validation(self):
        """Phase 3: Kubernetes deployment validation"""
        logger.info("☸️  PHASE 3: Kubernetes Validation")
        logger.info("-" * 50)

        phase_results = {"status": "running", "checks": {}}

        # Check if we can access the cluster
        try:
            result = subprocess.run(["kubectl", "cluster-info"], capture_output=True, text=True)
            if result.returncode == 0:
                phase_results["checks"]["cluster_access"] = {"status": "✅", "info": "Cluster accessible"}
                logger.info("✅ Kubernetes cluster accessible")

                # Check for Sophia AI namespace
                result = subprocess.run(["kubectl", "get", "namespace", "sophia-ai"],
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    phase_results["checks"]["namespace"] = {"status": "✅", "namespace": "sophia-ai"}
                    logger.info("✅ sophia-ai namespace exists")
                else:
                    phase_results["checks"]["namespace"] = {"status": "⚠️", "warning": "sophia-ai namespace not found"}
                    logger.warning("⚠️ sophia-ai namespace not found")

                # Check for existing deployments
                result = subprocess.run(["kubectl", "get", "deployments", "-A"],
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    deployments = result.stdout
                    phase_results["checks"]["deployments"] = {
                        "status": "✅",
                        "count": len(deployments.split('\n')) - 1,
                        "summary": deployments.split('\n')[0]  # Header line
                    }
                    logger.info(f"✅ Found {len(deployments.split('\n')) - 1} deployments")
                else:
                    phase_results["checks"]["deployments"] = {"status": "❌", "error": "Could not list deployments"}

            else:
                phase_results["checks"]["cluster_access"] = {"status": "❌", "error": result.stderr}
                logger.error(f"❌ Kubernetes cluster not accessible: {result.stderr}")

        except Exception as e:
            phase_results["checks"]["cluster_access"] = {"status": "❌", "error": str(e)}
            logger.error(f"❌ Kubernetes validation error: {e}")

        phase_results["status"] = "completed"
        self.results["phases"]["phase_3_kubernetes"] = phase_results
        logger.info("📊 Phase 3 Complete")
        logger.info("")

    async def _phase_4_mcp_testing(self):
        """Phase 4: MCP servers testing"""
        logger.info("🔌 PHASE 4: MCP Servers Testing")
        logger.info("-" * 50)

        phase_results = {"status": "running", "servers": {}}

        for server_name, config in self.mcp_servers.items():
            logger.info(f"🧪 Testing {server_name} (port {config['port']})...")

            server_results = {"port": config["port"], "tests": {}}

            # Test 1: Port accessibility
            try:
                result = subprocess.run([
                    "curl", "-f", "-s", "--connect-timeout", "5",
                    f"http://{self.lambda_labs_ip}:{config['port']}{config['health']}"
                ], capture_output=True, text=True)

                if result.returncode == 0:
                    server_results["tests"]["connectivity"] = {
                        "status": "✅",
                        "response": result.stdout[:100]  # First 100 chars
                    }
                    logger.info(f"  ✅ {server_name} connectivity OK")
                else:
                    server_results["tests"]["connectivity"] = {
                        "status": "❌",
                        "error": f"HTTP {result.returncode}"
                    }
                    logger.warning(f"  ❌ {server_name} not accessible")

            except Exception as e:
                server_results["tests"]["connectivity"] = {"status": "❌", "error": str(e)}
                logger.warning(f"  ❌ {server_name} connection error: {e}")

            # Test 2: Health endpoint
            if server_results["tests"]["connectivity"]["status"] == "✅":
                try:
                    result = subprocess.run([
                        "curl", "-f", "-s",
                        f"http://{self.lambda_labs_ip}:{config['port']}/health"
                    ], capture_output=True, text=True)

                    if result.returncode == 0:
                        try:
                            health_data = json.loads(result.stdout)
                            server_results["tests"]["health"] = {
                                "status": "✅",
                                "data": health_data
                            }
                            logger.info(f"  ✅ {server_name} health check passed")
                        except json.JSONDecodeError:
                            server_results["tests"]["health"] = {
                                "status": "⚠️",
                                "warning": "Health endpoint returned non-JSON"
                            }
                            logger.warning(f"  ⚠️ {server_name} health response not JSON")
                    else:
                        server_results["tests"]["health"] = {
                            "status": "❌",
                            "error": "Health endpoint failed"
                        }
                        logger.warning(f"  ❌ {server_name} health endpoint failed")

                except Exception as e:
                    server_results["tests"]["health"] = {"status": "❌", "error": str(e)}
                    logger.warning(f"  ❌ {server_name} health test error: {e}")
            else:
                server_results["tests"]["health"] = {"status": "⏭️", "reason": "Skipped due to connectivity failure"}

            phase_results["servers"][server_name] = server_results

        # Calculate success rate
        total_tests = sum(len(server["tests"]) for server in phase_results["servers"].values())
        successful_tests = sum(
            1 for server in phase_results["servers"].values()
            for test in server["tests"].values()
            if test["status"] == "✅"
        )

        phase_results["success_rate"] = successful_tests / total_tests if total_tests > 0 else 0
        phase_results["status"] = "completed"

        self.results["phases"]["phase_4_mcp"] = phase_results
        logger.info(f"📊 Phase 4 Complete: {phase_results['success_rate']:.1%} MCP success rate")
        logger.info("")

    async def _phase_5_performance_testing(self):
        """Phase 5: Performance testing"""
        logger.info("⚡ PHASE 5: Performance Testing")
        logger.info("-" * 50)

        phase_results = {"status": "running", "metrics": {}}

        # Test main application endpoints
        for endpoint_name, config in self.test_endpoints.items():
            logger.info(f"📊 Testing {endpoint_name} performance...")

            endpoint_results = {"endpoint": config["path"], "samples": []}

            # Run 5 performance samples
            for i in range(5):
                try:
                    start_time = time.time()

                    if config.get("method") == "POST":
                        # Simple POST test for chat endpoint
                        result = subprocess.run([
                            "curl", "-s", "-w", "%{http_code},%{time_total}",
                            "-X", "POST",
                            "-H", "Content-Type: application/json",
                            "-d", '{"message": "test", "session_id": "test"}',
                            f"http://{self.lambda_labs_ip}:8000{config['path']}"
                        ], capture_output=True, text=True, timeout=30)
                    else:
                        # Simple GET test
                        result = subprocess.run([
                            "curl", "-s", "-w", "%{http_code},%{time_total}",
                            f"http://{self.lambda_labs_ip}:8000{config['path']}"
                        ], capture_output=True, text=True, timeout=30)

                    response_time = time.time() - start_time

                    if result.returncode == 0:
                        # Parse curl output (status_code,total_time)
                        output_parts = result.stdout.split(',')
                        if len(output_parts) >= 2:
                            status_code = output_parts[-2]
                            curl_time = float(output_parts[-1])

                            endpoint_results["samples"].append({
                                "sample": i + 1,
                                "status_code": status_code,
                                "response_time": response_time,
                                "curl_time": curl_time,
                                "success": status_code.startswith('2')
                            })
                        else:
                            endpoint_results["samples"].append({
                                "sample": i + 1,
                                "error": "Could not parse curl output",
                                "success": False
                            })
                    else:
                        endpoint_results["samples"].append({
                            "sample": i + 1,
                            "error": f"Curl failed: {result.stderr}",
                            "success": False
                        })

                except subprocess.TimeoutExpired:
                    endpoint_results["samples"].append({
                        "sample": i + 1,
                        "error": "Request timeout (30s)",
                        "success": False
                    })
                except Exception as e:
                    endpoint_results["samples"].append({
                        "sample": i + 1,
                        "error": str(e),
                        "success": False
                    })

                # Small delay between requests
                await asyncio.sleep(1)

            # Calculate metrics
            successful_samples = [s for s in endpoint_results["samples"] if s.get("success")]
            if successful_samples:
                response_times = [s["response_time"] for s in successful_samples]
                endpoint_results["metrics"] = {
                    "success_rate": len(successful_samples) / len(endpoint_results["samples"]),
                    "avg_response_time": sum(response_times) / len(response_times),
                    "min_response_time": min(response_times),
                    "max_response_time": max(response_times)
                }

                logger.info(f"  ✅ {endpoint_name}: {endpoint_results['metrics']['avg_response_time']:.3f}s avg")
            else:
                endpoint_results["metrics"] = {
                    "success_rate": 0,
                    "error": "No successful requests"
                }
                logger.warning(f"  ❌ {endpoint_name}: All requests failed")

            phase_results["metrics"][endpoint_name] = endpoint_results

        phase_results["status"] = "completed"
        self.results["phases"]["phase_5_performance"] = phase_results
        self.results["performance"] = phase_results["metrics"]

        logger.info("📊 Phase 5 Complete")
        logger.info("")

    async def _phase_6_integration_testing(self):
        """Phase 6: Integration testing"""
        logger.info("🔗 PHASE 6: Integration Testing")
        logger.info("-" * 50)

        phase_results = {"status": "running", "integration_tests": {}}

        # Test 1: Dashboard + Chat integration
        logger.info("🧪 Testing Dashboard + Chat integration...")
        integration_results = {}

        try:
            # First get dashboard metrics
            dashboard_result = subprocess.run([
                "curl", "-s", "-f",
                f"http://{self.lambda_labs_ip}:8000/api/v1/dashboard/metrics"
            ], capture_output=True, text=True, timeout=15)

            if dashboard_result.returncode == 0:
                # Then test chat with business query
                chat_result = subprocess.run([
                    "curl", "-s", "-f",
                    "-X", "POST",
                    "-H", "Content-Type: application/json",
                    "-d", '{"message": "What is our current system status?", "session_id": "integration_test"}',
                    f"http://{self.lambda_labs_ip}:8000/api/v1/chat"
                ], capture_output=True, text=True, timeout=30)

                if chat_result.returncode == 0:
                    integration_results["dashboard_chat"] = {
                        "status": "✅",
                        "dashboard_response": len(dashboard_result.stdout),
                        "chat_response": len(chat_result.stdout)
                    }
                    logger.info("  ✅ Dashboard + Chat integration working")
                else:
                    integration_results["dashboard_chat"] = {
                        "status": "⚠️",
                        "warning": "Dashboard OK, Chat failed"
                    }
                    logger.warning("  ⚠️ Dashboard OK but Chat failed")
            else:
                integration_results["dashboard_chat"] = {
                    "status": "❌",
                    "error": "Dashboard endpoint failed"
                }
                logger.warning("  ❌ Dashboard endpoint failed")

        except Exception as e:
            integration_results["dashboard_chat"] = {"status": "❌", "error": str(e)}
            logger.warning(f"  ❌ Integration test error: {e}")

        # Test 2: MCP + API integration (if any MCP server is working)
        working_mcp_servers = [
            name for name, data in self.results["phases"].get("phase_4_mcp", {}).get("servers", {}).items()
            if any(test.get("status") == "✅" for test in data.get("tests", {}).values())
        ]

        if working_mcp_servers:
            logger.info(f"🧪 Testing MCP integration with {working_mcp_servers[0]}...")
            server_name = working_mcp_servers[0]
            server_config = self.mcp_servers[server_name]

            try:
                # Test MCP server health + main API health
                mcp_result = subprocess.run([
                    "curl", "-s", "-f",
                    f"http://{self.lambda_labs_ip}:{server_config['port']}/health"
                ], capture_output=True, text=True, timeout=10)

                api_result = subprocess.run([
                    "curl", "-s", "-f",
                    f"http://{self.lambda_labs_ip}:8000/health"
                ], capture_output=True, text=True, timeout=10)

                if mcp_result.returncode == 0 and api_result.returncode == 0:
                    integration_results["mcp_api"] = {
                        "status": "✅",
                        "mcp_server": server_name,
                        "both_healthy": True
                    }
                    logger.info(f"  ✅ MCP ({server_name}) + API integration working")
                else:
                    integration_results["mcp_api"] = {
                        "status": "⚠️",
                        "mcp_server": server_name,
                        "warning": "One or both endpoints failed"
                    }
                    logger.warning(f"  ⚠️ MCP ({server_name}) + API partial failure")

            except Exception as e:
                integration_results["mcp_api"] = {"status": "❌", "error": str(e)}
                logger.warning(f"  ❌ MCP integration test error: {e}")
        else:
            integration_results["mcp_api"] = {
                "status": "⏭️",
                "reason": "No working MCP servers found"
            }
            logger.info("  ⏭️ MCP integration test skipped (no working servers)")

        phase_results["integration_tests"] = integration_results
        phase_results["status"] = "completed"

        self.results["phases"]["phase_6_integration"] = phase_results
        logger.info("📊 Phase 6 Complete")
        logger.info("")

    def _final_assessment(self):
        """Generate final assessment and recommendations"""
        logger.info("🎯 FINAL ASSESSMENT")
        logger.info("-" * 50)

        # Calculate overall success metrics
        total_phases = len(self.results["phases"])
        successful_phases = len([p for p in self.results["phases"].values() if p.get("status") == "completed"])

        # Count successful tests across all phases
        total_tests = 0
        successful_tests = 0

        for phase_name, phase_data in self.results["phases"].items():
            if "checks" in phase_data:
                for check in phase_data["checks"].values():
                    total_tests += 1
                    if check.get("status") == "✅":
                        successful_tests += 1
            elif "servers" in phase_data:
                for server in phase_data["servers"].values():
                    for test in server.get("tests", {}).values():
                        total_tests += 1
                        if test.get("status") == "✅":
                            successful_tests += 1
            elif "integration_tests" in phase_data:
                for test in phase_data["integration_tests"].values():
                    total_tests += 1
                    if test.get("status") == "✅":
                        successful_tests += 1

        overall_success_rate = successful_tests / total_tests if total_tests > 0 else 0

        # Performance assessment
        performance_summary = {}
        if "performance" in self.results:
            for endpoint, data in self.results["performance"].items():
                if "metrics" in data and "avg_response_time" in data["metrics"]:
                    performance_summary[endpoint] = {
                        "avg_time": data["metrics"]["avg_response_time"],
                        "success_rate": data["metrics"]["success_rate"]
                    }

        # Determine final status
        if overall_success_rate >= 0.8:
            final_status = "excellent"
            status_emoji = "🟢"
        elif overall_success_rate >= 0.6:
            final_status = "good"
            status_emoji = "🟡"
        elif overall_success_rate >= 0.4:
            final_status = "partial"
            status_emoji = "🟠"
        else:
            final_status = "failed"
            status_emoji = "🔴"

        self.results["final_status"] = final_status
        self.results["overall_success_rate"] = overall_success_rate
        self.results["total_tests"] = total_tests
        self.results["successful_tests"] = successful_tests
        self.results["performance_summary"] = performance_summary
        self.results["deployment_end"] = datetime.now().isoformat()

        # Log final results
        logger.info(f"{status_emoji} OVERALL STATUS: {final_status.upper()}")
        logger.info(f"📊 Success Rate: {overall_success_rate:.1%} ({successful_tests}/{total_tests} tests passed)")
        logger.info(f"✅ Phases Completed: {successful_phases}/{total_phases}")

        if performance_summary:
            logger.info("⚡ Performance Summary:")
            for endpoint, metrics in performance_summary.items():
                logger.info(f"  - {endpoint}: {metrics['avg_time']:.3f}s avg ({metrics['success_rate']:.1%} success)")

        # Recommendations
        recommendations = []

        if overall_success_rate < 1.0:
            recommendations.append("Review failed tests and address infrastructure issues")

        if any(data.get("success_rate", 1) < 0.8 for data in self.results["phases"].values() if "success_rate" in data):
            recommendations.append("Investigate MCP server connectivity issues")

        if performance_summary:
            slow_endpoints = [ep for ep, metrics in performance_summary.items() if metrics.get("avg_time", 0) > 2.0]
            if slow_endpoints:
                recommendations.append(f"Optimize performance for slow endpoints: {', '.join(slow_endpoints)}")

        if not any("docker_build" in str(phase) and "✅" in str(phase) for phase in self.results["phases"].values()):
            recommendations.append("Address Docker build issues before production deployment")

        self.results["recommendations"] = recommendations

        if recommendations:
            logger.info("💡 Recommendations:")
            for i, rec in enumerate(recommendations, 1):
                logger.info(f"  {i}. {rec}")
        else:
            logger.info("🎉 No critical issues found - system ready for production!")

        logger.info("")
        logger.info("🏁 LAMBDA LABS DEPLOYMENT & TESTING COMPLETE")
        logger.info("=" * 80)


def main():
    """Main execution function"""
    print("🚀 Lambda Labs Deployment & Testing")
    print("=" * 50)
    print("📅 Date: July 5, 2025")
    print("🎯 Comprehensive deployment validation")
    print("")

    tester = LambdaLabsDeploymentTester()

    # Run async deployment test
    try:
        results = asyncio.run(tester.run_full_deployment_test())

        # Save results to file
        results_file = Path(f"lambda_labs_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)

        print(f"📄 Detailed results saved to: {results_file}")

        # Return appropriate exit code
        if results["final_status"] in ["excellent", "good"]:
            return 0
        elif results["final_status"] == "partial":
            return 1
        else:
            return 2

    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
        return 130
    except Exception as e:
        print(f"\n❌ Testing failed with error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
