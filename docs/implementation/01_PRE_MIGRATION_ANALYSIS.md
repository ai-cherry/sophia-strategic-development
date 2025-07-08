# Pre-Migration Analysis

## Overview

This document outlines the comprehensive analysis required before beginning the MCP server consolidation. All scripts and procedures must be executed to establish a baseline and identify potential conflicts.

## 1. Server Inventory Script

Create `scripts/migration/inventory_mcp_servers.py`:

```python
#!/usr/bin/env python3
"""
MCP Server Inventory Analysis
Generates comprehensive inventory of all MCP servers
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any
import ast
import re

class MCPServerInventory:
    def __init__(self):
        self.root = Path.cwd()
        self.servers = []
        self.port_map = {}
        self.import_graph = {}

    def scan_servers(self):
        """Scan all MCP server locations"""
        # Legacy V1 servers
        v1_path = self.root / "mcp-servers"
        if v1_path.exists():
            for server_dir in v1_path.iterdir():
                if server_dir.is_dir() and not server_dir.name.startswith('.'):
                    self._analyze_server(server_dir, "v1")

        # V2 servers
        v2_path = self.root / "infrastructure" / "mcp_servers"
        if v2_path.exists():
            for server_dir in v2_path.iterdir():
                if server_dir.is_dir() and not server_dir.name.startswith('.'):
                    self._analyze_server(server_dir, "v2")

    def _analyze_server(self, path: Path, version: str):
        """Analyze individual server"""
        server_info = {
            "name": path.name,
            "path": str(path.relative_to(self.root)),
            "version": version,
            "port": None,
            "base_class": None,
            "dependencies": [],
            "has_dockerfile": False,
            "has_tests": False,
            "fastapi_version": None,
            "issues": []
        }

        # Check for main server file
        server_files = list(path.glob("*server*.py")) + list(path.glob("main.py"))
        if server_files:
            server_info.update(self._analyze_python_file(server_files[0]))

        # Check for Dockerfile
        if (path / "Dockerfile").exists():
            server_info["has_dockerfile"] = True

        # Check for tests
        if (path / "tests").exists() or list(path.glob("test_*.py")):
            server_info["has_tests"] = True

        self.servers.append(server_info)

    def _analyze_python_file(self, file_path: Path) -> Dict[str, Any]:
        """Extract information from Python file"""
        results = {
            "port": None,
            "base_class": None,
            "dependencies": [],
            "fastapi_version": None
        }

        try:
            content = file_path.read_text()
            tree = ast.parse(content)

            # Extract port
            port_match = re.search(r'port["\']?\s*[:=]\s*(\d+)', content)
            if port_match:
                results["port"] = int(port_match.group(1))

            # Extract base class
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    for base in node.bases:
                        if isinstance(base, ast.Name):
                            results["base_class"] = base.id
                        elif isinstance(base, ast.Attribute):
                            results["base_class"] = f"{base.value.id}.{base.attr}"

            # Extract imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        results["dependencies"].append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        results["dependencies"].append(node.module)

        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")

        return results

    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive inventory report"""
        # Port conflicts
        port_conflicts = {}
        for server in self.servers:
            if server["port"]:
                if server["port"] not in port_conflicts:
                    port_conflicts[server["port"]] = []
                port_conflicts[server["port"]].append(server["name"])

        conflicts = {port: servers for port, servers in port_conflicts.items()
                    if len(servers) > 1}

        # Statistics
        stats = {
            "total_servers": len(self.servers),
            "v1_servers": len([s for s in self.servers if s["version"] == "v1"]),
            "v2_servers": len([s for s in self.servers if s["version"] == "v2"]),
            "servers_with_tests": len([s for s in self.servers if s["has_tests"]]),
            "servers_with_dockerfile": len([s for s in self.servers if s["has_dockerfile"]]),
            "port_conflicts": len(conflicts),
            "standardized_servers": len([s for s in self.servers
                                       if "StandardizedMCPServer" in str(s.get("base_class", ""))])
        }

        return {
            "stats": stats,
            "servers": self.servers,
            "port_conflicts": conflicts,
            "timestamp": str(Path.cwd()),
            "recommendations": self._generate_recommendations()
        }

    def _generate_recommendations(self) -> List[str]:
        """Generate migration recommendations"""
        recommendations = []

        # Check for servers without tests
        no_tests = [s["name"] for s in self.servers if not s["has_tests"]]
        if no_tests:
            recommendations.append(f"Add tests for: {', '.join(no_tests[:5])}...")

        # Check for non-standardized servers
        non_standard = [s["name"] for s in self.servers
                       if "StandardizedMCPServer" not in str(s.get("base_class", ""))]
        if non_standard:
            recommendations.append(f"Upgrade to StandardizedMCPServer: {', '.join(non_standard[:5])}...")

        return recommendations

def main():
    """Run inventory analysis"""
    print("🔍 Scanning MCP servers...")
    inventory = MCPServerInventory()
    inventory.scan_servers()

    report = inventory.generate_report()

    # Save report
    output_dir = Path("reports")
    output_dir.mkdir(exist_ok=True)

    with open(output_dir / "mcp_inventory_v1.json", "w") as f:
        json.dump(report, f, indent=2)

    # Print summary
    print("\n📊 Inventory Summary:")
    for key, value in report["stats"].items():
        print(f"  {key}: {value}")

    if report["port_conflicts"]:
        print("\n⚠️  Port Conflicts Detected:")
        for port, servers in report["port_conflicts"].items():
            print(f"  Port {port}: {', '.join(servers)}")

    print(f"\n✅ Report saved to: reports/mcp_inventory_v1.json")

if __name__ == "__main__":
    main()
```

