#!/usr/bin/env python3
"""
Generate Executive Quality Report for Sophia AI
CEO-level insights with business impact and ROI calculations
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


class ExecutiveReportGenerator:
    """Generate executive-level quality reports"""

    def __init__(self):
        self.report_data = None
        self.detailed_data = None

    def load_analysis_data(self):
        """Load analysis results"""
        try:
            # Load summary report
            report_path = Path("codacy_analysis_report.json")
            if report_path.exists():
                with open(report_path) as f:
                    self.report_data = json.load(f)

            # Load detailed results
            detailed_path = Path("codacy_detailed_results.json")
            if detailed_path.exists():
                with open(detailed_path) as f:
                    self.detailed_data = json.load(f)

            return self.report_data is not None

        except Exception as e:
            console.print(f"[red]Error loading data: {e}[/red]")
            return False

    def calculate_business_metrics(self) -> dict[str, Any]:
        """Calculate business-relevant metrics"""
        if not self.report_data:
            return {}

        summary = self.report_data.get("summary", {})

        # Calculate metrics
        total_files = summary.get("total_files", 0)
        total_issues = summary.get("total_issues", 0)
        critical_issues = summary.get("critical_issues", 0)
        debt_hours = summary.get("total_debt_hours", 0)

        # Business calculations
        metrics = {
            "quality_score": self._calculate_overall_quality_score(),
            "risk_assessment": self._assess_business_risk(
                critical_issues, total_issues
            ),
            "productivity_impact": self._calculate_productivity_impact(debt_hours),
            "roi_projection": self._project_roi(debt_hours, total_issues),
            "time_to_excellence": self._estimate_improvement_timeline(
                total_issues, debt_hours
            ),
            "competitive_advantage": self._assess_competitive_position(),
        }

        return metrics

    def _calculate_overall_quality_score(self) -> float:
        """Calculate weighted quality score"""
        if not self.report_data:
            return 0.0

        dist = self.report_data.get("quality_distribution", {})
        total = sum(dist.values())

        if total == 0:
            return 0.0

        # Weighted scoring
        score = (
            dist.get("excellent", 0) * 100
            + dist.get("good", 0) * 80
            + dist.get("fair", 0) * 60
            + dist.get("poor", 0) * 30
        ) / total

        return round(score, 1)

    def _assess_business_risk(self, critical: int, total: int) -> dict[str, Any]:
        """Assess business risk level"""
        if critical > 10:
            level = "CRITICAL"
            impact = "Immediate production risk, potential data breach"
            action = "Emergency remediation required within 24 hours"
        elif critical > 5:
            level = "HIGH"
            impact = "Significant security vulnerabilities"
            action = "Schedule immediate security sprint"
        elif total > 100:
            level = "MEDIUM"
            impact = "Technical debt impacting velocity"
            action = "Plan remediation over next sprint"
        else:
            level = "LOW"
            impact = "Manageable quality issues"
            action = "Continue normal development"

        return {
            "level": level,
            "impact": impact,
            "recommended_action": action,
            "estimated_incident_cost": critical * 50000,  # $50K per critical issue
        }

    def _calculate_productivity_impact(self, debt_hours: float) -> dict[str, Any]:
        """Calculate productivity impact"""
        # Assume 40 hour work week
        dev_weeks = debt_hours / 40

        # Productivity loss due to technical debt (research shows 23% on average)
        current_productivity_loss = min(debt_hours / 1000 * 23, 50)  # Cap at 50%

        return {
            "current_velocity_impact": f"-{current_productivity_loss:.0f}%",
            "developer_weeks_required": round(dev_weeks, 1),
            "opportunity_cost": round(
                debt_hours * 150 * 1.5, 0
            ),  # 1.5x for opportunity
            "projected_velocity_gain": f"+{current_productivity_loss * 0.8:.0f}%",  # 80% recovery
        }

    def _project_roi(self, debt_hours: float, issues: int) -> dict[str, Any]:
        """Project ROI from quality improvements"""
        # Investment
        fix_cost = debt_hours * 150  # Developer cost

        # Returns
        incident_reduction = issues * 0.1 * 5000  # 10% cause incidents, $5K each
        productivity_gain = debt_hours * 150 * 0.23 * 3  # 23% gain over 3 years

        total_return = incident_reduction + productivity_gain
        roi = ((total_return - fix_cost) / fix_cost * 100) if fix_cost > 0 else 0

        return {
            "investment_required": round(fix_cost, 0),
            "3_year_return": round(total_return, 0),
            "roi_percentage": round(roi, 0),
            "payback_months": round(fix_cost / (total_return / 36), 1)
            if total_return > 0
            else 999,
        }

    def _estimate_improvement_timeline(
        self, issues: int, debt_hours: float
    ) -> dict[str, Any]:
        """Estimate timeline to reach quality targets"""
        # Assume team can fix 20 issues per week
        weeks_to_fix = issues / 20

        return {
            "to_good_quality": round(weeks_to_fix * 0.5, 1),  # 50% improvement
            "to_excellent_quality": round(weeks_to_fix, 1),  # 100% improvement
            "quick_wins": round(issues * 0.3),  # 30% are quick wins
            "recommended_phases": max(3, int(weeks_to_fix / 4)),
        }

    def _assess_competitive_position(self) -> str:
        """Assess competitive position based on quality"""
        score = self._calculate_overall_quality_score()

        if score >= 90:
            return "Industry Leader - Top 5% code quality"
        elif score >= 80:
            return "Above Average - Top 20% code quality"
        elif score >= 70:
            return "Average - Middle 50% code quality"
        elif score >= 60:
            return "Below Average - Bottom 30% code quality"
        else:
            return "At Risk - Bottom 10% code quality"

    def generate_executive_summary(self) -> str:
        """Generate executive summary text"""
        if not self.report_data:
            return "No data available"

        metrics = self.calculate_business_metrics()
        risk = metrics.get("risk_assessment", {})
        roi = metrics.get("roi_projection", {})

        summary = f"""
