#!/usr/bin/env python3
"""
Sophia AI Codebase Audit Script
Phase 1A: Comprehensive audit of all modules, services, agents, and documentation
"""

import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List
from collections import defaultdict


class CodebaseAuditor:
    """Comprehensive codebase auditor for Sophia AI"""

    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path)
        self.audit_results = {
            "timestamp": datetime.now().isoformat(),
            "modules": {},
            "services": {},
            "agents": {},
            "integrations": {},
            "dead_code": [],
            "unused_imports": [],
            "compliance_sensitive": [],
            "external_endpoints": [],
            "secrets_usage": [],
            "documentation_status": {},
            "recommendations": [],
        }

    def audit_modules(self) -> Dict[str, List[str]]:
        """Inventory all Python modules and their dependencies"""
        modules = defaultdict(list)

        for py_file in self.root_path.rglob("*.py"):
            if any(
                skip in str(py_file)
                for skip in [".venv", "__pycache__", "node_modules"]
            ):
                continue

            module_name = str(py_file.relative_to(self.root_path))

            # Analyze imports
            try:
                with open(py_file, "r") as f:
                    content = f.read()
                    imports = re.findall(r"(?:from|import)\s+([^\s]+)", content)
                    modules[module_name] = list(set(imports))

                    # Check for dead code indicators
                    if self._is_dead_code(content, py_file):
                        self.audit_results["dead_code"].append(module_name)

            except Exception as e:
                modules[module_name] = [f"ERROR: {str(e)}"]

        self.audit_results["modules"] = dict(modules)
        return dict(modules)

    def audit_agents(self) -> Dict[str, Dict]:
        """Inventory all agents and MCP servers"""
        agents = {}

        # Check backend agents
        agent_dirs = [
            self.root_path / "backend" / "agents",
            self.root_path / "infrastructure" / "agents",
            self.root_path / "mcp-servers",
        ]

        for agent_dir in agent_dirs:
            if agent_dir.exists():
                for agent_file in agent_dir.rglob("*.py"):
                    agent_info = self._analyze_agent(agent_file)
                    if agent_info:
                        agents[str(agent_file.relative_to(self.root_path))] = agent_info

        self.audit_results["agents"] = agents
        return agents

    def audit_integrations(self) -> Dict[str, Dict]:
        """Inventory all external integrations"""
        integrations = {}

        integration_patterns = {
            "gong": r"gong|GONG",
            "slack": r"slack|SLACK",
            "linear": r"linear|LINEAR",
            "apollo": r"apollo|APOLLO",
            "costar": r"costar|COSTAR",
            "snowflake": r"snowflake|SNOWFLAKE",
            "openai": r"openai|OPENAI|gpt|GPT",
            "hubspot": r"hubspot|HUBSPOT",
            "vercel": r"vercel|VERCEL",
            "pulumi": r"pulumi|PULUMI",
        }

        for py_file in self.root_path.rglob("*.py"):
            if any(skip in str(py_file) for skip in [".venv", "__pycache__"]):
                continue

            try:
                with open(py_file, "r") as f:
                    content = f.read()

                for integration, pattern in integration_patterns.items():
                    if re.search(pattern, content):
                        file_path = str(py_file.relative_to(self.root_path))
                        if integration not in integrations:
                            integrations[integration] = {"files": [], "endpoints": []}
                        integrations[integration]["files"].append(file_path)

                        # Extract endpoints
                        endpoints = self._extract_endpoints(content)
                        integrations[integration]["endpoints"].extend(endpoints)

            except Exception:
                pass

        self.audit_results["integrations"] = integrations
        return integrations

    def audit_compliance(self) -> List[Dict]:
        """Identify compliance-sensitive code flows"""
        compliance_patterns = {
            "pci_dss": [r"payment", r"card", r"credit", r"billing"],
            "glba": [r"financial", r"customer.*data", r"personal.*information"],
            "fdcpa": [r"collection", r"debt", r"payment.*reminder"],
            "security": [r"password", r"secret", r"token", r"key", r"credential"],
        }

        sensitive_flows = []

        for py_file in self.root_path.rglob("*.py"):
            if any(skip in str(py_file) for skip in [".venv", "__pycache__"]):
                continue

            try:
                with open(py_file, "r") as f:
                    content = f.read()

                for compliance_type, patterns in compliance_patterns.items():
                    for pattern in patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            sensitive_flows.append(
                                {
                                    "file": str(py_file.relative_to(self.root_path)),
                                    "type": compliance_type,
                                    "pattern": pattern,
                                }
                            )
                            break

            except Exception:
                pass

        self.audit_results["compliance_sensitive"] = sensitive_flows
        return sensitive_flows

    def audit_documentation(self) -> Dict[str, Dict]:
        """Assess documentation coverage and quality"""
        doc_status = {
            "total_modules": 0,
            "documented_modules": 0,
            "readme_files": [],
            "api_docs": [],
            "missing_docs": [],
            "outdated_docs": [],
        }

        # Count Python modules with docstrings
        for py_file in self.root_path.rglob("*.py"):
            if any(skip in str(py_file) for skip in [".venv", "__pycache__"]):
                continue

            doc_status["total_modules"] += 1

            try:
                with open(py_file, "r") as f:
                    content = f.read()
                    if '"""' in content or "'''" in content:
                        doc_status["documented_modules"] += 1
                    else:
                        doc_status["missing_docs"].append(
                            str(py_file.relative_to(self.root_path))
                        )
            except Exception:
                pass

        # Find README files
        for readme in self.root_path.rglob("README*"):
            doc_status["readme_files"].append(str(readme.relative_to(self.root_path)))

        # Check docs directory
        docs_dir = self.root_path / "docs"
        if docs_dir.exists():
            for doc in docs_dir.rglob("*.md"):
                if "api" in doc.name.lower():
                    doc_status["api_docs"].append(str(doc.relative_to(self.root_path)))

                # Check if doc is outdated (simple heuristic: no updates in 90 days)
                if (
                    datetime.now() - datetime.fromtimestamp(doc.stat().st_mtime)
                ).days > 90:
                    doc_status["outdated_docs"].append(
                        str(doc.relative_to(self.root_path))
                    )

        self.audit_results["documentation_status"] = doc_status
        return doc_status

    def _is_dead_code(self, content: str, file_path: Path) -> bool:
        """Detect potential dead code"""
        # Simple heuristics for dead code
        indicators = [
            r"# TODO.*remove",
            r"# DEPRECATED",
            r"# UNUSED",
            r"# OLD",
            r"if False:",
            r"if 0:",
        ]

        for indicator in indicators:
            if re.search(indicator, content, re.IGNORECASE):
                return True

        # Check if file is imported anywhere
        file_name = file_path.stem
        is_imported = False

        for py_file in self.root_path.rglob("*.py"):
            if py_file == file_path:
                continue
            try:
                with open(py_file, "r") as f:
                    if file_name in f.read():
                        is_imported = True
                        break
            except Exception:
                pass

        return not is_imported and file_name != "__init__"

    def _analyze_agent(self, agent_file: Path) -> Dict:
        """Analyze an agent file"""
        agent_info = {
            "type": "unknown",
            "base_class": None,
            "capabilities": [],
            "dependencies": [],
            "status": "unknown",
        }

        try:
            with open(agent_file, "r") as f:
                content = f.read()

            # Detect agent type
            if "MCP" in content or "mcp" in content:
                agent_info["type"] = "mcp_server"
            elif "BaseAgent" in content:
                agent_info["type"] = "sophia_agent"

            # Extract base class
            base_match = re.search(r"class\s+\w+\((\w+)\)", content)
            if base_match:
                agent_info["base_class"] = base_match.group(1)

            # Extract capabilities (simple keyword search)
            capability_keywords = [
                "gong",
                "slack",
                "linear",
                "apollo",
                "competitive",
                "nmhc",
            ]
            for keyword in capability_keywords:
                if keyword in content.lower():
                    agent_info["capabilities"].append(keyword)

            # Check if actively used
            if "__main__" in content or "app.run" in content:
                agent_info["status"] = "active"
            elif "DEPRECATED" in content or "UNUSED" in content:
                agent_info["status"] = "deprecated"

        except Exception:
            pass

        return agent_info

    def _extract_endpoints(self, content: str) -> List[str]:
        """Extract API endpoints from code"""
        endpoints = []

        # Common endpoint patterns
        patterns = [
            r'https?://[^\s"\']+',
            r"api\.[\w\-\.]+",
            r"webhook[s]?\.[\w\-\.]+",
            r"\.sophia-intel\.ai",
        ]

        for pattern in patterns:
            matches = re.findall(pattern, content)
            endpoints.extend(matches)

        return list(set(endpoints))

    def generate_recommendations(self):
        """Generate actionable recommendations based on audit"""
        recommendations = []

        # Dead code recommendation
        if self.audit_results["dead_code"]:
            recommendations.append(
                {
                    "priority": "HIGH",
                    "category": "cleanup",
                    "action": f"Remove {len(self.audit_results['dead_code'])} dead code files",
                    "files": self.audit_results["dead_code"][:5],  # Show first 5
                }
            )

        # Documentation recommendation
        doc_status = self.audit_results["documentation_status"]
        doc_coverage = (
            doc_status["documented_modules"] / max(doc_status["total_modules"], 1) * 100
        )
        if doc_coverage < 80:
            recommendations.append(
                {
                    "priority": "MEDIUM",
                    "category": "documentation",
                    "action": f"Improve documentation coverage (currently {doc_coverage:.1f}%)",
                    "target": "80% minimum coverage",
                }
            )

        # Compliance recommendation
        if len(self.audit_results["compliance_sensitive"]) > 10:
            recommendations.append(
                {
                    "priority": "HIGH",
                    "category": "compliance",
                    "action": "Review and secure compliance-sensitive flows",
                    "count": len(self.audit_results["compliance_sensitive"]),
                }
            )

        # Integration consolidation
        if len(self.audit_results["integrations"]) > 5:
            recommendations.append(
                {
                    "priority": "MEDIUM",
                    "category": "architecture",
                    "action": "Consolidate integrations into unified directory structure",
                    "current_integrations": list(
                        self.audit_results["integrations"].keys()
                    ),
                }
            )

        self.audit_results["recommendations"] = recommendations

    def run_full_audit(self) -> Dict:
        """Run complete codebase audit"""
        print("=== Sophia AI Codebase Audit ===\n")

        print("1. Auditing modules...")
        self.audit_modules()
        print(f"   Found {len(self.audit_results['modules'])} modules")

        print("2. Auditing agents...")
        self.audit_agents()
        print(f"   Found {len(self.audit_results['agents'])} agents")

        print("3. Auditing integrations...")
        self.audit_integrations()
        print(f"   Found {len(self.audit_results['integrations'])} integrations")

        print("4. Auditing compliance...")
        self.audit_compliance()
        print(
            f"   Found {len(self.audit_results['compliance_sensitive'])} sensitive flows"
        )

        print("5. Auditing documentation...")
        self.audit_documentation()
        doc_status = self.audit_results["documentation_status"]
        print(
            f"   Documentation coverage: {doc_status['documented_modules']}/{doc_status['total_modules']}"
        )

        print("6. Generating recommendations...")
        self.generate_recommendations()
        print(
            f"   Generated {len(self.audit_results['recommendations'])} recommendations"
        )

        return self.audit_results

    def save_audit_report(self, output_file: str = "codebase_audit_report.json"):
        """Save audit results to file"""
        with open(output_file, "w") as f:
            json.dump(self.audit_results, f, indent=2)
        print(f"\nAudit report saved to {output_file}")


def main():
    """Run codebase audit"""
    auditor = CodebaseAuditor()
    results = auditor.run_full_audit()
    auditor.save_audit_report()

    print("\n=== Audit Summary ===")
    print(f"Dead code files: {len(results['dead_code'])}")
    print(f"Compliance-sensitive flows: {len(results['compliance_sensitive'])}")
    print(f"Recommendations: {len(results['recommendations'])}")

    print("\n=== Top Recommendations ===")
    for rec in results["recommendations"][:3]:
        print(f"[{rec['priority']}] {rec['category']}: {rec['action']}")


if __name__ == "__main__":
    main()
