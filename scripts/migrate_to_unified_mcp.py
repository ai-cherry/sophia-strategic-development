#!/usr/bin/env python3
"""
Migrate MCP servers to unified base class
"""

import ast
from pathlib import Path


class MCPMigrationAnalyzer:
    """Analyze and migrate MCP servers to unified base"""

    def __init__(self):
        self.servers_analyzed = []
        self.migration_plan = []

    def analyze_all_servers(self):
        """Analyze all MCP servers"""
        print("🔍 Analyzing MCP servers for migration...")

        # Find all MCP server files
        server_paths = []

        # Check backend/mcp_servers
        backend_path = Path("backend/mcp_servers")
        if backend_path.exists():
            server_paths.extend(backend_path.rglob("*_mcp_server.py"))

        # Check mcp-servers
        mcp_path = Path("mcp-servers")
        if mcp_path.exists():
            for subdir in mcp_path.iterdir():
                if subdir.is_dir():
                    server_paths.extend(subdir.rglob("*_mcp_server.py"))

        print(f"Found {len(server_paths)} MCP server files")

        for server_path in server_paths:
            self.analyze_server(server_path)

        self.generate_migration_plan()

    def analyze_server(self, file_path: Path):
        """Analyze a single server file"""
        try:
            with open(file_path) as f:
                content = f.read()

            # Parse AST
            tree = ast.parse(content)

            server_info = {
                "path": str(file_path),
                "name": file_path.stem,
                "base_classes": [],
                "imports": [],
                "methods": [],
                "complexity": self.calculate_complexity(tree),
                "lines": len(content.split("\n")),
            }

            # Find base classes
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    for base in node.bases:
                        if isinstance(base, ast.Name):
                            server_info["base_classes"].append(base.id)

                    # Find methods
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            server_info["methods"].append(item.name)

                # Find imports
                if isinstance(node, ast.ImportFrom):
                    if node.module and "mcp" in node.module:
                        server_info["imports"].append(node.module)

            self.servers_analyzed.append(server_info)

        except Exception as e:
            print(f"❌ Error analyzing {file_path}: {e}")

    def calculate_complexity(self, tree) -> int:
        """Calculate cyclomatic complexity"""
        complexity = 0
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
        return complexity

    def generate_migration_plan(self):
        """Generate migration plan"""
        print("\n📋 Migration Plan:")
        print("=" * 60)

        # Group by base class
        base_class_groups = {}
        for server in self.servers_analyzed:
            for base_class in server["base_classes"]:
                if base_class not in base_class_groups:
                    base_class_groups[base_class] = []
                base_class_groups[base_class].append(server)

        # Print analysis
        print("\n🔍 Base Class Distribution:")
        for base_class, servers in base_class_groups.items():
            print(f"  {base_class}: {len(servers)} servers")

        # Identify high priority migrations
        print("\n🚨 High Priority Migrations (>1000 lines or complexity >50):")
        high_priority = [
            s
            for s in self.servers_analyzed
            if s["lines"] > 1000 or s["complexity"] > 50
        ]

        for server in high_priority:
            print(
                f"  - {server['name']}: {server['lines']} lines, complexity {server['complexity']}"
            )

        # Generate migration steps
        print("\n📝 Migration Steps:")

        for i, server in enumerate(self.servers_analyzed, 1):
            migration_step = {
                "order": i,
                "server": server["name"],
                "current_base": server["base_classes"],
                "actions": [],
            }

            # Determine actions needed
            if "StandardizedMCPServer" in server["base_classes"]:
                migration_step["actions"].append("Update imports to UnifiedMCPServer")
                migration_step["actions"].append("Update config to MCPServerConfig")

            if "EnhancedStandardizedMCPServer" in server["base_classes"]:
                migration_step["actions"].append(
                    "Merge enhanced features into server_specific methods"
                )

            if not server["base_classes"]:
                migration_step["actions"].append("Add UnifiedMCPServer as base class")
                migration_step["actions"].append("Implement required abstract methods")

            self.migration_plan.append(migration_step)

        # Save migration plan
        self.save_migration_plan()

    def save_migration_plan(self):
        """Save migration plan to file"""
        with open("MCP_MIGRATION_PLAN.md", "w") as f:
            f.write("# MCP Server Migration Plan\n\n")
            f.write("## Summary\n")
            f.write(f"- Total Servers: {len(self.servers_analyzed)}\n")
            f.write(
                f"- Average Complexity: {sum(s['complexity'] for s in self.servers_analyzed) / len(self.servers_analyzed):.1f}\n"
            )
            f.write(
                f"- Total Lines: {sum(s['lines'] for s in self.servers_analyzed)}\n\n"
            )

            f.write("## Server Analysis\n\n")
            for server in self.servers_analyzed:
                f.write(f"### {server['name']}\n")
                f.write(f"- Path: `{server['path']}`\n")
                f.write(f"- Lines: {server['lines']}\n")
                f.write(f"- Complexity: {server['complexity']}\n")
                f.write(
                    f"- Base Classes: {', '.join(server['base_classes']) or 'None'}\n"
                )
                f.write(f"- Methods: {len(server['methods'])}\n\n")

            f.write("## Migration Steps\n\n")
            for step in self.migration_plan:
                f.write(f"### {step['order']}. {step['server']}\n")
                f.write(f"Current Base: {', '.join(step['current_base']) or 'None'}\n")
                f.write("Actions:\n")
                for action in step["actions"]:
                    f.write(f"- {action}\n")
                f.write("\n")

        print("\n✅ Migration plan saved to MCP_MIGRATION_PLAN.md")

    def generate_example_migration(self):
        """Generate an example migration"""
        example = '''#!/usr/bin/env python3
"""
Example MCP Server using Unified Base Class
"""

from typing import List, Dict, Any
from backend.mcp_servers.base.unified_mcp_base import (
    UnifiedMCPServer,
    MCPServerConfig,
    HealthCheckLevel,
    ServerStatus
)

class ExampleMCPServer(UnifiedMCPServer):
    """Example server implementation"""

    def __init__(self):
        config = MCPServerConfig(
            name="example",
            port=9999,
            version="1.0.0",
            enable_cortex=True,
            enable_caching=True
        )
        super().__init__(config)

    def _setup_server_routes(self):
        """Set up server-specific routes"""

        @self.app.get("/example/test")
        async def test_endpoint():
            return {"message": "Example endpoint"}

    async def server_specific_init(self):
        """Server-specific initialization"""
        # Initialize your server components here
        pass

    async def server_specific_health_check(self, level: HealthCheckLevel) -> Dict[str, Any]:
        """Server-specific health checks"""
        return {
            "example_status": "operational",
            "custom_metric": 42
        }

    async def list_tools(self) -> List[Dict[str, Any]]:
        """List available tools"""
        return [
            {
                "name": "example_tool",
                "description": "An example tool",
                "parameters": {
                    "input": {"type": "string", "required": True}
                }
            }
        ]

    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Execute a tool"""
        if tool_name == "example_tool":
            return {"result": f"Processed: {arguments.get('input')}"}
        else:
            raise ValueError(f"Unknown tool: {tool_name}")

    async def server_specific_cleanup(self):
        """Server-specific cleanup"""
        # Cleanup your server resources here
        pass

if __name__ == "__main__":
    import asyncio
    server = ExampleMCPServer()
    asyncio.run(server.start())
'''

        with open("example_unified_mcp_server.py", "w") as f:
            f.write(example)

        print("✅ Example migration saved to example_unified_mcp_server.py")


def main():
    """Main execution"""
    analyzer = MCPMigrationAnalyzer()
    analyzer.analyze_all_servers()
    analyzer.generate_example_migration()


if __name__ == "__main__":
    main()
