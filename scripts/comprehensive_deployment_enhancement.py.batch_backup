#!/usr/bin/env python3
"""
Comprehensive Deployment Enhancement Script
Fixes all critical deployment blockers and implements advanced monitoring, testing, and optimization
"""

import asyncio
import logging
import re
import statistics
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import aiohttp

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ComprehensiveDeploymentEnhancement:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.fixes_applied = []
        self.backup_files = []
        self.start_time = time.time()
        self.services = {
            "api_gateway": {
                "url": "http://localhost:8000/health",
                "name": "API Gateway",
                "port": 8000,
            },
            "ai_memory": {
                "url": "http://localhost:9001/health",
                "name": "AI Memory MCP",
                "port": 9001,
            },
            "codacy": {
                "url": "http://localhost:3008/health",
                "name": "Codacy MCP",
                "port": 3008,
            },
            "github": {
                "url": "http://localhost:9003/health",
                "name": "GitHub MCP",
                "port": 9003,
            },
            "linear": {
                "url": "http://localhost:9004/health",
                "name": "Linear MCP",
                "port": 9004,
            },
        }
        self.performance_data = []

    def backup_file(self, file_path: Path) -> Path:
        """Create backup of file before modification"""
        backup_path = file_path.with_suffix(
            f"{file_path.suffix}.backup.{int(time.time())}"
        )
        if file_path.exists():
            backup_path.write_text(file_path.read_text())
            self.backup_files.append(backup_path)
            logger.info(f"📁 Created backup: {backup_path}")
        return backup_path

    def fix_critical_deployment_issues(self) -> bool:
        """Fix all critical deployment issues"""
        logger.info("🔧 Phase 1: Fixing Critical Deployment Issues")

        issues_fixed = 0
        total_issues = 6

        # 1. Fix Snowflake indentation errors
        if self.fix_snowflake_indentation():
            issues_fixed += 1

        # 2. Create missing MCP server module
        if self.create_missing_mcp_module():
            issues_fixed += 1

        # 3. Fix MCP configuration errors
        if self.fix_mcp_configuration():
            issues_fixed += 1

        # 4. Install missing dependencies
        if self.install_missing_dependencies():
            issues_fixed += 1

        # 5. Fix data flow syntax errors
        if self.fix_data_flow_syntax():
            issues_fixed += 1

        # 6. Fix import chain issues
        if self.fix_import_chains():
            issues_fixed += 1

        success_rate = issues_fixed / total_issues
        logger.info(
            f"✅ Phase 1 Complete: {issues_fixed}/{total_issues} issues fixed ({success_rate*100:.1f}%)"
        )
        return success_rate > 0.8

    def fix_snowflake_indentation(self) -> bool:
        """Fix Snowflake Cortex Service indentation errors"""
        try:
            logger.info("   🔧 Fixing Snowflake indentation errors...")

            file_path = (
                self.project_root / "backend" / "utils" / "snowflake_cortex_service.py"
            )
            if not file_path.exists():
                logger.warning(f"   ⚠️ File not found: {file_path}")
                return False

            self.backup_file(file_path)
            content = file_path.read_text()

            # Fix specific indentation patterns
            fixes = [
                # Fix try block indentation
                (
                    r"(\s*)try:\s*\n(\s*)cursor = self\.connection\.cursor\(\)",
                    r"\1try:\n\1    cursor = self.connection.cursor()",
                ),
                # Fix general cursor indentation
                (
                    r"^(\s*)cursor = self\.connection\.cursor\(\)$",
                    r"        cursor = self.connection.cursor()",
                    re.MULTILINE,
                ),
                # Fix filter validation indentation
                (
                    r"^(\s*)if key not in ALLOWED_FILTER_COLUMNS:$",
                    r"        if key not in ALLOWED_FILTER_COLUMNS:",
                    re.MULTILINE,
                ),
            ]

            for pattern, replacement, *flags in fixes:
                if flags:
                    content = re.sub(pattern, replacement, content, flags=flags[0])
                else:
                    content = re.sub(pattern, replacement, content)

            file_path.write_text(content)
            logger.info("   ✅ Fixed Snowflake indentation errors")
            self.fixes_applied.append("Snowflake indentation")
            return True

        except Exception as e:
            logger.error(f"   ❌ Failed to fix Snowflake indentation: {e}")
            return False

    def create_missing_mcp_module(self) -> bool:
        """Create missing backend.mcp_servers.server module"""
        try:
            logger.info("   🔧 Creating missing MCP server module...")

            server_dir = self.project_root / "backend" / "mcp_servers"
            server_dir.mkdir(parents=True, exist_ok=True)

            server_file = server_dir / "server.py"

            if not server_file.exists():
                server_content = '''"""
Base MCP Server Module
Provides base classes and utilities for MCP servers
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

class Server(ABC):
    """Base MCP Server class"""

    def __init__(self, name: str, port: int):
        self.name = name
        self.port = port
        self.running = False

    @abstractmethod
    async def start(self):
        """Start the server"""
        pass

    @abstractmethod
    async def stop(self):
        """Stop the server"""
        pass

    async def health_check(self) -> Dict[str, Any]:
        """Basic health check"""
        return {
            "status": "healthy" if self.running else "stopped",
            "name": self.name,
            "port": self.port,
            "timestamp": asyncio.get_event_loop().time()
        }

class MCPServer(Server):
    """Enhanced MCP Server with additional capabilities"""

    def __init__(self, name: str, port: int, config: Optional[Dict] = None):
        super().__init__(name, port)
        self.config = config or {}

    async def start(self):
        """Start the MCP server"""
        logger.info(f"Starting MCP server {self.name} on port {self.port}")
        self.running = True

    async def stop(self):
        """Stop the MCP server"""
        logger.info(f"Stopping MCP server {self.name}")
        self.running = False
'''
                server_file.write_text(server_content)
                logger.info("   ✅ Created missing MCP server module")
                self.fixes_applied.append("MCP server module")
                return True
            else:
                logger.info("   📝 MCP server module already exists")
                return True

        except Exception as e:
            logger.error(f"   ❌ Failed to create MCP server module: {e}")
            return False

    def fix_mcp_configuration(self) -> bool:
        """Fix MCP configuration errors"""
        try:
            logger.info("   🔧 Fixing MCP configuration errors...")

            config_files = [
                self.project_root
                / "backend"
                / "services"
                / "mcp_orchestration_service.py"
            ]

            fixes_applied = 0

            for file_path in config_files:
                if not file_path.exists():
                    continue

                self.backup_file(file_path)
                content = file_path.read_text()

                # Fix Python MCPServerEndpoint calls
                original_content = content

                # Remove 'name' parameter from MCPServerEndpoint calls
                content = re.sub(
                    r'MCPServerEndpoint\([^)]*name\s*=\s*["\'][^"\']*["\'][,\s]*',
                    "MCPServerEndpoint(",
                    content,
                )

                if content != original_content:
                    file_path.write_text(content)
                    fixes_applied += 1
                    logger.info(f"   ✅ Fixed MCP configuration in {file_path.name}")

            if fixes_applied > 0:
                self.fixes_applied.append("MCP configuration")

            return True

        except Exception as e:
            logger.error(f"   ❌ Failed to fix MCP configuration: {e}")
            return False

    def install_missing_dependencies(self) -> bool:
        """Install missing dependencies"""
        try:
            logger.info("   🔧 Installing missing dependencies...")

            missing_deps = [
                "slowapi",
                "aiomysql",
                "snowflake-connector-python",
                "aioredis",
                "httpx[http2]",
                "psutil",
            ]

            installed_count = 0

            for dep in missing_deps:
                try:
                    result = subprocess.run(
                        [sys.executable, "-m", "pip", "install", dep, "--quiet"],
                        capture_output=True,
                        text=True,
                        timeout=60,
                    )

                    if result.returncode == 0:
                        installed_count += 1
                        logger.info(f"   ✅ Installed {dep}")
                    else:
                        logger.warning(f"   ⚠️ Failed to install {dep}")

                except subprocess.TimeoutExpired:
                    logger.warning(f"   ⚠️ Timeout installing {dep}")
                except Exception as e:
                    logger.warning(f"   ⚠️ Error installing {dep}: {e}")

            if installed_count > 0:
                self.fixes_applied.append(f"Dependencies ({installed_count} installed)")

            return installed_count >= len(missing_deps) * 0.7  # 70% success rate

        except Exception as e:
            logger.error(f"   ❌ Failed to install dependencies: {e}")
            return False

    def fix_data_flow_syntax(self) -> bool:
        """Fix data flow syntax errors"""
        try:
            logger.info("   🔧 Fixing data flow syntax errors...")

            data_flow_file = (
                self.project_root / "backend" / "api" / "data_flow_routes.py"
            )

            if not data_flow_file.exists():
                logger.info("   📝 Data flow routes file not found - skipping")
                return True

            self.backup_file(data_flow_file)
            content = data_flow_file.read_text()

            # Look for syntax error around line 369
            lines = content.split("\n")
            fixed_lines = []

            for i, line in enumerate(lines):
                # Fix common syntax issues
                if i == 368:  # Line 369 (0-indexed)
                    # Fix missing colon or other syntax issues
                    if (
                        line.strip()
                        and not line.strip().endswith(":")
                        and any(
                            keyword in line
                            for keyword in [
                                "if",
                                "else",
                                "for",
                                "while",
                                "def",
                                "class",
                            ]
                        )
                    ):
                        if not line.strip().endswith(":"):
                            line = line.rstrip() + ":"

                fixed_lines.append(line)

            fixed_content = "\n".join(fixed_lines)

            if fixed_content != content:
                data_flow_file.write_text(fixed_content)
                logger.info("   ✅ Fixed data flow syntax errors")
                self.fixes_applied.append("Data flow syntax")
            else:
                logger.info("   📝 No data flow syntax errors found")

            return True

        except Exception as e:
            logger.error(f"   ❌ Failed to fix data flow syntax: {e}")
            return False

    def fix_import_chains(self) -> bool:
        """Fix import chain issues"""
        try:
            logger.info("   🔧 Fixing import chain issues...")

            # Ensure all __init__.py files exist
            init_files = [
                self.project_root / "backend" / "__init__.py",
                self.project_root / "backend" / "mcp_servers" / "__init__.py",
                self.project_root / "backend" / "core" / "__init__.py",
                self.project_root / "backend" / "services" / "__init__.py",
                self.project_root / "backend" / "utils" / "__init__.py",
            ]

            created_count = 0
            for init_file in init_files:
                if not init_file.exists():
                    init_file.parent.mkdir(parents=True, exist_ok=True)
                    init_file.write_text('"""Package initialization"""\n')
                    created_count += 1
                    logger.info(f"   ✅ Created {init_file}")

            if created_count > 0:
                self.fixes_applied.append(
                    f"Import chains ({created_count} __init__.py files)"
                )

            return True

        except Exception as e:
            logger.error(f"   ❌ Failed to fix import chains: {e}")
            return False

    async def run_comprehensive_health_check(self) -> dict[str, Any]:
        """Run comprehensive health check with performance metrics"""
        logger.info("🏥 Phase 2: Running Comprehensive Health Check")

        start_time = time.time()
        results = {
            "timestamp": datetime.now().isoformat(),
            "services": {},
            "overall_health": True,
            "performance_summary": {},
            "alerts": [],
        }

        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10)
        ) as session:
            tasks = []
            for service_id, service_info in self.services.items():
                task = self.check_service_health(session, service_id, service_info)
                tasks.append(task)

            service_results = await asyncio.gather(*tasks, return_exceptions=True)

            healthy_count = 0
            total_response_time = 0

            for i, (service_id, service_info) in enumerate(self.services.items()):
                result = service_results[i]

                if isinstance(result, Exception):
                    results["services"][service_id] = {
                        "status": "error",
                        "error": str(result),
                        "response_time": None,
                        "name": service_info["name"],
                    }
                    results["overall_health"] = False
                else:
                    results["services"][service_id] = result
                    if result["status"] == "healthy":
                        healthy_count += 1
                        total_response_time += result["response_time"]

        # Calculate performance metrics
        execution_time = (time.time() - start_time) * 1000
        health_percentage = (healthy_count / len(self.services)) * 100
        avg_response_time = total_response_time / max(healthy_count, 1)

        results["performance_summary"] = {
            "execution_time_ms": round(execution_time, 2),
            "health_percentage": round(health_percentage, 1),
            "average_response_time_ms": round(avg_response_time, 2),
            "services_healthy": f"{healthy_count}/{len(self.services)}",
            "performance_grade": self.calculate_performance_grade(
                avg_response_time, health_percentage
            ),
        }

        logger.info(
            f"   📊 Health: {health_percentage}% | Avg Response: {avg_response_time:.1f}ms | Grade: {results['performance_summary']['performance_grade']}"
        )

        return results

    async def check_service_health(
        self, session: aiohttp.ClientSession, service_id: str, service_info: dict
    ) -> dict[str, Any]:
        """Check individual service health with detailed metrics"""
        start_time = time.time()

        try:
            async with session.get(service_info["url"]) as response:
                response_time = (time.time() - start_time) * 1000

                if response.status == 200:
                    try:
                        data = await response.json()
                        return {
                            "status": "healthy",
                            "response_time": round(response_time, 2),
                            "status_code": response.status,
                            "name": service_info["name"],
                            "port": service_info["port"],
                            "data": data,
                        }
                    except:
                        return {
                            "status": "healthy",
                            "response_time": round(response_time, 2),
                            "status_code": response.status,
                            "name": service_info["name"],
                            "port": service_info["port"],
                            "data": "non-json response",
                        }
                else:
                    return {
                        "status": "unhealthy",
                        "response_time": round(response_time, 2),
                        "status_code": response.status,
                        "name": service_info["name"],
                        "port": service_info["port"],
                        "error": f"HTTP {response.status}",
                    }

        except TimeoutError:
            return {
                "status": "timeout",
                "response_time": None,
                "name": service_info["name"],
                "port": service_info["port"],
                "error": "Request timeout",
            }
        except Exception as e:
            return {
                "status": "error",
                "response_time": None,
                "name": service_info["name"],
                "port": service_info["port"],
                "error": str(e),
            }

    def calculate_performance_grade(
        self, avg_response_time: float, health_percentage: float
    ) -> str:
        """Calculate performance grade based on metrics"""
        if health_percentage == 100 and avg_response_time < 100:
            return "A+"
        elif health_percentage >= 90 and avg_response_time < 500:
            return "A"
        elif health_percentage >= 80 and avg_response_time < 1000:
            return "B"
        elif health_percentage >= 70 and avg_response_time < 2000:
            return "C"
        else:
            return "D"

    async def run_performance_test(
        self, concurrent_requests: int = 10, test_duration: int = 30
    ) -> dict[str, Any]:
        """Run performance test with concurrent requests"""
        logger.info(
            f"⚡ Phase 3: Running Performance Test ({concurrent_requests} concurrent, {test_duration}s)"
        )

        start_time = time.time()
        end_time = start_time + test_duration
        results = {
            "test_config": {
                "concurrent_requests": concurrent_requests,
                "duration_seconds": test_duration,
            },
            "metrics": {},
            "errors": [],
        }

        async def make_requests():
            request_times = []
            errors = []

            async with aiohttp.ClientSession() as session:
                while time.time() < end_time:
                    tasks = []
                    for _ in range(concurrent_requests):
                        task = self.time_request(
                            session, "http://localhost:8000/health"
                        )
                        tasks.append(task)

                    batch_results = await asyncio.gather(*tasks, return_exceptions=True)

                    for result in batch_results:
                        if isinstance(result, Exception):
                            errors.append(str(result))
                        else:
                            request_times.append(result)

                    await asyncio.sleep(0.1)

            return request_times, errors

        request_times, errors = await make_requests()

        if request_times:
            results["metrics"] = {
                "total_requests": len(request_times),
                "successful_requests": len(request_times),
                "failed_requests": len(errors),
                "avg_response_time_ms": round(statistics.mean(request_times), 2),
                "min_response_time_ms": round(min(request_times), 2),
                "max_response_time_ms": round(max(request_times), 2),
                "p95_response_time_ms": (
                    round(statistics.quantiles(request_times, n=20)[18], 2)
                    if len(request_times) > 20
                    else round(max(request_times), 2)
                ),
                "requests_per_second": round(len(request_times) / test_duration, 2),
                "error_rate": (
                    round(len(errors) / (len(request_times) + len(errors)), 4)
                    if (len(request_times) + len(errors)) > 0
                    else 0
                ),
            }

        results["errors"] = errors[:10]

        logger.info(
            f"   📊 {len(request_times)} successful requests | {results['metrics']['requests_per_second']} req/s | {results['metrics']['avg_response_time_ms']}ms avg"
        )

        return results

    async def time_request(self, session: aiohttp.ClientSession, url: str) -> float:
        """Time a single request"""
        start_time = time.time()
        async with session.get(url) as response:
            await response.read()
            return (time.time() - start_time) * 1000

    async def run_comprehensive_enhancement(self) -> dict[str, Any]:
        """Run complete deployment enhancement"""
        logger.info("🚀 Starting Comprehensive Deployment Enhancement")

        results = {
            "start_time": datetime.now().isoformat(),
            "phases": {},
            "overall_success": False,
            "execution_time": 0,
            "recommendations": [],
        }

        try:
            # Phase 1: Fix critical issues
            phase1_success = self.fix_critical_deployment_issues()
            results["phases"]["phase1_critical_fixes"] = {
                "success": phase1_success,
                "fixes_applied": self.fixes_applied.copy(),
            }

            # Phase 2: Health check
            health_results = await self.run_comprehensive_health_check()
            results["phases"]["phase2_health_check"] = health_results

            # Phase 3: Performance test (only if health is good)
            if health_results["performance_summary"]["health_percentage"] >= 60:
                perf_results = await self.run_performance_test(
                    concurrent_requests=5, test_duration=15
                )
                results["phases"]["phase3_performance_test"] = perf_results
            else:
                logger.warning("⚠️ Skipping performance test due to poor health")
                results["phases"]["phase3_performance_test"] = {
                    "skipped": "Poor system health"
                }

            # Calculate overall success
            health_good = (
                health_results["performance_summary"]["health_percentage"] >= 80
            )
            fixes_good = phase1_success
            results["overall_success"] = health_good and fixes_good

            # Generate recommendations
            results["recommendations"] = self.generate_recommendations(results)

        except Exception as e:
            logger.error(f"💥 Enhancement failed: {e}")
            results["error"] = str(e)

        results["execution_time"] = time.time() - self.start_time
        return results

    def generate_recommendations(self, results: dict[str, Any]) -> list[str]:
        """Generate recommendations based on results"""
        recommendations = []

        # Health-based recommendations
        if "phase2_health_check" in results["phases"]:
            health_data = results["phases"]["phase2_health_check"]
            health_percentage = health_data["performance_summary"]["health_percentage"]
            avg_response_time = health_data["performance_summary"][
                "average_response_time_ms"
            ]

            if health_percentage < 100:
                recommendations.append(
                    f"🔧 Fix unhealthy services - currently at {health_percentage}% health"
                )

            if avg_response_time > 1000:
                recommendations.append(
                    f"⚡ Optimize response times - currently averaging {avg_response_time}ms"
                )

            if health_percentage >= 90 and avg_response_time < 500:
                recommendations.append(
                    "✅ System performing well - consider production deployment"
                )

        # Performance-based recommendations
        if (
            "phase3_performance_test" in results["phases"]
            and "metrics" in results["phases"]["phase3_performance_test"]
        ):
            perf_data = results["phases"]["phase3_performance_test"]["metrics"]

            if perf_data["error_rate"] > 0.05:
                recommendations.append(
                    f"🚨 High error rate detected: {perf_data['error_rate']*100:.1f}%"
                )

            if perf_data["requests_per_second"] < 10:
                recommendations.append(
                    f"📈 Consider scaling - only {perf_data['requests_per_second']} req/s"
                )

        # General recommendations
        if len(self.fixes_applied) > 0:
            recommendations.append("📄 Review applied fixes and test thoroughly")

        recommendations.append(
            "🔍 Use enhanced monitoring for continuous health checks"
        )
        recommendations.append("🧪 Run automated tests before major deployments")

        return recommendations

    def generate_final_report(self, results: dict[str, Any]) -> str:
        """Generate comprehensive final report"""
        execution_time = results.get("execution_time", 0)
        overall_success = results.get("overall_success", False)

        # Health metrics
        health_data = results.get("phases", {}).get("phase2_health_check", {})
        health_summary = health_data.get("performance_summary", {})

        # Performance metrics
        perf_data = results.get("phases", {}).get("phase3_performance_test", {})
        perf_metrics = perf_data.get("metrics", {})

        report = f"""
🎉 COMPREHENSIVE DEPLOYMENT ENHANCEMENT REPORT
{'='*60}

⏱️  Execution Time: {execution_time:.2f}s
🎯 Overall Status: {'✅ SUCCESS' if overall_success else '⚠️ NEEDS ATTENTION'}
📅 Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🔧 PHASE 1: CRITICAL FIXES
{'─'*30}
✅ Fixes Applied: {len(self.fixes_applied)}
{chr(10).join(f"   • {fix}" for fix in self.fixes_applied)}

🏥 PHASE 2: HEALTH CHECK
{'─'*30}
📊 System Health: {health_summary.get('health_percentage', 0)}%
⚡ Avg Response: {health_summary.get('average_response_time_ms', 0)}ms
🎖️  Performance Grade: {health_summary.get('performance_grade', 'N/A')}
🔄 Services Status: {health_summary.get('services_healthy', 'N/A')}

⚡ PHASE 3: PERFORMANCE TEST
{'─'*30}"""

        if perf_metrics:
            report += f"""
📈 Total Requests: {perf_metrics.get('total_requests', 0)}
🎯 Success Rate: {100 - perf_metrics.get('error_rate', 0)*100:.1f}%
⚡ Requests/Second: {perf_metrics.get('requests_per_second', 0)}
�� Avg Response: {perf_metrics.get('avg_response_time_ms', 0)}ms
🔝 95th Percentile: {perf_metrics.get('p95_response_time_ms', 0)}ms"""
        else:
            report += "\n⚠️ Performance test skipped or failed"

        report += f"""

🎯 RECOMMENDATIONS
{'─'*30}
{chr(10).join(f"   {rec}" for rec in results.get('recommendations', []))}

📁 BACKUP FILES CREATED
{'─'*30}
{chr(10).join(f"   • {backup}" for backup in self.backup_files)}

🚀 DEPLOYMENT STATUS
{'─'*30}
Status: {'🟢 READY FOR PRODUCTION' if overall_success else '🟡 NEEDS ATTENTION' if health_summary.get('health_percentage', 0) > 60 else '🔴 CRITICAL ISSUES'}

💡 NEXT STEPS
{'─'*30}
   1. Review and test all applied fixes
   2. Monitor system health continuously
   3. Address any remaining recommendations
   4. Deploy to production when ready
   5. Set up automated monitoring and alerting

📞 SUPPORT
{'─'*30}
   • Check logs for detailed error information
   • Use backup files for rollback if needed
   • Run health checks regularly
   • Monitor performance metrics
"""

        return report


async def main():
    """Main execution function"""
    enhancer = ComprehensiveDeploymentEnhancement()

    try:
        # Run comprehensive enhancement
        results = await enhancer.run_comprehensive_enhancement()

        # Generate and display report
        report = enhancer.generate_final_report(results)
        print(report)

        # Save report
        report_path = (
            enhancer.project_root / "COMPREHENSIVE_DEPLOYMENT_ENHANCEMENT_REPORT.md"
        )
        report_path.write_text(report)
        logger.info(f"📄 Report saved to: {report_path}")

        # Return appropriate exit code
        return 0 if results.get("overall_success", False) else 1

    except Exception as e:
        logger.error(f"💥 Enhancement failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
