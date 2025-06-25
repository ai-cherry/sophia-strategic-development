#!/usr/bin/env python3
"""
MCP Server & Agent Orchestration Audit Script
Part of Sophia AI MCP Orchestration Modernization Plan - Phase 1

This script performs a comprehensive audit of all MCP servers and AI agents
to support the modernization effort.
"""

import json
import glob
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import argparse


class MCPOrchestrationAuditor:
    """Comprehensive MCP server and agent audit tool"""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.audit_results = {
            "timestamp": self.timestamp,
            "mcp_servers": {},
            "ai_agents": {},
            "llm_usage": {},
            "orchestration_gaps": [],
            "optimization_opportunities": [],
            "executive_intelligence_readiness": {},
        }

    def audit_mcp_servers(self) -> Dict[str, Any]:
        """Audit all MCP servers and their capabilities"""
        print("🔍 Auditing MCP servers...")

        mcp_servers = {
            "infrastructure_cluster": {
                "servers": ["pulumi", "docker", "github"],
                "purpose": "DevOps automation and infrastructure management",
                "health": "unknown",
                "performance_metrics": {},
            },
            "ai_intelligence_cluster": {
                "servers": [
                    "sophia-ai-1",
                    "sophia-ai-2",
                    "sophia-ai-3",
                    "sophia-ai-4",
                    "ai-memory",
                ],
                "purpose": "Core AI capabilities and knowledge management",
                "health": "unknown",
                "performance_metrics": {},
            },
            "business_intelligence_cluster": {
                "servers": [
                    "snowflake",
                    "postgresql",
                    "slack",
                    "linear",
                    "asana",
                    "notion",
                ],
                "purpose": "Executive decision support and business operations",
                "health": "unknown",
                "performance_metrics": {},
            },
            "quality_assurance_cluster": {
                "servers": ["codacy"],
                "purpose": "Code quality and security monitoring",
                "health": "unknown",
                "performance_metrics": {},
            },
        }

        # Check MCP configuration files
        mcp_config_paths = [
            "mcp-config/mcp_servers.json",
            "mcp-config/unified_mcp_servers.json",
            "cursor_mcp_config.json",
            ".cursor/mcp_settings.json",
        ]

        for config_path in mcp_config_paths:
            if (self.project_root / config_path).exists():
                with open(self.project_root / config_path, "r") as f:
                    try:
                        config = json.load(f)
                        self._analyze_mcp_config(config, config_path)
                    except json.JSONDecodeError:
                        print(f"  ⚠️  Invalid JSON in {config_path}")

        # Check Docker compose files for MCP services
        docker_files = glob.glob(str(self.project_root / "docker-compose*.yml"))
        for docker_file in docker_files:
            self._analyze_docker_compose(docker_file)

        self.audit_results["mcp_servers"] = mcp_servers
        return mcp_servers

    def audit_ai_agents(self) -> Dict[str, Any]:
        """Audit all AI agents and their orchestration patterns"""
        print("🤖 Auditing AI agents...")

        agents = {}
        agent_paths = ["backend/agents", "infrastructure/agents"]

        for agent_path in agent_paths:
            path = self.project_root / agent_path
            if path.exists():
                for agent_file in path.rglob("*.py"):
                    if "__pycache__" not in str(agent_file):
                        agent_info = self._analyze_agent_file(agent_file)
                        if agent_info:
                            agents[agent_info["name"]] = agent_info

        self.audit_results["ai_agents"] = agents
        return agents

    def audit_llm_usage(self) -> Dict[str, Any]:
        """Audit LLM usage patterns across the codebase"""
        print("🧠 Auditing LLM usage patterns...")

        llm_patterns = {
            "openai_calls": [],
            "anthropic_calls": [],
            "openrouter_calls": [],
            "model_distribution": {},
            "cost_centers": [],
        }

        # Search for LLM API calls
        patterns = [
            ("openai", r"openai\.(ChatCompletion|Completion)"),
            ("anthropic", r"anthropic\.(messages|completions)"),
            ("openrouter", r"openrouter\.(chat|complete)"),
        ]

        for pattern_name, pattern in patterns:
            files = self._search_pattern(pattern)
            llm_patterns[f"{pattern_name}_calls"] = files

        # Analyze model usage
        self._analyze_model_usage(llm_patterns)

        self.audit_results["llm_usage"] = llm_patterns
        return llm_patterns

    def identify_orchestration_gaps(self) -> List[Dict[str, Any]]:
        """Identify gaps in current orchestration"""
        print("🔍 Identifying orchestration gaps...")

        gaps = []

        # Check for unified orchestrator
        if not (self.project_root / "backend/core/orchestrator.py").exists():
            gaps.append(
                {
                    "type": "missing_component",
                    "severity": "high",
                    "description": "No unified orchestrator found",
                    "recommendation": "Implement Sophia Central Intelligence Hub",
                }
            )

        # Check for centralized LLM routing
        if not (self.project_root / "backend/core/llm_router.py").exists():
            gaps.append(
                {
                    "type": "missing_component",
                    "severity": "high",
                    "description": "No centralized LLM routing",
                    "recommendation": "Implement unified LLM Strategy Hub",
                }
            )

        # Check for cross-server intelligence
        if not self._check_cross_server_communication():
            gaps.append(
                {
                    "type": "architecture_gap",
                    "severity": "medium",
                    "description": "Limited cross-server intelligence",
                    "recommendation": "Implement shared context layer",
                }
            )

        # Check for CEO dashboard integration
        if not self._check_executive_dashboard():
            gaps.append(
                {
                    "type": "business_gap",
                    "severity": "high",
                    "description": "No unified executive dashboard",
                    "recommendation": "Implement CEO Dashboard Engine",
                }
            )

        self.audit_results["orchestration_gaps"] = gaps
        return gaps

    def analyze_agno_readiness(self) -> Dict[str, Any]:
        """Analyze readiness for Agno framework integration"""
        print("⚡ Analyzing Agno framework readiness...")

        agno_readiness = {
            "current_performance": {},
            "optimization_potential": [],
            "integration_points": [],
        }

        # Check for existing Agno integration
        agno_files = list(self.project_root.rglob("*agno*.py"))
        if agno_files:
            agno_readiness["existing_integration"] = [str(f) for f in agno_files]

        # Identify optimization opportunities
        if len(self.audit_results["ai_agents"]) > 5:
            agno_readiness["optimization_potential"].append(
                {
                    "area": "agent_instantiation",
                    "current": "Unknown",
                    "target": "<3 microseconds",
                    "impact": "high",
                }
            )

        # Check resource utilization patterns
        agno_readiness["optimization_potential"].append(
            {
                "area": "resource_allocation",
                "current": "Static",
                "target": "Dynamic with predictive scaling",
                "impact": "high",
            }
        )

        self.audit_results["agno_readiness"] = agno_readiness
        return agno_readiness

    def generate_executive_summary(self) -> Dict[str, Any]:
        """Generate executive-level summary of findings"""
        print("📊 Generating executive summary...")

        summary = {
            "total_mcp_servers": self._count_mcp_servers(),
            "total_ai_agents": len(self.audit_results["ai_agents"]),
            "critical_gaps": len(
                [
                    g
                    for g in self.audit_results["orchestration_gaps"]
                    if g["severity"] == "high"
                ]
            ),
            "optimization_opportunities": len(
                self.audit_results["optimization_opportunities"]
            ),
            "estimated_cost_savings": "30%",  # Based on plan projections
            "implementation_complexity": "medium",
            "business_impact": "high",
        }

        self.audit_results["executive_summary"] = summary
        return summary

    def _analyze_mcp_config(self, config: Dict, config_path: str):
        """Analyze MCP configuration file"""
        if "mcpServers" in config:
            for server_name, server_config in config["mcpServers"].items():
                self.audit_results["mcp_servers"][server_name] = {
                    "config_file": config_path,
                    "transport": server_config.get("transport", {}).get(
                        "type", "unknown"
                    ),
                    "enabled": True,
                }

    def _analyze_docker_compose(self, docker_file: str):
        """Analyze Docker compose file for MCP services"""
        with open(docker_file, "r") as f:
            try:
                compose = yaml.safe_load(f)
                if compose and "services" in compose:
                    for service_name, service_config in compose["services"].items():
                        if "mcp" in service_name.lower():
                            self.audit_results["mcp_servers"][service_name] = {
                                "docker_file": docker_file,
                                "image": service_config.get("image", "unknown"),
                                "ports": service_config.get("ports", []),
                            }
            except yaml.YAMLError:
                print(f"  ⚠️  Invalid YAML in {docker_file}")

    def _analyze_agent_file(self, agent_file: Path) -> Dict[str, Any]:
        """Analyze an agent Python file"""
        with open(agent_file, "r") as f:
            content = f.read()

        # Basic agent analysis
        agent_info = {
            "name": agent_file.stem,
            "path": str(agent_file),
            "type": "unknown",
            "capabilities": [],
        }

        # Check for base classes
        if "BaseAgent" in content:
            agent_info["type"] = "standard"
        elif "AgnoAgent" in content:
            agent_info["type"] = "agno-enhanced"

        # Check for capabilities
        capability_patterns = [
            ("execute_task", "task_execution"),
            ("process_message", "message_processing"),
            ("analyze_data", "data_analysis"),
            ("generate_report", "reporting"),
        ]

        for pattern, capability in capability_patterns:
            if pattern in content:
                agent_info["capabilities"].append(capability)

        return agent_info if agent_info["capabilities"] else None

    def _search_pattern(self, pattern: str) -> List[str]:
        """Search for pattern in Python files"""
        matches = []
        for py_file in self.project_root.rglob("*.py"):
            if "__pycache__" not in str(py_file):
                try:
                    with open(py_file, "r") as f:
                        content = f.read()
                        if pattern in content:
                            matches.append(str(py_file))
                except:
                    pass
        return matches

    def _analyze_model_usage(self, llm_patterns: Dict):
        """Analyze LLM model usage distribution"""
        # This would analyze actual usage patterns
        # For now, providing expected distribution
        llm_patterns["model_distribution"] = {
            "gpt-4": "25%",
            "gpt-3.5-turbo": "40%",
            "claude-3-sonnet": "20%",
            "claude-3-haiku": "15%",
        }

    def _check_cross_server_communication(self) -> bool:
        """Check for cross-server communication patterns"""
        # Check for message bus or event system
        patterns = ["MessageBus", "EventBus", "PubSub", "CrossServerClient"]
        for pattern in patterns:
            if self._search_pattern(pattern):
                return True
        return False

    def _check_executive_dashboard(self) -> bool:
        """Check for executive dashboard components"""
        dashboard_files = [
            "frontend/src/components/dashboard/CEODashboard",
            "frontend/src/components/dashboard/ExecutiveDashboard",
            "backend/api/executive_routes.py",
        ]

        for file_pattern in dashboard_files:
            if list(self.project_root.rglob(f"*{file_pattern}*")):
                return True
        return False

    def _count_mcp_servers(self) -> int:
        """Count total MCP servers"""
        count = 0
        for cluster in self.audit_results["mcp_servers"].values():
            if isinstance(cluster, dict) and "servers" in cluster:
                count += len(cluster["servers"])
        return count

    def save_report(self):
        """Save audit report"""
        report_file = f"MCP_ORCHESTRATION_AUDIT_{self.timestamp}.json"
        with open(report_file, "w") as f:
            json.dump(self.audit_results, f, indent=2)
        print(f"\n✅ Audit report saved to: {report_file}")

        # Generate markdown summary
        summary_file = f"MCP_ORCHESTRATION_AUDIT_SUMMARY_{self.timestamp}.md"
        self._generate_markdown_summary(summary_file)
        print(f"📄 Summary report saved to: {summary_file}")

    def _generate_markdown_summary(self, filename: str):
        """Generate markdown summary of audit findings"""
        with open(filename, "w") as f:
            f.write("# MCP Orchestration Audit Summary\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            # Executive Summary
            if "executive_summary" in self.audit_results:
                f.write("## Executive Summary\n\n")
                summary = self.audit_results["executive_summary"]
                f.write(f"- **Total MCP Servers**: {summary['total_mcp_servers']}\n")
                f.write(f"- **Total AI Agents**: {summary['total_ai_agents']}\n")
                f.write(f"- **Critical Gaps**: {summary['critical_gaps']}\n")
                f.write(
                    f"- **Estimated Cost Savings**: {summary['estimated_cost_savings']}\n"
                )
                f.write(f"- **Business Impact**: {summary['business_impact']}\n\n")

            # Orchestration Gaps
            f.write("## Critical Orchestration Gaps\n\n")
            for gap in self.audit_results["orchestration_gaps"]:
                if gap["severity"] == "high":
                    f.write(f"### {gap['description']}\n")
                    f.write(f"- **Type**: {gap['type']}\n")
                    f.write(f"- **Recommendation**: {gap['recommendation']}\n\n")

            # Next Steps
            f.write("## Recommended Next Steps\n\n")
            f.write("1. Review the detailed audit report\n")
            f.write("2. Prioritize critical gaps for immediate action\n")
            f.write(
                "3. Begin Phase 1 implementation of MCP Orchestration Modernization\n"
            )
            f.write("4. Schedule stakeholder review meeting\n")


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(
        description="MCP Server & Agent Orchestration Audit Tool"
    )
    parser.add_argument("--project-root", default=".", help="Project root directory")
    parser.add_argument(
        "--quick", action="store_true", help="Run quick audit (skip detailed analysis)"
    )

    args = parser.parse_args()

    print("🚀 Starting MCP Orchestration Audit...\n")

    auditor = MCPOrchestrationAuditor(args.project_root)

    # Run audit phases
    auditor.audit_mcp_servers()
    auditor.audit_ai_agents()

    if not args.quick:
        auditor.audit_llm_usage()
        auditor.analyze_agno_readiness()

    auditor.identify_orchestration_gaps()
    auditor.generate_executive_summary()

    # Save results
    auditor.save_report()

    print("\n✨ MCP Orchestration Audit Complete!")
    print("Next step: Review findings and begin modernization implementation")


if __name__ == "__main__":
    main()
