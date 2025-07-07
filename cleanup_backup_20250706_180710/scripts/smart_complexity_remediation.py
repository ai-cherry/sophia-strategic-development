#!/usr/bin/env python3
"""
Smart Complexity Remediation Script for Sophia AI

This script implements automated analysis and refactoring for the 86 medium complexity
issues identified in the codebase, prioritizing by business impact and applying
appropriate refactoring patterns.
"""

import ast
import logging
import os
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ComplexityIssueType(Enum):
    """Types of complexity issues"""

    LONG_FUNCTION = "long_function"
    HIGH_CYCLOMATIC = "high_cyclomatic"
    TOO_MANY_PARAMETERS = "too_many_parameters"
    LARGE_FILE = "large_file"


class RefactoringStrategy(Enum):
    """Refactoring strategies"""

    EXTRACT_METHOD = "extract_method"
    STRATEGY_PATTERN = "strategy_pattern"
    BUILDER_PATTERN = "builder_pattern"
    TEMPLATE_METHOD = "template_method"


class Priority(Enum):
    """Issue priority levels"""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class ComplexityIssue:
    """Represents a complexity issue in the codebase"""

    file_path: str
    function_name: str
    issue_type: ComplexityIssueType
    severity: str
    metric_value: int
    line_number: int
    priority: Priority
    business_impact: str
    recommended_strategy: RefactoringStrategy
    estimated_effort_hours: float


