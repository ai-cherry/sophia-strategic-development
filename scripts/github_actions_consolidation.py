#!/usr/bin/env python3
"""
Sophia AI - GitHub Actions Workflow Consolidation
Analyzes existing workflows and creates reusable templates to reduce from 25+ to ~8 core workflows
"""

import json
import os
import re
import yaml
from pathlib import Path
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict

@dataclass
class WorkflowAnalysis:
    """Analysis of a GitHub Actions workflow."""
    name: str
    file_path: str
    triggers: List[str]
    jobs: List[str]
    secrets_used: Set[str]
    complexity_score: int
    lines_of_code: int
    consolidation_group: str

@dataclass
class ConsolidationTemplate:
    """Template for consolidated workflow."""
    name: str
    description: str
    template_path: str
    replaces_workflows: List[str]
    reusable: bool
    parameters: List[str]

class GitHubActionsConsolidator:
    """Consolidates GitHub Actions workflows into reusable templates."""
    
    def __init__(self):
        self.workspace_root = Path.cwd()
        self.workflows_dir = self.workspace_root / ".github" / "workflows"
        self.templates_dir = self.workspace_root / ".github" / "workflow-templates"
        self.workflows = []
        self.analysis_results = []
        
        # Create templates directory
        self.templates_dir.mkdir(exist_ok=True)
        
        # Common secret patterns that can be reused
        self.common_secrets = {
            "PULUMI_ACCESS_TOKEN", "OPENAI_API_KEY", "ANTHROPIC_API_KEY",
            "GONG_ACCESS_KEY", "GONG_CLIENT_SECRET", "SNOWFLAKE_ACCOUNT",
            "SNOWFLAKE_USER", "SNOWFLAKE_PASSWORD", "VERCEL_ACCESS_TOKEN",
            "SLACK_BOT_TOKEN", "DOCKER_USERNAME", "DOCKER_TOKEN"
        }

    def analyze_existing_workflows(self) -> List[WorkflowAnalysis]:
        """Analyze all existing GitHub Actions workflows."""
        print("🔍 Analyzing existing GitHub Actions workflows...")
        
        if not self.workflows_dir.exists():
            print("❌ No .github/workflows directory found")
            return []
            
        workflow_files = list(self.workflows_dir.glob("*.yml"))
        print(f"📁 Found {len(workflow_files)} workflow files")
        
        for workflow_file in workflow_files:
            try:
                analysis = self._analyze_single_workflow(workflow_file)
                self.analysis_results.append(analysis)
            except Exception as e:
                print(f"⚠️  Failed to analyze {workflow_file.name}: {e}")
        
        return self.analysis_results

    def _analyze_single_workflow(self, workflow_file: Path) -> WorkflowAnalysis:
        """Analyze a single workflow file."""
        with open(workflow_file, 'r') as f:
            content = f.read()
            
        try:
            workflow_data = yaml.safe_load(content)
        except yaml.YAMLError:
            # Fallback to text analysis if YAML parsing fails
            workflow_data = {"name": workflow_file.stem, "on": [], "jobs": {}}
        
        # Extract workflow name
        name = workflow_data.get("name", workflow_file.stem)
        
        # Extract triggers
        triggers = []
        if "on" in workflow_data:
            if isinstance(workflow_data["on"], str):
                triggers = [workflow_data["on"]]
            elif isinstance(workflow_data["on"], list):
                triggers = workflow_data["on"]
            elif isinstance(workflow_data["on"], dict):
                triggers = list(workflow_data["on"].keys())
        
        # Extract jobs
        jobs = list(workflow_data.get("jobs", {}).keys())
        
        # Extract secrets used
        secrets_used = set(re.findall(r'secrets\.([A-Z_]+)', content))
        
        # Calculate complexity score
        lines_of_code = len(content.split('\n'))
        complexity_score = (
            lines_of_code + 
            len(jobs) * 50 + 
            len(secrets_used) * 10 +
            len(triggers) * 25
        )
        
        # Determine consolidation group
        consolidation_group = self._determine_consolidation_group(name, triggers, jobs, content)
        
        return WorkflowAnalysis(
            name=name,
            file_path=str(workflow_file.relative_to(self.workspace_root)),
            triggers=triggers,
            jobs=jobs,
            secrets_used=secrets_used,
            complexity_score=complexity_score,
            lines_of_code=lines_of_code,
            consolidation_group=consolidation_group
        )

    def _determine_consolidation_group(self, name: str, triggers: List[str], jobs: List[str], content: str) -> str:
        """Determine which consolidation group a workflow belongs to."""
        name_lower = name.lower()
        content_lower = content.lower()
        
        # Deployment-related workflows
        if any(keyword in name_lower for keyword in ["deploy", "deployment", "infrastructure", "pulumi"]):
            return "deployment"
        
        # Testing and validation workflows  
        if any(keyword in name_lower for keyword in ["test", "quality", "lint", "validation"]):
            return "testing"
            
        # Monitoring and health check workflows
        if any(keyword in name_lower for keyword in ["monitor", "health", "alert", "check"]):
            return "monitoring"
            
        # Secret and configuration management
        if any(keyword in name_lower for keyword in ["secret", "sync", "config", "esc"]):
            return "configuration"
            
        # Documentation and analysis
        if any(keyword in name_lower for keyword in ["doc", "analysis", "report", "enhancement"]):
            return "documentation"
            
        # Data pipeline and ETL
        if any(keyword in name_lower for keyword in ["gong", "airbyte", "etl", "pipeline", "data"]):
            return "data_pipeline"
            
        # Integration and MCP
        if any(keyword in name_lower for keyword in ["mcp", "integration", "cursor"]):
            return "integration"
            
        return "miscellaneous"

    def generate_consolidation_report(self) -> Dict:
        """Generate comprehensive consolidation report."""
        print("📊 Generating consolidation report...")
        
        # Analyze existing workflows
        self.analyze_existing_workflows()
        
        # Calculate consolidation metrics
        total_workflows = len(self.analysis_results)
        
        # Group analysis by consolidation group
        groups = defaultdict(list)
        for analysis in self.analysis_results:
            groups[analysis.consolidation_group].append(analysis)
        
        # Estimate consolidation potential
        consolidatable_workflows = sum(len(workflows) for workflows in groups.values() if len(workflows) > 1)
        estimated_templates = len([group for group, workflows in groups.items() if len(workflows) > 1])
        
        report = {
            "consolidation_summary": {
                "total_workflows_analyzed": total_workflows,
                "consolidatable_workflows": consolidatable_workflows,
                "estimated_templates_needed": estimated_templates,
                "consolidation_ratio": f"{consolidatable_workflows}:{estimated_templates}",
                "estimated_maintenance_reduction": f"{(consolidatable_workflows / total_workflows * 100):.1f}%"
            },
            "workflow_analysis": [asdict(analysis) for analysis in self.analysis_results],
            "consolidation_groups": {
                group: len(workflows) for group, workflows in groups.items()
            },
            "high_complexity_workflows": [
                analysis.name for analysis in self.analysis_results 
                if analysis.complexity_score > 1000
            ],
            "implementation_plan": {
                "phase_1": "Replace deployment workflows with unified deployment template",
                "phase_2": "Consolidate testing workflows into comprehensive testing suite", 
                "phase_3": "Merge monitoring and health check workflows",
                "phase_4": "Unify configuration and secret management workflows",
                "phase_5": "Consolidate data pipeline workflows",
                "phase_6": "Remove redundant workflows and update references"
            },
            "recommended_templates": [
                {
                    "name": "Unified Deployment Pipeline",
                    "consolidates": [w.name for w in groups.get("deployment", [])],
                    "description": "Single workflow for frontend, backend, and infrastructure deployment"
                },
                {
                    "name": "Comprehensive Testing Suite",
                    "consolidates": [w.name for w in groups.get("testing", [])],
                    "description": "Unified testing workflow for all test types"
                },
                {
                    "name": "Configuration Management",
                    "consolidates": [w.name for w in groups.get("configuration", [])],
                    "description": "Secret sync and configuration management"
                },
                {
                    "name": "Data Pipeline Operations", 
                    "consolidates": [w.name for w in groups.get("data_pipeline", [])],
                    "description": "ETL and data processing workflows"
                }
            ],
            "next_steps": [
                "Create reusable workflow templates in .github/workflow-templates/",
                "Test templates in development environment",
                "Update existing workflows to use reusable templates",
                "Remove redundant workflow files",
                "Update documentation and README files"
            ]
        }
        
        # Save report
        with open('github_actions_consolidation_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        return report

def main():
    """Main execution function."""
    print("🔧 Sophia AI - GitHub Actions Workflow Consolidation")
    print("=" * 60)
    
    consolidator = GitHubActionsConsolidator()
    report = consolidator.generate_consolidation_report()
    
    print("\n📊 CONSOLIDATION SUMMARY")
    print("-" * 40)
    summary = report["consolidation_summary"]
    print(f"Total workflows analyzed: {summary['total_workflows_analyzed']}")
    print(f"Consolidatable workflows: {summary['consolidatable_workflows']}")
    print(f"Estimated templates needed: {summary['estimated_templates_needed']}")
    print(f"Consolidation ratio: {summary['consolidation_ratio']}")
    print(f"Maintenance reduction: {summary['estimated_maintenance_reduction']}")
    
    print("\n🔧 CONSOLIDATION GROUPS")
    print("-" * 40)
    for group, count in report["consolidation_groups"].items():
        print(f"{group.title().replace('_', ' ')}: {count} workflows")
    
    print(f"\n✅ Consolidation report saved: github_actions_consolidation_report.json")
    print("🎯 Next: Create reusable workflow templates")

if __name__ == "__main__":
    main() 