#!/usr/bin/env python3
"""
Cursor AI Analysis Script
AI-enhanced code analysis optimized for Cursor GitHub integration
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

import ast
import git
from dataclasses import dataclass, asdict

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class CodeAnalysisResult:
    """Code analysis result structure"""

    quality_score: int
    security_issues: int
    performance_opportunities: int
    cursor_optimizations: List[str]
    mcp_integration_health: Dict[str, Any]
    github_integration_status: Dict[str, Any]
    recommendations: List[str]
    analysis_timestamp: str
    commit_hash: str
    branch: str


class CursorAIAnalyzer:
    """AI-enhanced code analyzer for Cursor GitHub integration"""

    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)
        self.repo = git.Repo(repo_path)
        self.analysis_results = {}

    def analyze_codebase(
        self, github_event: str, branch: str, commit: str
    ) -> CodeAnalysisResult:
        """Perform comprehensive AI-enhanced code analysis"""
        logger.info(f"🧠 Starting Cursor AI analysis for {branch}@{commit[:8]}")

        # Core analysis components
        quality_score = self._calculate_quality_score()
        security_issues = self._analyze_security()
        performance_opportunities = self._analyze_performance()
        cursor_optimizations = self._analyze_cursor_optimizations()
        mcp_health = self._analyze_mcp_integration()
        github_status = self._analyze_github_integration()
        recommendations = self._generate_recommendations()

        result = CodeAnalysisResult(
            quality_score=quality_score,
            security_issues=security_issues,
            performance_opportunities=performance_opportunities,
            cursor_optimizations=cursor_optimizations,
            mcp_integration_health=mcp_health,
            github_integration_status=github_status,
            recommendations=recommendations,
            analysis_timestamp=datetime.now().isoformat(),
            commit_hash=commit,
            branch=branch,
        )

        logger.info(f"✅ Analysis complete - Quality Score: {quality_score}/100")
        return result

    def _calculate_quality_score(self) -> int:
        """Calculate overall code quality score"""
        scores = []

        # Python code quality
        python_files = list(self.repo_path.rglob("*.py"))
        if python_files:
            python_score = self._analyze_python_quality(python_files)
            scores.append(python_score)

        # Configuration quality
        config_score = self._analyze_config_quality()
        scores.append(config_score)

        # Documentation quality
        doc_score = self._analyze_documentation_quality()
        scores.append(doc_score)

        # MCP integration quality
        mcp_score = self._analyze_mcp_quality()
        scores.append(mcp_score)

        return int(sum(scores) / len(scores)) if scores else 50

    def _analyze_python_quality(self, python_files: List[Path]) -> int:
        """Analyze Python code quality"""
        total_score = 0
        file_count = 0

        for file_path in python_files:
            if file_path.name.startswith(".") or "venv" in str(file_path):
                continue

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Parse AST for analysis
                tree = ast.parse(content)
                file_score = self._analyze_ast(tree, content)
                total_score += file_score
                file_count += 1

            except Exception as e:
                logger.warning(f"Could not analyze {file_path}: {e}")
                continue

        return int(total_score / file_count) if file_count > 0 else 50

    def _analyze_ast(self, tree: ast.AST, content: str) -> int:
        """Analyze Python AST for quality metrics"""
        score = 100

        # Check for docstrings
        functions = [
            node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
        ]
        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]

        # Docstring coverage
        functions_with_docs = sum(1 for func in functions if ast.get_docstring(func))
        classes_with_docs = sum(1 for cls in classes if ast.get_docstring(cls))

        total_items = len(functions) + len(classes)
        if total_items > 0:
            doc_coverage = (functions_with_docs + classes_with_docs) / total_items
            score = int(score * (0.7 + 0.3 * doc_coverage))

        # Type hints coverage
        typed_functions = sum(
            1
            for func in functions
            if func.returns or any(arg.annotation for arg in func.args.args)
        )
        if functions:
            type_coverage = typed_functions / len(functions)
            score = int(score * (0.8 + 0.2 * type_coverage))

        # Complexity analysis
        complexity_penalty = self._calculate_complexity_penalty(tree)
        score = max(20, score - complexity_penalty)

        return score

    def _calculate_complexity_penalty(self, tree: ast.AST) -> int:
        """Calculate complexity penalty"""
        penalty = 0

        for node in ast.walk(tree):
            # Nested loops penalty
            if isinstance(node, (ast.For, ast.While)):
                nested_loops = sum(
                    1
                    for child in ast.walk(node)
                    if isinstance(child, (ast.For, ast.While)) and child != node
                )
                penalty += nested_loops * 5

            # Deep nesting penalty
            if isinstance(node, ast.FunctionDef):
                max_depth = self._calculate_nesting_depth(node)
                if max_depth > 4:
                    penalty += (max_depth - 4) * 3

        return penalty

    def _calculate_nesting_depth(self, node: ast.AST, depth: int = 0) -> int:
        """Calculate maximum nesting depth"""
        max_depth = depth

        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                child_depth = self._calculate_nesting_depth(child, depth + 1)
                max_depth = max(max_depth, child_depth)

        return max_depth

    def _analyze_security(self) -> int:
        """Analyze security issues"""
        security_issues = 0

        # Check for hardcoded secrets
        python_files = list(self.repo_path.rglob("*.py"))
        for file_path in python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Common security patterns
                security_patterns = [
                    'password = "',
                    'api_key = "',
                    'secret = "',
                    'token = "',
                    "AWS_SECRET_ACCESS_KEY",
                    'OPENAI_API_KEY = "sk-',
                ]

                for pattern in security_patterns:
                    if pattern in content:
                        security_issues += 1
                        logger.warning(f"🔒 Potential hardcoded secret in {file_path}")

            except Exception as e:
                logger.warning(f"Could not analyze {file_path} for security: {e}")

        return security_issues

    def _analyze_performance(self) -> int:
        """Analyze performance opportunities"""
        opportunities = 0

        python_files = list(self.repo_path.rglob("*.py"))
        for file_path in python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Performance anti-patterns
                if "for i in range(len(" in content:
                    opportunities += 1
                if "time.sleep(" in content and "async" not in content:
                    opportunities += 1
                if ".append(" in content and "for " in content:
                    opportunities += 1  # Potential list comprehension

            except Exception:
                continue

        return opportunities

    def _analyze_cursor_optimizations(self) -> List[str]:
        """Analyze Cursor-specific optimizations"""
        optimizations = []

        # Check .cursorrules file
        cursorrules_path = self.repo_path / ".cursorrules"
        if not cursorrules_path.exists():
            optimizations.append("Create .cursorrules file for Cursor AI optimization")
        else:
            with open(cursorrules_path, "r") as f:
                content = f.read()
                if "MCP" not in content:
                    optimizations.append("Add MCP integration rules to .cursorrules")
                if "GitHub" not in content:
                    optimizations.append("Add GitHub integration rules to .cursorrules")

        # Check MCP configuration
        mcp_config_path = self.repo_path / "cursor_mcp_config.json"
        if mcp_config_path.exists():
            with open(mcp_config_path, "r") as f:
                config = json.load(f)
                if "autoTriggers" not in str(config):
                    optimizations.append("Enable auto-triggers in MCP configuration")
                if "workflows" not in config:
                    optimizations.append("Add workflow automation to MCP configuration")

        return optimizations

    def _analyze_mcp_integration(self) -> Dict[str, Any]:
        """Analyze MCP integration health"""
        health = {
            "servers_configured": 0,
            "servers_with_health_checks": 0,
            "auto_triggers_enabled": False,
            "workflow_automation": False,
            "issues": [],
        }

        mcp_config_path = self.repo_path / "cursor_mcp_config.json"
        if mcp_config_path.exists():
            try:
                with open(mcp_config_path, "r") as f:
                    config = json.load(f)

                if "mcpServers" in config:
                    health["servers_configured"] = len(config["mcpServers"])

                    # Check for health monitoring
                    for server_name, server_config in config["mcpServers"].items():
                        if "healthCheck" in str(server_config):
                            health["servers_with_health_checks"] += 1

                if "workflows" in config:
                    health["workflow_automation"] = True

                if "autoTriggers" in str(config):
                    health["auto_triggers_enabled"] = True

            except Exception as e:
                health["issues"].append(f"Could not parse MCP config: {e}")
        else:
            health["issues"].append("No MCP configuration found")

        return health

    def _analyze_github_integration(self) -> Dict[str, Any]:
        """Analyze GitHub integration status"""
        status = {
            "workflows_configured": 0,
            "cursor_specific_workflows": False,
            "automated_analysis": False,
            "issues": [],
        }

        workflows_dir = self.repo_path / ".github" / "workflows"
        if workflows_dir.exists():
            workflow_files = list(workflows_dir.glob("*.yml")) + list(
                workflows_dir.glob("*.yaml")
            )
            status["workflows_configured"] = len(workflow_files)

            for workflow_file in workflow_files:
                try:
                    with open(workflow_file, "r") as f:
                        content = f.read()
                        if "cursor" in content.lower():
                            status["cursor_specific_workflows"] = True
                        if "analysis" in content.lower():
                            status["automated_analysis"] = True
                except Exception:
                    continue
        else:
            status["issues"].append("No GitHub workflows directory found")

        return status

    def _analyze_config_quality(self) -> int:
        """Analyze configuration quality"""
        score = 100

        # Check for essential config files
        essential_configs = [
            "cursor_mcp_config.json",
            ".cursorrules",
            "requirements.txt",
            "docker-compose.yml",
        ]

        missing_configs = []
        for config in essential_configs:
            if not (self.repo_path / config).exists():
                missing_configs.append(config)
                score -= 15

        return max(20, score)

    def _analyze_documentation_quality(self) -> int:
        """Analyze documentation quality"""
        score = 100

        # Check for README
        readme_files = list(self.repo_path.glob("README*"))
        if not readme_files:
            score -= 30

        # Check for docs directory
        docs_dir = self.repo_path / "docs"
        if not docs_dir.exists():
            score -= 20

        return max(20, score)

    def _analyze_mcp_quality(self) -> int:
        """Analyze MCP integration quality"""
        score = 100

        mcp_servers_dir = self.repo_path / "mcp-servers"
        if not mcp_servers_dir.exists():
            return 50

        # Count MCP servers
        mcp_servers = [d for d in mcp_servers_dir.iterdir() if d.is_dir()]
        if len(mcp_servers) < 3:
            score -= 20

        # Check for health checks
        servers_with_health = 0
        for server_dir in mcp_servers:
            server_files = list(server_dir.glob("*.py"))
            for server_file in server_files:
                try:
                    with open(server_file, "r") as f:
                        content = f.read()
                        if "health_check" in content:
                            servers_with_health += 1
                            break
                except Exception:
                    continue

        if servers_with_health < len(mcp_servers) * 0.8:
            score -= 15

        return max(20, score)

    def _generate_recommendations(self) -> List[str]:
        """Generate AI-powered recommendations"""
        recommendations = []

        # Based on analysis results
        if self.analysis_results.get("quality_score", 100) < 80:
            recommendations.append(
                "🎯 Improve code quality by adding docstrings and type hints"
            )

        if self.analysis_results.get("security_issues", 0) > 0:
            recommendations.append(
                "🔒 Review and remove hardcoded secrets - use Pulumi ESC"
            )

        if self.analysis_results.get("performance_opportunities", 0) > 5:
            recommendations.append(
                "⚡ Optimize performance bottlenecks using async/await patterns"
            )

        # Cursor-specific recommendations
        mcp_health = self.analysis_results.get("mcp_integration_health", {})
        if not mcp_health.get("auto_triggers_enabled", False):
            recommendations.append(
                "🔄 Enable auto-triggers in Cursor MCP configuration"
            )

        if not mcp_health.get("workflow_automation", False):
            recommendations.append(
                "🤖 Add workflow automation to enhance development productivity"
            )

        # GitHub integration recommendations
        github_status = self.analysis_results.get("github_integration_status", {})
        if not github_status.get("cursor_specific_workflows", False):
            recommendations.append(
                "🔗 Add Cursor-specific GitHub workflows for enhanced integration"
            )

        return recommendations

    def save_results(self, result: CodeAnalysisResult, output_file: str):
        """Save analysis results to file"""
        self.analysis_results = asdict(result)

        with open(output_file, "w") as f:
            json.dump(self.analysis_results, f, indent=2)

        logger.info(f"📊 Analysis results saved to {output_file}")


def main():
    """Main analysis function"""
    parser = argparse.ArgumentParser(description="Cursor AI Code Analysis")
    parser.add_argument("--github-event", default="push", help="GitHub event type")
    parser.add_argument("--branch", default="main", help="Git branch")
    parser.add_argument("--commit", default="HEAD", help="Git commit hash")
    parser.add_argument("--output", default="analysis_results.json", help="Output file")
    parser.add_argument("--repo-path", default=".", help="Repository path")

    args = parser.parse_args()

    try:
        analyzer = CursorAIAnalyzer(args.repo_path)
        result = analyzer.analyze_codebase(args.github_event, args.branch, args.commit)
        analyzer.save_results(result, args.output)

        print(f"✅ Analysis complete - Quality Score: {result.quality_score}/100")
        print(f"📊 Security Issues: {result.security_issues}")
        print(f"⚡ Performance Opportunities: {result.performance_opportunities}")
        print(f"🎯 Recommendations: {len(result.recommendations)}")

        return 0

    except Exception as e:
        logger.error(f"❌ Analysis failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