EXECUTIVE SUMMARY - Sophia AI Code Quality Assessment

Current State:
- Overall Quality Score: {metrics.get('quality_score', 0):.1f}/100
- Risk Level: {risk.get('level', 'UNKNOWN')}
- Competitive Position: {metrics.get('competitive_advantage', 'Unknown')}

Business Impact:
- Productivity Impact: {metrics.get('productivity_impact', {}).get('current_velocity_impact', 'N/A')}
- Estimated Incident Cost Risk: ${risk.get('estimated_incident_cost', 0):,}

Investment Opportunity:
- Required Investment: ${roi.get('investment_required', 0):,}
- Projected 3-Year Return: ${roi.get('3_year_return', 0):,}
- ROI: {roi.get('roi_percentage', 0):.0f}%
- Payback Period: {roi.get('payback_months', 0):.1f} months

Recommendation: {risk.get('recommended_action', 'Continue monitoring')}
"""

        return summary

    def display_executive_report(self):
        """Display the executive report"""
        console.clear()

        # Header
        console.print(
            Panel.fit(
                "[bold cyan]SOPHIA AI - EXECUTIVE QUALITY REPORT[/bold cyan]\n"
                + f"[dim]{datetime.now().strftime('%B %d, %Y')}[/dim]",
                box=box.DOUBLE,
            )
        )

        # Executive Summary
        console.print("\n[bold]EXECUTIVE SUMMARY[/bold]")
        console.print(Panel(self.generate_executive_summary(), box=box.ROUNDED))

        # Key Metrics Dashboard
        metrics = self.calculate_business_metrics()

        # Quality Score Gauge
        score = metrics.get("quality_score", 0)
        score_color = "green" if score >= 80 else "yellow" if score >= 60 else "red"
        console.print(
            f"\n[bold]Overall Quality Score: [{score_color}]{score:.1f}/100[/{score_color}][/bold]"
        )

        # Risk Assessment
        risk = metrics.get("risk_assessment", {})
        risk_color = (
            "red"
            if risk.get("level") == "CRITICAL"
            else "yellow"
            if risk.get("level") == "HIGH"
            else "green"
        )

        risk_table = Table(title="Risk Assessment", box=box.ROUNDED)
        risk_table.add_column("Metric", style="cyan")
        risk_table.add_column("Value", style=risk_color)

        risk_table.add_row("Risk Level", risk.get("level", "UNKNOWN"))
        risk_table.add_row("Business Impact", risk.get("impact", "Unknown"))
        risk_table.add_row(
            "Incident Cost Risk", f"${risk.get('estimated_incident_cost', 0):,}"
        )

        console.print("\n", risk_table)

        # ROI Analysis
        roi = metrics.get("roi_projection", {})

        roi_table = Table(title="ROI Analysis", box=box.ROUNDED)
        roi_table.add_column("Metric", style="cyan")
        roi_table.add_column("Value", style="green")

        roi_table.add_row(
            "Investment Required", f"${roi.get('investment_required', 0):,}"
        )
        roi_table.add_row("3-Year Return", f"${roi.get('3_year_return', 0):,}")
        roi_table.add_row("ROI", f"{roi.get('roi_percentage', 0):.0f}%")
        roi_table.add_row(
            "Payback Period", f"{roi.get('payback_months', 0):.1f} months"
        )

        console.print("\n", roi_table)

        # Timeline
        timeline = metrics.get("time_to_excellence", {})

        timeline_table = Table(title="Improvement Timeline", box=box.ROUNDED)
        timeline_table.add_column("Milestone", style="cyan")
        timeline_table.add_column("Timeline", style="yellow")

        timeline_table.add_row("Quick Wins", f"{timeline.get('quick_wins', 0)} issues")
        timeline_table.add_row(
            "Good Quality (80+)", f"{timeline.get('to_good_quality', 0)} weeks"
        )
        timeline_table.add_row(
            "Excellent Quality (90+)",
            f"{timeline.get('to_excellent_quality', 0)} weeks",
        )

        console.print("\n", timeline_table)

        # Strategic Recommendations
        console.print("\n[bold]STRATEGIC RECOMMENDATIONS[/bold]")

        recommendations = []

        if risk.get("level") in ["CRITICAL", "HIGH"]:
            recommendations.append(
                "🚨 Immediate Action: Deploy emergency quality task force"
            )

        if score < 70:
            recommendations.append("📊 Implement mandatory code quality gates in CI/CD")

        if roi.get("roi_percentage", 0) > 200:
            recommendations.append(
                "💰 High ROI opportunity - prioritize quality investment"
            )

        productivity = metrics.get("productivity_impact", {})
        if productivity.get("developer_weeks_required", 0) > 10:
            recommendations.append("👥 Consider dedicated quality improvement team")

        recommendations.append(
            "🎯 Set target: Achieve 90+ quality score within 3 months"
        )

        for i, rec in enumerate(recommendations, 1):
            console.print(f"  {i}. {rec}")

        # Footer
        console.print("\n" + "─" * 80)
        console.print(
            "[dim]Report generated by Enhanced Codacy AI Analysis System[/dim]"
        )
        console.print(
            "[dim]For detailed technical analysis, see codacy_detailed_results.json[/dim]"
        )

    def save_executive_report(self):
        """Save executive report to file"""
        report = {
            "generated_at": datetime.now().isoformat(),
            "executive_summary": self.generate_executive_summary(),
            "business_metrics": self.calculate_business_metrics(),
            "raw_data": self.report_data,
        }

        report_path = Path("executive_quality_report.json")
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        console.print(f"\n[green]✅ Executive report saved to {report_path}[/green]")


def main():
    """Main entry point"""
    generator = ExecutiveReportGenerator()

    # Load analysis data
    if not generator.load_analysis_data():
        console.print("[red]❌ No analysis data found[/red]")
        console.print(
            "Run 'python scripts/analyze_entire_codebase_with_codacy.py' first"
        )
        return

    # Generate and display report
    generator.display_executive_report()

    # Save report
    generator.save_executive_report()


if __name__ == "__main__":
    main()
