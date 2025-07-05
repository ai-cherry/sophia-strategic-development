#!/usr/bin/env python3
"""
Analyze Entire Sophia AI Codebase with Enhanced Codacy
Generates comprehensive quality report with business impact
"""

import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

import aiohttp
from rich.console import Console
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn
from rich.table import Table

console = Console()


class CodebaseAnalyzer:
    """Analyze entire codebase with enhanced Codacy"""

    def __init__(self):
        self.base_url = "http://localhost:3008"
        self.results = []
        self.summary = {
            "total_files": 0,
            "total_issues": 0,
            "critical_issues": 0,
            "high_issues": 0,
            "total_debt_hours": 0,
            "total_cost": 0,
            "files_by_score": {
                "excellent": [],  # 90-100
                "good": [],  # 70-89
                "fair": [],  # 50-69
                "poor": [],  # 0-49
            },
        }

    def get_python_files(self, root_dir: str = ".") -> list[Path]:
        """Get all Python files in the codebase"""
        python_files = []

        # Directories to skip
        skip_dirs = {
            ".venv",
            "__pycache__",
            ".git",
            "node_modules",
            "build",
            "dist",
            ".pytest_cache",
            ".mypy_cache",
        }

        for root, dirs, files in os.walk(root_dir):
            # Remove skip directories from dirs to prevent walking into them
            dirs[:] = [d for d in dirs if d not in skip_dirs]

            for file in files:
                if file.endswith(".py") and not file.startswith("."):
                    filepath = Path(root) / file
                    # Skip test files for now
                    if "test_" not in file and "_test" not in file:
                        python_files.append(filepath)

        return python_files

    async def analyze_file(self, filepath: Path) -> dict[str, Any]:
        """Analyze a single file"""
        try:
            # Read the file content
            with open(filepath, encoding="utf-8") as f:
                code = f.read()

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/v1/analyze/code",
                    json={
                        "code": code,
                        "filename": str(filepath),
                        "language": "python",
                        "enable_ai_insights": True,
                        "enable_auto_fix": True,
                        "context": {"is_production": "production" in str(filepath)},
                    },
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        console.print(
                            f"[red]Error analyzing {filepath}: {response.status}[/red]"
                        )
                        return None
        except Exception as e:
            console.print(f"[red]Error analyzing {filepath}: {e}[/red]")
            return None

    async def analyze_batch(self, files: list[Path], progress) -> list[dict[str, Any]]:
        """Analyze a batch of files concurrently"""
        task_id = progress.add_task("[cyan]Analyzing files...", total=len(files))
        results = []

        # Process in batches to avoid overwhelming the server
        batch_size = 5
        for i in range(0, len(files), batch_size):
            batch = files[i : i + batch_size]
            tasks = [self.analyze_file(f) for f in batch]
            batch_results = await asyncio.gather(*tasks)

            for filepath, result in zip(batch, batch_results, strict=False):
                if result:
                    results.append(result)
                    self.update_summary(result)
                progress.update(task_id, advance=1)

        return results

    def update_summary(self, result: dict[str, Any]):
        """Update summary statistics"""
        self.summary["total_files"] += 1

        issues = result.get("issues", [])
        self.summary["total_issues"] += len(issues)

        # Count by severity
        for issue in issues:
            severity = issue.get("severity", "").lower()
            if severity == "critical":
                self.summary["critical_issues"] += 1
            elif severity == "high":
                self.summary["high_issues"] += 1

        # Technical debt
        metrics = result.get("metrics", {})
        debt_hours = metrics.get("technical_debt_hours", 0)
        self.summary["total_debt_hours"] += debt_hours

        # Cost (assuming $150/hour)
        self.summary["total_cost"] += debt_hours * 150

        # Categorize by score
        score = metrics.get("overall_score", 0)
        filename = result.get("filename", "unknown")

        if score >= 90:
            self.summary["files_by_score"]["excellent"].append((filename, score))
        elif score >= 70:
            self.summary["files_by_score"]["good"].append((filename, score))
        elif score >= 50:
            self.summary["files_by_score"]["fair"].append((filename, score))
        else:
            self.summary["files_by_score"]["poor"].append((filename, score))

    def generate_report(self) -> dict[str, Any]:
        """Generate comprehensive report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": self.summary,
            "quality_distribution": {
                "excellent": len(self.summary["files_by_score"]["excellent"]),
                "good": len(self.summary["files_by_score"]["good"]),
                "fair": len(self.summary["files_by_score"]["fair"]),
                "poor": len(self.summary["files_by_score"]["poor"]),
            },
            "business_impact": {
                "total_technical_debt_cost": f"${self.summary['total_cost']:,.0f}",
                "estimated_fix_time": f"{self.summary['total_debt_hours']:.1f} hours",
                "critical_risk_files": len(self.summary["files_by_score"]["poor"]),
                "immediate_action_required": self.summary["critical_issues"] > 0,
            },
            "recommendations": self.generate_recommendations(),
        }

        return report

    def generate_recommendations(self) -> list[str]:
        """Generate strategic recommendations"""
        recommendations = []

        if self.summary["critical_issues"] > 0:
            recommendations.append(
                f"🚨 URGENT: Fix {self.summary['critical_issues']} critical security issues immediately"
            )

        poor_files = len(self.summary["files_by_score"]["poor"])
        if poor_files > 0:
            recommendations.append(
                f"🔧 Refactor {poor_files} poor quality files to prevent production issues"
            )

        if self.summary["total_debt_hours"] > 100:
            recommendations.append(
                f"📊 Schedule technical debt sprint to address {self.summary['total_debt_hours']:.0f} hours of debt"
            )

        if self.summary["total_files"] > 0:
            avg_score = (
                sum(
                    score
                    for files in self.summary["files_by_score"].values()
                    for _, score in files
                )
                / self.summary["total_files"]
            )

            if avg_score < 70:
                recommendations.append(
                    "⚠️ Overall code quality below target - implement stricter quality gates"
                )

        return recommendations

    def display_results(self, report: dict[str, Any]):
        """Display results in a formatted way"""
        console.print(
            "\n[bold cyan]═══ Sophia AI Codebase Analysis Report ═══[/bold cyan]\n"
        )

        # Summary table
        summary_table = Table(title="Summary Statistics")
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", style="green")

        summary_table.add_row("Total Files Analyzed", str(self.summary["total_files"]))
        summary_table.add_row("Total Issues Found", str(self.summary["total_issues"]))
        summary_table.add_row(
            "Critical Issues", f"[red]{self.summary['critical_issues']}[/red]"
        )
        summary_table.add_row(
            "High Priority Issues", f"[yellow]{self.summary['high_issues']}[/yellow]"
        )
        summary_table.add_row(
            "Technical Debt", f"{self.summary['total_debt_hours']:.1f} hours"
        )
        summary_table.add_row("Estimated Cost", f"${self.summary['total_cost']:,.0f}")

        console.print(summary_table)

        # Quality distribution
        console.print("\n[bold]Quality Distribution:[/bold]")
        dist_table = Table()
        dist_table.add_column("Category", style="cyan")
        dist_table.add_column("Count", style="green")
        dist_table.add_column("Percentage")

        total = self.summary["total_files"]
        for category, count in report["quality_distribution"].items():
            percentage = (count / total * 100) if total > 0 else 0
            dist_table.add_row(category.capitalize(), str(count), f"{percentage:.1f}%")

        console.print(dist_table)

        # Worst files
        console.print("\n[bold red]Files Requiring Immediate Attention:[/bold red]")
        poor_files = sorted(self.summary["files_by_score"]["poor"], key=lambda x: x[1])[
            :10
        ]  # Top 10 worst

        if poor_files:
            worst_table = Table()
            worst_table.add_column("File", style="red")
            worst_table.add_column("Score", style="red")

            for filepath, score in poor_files:
                worst_table.add_row(
                    str(Path(filepath).relative_to(".")), f"{score:.1f}"
                )

            console.print(worst_table)
        else:
            console.print("[green]No files with poor quality scores![/green]")

        # Recommendations
        console.print("\n[bold]Strategic Recommendations:[/bold]")
        for rec in report["recommendations"]:
            console.print(f"  {rec}")

        # Business impact
        console.print("\n[bold]Business Impact:[/bold]")
        impact = report["business_impact"]
        console.print(
            f"  💰 Total Technical Debt Cost: {impact['total_technical_debt_cost']}"
        )
        console.print(f"  ⏱️  Estimated Fix Time: {impact['estimated_fix_time']}")
        console.print(f"  🚨 Critical Risk Files: {impact['critical_risk_files']}")

        if impact["immediate_action_required"]:
            console.print("\n[bold red]⚠️  IMMEDIATE ACTION REQUIRED[/bold red]")

    async def analyze_codebase(self):
        """Main analysis function"""
        console.print(
            "[bold cyan]Starting Sophia AI Codebase Analysis...[/bold cyan]\n"
        )

        # Get all Python files
        console.print("Scanning for Python files...")
        python_files = self.get_python_files()
        console.print(f"Found {len(python_files)} Python files to analyze\n")

        # Analyze files with progress bar
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console,
        ) as progress:
            self.results = await self.analyze_batch(python_files, progress)

        # Generate report
        report = self.generate_report()

        # Display results
        self.display_results(report)

        # Save report
        report_path = Path("codacy_analysis_report.json")
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        console.print(f"\n[green]✅ Report saved to {report_path}[/green]")

        # Save detailed results
        detailed_path = Path("codacy_detailed_results.json")
        with open(detailed_path, "w") as f:
            json.dump(self.results, f, indent=2)

        console.print(f"[green]✅ Detailed results saved to {detailed_path}[/green]")


async def main():
    """Main entry point"""
    analyzer = CodebaseAnalyzer()

    # Check if server is running
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:3008/health") as response:
                if response.status != 200:
                    console.print("[red]❌ Codacy server not responding[/red]")
                    return
    except:
        console.print("[red]❌ Codacy server not running on port 3008[/red]")
        console.print(
            "Start it with: cd mcp-servers/codacy && python enhanced_codacy_mcp_server.py"
        )
        return

    await analyzer.analyze_codebase()


if __name__ == "__main__":
    asyncio.run(main())
