#!/usr/bin/env python3
"""
Fix all Docker path references in the codebase
"""

import json
import re
from pathlib import Path


class DockerPathFixer:
    def __init__(self):
        self.root_dir = Path(__file__).parent.parent
        self.fixes_applied = []

        # Path mappings
        self.path_mappings = {
            # Old path -> New path
            "./mcp-servers/": "./backend/mcp_servers/",
            "backend.mcp.": "backend.mcp_servers.",
            "mcp-servers/": "backend/mcp_servers/",
            "backend/mcp/": "backend/mcp_servers/",
        }

        # Module mappings for specific servers
        self.module_mappings = {
            "ai_memory_mcp_server": "backend.mcp_servers.ai_memory.ai_memory_mcp_server",
            "snowflake_admin_mcp_server": "backend.mcp_servers.snowflake_admin_mcp_server",
            "codacy_mcp_server": "mcp-servers.codacy.production_codacy_server",
            "linear_mcp_server": "mcp-servers.linear.linear_mcp_server",
            "github_mcp_server": "mcp-servers.github.github_mcp_server",
            "asana_mcp_server": "mcp-servers.asana.asana_mcp_server",
            "notion_mcp_server": "mcp-servers.notion.enhanced_notion_mcp_server",
            "ui_ux_agent_mcp_server": "mcp-servers.ui_ux_agent.ui_ux_agent_mcp_server",
            "portkey_admin_mcp_server": "mcp-servers.portkey_admin.portkey_admin_mcp_server",
            "lambda_labs_cli_mcp_server": "mcp-servers.lambda_labs_cli.lambda_labs_cli_mcp_server",
            "snowflake_cortex_mcp_server": "mcp-servers.snowflake_cortex.production_snowflake_cortex_mcp_server",
        }

    def fix_file(self, filepath: Path) -> list[tuple[str, str]]:
        """Fix path references in a single file"""
        fixes = []

        try:
            with open(filepath, encoding="utf-8") as f:
                content = f.read()

            original_content = content

            # Apply path mappings
            for old_path, new_path in self.path_mappings.items():
                if old_path in content:
                    content = content.replace(old_path, new_path)
                    fixes.append((old_path, new_path))

            # Apply module mappings
            for old_module, new_module in self.module_mappings.items():
                # Look for patterns like "module": "backend.mcp.ai_memory_mcp_server"
                pattern = rf'"module":\s*"[^"]*{old_module}"'
                replacement = f'"module": "{new_module}"'
                if re.search(pattern, content):
                    content = re.sub(pattern, replacement, content)
                    fixes.append((old_module, new_module))

            # Save if changes were made
            if content != original_content:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content)
                self.fixes_applied.append((str(filepath), fixes))

        except Exception as e:
            print(f"Error processing {filepath}: {e}")

        return fixes

    def fix_deploy_script(self):
        """Fix the deploy_mcp_servers.py script"""
        deploy_script = self.root_dir / "scripts" / "deploy_mcp_servers.py"
        if deploy_script.exists():
            print(f"Fixing {deploy_script}")
            fixes = self.fix_file(deploy_script)
            if fixes:
                print(f"  Applied {len(fixes)} fixes")

    def fix_docker_compose_files(self):
        """Fix all docker-compose files"""
        compose_files = [
            "docker-compose.yml",
            "docker-compose.mcp.yml",
            "docker-compose.production.yml",
            "docker-compose.dev.yml",
        ]

        for compose_file in compose_files:
            filepath = self.root_dir / compose_file
            if filepath.exists():
                print(f"Fixing {filepath}")
                fixes = self.fix_file(filepath)
                if fixes:
                    print(f"  Applied {len(fixes)} fixes")

    def fix_dockerfile_references(self):
        """Fix references in Dockerfiles"""
        # Find all Dockerfiles
        dockerfiles = list(self.root_dir.rglob("Dockerfile*"))

        for dockerfile in dockerfiles:
            if dockerfile.is_file():
                print(f"Fixing {dockerfile}")
                fixes = self.fix_file(dockerfile)
                if fixes:
                    print(f"  Applied {len(fixes)} fixes")

    def create_missing_dockerfiles(self):
        """Create missing Dockerfiles for MCP servers"""
        template_path = self.root_dir / "docker" / "Dockerfile.mcp-server"

        if not template_path.exists():
            print(f"Warning: Template Dockerfile not found at {template_path}")
            return

        # MCP servers that need Dockerfiles
        mcp_servers = [
            (
                "mcp-servers/ai_memory",
                "backend.mcp_servers.ai_memory.ai_memory_mcp_server",
                9001,
            ),
            ("mcp-servers/codacy", "mcp-servers.codacy.production_codacy_server", 3008),
            ("mcp-servers/linear", "mcp-servers.linear.linear_mcp_server", 9004),
            ("mcp-servers/github", "mcp-servers.github.github_mcp_server", 9103),
            ("mcp-servers/asana", "mcp-servers.asana.asana_mcp_server", 9100),
            (
                "mcp-servers/notion",
                "mcp-servers.notion.enhanced_notion_mcp_server",
                9005,
            ),
            (
                "mcp-servers/ui_ux_agent",
                "mcp-servers.ui_ux_agent.ui_ux_agent_mcp_server",
                9002,
            ),
            (
                "mcp-servers/portkey_admin",
                "mcp-servers.portkey_admin.portkey_admin_mcp_server",
                9013,
            ),
            (
                "mcp-servers/lambda_labs_cli",
                "mcp-servers.lambda_labs_cli.lambda_labs_cli_mcp_server",
                9020,
            ),
            (
                "mcp-servers/snowflake_cortex",
                "mcp-servers.snowflake_cortex.production_snowflake_cortex_mcp_server",
                9030,
            ),
        ]

        with open(template_path) as f:
            template = f.read()

        for server_dir, module_path, port in mcp_servers:
            dockerfile_path = self.root_dir / server_dir / "Dockerfile"

            if not dockerfile_path.exists():
                dockerfile_path.parent.mkdir(parents=True, exist_ok=True)

                # Customize the template
                dockerfile_content = template.replace("${MODULE_PATH}", module_path)
                dockerfile_content = dockerfile_content.replace("${PORT}", str(port))

                with open(dockerfile_path, "w") as f:
                    f.write(dockerfile_content)

                print(f"Created Dockerfile for {server_dir}")
                self.fixes_applied.append(
                    (str(dockerfile_path), ["Created new Dockerfile"])
                )

    def generate_report(self):
        """Generate a report of all fixes applied"""
        report = {
            "summary": {
                "total_files_modified": len(self.fixes_applied),
                "total_fixes": sum(len(fixes) for _, fixes in self.fixes_applied),
            },
            "files": {},
        }

        for filepath, fixes in self.fixes_applied:
            report["files"][filepath] = [
                {"old": fix[0], "new": fix[1]} if isinstance(fix, tuple) else fix
                for fix in fixes
            ]

        report_path = self.root_dir / "docker_path_fixes_report.json"
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        print(f"\nReport saved to: {report_path}")
        print(f"Total files modified: {report['summary']['total_files_modified']}")
        print(f"Total fixes applied: {report['summary']['total_fixes']}")

    def run(self):
        """Run all fixes"""
        print("🔧 Fixing Docker path references...")
        print("=" * 60)

        # Fix specific files
        self.fix_deploy_script()
        self.fix_docker_compose_files()
        self.fix_dockerfile_references()

        # Create missing Dockerfiles
        print("\n📄 Creating missing Dockerfiles...")
        self.create_missing_dockerfiles()

        # Generate report
        print("\n📊 Generating report...")
        self.generate_report()

        print("\n✅ Docker path fixes complete!")


if __name__ == "__main__":
    fixer = DockerPathFixer()
    fixer.run()
