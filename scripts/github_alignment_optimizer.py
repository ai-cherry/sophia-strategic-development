#!/usr/bin/env python3
"""
GitHub Alignment Optimizer
Optimizes GitHub workflows, secrets, and repository configuration for Sophia AI
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any


class GitHubAlignmentOptimizer:
    """Optimizes GitHub configuration and workflows for maximum efficiency"""
    
    def __init__(self):
        self.repo_root = Path.cwd()
        self.workflows_dir = self.repo_root / ".github" / "workflows"
        self.archive_dir = self.repo_root / "archive" / ".github" / "workflows"
        self.optimization_report = {
            "timestamp": datetime.utcnow().isoformat(),
            "optimizations": [],
            "issues_found": [],
            "recommendations": []
        }
    
    def run_gh_command(self, cmd: List[str]) -> Dict[str, Any]:
        """Run GitHub CLI command and return result"""
        try:
            result = subprocess.run(
                ["gh"] + cmd,
                capture_output=True,
                text=True,
                check=True
            )
            return {
                "success": True,
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip()
            }
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "stdout": e.stdout,
                "stderr": e.stderr,
                "returncode": e.returncode
            }
    
    def analyze_workflow_redundancy(self) -> Dict[str, Any]:
        """Analyze workflow files for redundancy and conflicts"""
        workflows = list(self.workflows_dir.glob("*.yml"))
        archived_workflows = list(self.archive_dir.glob("*.yml")) if self.archive_dir.exists() else []
        
        analysis = {
            "active_workflows": len(workflows),
            "archived_workflows": len(archived_workflows),
            "workflow_files": [w.name for w in workflows],
            "redundancy_issues": [],
            "optimization_opportunities": []
        }
        
        # Check for redundant deployment workflows
        deployment_workflows = [w for w in workflows if "deploy" in w.name.lower() or "production" in w.name.lower()]
        if len(deployment_workflows) > 1:
            analysis["redundancy_issues"].append({
                "type": "multiple_deployment_workflows",
                "files": [w.name for w in deployment_workflows],
                "recommendation": "Consolidate into single production-deployment.yml"
            })
        
        # Check for deprecated action versions
        for workflow in workflows:
            content = workflow.read_text()
            if "actions/upload-artifact@v3" in content:
                analysis["redundancy_issues"].append({
                    "type": "deprecated_action",
                    "file": workflow.name,
                    "issue": "Using deprecated upload-artifact@v3",
                    "fix": "Update to upload-artifact@v4"
                })
            
            if "actions/setup-python@v4" in content:
                analysis["redundancy_issues"].append({
                    "type": "outdated_action",
                    "file": workflow.name,
                    "issue": "Using outdated setup-python@v4",
                    "fix": "Update to setup-python@v5"
                })
        
        return analysis
    
    def analyze_secret_management(self) -> Dict[str, Any]:
        """Analyze secret management configuration"""
        # Get organization secrets
        org_secrets_result = self.run_gh_command(["secret", "list", "--org", "ai-cherry"])
        repo_secrets_result = self.run_gh_command(["secret", "list"])
        
        analysis = {
            "org_secrets_accessible": org_secrets_result["success"],
            "repo_secrets_accessible": repo_secrets_result["success"],
            "secret_alignment_issues": [],
            "recommendations": []
        }
        
        if org_secrets_result["success"]:
            org_secrets = org_secrets_result["stdout"].split("\n")
            analysis["org_secrets_count"] = len([s for s in org_secrets if s.strip()])
        
        if repo_secrets_result["success"]:
            repo_secrets = repo_secrets_result["stdout"].split("\n")
            analysis["repo_secrets_count"] = len([s for s in repo_secrets if s.strip()])
            
            # Check for secrets that should be in organization
            critical_secrets = [
                "PULUMI_ACCESS_TOKEN", "OPENAI_API_KEY", "ANTHROPIC_API_KEY",
                "PORTKEY_API_KEY", "DOCKER_PERSONAL_ACCESS_TOKEN"
            ]
            
            for secret_line in repo_secrets:
                if any(critical in secret_line for critical in critical_secrets):
                    analysis["secret_alignment_issues"].append({
                        "type": "critical_secret_in_repo",
                        "secret": secret_line.split()[0] if secret_line.strip() else "",
                        "recommendation": "Move to organization secrets for better management"
                    })
        
        return analysis
    
    def analyze_pull_request_health(self) -> Dict[str, Any]:
        """Analyze pull request status and health"""
        pr_result = self.run_gh_command([
            "pr", "list", "--state", "all", "--limit", "50", 
            "--json", "number,title,state,author,createdAt"
        ])
        
        analysis = {
            "pr_analysis_success": pr_result["success"],
            "total_prs": 0,
            "open_prs": 0,
            "dependabot_prs": 0,
            "stale_prs": [],
            "recommendations": []
        }
        
        if pr_result["success"]:
            try:
                prs = json.loads(pr_result["stdout"])
                analysis["total_prs"] = len(prs)
                
                for pr in prs:
                    if pr["state"] == "OPEN":
                        analysis["open_prs"] += 1
                        
                        if pr["author"]["login"] == "app/dependabot":
                            analysis["dependabot_prs"] += 1
                        
                        # Check for stale PRs (older than 30 days)
                        created_date = datetime.fromisoformat(pr["createdAt"].replace("Z", "+00:00"))
                        days_old = (datetime.now().astimezone() - created_date).days
                        
                        if days_old > 30:
                            analysis["stale_prs"].append({
                                "number": pr["number"],
                                "title": pr["title"],
                                "days_old": days_old,
                                "author": pr["author"]["login"]
                            })
                
                # Recommendations
                if analysis["dependabot_prs"] > 10:
                    analysis["recommendations"].append(
                        "Consider batch-merging Dependabot PRs to reduce noise"
                    )
                
                if len(analysis["stale_prs"]) > 5:
                    analysis["recommendations"].append(
                        "Review and close stale PRs to maintain repository hygiene"
                    )
                    
            except json.JSONDecodeError:
                analysis["error"] = "Failed to parse PR data"
        
        return analysis
    
    def analyze_workflow_performance(self) -> Dict[str, Any]:
        """Analyze workflow run performance and failure rates"""
        runs_result = self.run_gh_command([
            "run", "list", "--limit", "50", 
            "--json", "status,conclusion,workflowName,createdAt,databaseId"
        ])
        
        analysis = {
            "performance_analysis_success": runs_result["success"],
            "total_runs": 0,
            "failure_rate": 0.0,
            "workflow_stats": {},
            "recent_failures": [],
            "performance_issues": []
        }
        
        if runs_result["success"]:
            try:
                runs = json.loads(runs_result["stdout"])
                analysis["total_runs"] = len(runs)
                
                failures = 0
                workflow_counts = {}
                workflow_failures = {}
                
                for run in runs:
                    workflow_name = run["workflowName"]
                    
                    # Count by workflow
                    workflow_counts[workflow_name] = workflow_counts.get(workflow_name, 0) + 1
                    
                    if run["conclusion"] == "failure":
                        failures += 1
                        workflow_failures[workflow_name] = workflow_failures.get(workflow_name, 0) + 1
                        
                        # Track recent failures
                        if len(analysis["recent_failures"]) < 10:
                            analysis["recent_failures"].append({
                                "workflow": workflow_name,
                                "id": run["databaseId"],
                                "created_at": run["createdAt"]
                            })
                
                # Calculate failure rate
                if analysis["total_runs"] > 0:
                    analysis["failure_rate"] = (failures / analysis["total_runs"]) * 100
                
                # Calculate per-workflow stats
                for workflow, count in workflow_counts.items():
                    failure_count = workflow_failures.get(workflow, 0)
                    failure_rate = (failure_count / count) * 100 if count > 0 else 0
                    
                    analysis["workflow_stats"][workflow] = {
                        "total_runs": count,
                        "failures": failure_count,
                        "failure_rate": failure_rate
                    }
                    
                    # Flag high-failure workflows
                    if failure_rate > 50 and count > 5:
                        analysis["performance_issues"].append({
                            "workflow": workflow,
                            "failure_rate": failure_rate,
                            "recommendation": "Investigate and fix recurring failures"
                        })
                        
            except json.JSONDecodeError:
                analysis["error"] = "Failed to parse workflow run data"
        
        return analysis
    
    def generate_optimization_recommendations(self, analyses: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate comprehensive optimization recommendations"""
        recommendations = []
        
        # Workflow optimization
        workflow_analysis = analyses.get("workflow_redundancy", {})
        if workflow_analysis.get("redundancy_issues"):
            recommendations.append({
                "category": "workflow_optimization",
                "priority": "high",
                "title": "Consolidate Redundant Workflows",
                "description": "Multiple deployment workflows detected",
                "action": "Merge into single production-deployment.yml",
                "impact": "Reduced complexity, fewer conflicts"
            })
        
        # Secret management
        secret_analysis = analyses.get("secret_management", {})
        if secret_analysis.get("secret_alignment_issues"):
            recommendations.append({
                "category": "secret_management",
                "priority": "high",
                "title": "Centralize Critical Secrets",
                "description": "Critical secrets found in repository instead of organization",
                "action": "Move to GitHub Organization Secrets",
                "impact": "Better security, centralized management"
            })
        
        # Performance optimization
        performance_analysis = analyses.get("workflow_performance", {})
        if performance_analysis.get("failure_rate", 0) > 30:
            recommendations.append({
                "category": "performance",
                "priority": "critical",
                "title": "Fix High Failure Rate",
                "description": f"Workflow failure rate: {performance_analysis['failure_rate']:.1f}%",
                "action": "Investigate and fix failing workflows",
                "impact": "Reliable deployments, faster development"
            })
        
        # Repository hygiene
        pr_analysis = analyses.get("pull_request_health", {})
        if len(pr_analysis.get("stale_prs", [])) > 5:
            recommendations.append({
                "category": "repository_hygiene",
                "priority": "medium",
                "title": "Clean Up Stale Pull Requests",
                "description": f"{len(pr_analysis['stale_prs'])} stale PRs found",
                "action": "Review and close outdated PRs",
                "impact": "Cleaner repository, better organization"
            })
        
        return recommendations
    
    def implement_workflow_fixes(self) -> Dict[str, Any]:
        """Implement automated workflow fixes"""
        fixes_applied = []
        
        # Fix deprecated actions
        for workflow_file in self.workflows_dir.glob("*.yml"):
            content = workflow_file.read_text()
            original_content = content
            
            # Update deprecated actions
            content = content.replace("actions/upload-artifact@v3", "actions/upload-artifact@v4")
            content = content.replace("actions/setup-python@v4", "actions/setup-python@v5")
            content = content.replace("pulumi/actions@v4", "pulumi/actions@v6")
            
            if content != original_content:
                workflow_file.write_text(content)
                fixes_applied.append({
                    "file": workflow_file.name,
                    "fix": "Updated deprecated GitHub Actions"
                })
        
        return {"fixes_applied": fixes_applied}
    
    def run_comprehensive_analysis(self) -> Dict[str, Any]:
        """Run comprehensive GitHub alignment analysis"""
        print("🔍 Running comprehensive GitHub alignment analysis...")
        
        analyses = {
            "workflow_redundancy": self.analyze_workflow_redundancy(),
            "secret_management": self.analyze_secret_management(),
            "pull_request_health": self.analyze_pull_request_health(),
            "workflow_performance": self.analyze_workflow_performance()
        }
        
        recommendations = self.generate_optimization_recommendations(analyses)
        workflow_fixes = self.implement_workflow_fixes()
        
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "repository": "ai-cherry/sophia-main",
            "analyses": analyses,
            "recommendations": recommendations,
            "automated_fixes": workflow_fixes,
            "summary": {
                "total_issues": sum(len(a.get("redundancy_issues", [])) + 
                                  len(a.get("secret_alignment_issues", [])) + 
                                  len(a.get("performance_issues", [])) 
                                  for a in analyses.values()),
                "critical_recommendations": len([r for r in recommendations if r.get("priority") == "critical"]),
                "high_priority_recommendations": len([r for r in recommendations if r.get("priority") == "high"]),
                "automated_fixes_applied": len(workflow_fixes.get("fixes_applied", []))
            }
        }
        
        return report


def main():
    """Main execution function"""
    optimizer = GitHubAlignmentOptimizer()
    
    try:
        report = optimizer.run_comprehensive_analysis()
        
        # Save report
        report_file = Path("github_alignment_report.json")
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📊 Analysis complete! Report saved to {report_file}")
        print(f"📈 Summary:")
        print(f"   - Total issues found: {report['summary']['total_issues']}")
        print(f"   - Critical recommendations: {report['summary']['critical_recommendations']}")
        print(f"   - High priority recommendations: {report['summary']['high_priority_recommendations']}")
        print(f"   - Automated fixes applied: {report['summary']['automated_fixes_applied']}")
        
        # Print top recommendations
        if report["recommendations"]:
            print("\n🎯 Top Recommendations:")
            for i, rec in enumerate(report["recommendations"][:3], 1):
                print(f"   {i}. {rec['title']} ({rec['priority']} priority)")
                print(f"      {rec['description']}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