class SmartComplexityAnalyzer:
    """Analyzes codebase for complexity issues and generates remediation plans"""

    def __init__(self):
        self.issues = []
        self.critical_functions = {
            # Core API Endpoints
            "unified_business_query": Priority.CRITICAL,
            "get_current_configuration": Priority.CRITICAL,
            "update_user_permissions": Priority.CRITICAL,
            "search_issues": Priority.CRITICAL,
            # MCP Server Core Functions
            "smart_recall_enhanced": Priority.CRITICAL,
            "handle_tool_call": Priority.CRITICAL,
            "call_tool": Priority.CRITICAL,
            "handle_list_tools": Priority.CRITICAL,
            "get_issue_details": Priority.CRITICAL,
            "auto_fix_enhanced": Priority.CRITICAL,
            # Sales Intelligence Core
            "analyze_pipeline_health": Priority.CRITICAL,
            "get_competitor_talking_points": Priority.CRITICAL,
            "store_gong_call_insight": Priority.CRITICAL,
            # High Priority Performance Functions
            "generate_marketing_content": Priority.HIGH,
            "create_transformation_procedures": Priority.HIGH,
            "orchestrate_concurrent_workflow": Priority.HIGH,
            "_process_unified_intelligence": Priority.HIGH,
        }

        self.business_impact_map = {
            "smart_recall_enhanced": "Core AI Memory functionality - affects all MCP operations",
            "unified_business_query": "Central business intelligence - affects executive dashboard",
            "analyze_pipeline_health": "Sales forecasting accuracy - affects revenue predictions",
            "generate_marketing_content": "Marketing automation efficiency - affects lead generation",
            "create_transformation_procedures": "Data pipeline reliability - affects analytics accuracy",
            "orchestrate_concurrent_workflow": "System performance - affects user experience",
            "get_competitor_talking_points": "Sales enablement - affects deal closure rates",
        }

    def analyze_codebase(self, root_path: str = ".") -> list[ComplexityIssue]:
        """Analyze entire codebase for complexity issues"""
        logger.info("🔍 Starting comprehensive complexity analysis...")

        python_files = self._find_python_files(root_path)

        for file_path in python_files:
            try:
                issues = self._analyze_file(file_path)
                self.issues.extend(issues)
            except Exception as e:
                logger.warning(f"⚠️ Could not analyze {file_path}: {e}")

        # Prioritize issues
        self._prioritize_issues()

        logger.info(f"✅ Analysis complete. Found {len(self.issues)} complexity issues")
        return self.issues

    def _find_python_files(self, root_path: str) -> list[str]:
        """Find all Python files in the codebase"""
        python_files = []
        exclude_patterns = [
            "__pycache__",
            ".git",
            ".venv",
            "node_modules",
            ".backup",
            "migrations",
            "tests",
        ]

        for root, dirs, files in os.walk(root_path):
            # Filter out excluded directories
            dirs[:] = [
                d for d in dirs if not any(pattern in d for pattern in exclude_patterns)
            ]

            for file in files:
                if file.endswith(".py") and not file.startswith("."):
                    file_path = os.path.join(root, file)
                    if not any(pattern in file_path for pattern in exclude_patterns):
                        python_files.append(file_path)

        return python_files

    def _analyze_file(self, file_path: str) -> list[ComplexityIssue]:
        """Analyze a single file for complexity issues"""
        issues = []

        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Parse AST
            tree = ast.parse(content)

            # Check file size
            lines = len(content.split("\n"))
            if lines > 600:
                issues.append(
                    ComplexityIssue(
                        file_path=file_path,
                        function_name="<file>",
                        issue_type=ComplexityIssueType.LARGE_FILE,
                        severity="MEDIUM",
                        metric_value=lines,
                        line_number=1,
                        priority=Priority.MEDIUM,
                        business_impact="Large files are harder to maintain and navigate",
                        recommended_strategy=RefactoringStrategy.EXTRACT_METHOD,
                        estimated_effort_hours=4.0,
                    )
                )

            # Analyze functions
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                    function_issues = self._analyze_function(file_path, node)
                    issues.extend(function_issues)

        except SyntaxError as e:
            logger.warning(f"Syntax error in {file_path}: {e}")
        except Exception as e:
            logger.error(f"Error analyzing {file_path}: {e}")

        return issues

    def _analyze_function(self, file_path: str, node: ast.AST) -> list[ComplexityIssue]:
        """Analyze a single function for complexity issues"""
        issues = []
        function_name = node.name

        # Calculate metrics
        line_count = node.end_lineno - node.lineno + 1
        complexity = self._calculate_cyclomatic_complexity(node)
        param_count = (
            len(node.args.args) + len(node.args.posonlyargs) + len(node.args.kwonlyargs)
        )
        if node.args.vararg:
            param_count += 1
        if node.args.kwarg:
            param_count += 1

        # Check function length
        if line_count > 50:
            priority = self.critical_functions.get(function_name, Priority.MEDIUM)
            business_impact = self.business_impact_map.get(
                function_name,
                "Function complexity affects maintainability and debugging",
            )

            issues.append(
                ComplexityIssue(
                    file_path=file_path,
                    function_name=function_name,
                    issue_type=ComplexityIssueType.LONG_FUNCTION,
                    severity="MEDIUM",
                    metric_value=line_count,
                    line_number=node.lineno,
                    priority=priority,
                    business_impact=business_impact,
                    recommended_strategy=RefactoringStrategy.EXTRACT_METHOD,
                    estimated_effort_hours=self._estimate_effort(
                        line_count, complexity
                    ),
                )
            )

        # Check cyclomatic complexity
        if complexity > 8:
            priority = self.critical_functions.get(function_name, Priority.MEDIUM)
            business_impact = self.business_impact_map.get(
                function_name,
                "High complexity increases bug risk and reduces maintainability",
            )

            issues.append(
                ComplexityIssue(
                    file_path=file_path,
                    function_name=function_name,
                    issue_type=ComplexityIssueType.HIGH_CYCLOMATIC,
                    severity="MEDIUM" if complexity <= 15 else "HIGH",
                    metric_value=complexity,
                    line_number=node.lineno,
                    priority=priority,
                    business_impact=business_impact,
                    recommended_strategy=RefactoringStrategy.STRATEGY_PATTERN,
                    estimated_effort_hours=self._estimate_effort(
                        line_count, complexity
                    ),
                )
            )

        # Check parameter count
        if param_count > 8:
            issues.append(
                ComplexityIssue(
                    file_path=file_path,
                    function_name=function_name,
                    issue_type=ComplexityIssueType.TOO_MANY_PARAMETERS,
                    severity="MEDIUM",
                    metric_value=param_count,
                    line_number=node.lineno,
                    priority=Priority.HIGH,
                    business_impact="Too many parameters make functions hard to use and test",
                    recommended_strategy=RefactoringStrategy.BUILDER_PATTERN,
                    estimated_effort_hours=2.0,
                )
            )

        return issues

    def _calculate_cyclomatic_complexity(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity of a function"""
        complexity = 1  # Base complexity

        for child in ast.walk(node):
            if isinstance(
                child,
                ast.If
                | ast.While
                | ast.For
                | ast.AsyncFor
                | ast.ExceptHandler
                | (ast.And | ast.Or)
                | ast.ListComp
                | ast.DictComp
                | ast.SetComp
                | ast.GeneratorExp,
            ):
                complexity += 1

        return complexity

    def _estimate_effort(self, line_count: int, complexity: int) -> float:
        """Estimate refactoring effort in hours"""
        base_effort = 1.0

        # Add effort based on function size
        if line_count > 100:
            base_effort += 3.0
        elif line_count > 75:
            base_effort += 2.0
        elif line_count > 50:
            base_effort += 1.0

        # Add effort based on complexity
        if complexity > 20:
            base_effort += 2.0
        elif complexity > 15:
            base_effort += 1.5
        elif complexity > 10:
            base_effort += 1.0

        return base_effort

    def _prioritize_issues(self):
        """Prioritize issues based on business impact and complexity"""
        priority_order = {
            Priority.CRITICAL: 0,
            Priority.HIGH: 1,
            Priority.MEDIUM: 2,
            Priority.LOW: 3,
        }

        self.issues.sort(
            key=lambda x: (priority_order[x.priority], -x.metric_value, x.function_name)
        )


def main():
    """Main entry point for the complexity analysis script"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Smart Complexity Analysis for Sophia AI"
    )
    parser.add_argument("--root-path", default=".", help="Root path to analyze")

    args = parser.parse_args()

    analyzer = SmartComplexityAnalyzer()
    issues = analyzer.analyze_codebase(args.root_path)

    if not issues:
        return

    # Categorize issues
    critical_issues = [i for i in issues if i.priority == Priority.CRITICAL]
    high_issues = [i for i in issues if i.priority == Priority.HIGH]
    [i for i in issues if i.priority == Priority.MEDIUM]

    for _i, _issue in enumerate(critical_issues[:10], 1):
        pass

    for _i, _issue in enumerate(high_issues[:10], 1):
        pass


if __name__ == "__main__":
    main()
