#!/usr/bin/env python3
"""Check Architecture Consistency
This script checks for architecture inconsistencies in the codebase.
"""

import asyncio
import glob
import logging
import os
import re
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ArchitectureConsistencyChecker:
    """Checks for architecture inconsistencies in the codebase."""

    def __init__(self, root_dir: str = "."):
        self.root_dir = root_dir
        self.inconsistencies = {
            "direct_api_calls": [],
            "direct_pulumi_commands": [],
            "old_ui_references": [],
            "direct_vector_store_access": [],
        }
        self.patterns = {
            "direct_api_calls": [
                r"import\s+requests",
                r"requests\.(get|post|put|delete|patch)\(",
                r"import\s+urllib",
                r"urllib\.(request|parse|error)",
                r"import\s+http",
                r"http\.(client|server)",
                r"\.api\.gong\.io",
            ],
            "direct_pulumi_commands": [
                r"pulumi\s+(up|preview|destroy|stack)",
                r"import\s+pulumi(?!_mcp)",
                r"from\s+pulumi\s+import",
                r"pulumi\.(export|Config|Output)",
            ],
            "old_ui_references": [
                r"sophia_admin_frontend",
                r"npm\s+(install|run|build)",
                r"react",
                r"webpack",
                r"babel",
            ],
            "direct_vector_store_access": [
                r"import\s+pinecone",
                r"from\s+pinecone\s+import",
                r"import\s+weaviate",
                r"from\s+weaviate\s+import",
                r"pinecone\.init\(",
                r"pinecone\.Index\(",
                r"weaviate\.Client\(",
            ],
        }
        self.exclusions = {
            "direct_api_calls": [
                r"backend/mcp/.*_mcp_server\.py",
                r"backend/integrations/.*_integration\.py",
                r"examples/.*\.py",
            ],
            "direct_pulumi_commands": [
                r"infrastructure/pulumi/.*\.py",
                r"backend/mcp/pulumi_mcp_server\.py",
                r"examples/.*\.py",
            ],
            "old_ui_references": [r"architecture_.*\.md", r"examples/.*\.py"],
            "direct_vector_store_access": [
                r"backend/core/comprehensive_memory_manager\.py",
                r"backend/knowledge/hybrid_rag_manager\.py",
                r"examples/.*\.py",
            ],
        }
        self.check_results = {
            "scanned_files": 0,
            "inconsistent_files": 0,
            "inconsistencies": {
                "direct_api_calls": 0,
                "direct_pulumi_commands": 0,
                "old_ui_references": 0,
                "direct_vector_store_access": 0,
            },
            "files": {
                "direct_api_calls": [],
                "direct_pulumi_commands": [],
                "old_ui_references": [],
                "direct_vector_store_access": [],
            },
        }

    def is_excluded(self, file_path: str, inconsistency_type: str) -> bool:
        """Check if a file is excluded from a specific inconsistency check."""
        for exclusion_pattern in self.exclusions.get(inconsistency_type, []):
            if re.match(exclusion_pattern, file_path):
                return True
        return False

    async def check_file(self, file_path: str):
        """Check a file for architecture inconsistencies."""
        try:
            with open(file_path, "r") as f:
                content = f.read()

            # Check for each type of inconsistency
            for inconsistency_type, patterns in self.patterns.items():
                # Skip if the file is excluded from this check
                if self.is_excluded(file_path, inconsistency_type):
                    continue

                # Check for patterns
                for pattern in patterns:
                    if re.search(pattern, content):
                        self.inconsistencies[inconsistency_type].append(file_path)
                        self.check_results["inconsistencies"][inconsistency_type] += 1
                        if (
                            file_path
                            not in self.check_results["files"][inconsistency_type]
                        ):
                            self.check_results["files"][inconsistency_type].append(
                                file_path
                            )
                        break

        except Exception as e:
            logger.error(f"Error checking file {file_path}: {e}")

    async def check_files(self):
        """Check all files for architecture inconsistencies."""
        logger.info(
            f"Checking files in {self.root_dir} for architecture inconsistencies..."
        )

        # Find all relevant files
        python_files = glob.glob(f"{self.root_dir}/**/*.py", recursive=True)
        shell_files = glob.glob(f"{self.root_dir}/**/*.sh", recursive=True)
        js_files = glob.glob(f"{self.root_dir}/**/*.js", recursive=True) + glob.glob(
            f"{self.root_dir}/**/*.jsx", recursive=True
        )
        md_files = glob.glob(f"{self.root_dir}/**/*.md", recursive=True)

        all_files = python_files + shell_files + js_files + md_files
        self.check_results["scanned_files"] = len(all_files)

        # Check each file
        for file_path in all_files:
            await self.check_file(file_path)

        # Count inconsistent files
        inconsistent_files = set()
        for inconsistency_type, files in self.check_results["files"].items():
            inconsistent_files.update(files)
        self.check_results["inconsistent_files"] = len(inconsistent_files)

        logger.info(
            f"Found {self.check_results['inconsistent_files']} files with architecture inconsistencies."
        )
        return self.check_results

    async def generate_report(self) -> str:
        """Generate a report of architecture inconsistencies."""
        report = "# Architecture Consistency Report\n\n"
        report += f"Scanned {self.check_results['scanned_files']} files.\n"
        report += f"Found {self.check_results['inconsistent_files']} files with architecture inconsistencies.\n\n"

        report += "## Inconsistencies\n\n"

        for inconsistency_type, count in self.check_results["inconsistencies"].items():
            report += f"### {inconsistency_type.replace('_', ' ').title()}: {count}\n\n"

            if count > 0:
                report += "Files:\n"
                for file_path in self.check_results["files"][inconsistency_type]:
                    report += f"- {file_path}\n"
                report += "\n"

        report += "## Recommendations\n\n"

        if self.check_results["inconsistencies"]["direct_api_calls"] > 0:
            report += "### Direct API Calls\n\n"
            report += "Use the MCP client to call the appropriate MCP server instead of making direct API calls.\n\n"
            report += "Example:\n\n"
            report += "```python\n"
            report += "from backend.mcp.mcp_client import MCPClient\n\n"
            report += "async def gong_api_call():\n"
            report += '    mcp_client = MCPClient("http://localhost:8090")\n'
            report += "    await mcp_client.connect()\n"
            report += "    \n"
            report += "    result = await mcp_client.call_tool(\n"
            report += '        "gong",\n'
            report += '        "get_users",\n'
            report += "        {}\n"
            report += "    )\n"
            report += "    \n"
            report += "    await mcp_client.close()\n"
            report += "    return result\n"
            report += "```\n\n"

        if self.check_results["inconsistencies"]["direct_pulumi_commands"] > 0:
            report += "### Direct Pulumi Commands\n\n"
            report += "Use the MCP client to call the Pulumi MCP server instead of running Pulumi commands directly.\n\n"
            report += "Example:\n\n"
            report += "```python\n"
            report += "from backend.mcp.mcp_client import MCPClient\n\n"
            report += "async def deploy_infrastructure():\n"
            report += '    mcp_client = MCPClient("http://localhost:8090")\n'
            report += "    await mcp_client.connect()\n"
            report += "    \n"
            report += "    result = await mcp_client.call_tool(\n"
            report += '        "pulumi",\n'
            report += '        "run_pulumi_up",\n'
            report += "        {\n"
            report += '            "stack_name": "dev"\n'
            report += "        }\n"
            report += "    )\n"
            report += "    \n"
            report += "    await mcp_client.close()\n"
            report += "    return result\n"
            report += "```\n\n"

        if self.check_results["inconsistencies"]["old_ui_references"] > 0:
            report += "### Old UI References\n\n"
            report += (
                "Replace the old `sophia_admin_frontend` UI with Retool dashboards.\n\n"
            )
            report += "Example:\n\n"
            report += "```python\n"
            report += "from backend.mcp.mcp_client import MCPClient\n\n"
            report += "async def build_admin_dashboard():\n"
            report += '    mcp_client = MCPClient("http://localhost:8090")\n'
            report += "    await mcp_client.connect()\n"
            report += "    \n"
            report += "    result = await mcp_client.call_tool(\n"
            report += '        "retool",\n'
            report += '        "create_admin_dashboard",\n'
            report += "        {\n"
            report += '            "dashboard_name": "sophia_admin",\n'
            report += '            "description": "Sophia AI Admin Dashboard"\n'
            report += "        }\n"
            report += "    )\n"
            report += "    \n"
            report += "    await mcp_client.close()\n"
            report += "    return result\n"
            report += "```\n\n"

        if self.check_results["inconsistencies"]["direct_vector_store_access"] > 0:
            report += "### Direct Vector Store Access\n\n"
            report += "Use the ComprehensiveMemoryManager instead of directly accessing vector stores.\n\n"
            report += "Example:\n\n"
            report += "```python\n"
            report += "from backend.core.comprehensive_memory_manager import comprehensive_memory_manager, MemoryRequest, MemoryOperationType\n\n"
            report += "async def store_memory(agent_id, content, metadata):\n"
            report += "    request = MemoryRequest(\n"
            report += "        operation=MemoryOperationType.STORE,\n"
            report += "        agent_id=agent_id,\n"
            report += "        content=content,\n"
            report += "        metadata=metadata\n"
            report += "    )\n"
            report += "    \n"
            report += "    response = await comprehensive_memory_manager.process_memory_request(request)\n"
            report += "    return response\n"
            report += "```\n\n"

        return report

    async def run(self):
        """Run the architecture consistency check."""
        await self.check_files()
        report = await self.generate_report()

        # Write the report to a file
        report_path = os.path.join(self.root_dir, "architecture_consistency_report.md")
        with open(report_path, "w") as f:
            f.write(report)

        logger.info(f"Report written to {report_path}")
        return self.check_results


async def main():
    """Main function to run the architecture consistency checker."""
    root_dir = "."
    if len(sys.argv) > 1:
        root_dir = sys.argv[1]

    checker = ArchitectureConsistencyChecker(root_dir)
    results = await checker.run()

    print("\n--- Architecture Consistency Check Summary ---")
    print(f"Scanned files: {results['scanned_files']}")
    print(f"Inconsistent files: {results['inconsistent_files']}")
    print("\nInconsistencies:")
    for inconsistency_type, count in results["inconsistencies"].items():
        print(f"- {inconsistency_type.replace('_', ' ').title()}: {count}")

    print("\nCheck complete!")
    print("A detailed report has been written to architecture_consistency_report.md")


if __name__ == "__main__":
    asyncio.run(main())
