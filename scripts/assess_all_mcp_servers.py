#!/usr/bin/env python3
"""
MCP Server Assessment Tool
Comprehensive analysis of all MCP servers for compliance with StandardizedMCPServer patterns
"""

import ast
import asyncio
import json
import logging
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path

import aiohttp

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class MCPServerAssessment:
    """Assessment result for a single MCP server"""

    server_name: str
    server_path: str
    port: int

    # Compliance metrics
    standardized_base: bool = False
    health_checks: bool = False
    metrics: bool = False
    cline_v3_18: bool = False
    lambda_ready: bool = False
    proper_imports: bool = False
    async_patterns: bool = False
    error_handling: bool = False

    # Quality metrics
    test_coverage: float = 0.0
    documentation: bool = False
    code_quality_score: float = 0.0
    lines_of_code: int = 0

    # Operational metrics
    is_operational: bool = False
    health_status: str = "unknown"
    response_time_ms: float = 0.0

    # Issues found
    critical_issues: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)

    # Overall score
    compliance_score: float = 0.0


class MCPServerAssessor:
    """Comprehensive MCP server assessor"""

    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        self.mcp_servers_path = self.base_path / "mcp-servers"
        self.config_path = self.base_path / "config/consolidated_mcp_ports.json"
        self.session: aiohttp.ClientSession | None = None

    async def assess_all_servers(self) -> dict[str, MCPServerAssessment]:
        """Assess all MCP servers for compliance and health"""
        logger.info("🔍 Starting comprehensive MCP server assessment...")

        # Load server configuration
        server_config = self._load_server_config()

        # Initialize HTTP session
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10))

        assessments = {}

        try:
            # Assess each server directory
            for server_dir in self.mcp_servers_path.iterdir():
                if server_dir.is_dir() and not server_dir.name.startswith("."):
                    server_name = server_dir.name
                    port = server_config.get(server_name, {}).get("port", 0)

                    logger.info(f"📊 Assessing {server_name}...")
                    assessment = await self._assess_server(
                        server_name, server_dir, port
                    )
                    assessments[server_name] = assessment

        finally:
            if self.session:
                await self.session.close()

        # Generate summary report
        self._generate_summary_report(assessments)

        logger.info("✅ MCP server assessment completed")
        return assessments

    def _load_server_config(self) -> dict:
        """Load server configuration from consolidated ports"""
        try:
            with open(self.config_path) as f:
                config = json.load(f)
                return {
                    server: {"port": port}
                    for server, port in config.get("active_servers", {}).items()
                }
        except Exception as e:
            logger.warning(f"Failed to load server config: {e}")
            return {}

    async def _assess_server(
        self, server_name: str, server_path: Path, port: int
    ) -> MCPServerAssessment:
        """Assess a single MCP server"""
        assessment = MCPServerAssessment(
            server_name=server_name, server_path=str(server_path), port=port
        )

        # Find main server file
        server_file = self._find_server_file(server_path)
        if not server_file:
            assessment.critical_issues.append("No main server file found")
            return assessment

        # Analyze code structure
        await self._analyze_code_structure(server_file, assessment)

        # Test server health if operational
        if port > 0:
            await self._test_server_health(port, assessment)

        # Calculate compliance score
        self._calculate_compliance_score(assessment)

        return assessment

    def _find_server_file(self, server_path: Path) -> Path | None:
        """Find the main server file in the directory"""
        possible_names = [
            f"{server_path.name}_mcp_server.py",
            "mcp_server.py",
            "server.py",
            "main.py",
        ]

        for name in possible_names:
            file_path = server_path / name
            if file_path.exists():
                return file_path

        # Look for any Python file
        python_files = list(server_path.glob("*.py"))
        if python_files:
            return python_files[0]

        return None

    async def _analyze_code_structure(
        self, server_file: Path, assessment: MCPServerAssessment
    ):
        """Analyze the code structure of the server file"""
        try:
            with open(server_file, encoding="utf-8") as f:
                content = f.read()

            # Count lines of code
            assessment.lines_of_code = len(
                [line for line in content.split("\n") if line.strip()]
            )

            # Parse AST for analysis
            try:
                tree = ast.parse(content)
                await self._analyze_ast(tree, content, assessment)
            except SyntaxError as e:
                assessment.critical_issues.append(f"Syntax error: {e}")

        except Exception as e:
            assessment.critical_issues.append(f"Failed to read server file: {e}")

    async def _analyze_ast(
        self, tree: ast.AST, content: str, assessment: MCPServerAssessment
    ):
        """Analyze the AST for compliance patterns"""
        content_lower = content.lower()

        # Check for StandardizedMCPServer inheritance
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for base in node.bases:
                    if (
                        isinstance(base, ast.Name)
                        and base.id == "StandardizedMCPServer"
                    ):
                        assessment.standardized_base = True
                        break
                    elif (
                        isinstance(base, ast.Attribute)
                        and base.attr == "StandardizedMCPServer"
                    ):
                        assessment.standardized_base = True
                        break

        # Check for proper imports
        standardized_import = "standardized_mcp_server" in content
        proper_typing = "from typing import" in content or "import typing" in content
        assessment.proper_imports = standardized_import and proper_typing

        # Check for health checks
        assessment.health_checks = (
            "health_check" in content_lower
            or "get_health" in content_lower
            or "/health" in content
        )

        # Check for metrics
        assessment.metrics = (
            "prometheus" in content_lower
            or "metrics" in content_lower
            or "counter" in content_lower
            or "gauge" in content_lower
        )

        # Check for Cline v3.18 features
        cline_features = [
            "webfetch",
            "self_knowledge",
            "improved_diff",
            "ModelProvider",
            "ServerCapability",
            "WebFetchResult",
        ]
        assessment.cline_v3_18 = any(feature in content for feature in cline_features)

        # Check for Lambda Labs compatibility
        lambda_patterns = [
            "lambda_labs",
            "gpu",
            "cuda",
            "nvidia",
            "kubernetes",
            "k8s",
            "container",
        ]
        assessment.lambda_ready = any(
            pattern in content_lower for pattern in lambda_patterns
        )

        # Check for async patterns
        async_functions = [
            node for node in ast.walk(tree) if isinstance(node, ast.AsyncFunctionDef)
        ]
        assessment.async_patterns = len(async_functions) > 0

        # Check for error handling
        try_except_count = len(
            [node for node in ast.walk(tree) if isinstance(node, ast.Try)]
        )
        assessment.error_handling = try_except_count >= 3  # Reasonable threshold

        # Check for documentation
        docstring_count = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
                if ast.get_docstring(node):
                    docstring_count += 1

        total_definitions = len(
            [
                node
                for node in ast.walk(tree)
                if isinstance(
                    node, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef
                )
            ]
        )

        assessment.documentation = (
            docstring_count / max(total_definitions, 1)
        ) > 0.5  # At least 50% documented

    async def _test_server_health(self, port: int, assessment: MCPServerAssessment):
        """Test server health if it's running"""
        if not self.session:
            assessment.health_status = "no_session"
            assessment.warnings.append("HTTP session not available for health check")
            return

        try:
            start_time = time.time()

            async with self.session.get(f"http://localhost:{port}/health") as response:
                response_time = (time.time() - start_time) * 1000
                assessment.response_time_ms = response_time

                if response.status == 200:
                    assessment.is_operational = True
                    assessment.health_status = "healthy"

                    # Try to get detailed health data
                    try:
                        health_data = await response.json()
                        if isinstance(health_data, dict):
                            # Extract additional health metrics
                            status = health_data.get("status", "unknown")
                            assessment.health_status = status
                    except Exception:
                        pass  # JSON parsing failed, but server responded
                else:
                    assessment.health_status = f"unhealthy (HTTP {response.status})"

        except TimeoutError:
            assessment.health_status = "timeout"
            assessment.warnings.append("Health check timed out")
        except Exception as e:
            assessment.health_status = "unreachable"
            assessment.warnings.append(f"Health check failed: {str(e)[:100]}")

    def _calculate_compliance_score(self, assessment: MCPServerAssessment):
        """Calculate overall compliance score (0-100)"""
        score = 0.0
        max_score = 100.0

        # Critical compliance factors (60 points)
        if assessment.standardized_base:
            score += 20
        if assessment.health_checks:
            score += 15
        if assessment.proper_imports:
            score += 10
        if assessment.async_patterns:
            score += 10
        if assessment.error_handling:
            score += 5

        # Modern features (20 points)
        if assessment.metrics:
            score += 10
        if assessment.cline_v3_18:
            score += 10

        # Quality factors (15 points)
        if assessment.documentation:
            score += 10
        if assessment.lines_of_code > 50:  # Non-trivial implementation
            score += 5

        # Operational readiness (5 points)
        if assessment.is_operational:
            score += 5

        # Penalties for critical issues
        score -= len(assessment.critical_issues) * 10
        score = max(0, score)  # Don't go below 0

        assessment.compliance_score = min(score, max_score)

        # Generate recommendations
        self._generate_recommendations(assessment)

    def _generate_recommendations(self, assessment: MCPServerAssessment):
        """Generate actionable recommendations"""
        if not assessment.standardized_base:
            assessment.recommendations.append(
                "🏗️ Migrate to StandardizedMCPServer base class for consistency"
            )

        if not assessment.health_checks:
            assessment.recommendations.append(
                "❤️ Implement comprehensive health checks (/health endpoint)"
            )

        if not assessment.metrics:
            assessment.recommendations.append("📊 Add Prometheus metrics for monitoring")

        if not assessment.cline_v3_18:
            assessment.recommendations.append(
                "🆕 Upgrade to Cline v3.18 features (WebFetch, self-knowledge, improved diff)"
            )

        if not assessment.documentation:
            assessment.recommendations.append(
                "📚 Improve documentation with comprehensive docstrings"
            )

        if not assessment.async_patterns:
            assessment.recommendations.append(
                "⚡ Implement async patterns for better performance"
            )

        if not assessment.error_handling:
            assessment.recommendations.append(
                "🛡️ Add comprehensive error handling and logging"
            )

        if assessment.compliance_score < 70:
            assessment.critical_issues.append(
                f"Low compliance score ({assessment.compliance_score:.1f}/100) - requires immediate attention"
            )

    def _generate_summary_report(self, assessments: dict[str, MCPServerAssessment]):
        """Generate comprehensive summary report"""
        timestamp = datetime.now().isoformat()
        total_servers = len(assessments)

        # Calculate statistics
        operational_count = sum(1 for a in assessments.values() if a.is_operational)
        standardized_count = sum(1 for a in assessments.values() if a.standardized_base)
        avg_compliance = sum(a.compliance_score for a in assessments.values()) / max(
            total_servers, 1
        )

        # Categorize servers
        excellent = [
            name for name, a in assessments.items() if a.compliance_score >= 90
        ]
        good = [
            name for name, a in assessments.items() if 70 <= a.compliance_score < 90
        ]
        needs_work = [
            name for name, a in assessments.items() if 50 <= a.compliance_score < 70
        ]
        critical = [name for name, a in assessments.items() if a.compliance_score < 50]

        # Generate report
        report = {
            "assessment_timestamp": timestamp,
            "summary": {
                "total_servers": total_servers,
                "operational_servers": operational_count,
                "standardized_servers": standardized_count,
                "average_compliance_score": round(avg_compliance, 1),
                "operational_percentage": round(
                    (operational_count / max(total_servers, 1)) * 100, 1
                ),
                "standardized_percentage": round(
                    (standardized_count / max(total_servers, 1)) * 100, 1
                ),
            },
            "categorization": {
                "excellent_servers": excellent,
                "good_servers": good,
                "needs_work": needs_work,
                "critical_servers": critical,
            },
            "detailed_assessments": {
                name: asdict(assessment) for name, assessment in assessments.items()
            },
            "recommendations": {
                "immediate_actions": [
                    (
                        f"Fix critical issues in: {', '.join(critical)}"
                        if critical
                        else None
                    ),
                    (
                        f"Standardize servers: {', '.join([name for name, a in assessments.items() if not a.standardized_base])}"
                        if any(not a.standardized_base for a in assessments.values())
                        else None
                    ),
                    (
                        f"Add health checks to: {', '.join([name for name, a in assessments.items() if not a.health_checks])}"
                        if any(not a.health_checks for a in assessments.values())
                        else None
                    ),
                ],
                "strategic_improvements": [
                    "Implement Cline v3.18 features across all servers",
                    "Add comprehensive monitoring and metrics",
                    "Standardize documentation and testing",
                    "Optimize for Lambda Labs infrastructure",
                ],
            },
        }

        # Remove None values from immediate actions
        report["recommendations"]["immediate_actions"] = [
            action
            for action in report["recommendations"]["immediate_actions"]
            if action
        ]

        # Save report
        report_file = (
            self.base_path
            / f"MCP_ASSESSMENT_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        # Print summary to console
        self._print_summary(report)

        logger.info(f"📄 Detailed report saved to: {report_file}")

    def _print_summary(self, report: dict):
        """Print assessment summary to console"""
        summary = report["summary"]
        categorization = report["categorization"]

        print("\n" + "=" * 70)
        print("🔍 MCP SERVER ASSESSMENT SUMMARY")
        print("=" * 70)

        print("\n📊 OVERVIEW:")
        print(f"   Total Servers: {summary['total_servers']}")
        print(
            f"   Operational: {summary['operational_servers']} ({summary['operational_percentage']}%)"
        )
        print(
            f"   Standardized: {summary['standardized_servers']} ({summary['standardized_percentage']}%)"
        )
        print(f"   Average Compliance: {summary['average_compliance_score']}/100")

        print("\n🏆 SERVER CATEGORIES:")
        if categorization["excellent_servers"]:
            print(
                f"   ✅ Excellent (90-100): {', '.join(categorization['excellent_servers'])}"
            )
        if categorization["good_servers"]:
            print(f"   🟢 Good (70-89): {', '.join(categorization['good_servers'])}")
        if categorization["needs_work"]:
            print(f"   🟡 Needs Work (50-69): {', '.join(categorization['needs_work'])}")
        if categorization["critical_servers"]:
            print(
                f"   🔴 Critical (<50): {', '.join(categorization['critical_servers'])}"
            )

        print("\n🎯 IMMEDIATE ACTIONS NEEDED:")
        for action in report["recommendations"]["immediate_actions"]:
            print(f"   • {action}")

        print("\n🚀 STRATEGIC IMPROVEMENTS:")
        for improvement in report["recommendations"]["strategic_improvements"]:
            print(f"   • {improvement}")

        print("\n" + "=" * 70)


async def main():
    """Main assessment function"""
    assessor = MCPServerAssessor()
    assessments = await assessor.assess_all_servers()

    # Return assessment results for potential scripting use
    return assessments


if __name__ == "__main__":
    asyncio.run(main())