## 2. Dependency Analysis Script

Create `scripts/migration/analyze_dependencies.py`:

```python
#!/usr/bin/env python3
"""
Dependency Analysis for MCP Servers
Identifies version conflicts and circular dependencies
"""

import subprocess
import json
from pathlib import Path
from typing import Dict, Set, List
import pkg_resources
import re

class DependencyAnalyzer:
    def __init__(self):
        self.dependencies = {}
        self.conflicts = []
        self.circular_deps = []

    def analyze_pyproject(self):
        """Analyze pyproject.toml dependencies"""
        pyproject_path = Path("pyproject.toml")
        if not pyproject_path.exists():
            print("❌ pyproject.toml not found")
            return

        # Get current dependencies
        result = subprocess.run(
            ["uv", "pip", "freeze"],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            for line in result.stdout.strip().split('\n'):
                if '==' in line:
                    name, version = line.split('==')
                    self.dependencies[name.lower()] = version

    def check_fastapi_versions(self):
        """Check for multiple FastAPI versions"""
        fastapi_imports = []

        for py_file in Path(".").rglob("*.py"):
            try:
                content = py_file.read_text()
                if "from fastapi" in content or "import fastapi" in content:
                    # Extract FastAPI usage
                    if "FastAPI(" in content:
                        fastapi_imports.append({
                            "file": str(py_file),
                            "pattern": self._extract_fastapi_pattern(content)
                        })
            except:
                pass

        return fastapi_imports

    def _extract_fastapi_pattern(self, content: str) -> str:
        """Extract FastAPI initialization pattern"""
        if "lifespan=" in content:
            return "FastAPI 0.100+ (lifespan)"
        elif "@app.on_event" in content:
            return "FastAPI <0.100 (on_event)"
        else:
            return "FastAPI (unknown pattern)"

    def check_import_conflicts(self):
        """Check for import conflicts between V1 and V2"""
        import_map = {}

        # Scan all Python files
        for py_file in Path(".").rglob("*.py"):
            if "test" in str(py_file).lower():
                continue

            try:
                content = py_file.read_text()
                imports = re.findall(r'from\s+(\S+)\s+import', content)
                imports.extend(re.findall(r'import\s+(\S+)', content))

                for imp in imports:
                    if imp not in import_map:
                        import_map[imp] = []
                    import_map[imp].append(str(py_file))

            except:
                pass

        # Find conflicts
        conflicts = {}
        for imp, files in import_map.items():
            if len(files) > 1 and ("mcp-servers" in imp or "mcp_servers" in imp):
                conflicts[imp] = files

        return conflicts

    def generate_report(self) -> Dict:
        """Generate dependency analysis report"""
        fastapi_versions = self.check_fastapi_versions()
        import_conflicts = self.check_import_conflicts()

        return {
            "total_dependencies": len(self.dependencies),
            "fastapi_version": self.dependencies.get("fastapi", "not found"),
            "pydantic_version": self.dependencies.get("pydantic", "not found"),
            "fastapi_patterns": fastapi_versions,
            "import_conflicts": import_conflicts,
            "critical_versions": {
                "fastapi": self.dependencies.get("fastapi"),
                "pydantic": self.dependencies.get("pydantic"),
                "sqlalchemy": self.dependencies.get("sqlalchemy"),
                "redis": self.dependencies.get("redis"),
                "httpx": self.dependencies.get("httpx")
            }
        }

def main():
    """Run dependency analysis"""
    print("🔍 Analyzing dependencies...")
    analyzer = DependencyAnalyzer()

    analyzer.analyze_pyproject()
    report = analyzer.generate_report()

    # Save report
    output_dir = Path("reports")
    output_dir.mkdir(exist_ok=True)

    with open(output_dir / "dependency_analysis.json", "w") as f:
        json.dump(report, f, indent=2)

    # Print summary
    print(f"\n📦 Total dependencies: {report['total_dependencies']}")
    print(f"FastAPI version: {report['fastapi_version']}")
    print(f"Pydantic version: {report['pydantic_version']}")

    if report['import_conflicts']:
        print("\n⚠️  Import conflicts detected:")
        for imp, files in list(report['import_conflicts'].items())[:5]:
            print(f"  {imp}: {len(files)} files")

    print(f"\n✅ Report saved to: reports/dependency_analysis.json")

if __name__ == "__main__":
    main()
```

