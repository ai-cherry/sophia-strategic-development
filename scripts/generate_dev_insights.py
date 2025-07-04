#!/usr/bin/env python3
"""
Development Insights Generator
Generate actionable development insights from analysis results
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DevelopmentInsightsGenerator:
    """Generate development insights from analysis data"""

    def __init__(self, analysis_file: str):
        self.analysis_file = Path(analysis_file)
        self.analysis_data = self._load_analysis_data()

    def _load_analysis_data(self) -> dict[str, Any]:
        """Load analysis data from file"""
        if not self.analysis_file.exists():
            raise FileNotFoundError(f"Analysis file not found: {self.analysis_file}")

        with open(self.analysis_file) as f:
            return json.load(f)

    def generate_insights(self) -> dict[str, Any]:
        """Generate comprehensive development insights"""
        insights = {
            "timestamp": datetime.now().isoformat(),
            "analysis_summary": self._generate_analysis_summary(),
            "quality_insights": self._generate_quality_insights(),
            "security_insights": self._generate_security_insights(),
            "performance_insights": self._generate_performance_insights(),
            "cursor_optimization_insights": self._generate_cursor_insights(),
            "mcp_integration_insights": self._generate_mcp_insights(),
            "github_integration_insights": self._generate_github_insights(),
            "recommendations": self._generate_recommendations(),
            "action_items": self._generate_action_items(),
        }

        return insights

    def _generate_analysis_summary(self) -> dict[str, Any]:
        """Generate high-level analysis summary"""
        return {
            "overall_quality_score": self.analysis_data.get("quality_score", 0),
            "total_security_issues": self.analysis_data.get("security_issues", 0),
            "performance_opportunities": self.analysis_data.get(
                "performance_opportunities", 0
            ),
            "branch": self.analysis_data.get("branch", "unknown"),
            "commit": self.analysis_data.get("commit_hash", "unknown")[:8],
            "analysis_timestamp": self.analysis_data.get("analysis_timestamp"),
        }

    def _generate_quality_insights(self) -> dict[str, Any]:
        """Generate code quality insights"""
        quality_score = self.analysis_data.get("quality_score", 0)

        if quality_score >= 90:
            quality_level = "excellent"
            quality_message = "Code quality is excellent! Keep up the great work."
        elif quality_score >= 80:
            quality_level = "good"
            quality_message = "Code quality is good with room for minor improvements."
        elif quality_score >= 70:
            quality_level = "fair"
            quality_message = (
                "Code quality is fair but needs attention in several areas."
            )
        else:
            quality_level = "needs_improvement"
            quality_message = "Code quality needs significant improvement."

        return {
            "score": quality_score,
            "level": quality_level,
            "message": quality_message,
            "trend": self._calculate_quality_trend(),
            "improvement_areas": self._identify_quality_improvement_areas(),
        }

    def _generate_security_insights(self) -> dict[str, Any]:
        """Generate security insights"""
        security_issues = self.analysis_data.get("security_issues", 0)

        if security_issues == 0:
            security_level = "secure"
            security_message = "No security issues detected. Great job!"
        elif security_issues <= 2:
            security_level = "minor_issues"
            security_message = f"{security_issues} minor security issues detected."
        elif security_issues <= 5:
            security_level = "moderate_issues"
            security_message = f"{security_issues} security issues require attention."
        else:
            security_level = "critical_issues"
            security_message = (
                f"{security_issues} security issues need immediate attention!"
            )

        return {
            "issues_count": security_issues,
            "level": security_level,
            "message": security_message,
            "recommendations": self._generate_security_recommendations(),
        }

    def _generate_performance_insights(self) -> dict[str, Any]:
        """Generate performance insights"""
        perf_opportunities = self.analysis_data.get("performance_opportunities", 0)

        return {
            "opportunities_count": perf_opportunities,
            "optimization_potential": (
                "high"
                if perf_opportunities > 10
                else "medium"
                if perf_opportunities > 5
                else "low"
            ),
            "recommendations": self._generate_performance_recommendations(),
        }

    def _generate_cursor_insights(self) -> dict[str, Any]:
        """Generate Cursor optimization insights"""
        optimizations = self.analysis_data.get("cursor_optimizations", [])

        return {
            "optimization_count": len(optimizations),
            "optimizations": optimizations,
            "cursor_readiness": (
                "optimized" if len(optimizations) == 0 else "needs_optimization"
            ),
        }

    def _generate_mcp_insights(self) -> dict[str, Any]:
        """Generate MCP integration insights"""
        mcp_health = self.analysis_data.get("mcp_integration_health", {})

        servers_configured = mcp_health.get("servers_configured", 0)
        auto_triggers = mcp_health.get("auto_triggers_enabled", False)
        workflow_automation = mcp_health.get("workflow_automation", False)

        health_score = 0
        if servers_configured > 0:
            health_score += 40
        if auto_triggers:
            health_score += 30
        if workflow_automation:
            health_score += 30

        return {
            "health_score": health_score,
            "servers_configured": servers_configured,
            "auto_triggers_enabled": auto_triggers,
            "workflow_automation_enabled": workflow_automation,
            "status": "healthy" if health_score >= 80 else "needs_attention",
            "issues": mcp_health.get("issues", []),
        }

    def _generate_github_insights(self) -> dict[str, Any]:
        """Generate GitHub integration insights"""
        github_status = self.analysis_data.get("github_integration_status", {})

        workflows_configured = github_status.get("workflows_configured", 0)
        cursor_workflows = github_status.get("cursor_specific_workflows", False)
        automated_analysis = github_status.get("automated_analysis", False)

        integration_score = 0
        if workflows_configured > 0:
            integration_score += 40
        if cursor_workflows:
            integration_score += 30
        if automated_analysis:
            integration_score += 30

        return {
            "integration_score": integration_score,
            "workflows_configured": workflows_configured,
            "cursor_workflows_enabled": cursor_workflows,
            "automated_analysis_enabled": automated_analysis,
            "status": (
                "well_integrated" if integration_score >= 80 else "needs_enhancement"
            ),
            "issues": github_status.get("issues", []),
        }

    def _generate_recommendations(self) -> list[str]:
        """Generate actionable recommendations"""
        recommendations = []

        # Quality recommendations
        quality_score = self.analysis_data.get("quality_score", 0)
        if quality_score < 80:
            recommendations.append(
                "🎯 Improve code quality by adding docstrings and type hints"
            )

        # Security recommendations
        security_issues = self.analysis_data.get("security_issues", 0)
        if security_issues > 0:
            recommendations.append(
                "🔒 Address security issues by removing hardcoded secrets"
            )

        # Performance recommendations
        perf_opportunities = self.analysis_data.get("performance_opportunities", 0)
        if perf_opportunities > 5:
            recommendations.append("⚡ Optimize performance using async/await patterns")

        # Cursor recommendations
        cursor_optimizations = self.analysis_data.get("cursor_optimizations", [])
        if cursor_optimizations:
            recommendations.append(
                "🔧 Apply Cursor optimizations for better AI integration"
            )

        # MCP recommendations
        mcp_health = self.analysis_data.get("mcp_integration_health", {})
        if not mcp_health.get("auto_triggers_enabled", False):
            recommendations.append("🔄 Enable auto-triggers in MCP configuration")

        # GitHub recommendations
        github_status = self.analysis_data.get("github_integration_status", {})
        if not github_status.get("cursor_specific_workflows", False):
            recommendations.append("🔗 Add Cursor-specific GitHub workflows")

        return recommendations

    def _generate_action_items(self) -> list[dict[str, Any]]:
        """Generate specific action items with priorities"""
        action_items = []

        # High priority items
        security_issues = self.analysis_data.get("security_issues", 0)
        if security_issues > 0:
            action_items.append(
                {
                    "priority": "high",
                    "category": "security",
                    "title": "Fix Security Issues",
                    "description": f"Address {security_issues} security issues found in code",
                    "estimated_time": "2-4 hours",
                }
            )

        # Medium priority items
        quality_score = self.analysis_data.get("quality_score", 0)
        if quality_score < 80:
            action_items.append(
                {
                    "priority": "medium",
                    "category": "quality",
                    "title": "Improve Code Quality",
                    "description": "Add missing docstrings and type hints",
                    "estimated_time": "4-8 hours",
                }
            )

        # Low priority items
        cursor_optimizations = self.analysis_data.get("cursor_optimizations", [])
        if cursor_optimizations:
            action_items.append(
                {
                    "priority": "low",
                    "category": "optimization",
                    "title": "Apply Cursor Optimizations",
                    "description": "Implement suggested Cursor configuration improvements",
                    "estimated_time": "1-2 hours",
                }
            )

        return action_items

    def _calculate_quality_trend(self) -> str:
        """Calculate quality trend (placeholder for historical data)"""
        # In real implementation, compare with historical data
        return "stable"

    def _identify_quality_improvement_areas(self) -> list[str]:
        """Identify specific areas for quality improvement"""
        areas = []

        quality_score = self.analysis_data.get("quality_score", 0)
        if quality_score < 80:
            areas.extend(["documentation", "type_hints", "code_complexity"])

        return areas

    def _generate_security_recommendations(self) -> list[str]:
        """Generate security-specific recommendations"""
        recommendations = []

        security_issues = self.analysis_data.get("security_issues", 0)
        if security_issues > 0:
            recommendations.extend(
                [
                    "Use Pulumi ESC for secret management",
                    "Remove hardcoded credentials from code",
                    "Implement proper input validation",
                    "Add security scanning to CI/CD pipeline",
                ]
            )

        return recommendations

    def _generate_performance_recommendations(self) -> list[str]:
        """Generate performance-specific recommendations"""
        recommendations = []

        perf_opportunities = self.analysis_data.get("performance_opportunities", 0)
        if perf_opportunities > 0:
            recommendations.extend(
                [
                    "Use list comprehensions instead of loops",
                    "Implement async/await for I/O operations",
                    "Optimize database queries",
                    "Add caching for expensive operations",
                ]
            )

        return recommendations

    def generate_github_comment(self) -> str:
        """Generate GitHub comment format"""
        insights = self.generate_insights()

        comment = []
        comment.append("## 🧠 Development Insights")
        comment.append("")

        # Summary
        summary = insights["analysis_summary"]
        comment.append(f"**Quality Score**: {summary['overall_quality_score']}/100")
        comment.append(f"**Security Issues**: {summary['total_security_issues']}")
        comment.append(
            f"**Performance Opportunities**: {summary['performance_opportunities']}"
        )
        comment.append("")

        # Recommendations
        comment.append("### 🎯 Key Recommendations")
        for rec in insights["recommendations"][:5]:  # Top 5 recommendations
            comment.append(f"- {rec}")
        comment.append("")

        # Action Items
        action_items = insights["action_items"]
        if action_items:
            comment.append("### 📋 Action Items")
            for item in action_items:
                priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}
                emoji = priority_emoji.get(item["priority"], "⚪")
                comment.append(
                    f"- {emoji} **{item['title']}** ({item['estimated_time']})"
                )
                comment.append(f"  {item['description']}")
            comment.append("")

        comment.append("---")
        comment.append("*Generated by Sophia AI Development Insights*")

        return "\n".join(comment)

    def generate_markdown_report(self) -> str:
        """Generate comprehensive markdown report"""
        insights = self.generate_insights()

        report = []
        report.append("# 📊 Development Insights Report")
        report.append("")
        report.append(f"**Generated**: {insights['timestamp']}")
        report.append(f"**Branch**: {insights['analysis_summary']['branch']}")
        report.append(f"**Commit**: {insights['analysis_summary']['commit']}")
        report.append("")

        # Quality Section
        quality = insights["quality_insights"]
        report.append("## 🎯 Code Quality")
        report.append(f"**Score**: {quality['score']}/100 ({quality['level']})")
        report.append(f"**Status**: {quality['message']}")
        report.append("")

        # Security Section
        security = insights["security_insights"]
        report.append("## 🔒 Security")
        report.append(f"**Issues**: {security['issues_count']} ({security['level']})")
        report.append(f"**Status**: {security['message']}")
        if security["recommendations"]:
            report.append("**Recommendations**:")
            for rec in security["recommendations"]:
                report.append(f"- {rec}")
        report.append("")

        # Performance Section
        performance = insights["performance_insights"]
        report.append("## ⚡ Performance")
        report.append(f"**Opportunities**: {performance['opportunities_count']}")
        report.append(
            f"**Optimization Potential**: {performance['optimization_potential']}"
        )
        report.append("")

        # MCP Integration
        mcp = insights["mcp_integration_insights"]
        report.append("## 🔌 MCP Integration")
        report.append(f"**Health Score**: {mcp['health_score']}/100")
        report.append(f"**Servers Configured**: {mcp['servers_configured']}")
        report.append(
            f"**Auto-triggers**: {'✅' if mcp['auto_triggers_enabled'] else '❌'}"
        )
        report.append("")

        # GitHub Integration
        github = insights["github_integration_insights"]
        report.append("## 🔗 GitHub Integration")
        report.append(f"**Integration Score**: {github['integration_score']}/100")
        report.append(f"**Workflows**: {github['workflows_configured']}")
        report.append(
            f"**Cursor Workflows**: {'✅' if github['cursor_workflows_enabled'] else '❌'}"
        )
        report.append("")

        # Recommendations
        report.append("## 🎯 Recommendations")
        for rec in insights["recommendations"]:
            report.append(f"- {rec}")
        report.append("")

        # Action Items
        action_items = insights["action_items"]
        if action_items:
            report.append("## 📋 Action Items")
            for item in action_items:
                report.append(
                    f"### {item['title']} ({item['priority'].title()} Priority)"
                )
                report.append(f"**Category**: {item['category']}")
                report.append(f"**Description**: {item['description']}")
                report.append(f"**Estimated Time**: {item['estimated_time']}")
                report.append("")

        return "\n".join(report)


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Generate Development Insights")
    parser.add_argument("--analysis-file", required=True, help="Analysis results file")
    parser.add_argument(
        "--output-format",
        choices=["json", "markdown", "github-comment"],
        default="json",
        help="Output format",
    )
    parser.add_argument("--output-file", help="Output file path")

    args = parser.parse_args()

    try:
        generator = DevelopmentInsightsGenerator(args.analysis_file)

        if args.output_format == "json":
            insights = generator.generate_insights()
            output = json.dumps(insights, indent=2)
        elif args.output_format == "markdown":
            output = generator.generate_markdown_report()
        elif args.output_format == "github-comment":
            output = generator.generate_github_comment()

        if args.output_file:
            with open(args.output_file, "w") as f:
                f.write(output)
            logger.info(f"📊 Insights saved to {args.output_file}")
        else:
            print(output)

        return 0

    except Exception as e:
        logger.error(f"❌ Failed to generate insights: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
