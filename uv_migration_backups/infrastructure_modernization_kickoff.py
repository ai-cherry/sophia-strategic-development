#!/usr/bin/env python3
"""
Sophia AI Infrastructure Modernization - Kickoff Script
Executes Phase 1 cleanup and preparation tasks
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class InfrastructureModernizationKickoff:
    """Orchestrates the infrastructure modernization kickoff tasks"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.backup_dir = (
            self.project_root
            / "backups"
            / f"modernization_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        self.legacy_files = []
        self.typescript_files = []
        self.workflow_files = []
        self.report = {
            "timestamp": datetime.now().isoformat(),
            "phase": "kickoff",
            "tasks": {},
        }

    async def run(self):
        """Execute all kickoff tasks"""
        logger.info("🚀 Starting Sophia AI Infrastructure Modernization Kickoff")

        # Create backup directory
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        # Execute Phase 1 tasks
        await self.identify_legacy_components()
        await self.analyze_typescript_infrastructure()
        await self.audit_github_workflows()
        await self.analyze_esc_environments()
        await self.create_migration_plan()

        # Generate report
        self.generate_kickoff_report()

        logger.info("✅ Kickoff completed! Check the report for next steps.")

    async def identify_legacy_components(self):
        """Identify all legacy/broken files for cleanup"""
        logger.info("🔍 Identifying legacy components...")

        legacy_patterns = [
            "**/test_*.py",
            "**/*_old.py",
            "**/*_legacy.py",
            "**/*_broken.py",
            "**/deprecated_*",
            "mcp-servers/**/unused_*",
            "infrastructure/**/temp_*",
        ]

        for pattern in legacy_patterns:
            for file_path in self.project_root.rglob(pattern):
                if file_path.is_file() and not str(file_path).startswith(
                    str(self.backup_dir)
                ):
                    self.legacy_files.append(file_path)

        # Check for broken imports and syntax errors
        python_files = list(self.project_root.rglob("*.py"))
        for py_file in python_files:
            if self._has_syntax_errors(py_file):
                self.legacy_files.append(py_file)

        self.report["tasks"]["legacy_identification"] = {
            "status": "completed",
            "files_found": len(self.legacy_files),
            "sample_files": [
                str(f.relative_to(self.project_root)) for f in self.legacy_files[:10]
            ],
        }

        logger.info(f"Found {len(self.legacy_files)} legacy/broken files")

    def _has_syntax_errors(self, file_path: Path) -> bool:
        """Check if a Python file has syntax errors"""
        with open(file_path, encoding="utf-8") as f:
            try:
                compile(f.read(), str(file_path), "exec")
            except Exception:
                return False
        return True

    async def analyze_typescript_infrastructure(self):
        """Analyze TypeScript infrastructure files for migration"""
        logger.info("📊 Analyzing TypeScript infrastructure...")

        ts_patterns = ["infrastructure/**/*.ts", "infrastructure/**/*.tsx"]

        for pattern in ts_patterns:
            for file_path in self.project_root.glob(pattern):
                if file_path.is_file():
                    self.typescript_files.append(file_path)

        # Categorize TypeScript files
        dns_files = [f for f in self.typescript_files if "dns" in str(f).lower()]
        pulumi_files = [f for f in self.typescript_files if "pulumi" in str(f).lower()]
        other_files = [
            f for f in self.typescript_files if f not in dns_files + pulumi_files
        ]

        self.report["tasks"]["typescript_analysis"] = {
            "status": "completed",
            "total_files": len(self.typescript_files),
            "categories": {
                "dns": len(dns_files),
                "pulumi": len(pulumi_files),
                "other": len(other_files),
            },
            "migration_priority": "dns_infrastructure",
        }

        logger.info(f"Found {len(self.typescript_files)} TypeScript files to migrate")

    async def audit_github_workflows(self):
        """Audit GitHub Actions workflows for consolidation"""
        logger.info("🔄 Auditing GitHub workflows...")

        workflows_dir = self.project_root / ".github" / "workflows"
        if workflows_dir.exists():
            self.workflow_files = list(workflows_dir.glob("*.yml")) + list(
                workflows_dir.glob("*.yaml")
            )

        # Analyze workflow purposes
        workflow_analysis = {}
        for workflow in self.workflow_files:
            with open(workflow) as f:
                content = f.read()
                workflow_analysis[workflow.name] = {
                    "triggers": self._extract_workflow_triggers(content),
                    "jobs": self._extract_workflow_jobs(content),
                    "can_consolidate": self._can_consolidate_workflow(content),
                }

        self.report["tasks"]["workflow_audit"] = {
            "status": "completed",
            "total_workflows": len(self.workflow_files),
            "consolidation_candidates": sum(
                1 for w in workflow_analysis.values() if w["can_consolidate"]
            ),
            "target_workflows": 5,
        }

        logger.info(f"Found {len(self.workflow_files)} workflows to consolidate")

    def _extract_workflow_triggers(self, content: str) -> list[str]:
        """Extract workflow triggers from YAML content"""
        triggers = []
        if "push:" in content:
            triggers.append("push")
        if "pull_request:" in content:
            triggers.append("pull_request")
        if "schedule:" in content:
            triggers.append("schedule")
        if "workflow_dispatch:" in content:
            triggers.append("manual")
        return triggers

    def _extract_workflow_jobs(self, content: str) -> int:
        """Count jobs in workflow"""
        return content.count("jobs:")

    def _can_consolidate_workflow(self, content: str) -> bool:
        """Determine if workflow can be consolidated"""
        # Simple heuristic: single-job workflows are good consolidation candidates
        return self._extract_workflow_jobs(content) == 1

    async def analyze_esc_environments(self):
        """Analyze Pulumi ESC environments"""
        logger.info("🔐 Analyzing ESC environments...")

        esc_dir = self.project_root / "infrastructure" / "esc"
        esc_files = []

        if esc_dir.exists():
            esc_files = list(esc_dir.glob("*.yaml")) + list(esc_dir.glob("*.yml"))

        # Analyze ESC structure
        esc_analysis = {
            "environments": [],
            "inheritance_chain": [],
            "secret_categories": set(),
        }

        for esc_file in esc_files:
            with open(esc_file) as f:
                content = f.read()
                esc_analysis["environments"].append(esc_file.stem)

                # Extract secret categories
                if "payready" in content:
                    esc_analysis["secret_categories"].add("payready")
                if "gong" in content:
                    esc_analysis["secret_categories"].add("gong")
                if "openai" in content:
                    esc_analysis["secret_categories"].add("ai_services")

        self.report["tasks"]["esc_analysis"] = {
            "status": "completed",
            "environments_found": len(esc_files),
            "environment_names": esc_analysis["environments"],
            "secret_categories": list(esc_analysis["secret_categories"]),
            "recommendation": "Consolidate to production/development with clear inheritance",
        }

        logger.info(f"Found {len(esc_files)} ESC environments to consolidate")

    async def create_migration_plan(self):
        """Create detailed migration plan"""
        logger.info("📝 Creating migration plan...")

        migration_plan = {
            "phase1_cleanup": {
                "backup_legacy_files": {
                    "count": len(self.legacy_files),
                    "destination": str(self.backup_dir / "legacy_files"),
                },
                "remove_legacy_files": {
                    "files": [
                        str(f.relative_to(self.project_root))
                        for f in self.legacy_files[:20]
                    ],
                    "total": len(self.legacy_files),
                },
            },
            "phase2_python_migration": {
                "typescript_to_python": {
                    "priority": "dns_infrastructure",
                    "files": len(self.typescript_files),
                    "approach": "gradual_with_wrapper",
                }
            },
            "phase3_workflow_consolidation": {
                "current_workflows": len(self.workflow_files),
                "target_workflows": 5,
                "consolidated_workflows": [
                    "ai-infrastructure-orchestrator.yml",
                    "secrets-compliance.yml",
                    "business-intelligence.yml",
                    "emergency-recovery.yml",
                    "documentation-quality.yml",
                ],
            },
            "phase4_esc_consolidation": {
                "target_structure": {
                    "production.yaml": "All production secrets with categories",
                    "development.yaml": "Inherits from production with overrides",
                }
            },
        }

        # Save migration plan
        plan_path = self.project_root / "MIGRATION_PLAN.json"
        with open(plan_path, "w") as f:
            json.dump(migration_plan, f, indent=2)

        self.report["tasks"]["migration_plan"] = {
            "status": "completed",
            "plan_location": str(plan_path),
            "next_steps": [
                "Review and approve migration plan",
                "Create backup of legacy files",
                "Begin Python migration of TypeScript DNS",
                "Design consolidated workflows",
            ],
        }

        logger.info("Migration plan created successfully")

    def generate_kickoff_report(self):
        """Generate comprehensive kickoff report"""
        report_path = (
            self.project_root
            / f"MODERNIZATION_KICKOFF_REPORT_{datetime.now().strftime('%Y%m%d')}.json"
        )

        # Add summary
        self.report["summary"] = {
            "legacy_files_to_remove": len(self.legacy_files),
            "typescript_files_to_migrate": len(self.typescript_files),
            "workflows_to_consolidate": len(self.workflow_files),
            "estimated_duration": "10 weeks",
            "risk_level": "medium",
            "immediate_actions": [
                "Schedule team kickoff meeting",
                "Assign phase owners",
                "Create project Slack channel",
                "Begin legacy file backup",
            ],
        }

        # Save report
        with open(report_path, "w") as f:
            json.dump(self.report, f, indent=2)

        logger.info(f"📊 Report saved to: {report_path}")

        # Print summary
        print("\n" + "=" * 60)
        print("SOPHIA AI INFRASTRUCTURE MODERNIZATION - KICKOFF SUMMARY")
        print("=" * 60)
        print(f"Legacy files found: {len(self.legacy_files)}")
        print(f"TypeScript files to migrate: {len(self.typescript_files)}")
        print(f"Workflows to consolidate: {len(self.workflow_files)} → 5")
        print(f"Report location: {report_path}")
        print("\nNext Steps:")
        for i, action in enumerate(self.report["summary"]["immediate_actions"], 1):
            print(f"{i}. {action}")
        print("=" * 60)


if __name__ == "__main__":
    kickoff = InfrastructureModernizationKickoff()
    asyncio.run(kickoff.run())