## 3. Port Allocation Strategy

Create `scripts/migration/allocate_ports.py`:

```python
#!/usr/bin/env python3
"""
Port Allocation Strategy for V2+ Migration
Ensures no port conflicts during blue-green deployment
"""

import json
from pathlib import Path
from typing import Dict, List

class PortAllocator:
    def __init__(self):
        self.v1_ports = {}
        self.v2_ports = {}
        self.reserved_ranges = {
            "system": range(1, 1024),
            "common": range(3000, 3100),  # Frontend, monitoring
            "v1_legacy": range(8000, 8999),
            "v2_new": range(9000, 9099),
            "testing": range(9900, 9999)
        }

    def load_current_ports(self):
        """Load current port allocations"""
        ports_file = Path("config/consolidated_mcp_ports.json")
        if ports_file.exists():
            with open(ports_file) as f:
                current = json.load(f)
                for server, port in current.items():
                    if "_v2" in server:
                        self.v2_ports[server] = port
                    else:
                        self.v1_ports[server] = port

    def allocate_v2_ports(self, servers: List[str]) -> Dict[str, int]:
        """Allocate ports for V2 servers"""
        allocated = {}
        used_ports = set(self.v1_ports.values()) | set(self.v2_ports.values())

        next_port = 9000
        for server in servers:
            # Skip if already allocated
            if server in self.v2_ports:
                allocated[server] = self.v2_ports[server]
                continue

            # Find next available port
            while next_port in used_ports or any(
                next_port in range_obj for range_obj in [
                    self.reserved_ranges["system"],
                    self.reserved_ranges["common"]
                ]
            ):
                next_port += 1

            allocated[server] = next_port
            used_ports.add(next_port)
            next_port += 1

        return allocated

    def generate_migration_map(self) -> Dict:
        """Generate complete migration port map"""
        # Phase 1 servers
        phase1_servers = [
            "snowflake_v2",
            "ai_memory_v2",
            "postgres_v2",
            "redis_cache_v2",
            "infrastructure_management_v2",
            "lambda_labs_cli_v2"
        ]

        # Phase 2 servers
        phase2_servers = [
            "salesforce_v2",
            "hubspot_unified_v2",
            "gong_v2",
            "linear_v2",
            "asana_v2",
            "sophia_intelligence_v2"
        ]

        # Phase 3 servers
        phase3_servers = [
            "slack_v2",
            "notion_v2",
            "github_v2",
            "graphiti_v2",
            "ai_operations_v2",
            "design_intelligence_v2",
            "code_management_v2"
        ]

        # Phase 4 servers
        phase4_servers = [
            "data_collection_v2",
            "playwright_v2",
            "huggingface_ai_v2",
            "estuary_v2",
            "airbyte_v2"
        ]

        all_servers = phase1_servers + phase2_servers + phase3_servers + phase4_servers
        port_map = self.allocate_v2_ports(all_servers)

        return {
            "port_allocations": port_map,
            "phases": {
                "phase1": {server: port_map[server] for server in phase1_servers},
                "phase2": {server: port_map[server] for server in phase2_servers},
                "phase3": {server: port_map[server] for server in phase3_servers},
                "phase4": {server: port_map[server] for server in phase4_servers}
            },
            "migration_rules": [
                "Never reuse V1 ports during migration",
                "V2 ports start at 9000",
                "Keep 10-port gaps between phases",
                "Reserve 9900-9999 for testing"
            ]
        }

def main():
    """Generate port allocation strategy"""
    print("🔍 Generating port allocation strategy...")

    allocator = PortAllocator()
    allocator.load_current_ports()

    migration_map = allocator.generate_migration_map()

    # Save allocation
    output_dir = Path("reports")
    output_dir.mkdir(exist_ok=True)

    with open(output_dir / "port_allocation_v2.json", "w") as f:
        json.dump(migration_map, f, indent=2)

    # Print summary
    print("\n📊 Port Allocation Summary:")
    for phase, ports in migration_map["phases"].items():
        print(f"\n{phase.upper()}:")
        for server, port in ports.items():
            print(f"  {server}: {port}")

    print(f"\n✅ Allocation saved to: reports/port_allocation_v2.json")

if __name__ == "__main__":
    main()
```

## 4. Pre-Migration Validation Checklist

Run these commands in sequence:

```bash
# 1. Create feature branch
git checkout -b feature/mcp-v2-consolidation

# 2. Ensure clean working directory
git status

# 3. Run baseline tests
uv sync
uv run pytest -q

# 4. Generate inventory
uv run python scripts/migration/inventory_mcp_servers.py

# 5. Analyze dependencies
uv run python scripts/migration/analyze_dependencies.py

# 6. Allocate ports
uv run python scripts/migration/allocate_ports.py

# 7. Backup current configuration
cp config/consolidated_mcp_ports.json reports/ports_backup_$(date +%Y%m%d).json

# 8. Tag current state in Pulumi
pulumi stack tag set pre-v2-migration=$(date +%Y-%m-%d)

# 9. Verify secrets sync
gh workflow run sync_secrets.yml
gh run watch --exit-status
```

## 5. Success Criteria

Before proceeding to Phase 1:

- [ ] All baseline tests pass
- [ ] Inventory report generated with no critical issues
- [ ] No unresolved port conflicts
- [ ] Dependencies analyzed with upgrade path identified
- [ ] Pulumi state tagged
- [ ] Secrets sync confirmed
- [ ] Team notified of migration start

## Next Steps

Once all pre-migration tasks are complete:
1. Review generated reports in `reports/` directory
2. Address any critical issues identified
3. Proceed to [Conflict Resolution Strategy](./02_CONFLICT_RESOLUTION_STRATEGY.md)
