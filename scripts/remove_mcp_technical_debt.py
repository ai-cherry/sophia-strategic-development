#!/usr/bin/env python3
"""
Remove all MCP technical debt and duplications
This script aggressively cleans up all duplicate MCP implementations
"""

import logging
import os
import shutil
from pathlib import Path

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class MCPTechnicalDebtRemover:
    """Removes all technical debt from MCP servers"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.removed_count = 0
        self.kept_paths: set[Path] = set()

        # Define the directories and files to keep
        self.keep_structure = {
            "mcp-servers": {
                "base": ["unified_standardized_base.py"],
                "ai_memory": ["server.py"],
                "snowflake_unified": ["server.py"],
                "gong": ["server.py"],
                "hubspot_unified": ["server.py"],
                "slack": ["server.py"],
                "github": ["server.py"],
                "linear": ["server.py"],
                "asana": ["server.py"],
                "notion": ["server.py"],
                "codacy": ["server.py"],
                "figma": ["server.py"],
                "lambda_labs_cli": ["server.py"],
                "ui_ux_agent": ["server.py"],
            },
            "kubernetes/mcp-servers": ["namespace.yaml", "configmap.yaml", "helm/"],
            "config": ["unified_mcp_configuration.yaml"],
            "docker": ["Dockerfile.mcp-base"],
            "scripts": [
                "deploy_to_lambda_labs_kubernetes.py",
                "consolidate_mcp_servers.py",
                "remove_mcp_technical_debt.py",
            ],
        }

    def identify_duplicates(self) -> list[Path]:
        """Identify all duplicate MCP implementations"""
        duplicates = []

        # Find all duplicate base classes
        base_class_files = [
            "standalone_mcp_base.py",
            "standalone_mcp_base_v2.py",
            "standalone_mcp_server.py",
            "base_mcp_server.py",
            "mcp_base.py",
            "standardized_mcp_server.py",
        ]

        for root, dirs, files in os.walk(self.project_root):
            root_path = Path(root)

            # Skip node_modules and .git
            if ".git" in str(root_path) or "node_modules" in str(root_path):
                continue

            for file in files:
                file_path = root_path / file

                # Check for duplicate base classes
                if (
                    file in base_class_files
                    and "unified_standardized_base.py" not in str(file_path)
                ):
                    duplicates.append(file_path)

                # Check for v2 versions (we want to remove these)
                if "_v2" in file and file.endswith(".py"):
                    duplicates.append(file_path)

        return duplicates

    def identify_old_implementations(self) -> list[Path]:
        """Identify old MCP server implementations to remove"""
        old_implementations = []

        # Infrastructure directory with v2 servers
        infra_mcp_dir = self.project_root / "infrastructure/mcp_servers"
        if infra_mcp_dir.exists():
            for item in infra_mcp_dir.iterdir():
                if item.is_dir() and item.name.endswith("_v2"):
                    old_implementations.append(item)

        # Old MCP config files
        old_configs = [
            "mcp_servers.json",
            "mcp_config.json",
            "mcp-config.json",
            "mcp_ports.json",
            "enhanced_mcp_ports.json",
        ]

        for root, dirs, files in os.walk(self.project_root):
            root_path = Path(root)
            for file in files:
                if file in old_configs and file != "unified_mcp_configuration.yaml":
                    old_implementations.append(root_path / file)

        return old_implementations

    def identify_unused_dockerfiles(self) -> list[Path]:
        """Identify unused Dockerfiles"""
        unused = []

        for root, dirs, files in os.walk(self.project_root):
            root_path = Path(root)
            for file in files:
                if file.startswith("Dockerfile") and file != "Dockerfile.mcp-base":
                    file_path = root_path / file
                    # Keep main Dockerfiles in key directories
                    if "mcp" in str(file_path) and file != "Dockerfile.mcp-base":
                        unused.append(file_path)

        return unused

    def clean_mcp_servers_directory(self):
        """Clean up the mcp-servers directory to only keep the unified structure"""
        logger.info("Cleaning mcp-servers directory...")

        mcp_dir = self.project_root / "mcp-servers"
        if not mcp_dir.exists():
            return

        # First, identify what to keep
        for server_name, files in self.keep_structure["mcp-servers"].items():
            server_dir = mcp_dir / server_name
            if server_dir.exists():
                for file in files:
                    file_path = server_dir / file
                    if file_path.exists():
                        self.kept_paths.add(file_path)

        # Now remove everything not in kept_paths
        for item in mcp_dir.iterdir():
            if item.is_dir():
                if item.name in self.keep_structure["mcp-servers"]:
                    # Clean inside the directory
                    for sub_item in item.rglob("*"):
                        if sub_item.is_file() and sub_item not in self.kept_paths:
                            logger.info(
                                f"  Removing: {sub_item.relative_to(self.project_root)}"
                            )
                            sub_item.unlink()
                            self.removed_count += 1
                else:
                    # Remove entire directory
                    logger.info(
                        f"  Removing directory: {item.relative_to(self.project_root)}"
                    )
                    shutil.rmtree(item)
                    self.removed_count += 1

    def remove_all_technical_debt(self):
        """Main function to remove all technical debt"""
        logger.info("Starting MCP technical debt removal...")

        # 1. Clean main mcp-servers directory
        self.clean_mcp_servers_directory()

        # 2. Remove duplicate base classes
        duplicates = self.identify_duplicates()
        logger.info(f"\nFound {len(duplicates)} duplicate files to remove")
        for dup in duplicates:
            if dup.exists():
                logger.info(
                    f"  Removing duplicate: {dup.relative_to(self.project_root)}"
                )
                dup.unlink()
                self.removed_count += 1

        # 3. Remove old implementations
        old_impls = self.identify_old_implementations()
        logger.info(f"\nFound {len(old_impls)} old implementations to remove")
        for old in old_impls:
            if old.exists():
                if old.is_dir():
                    logger.info(
                        f"  Removing old directory: {old.relative_to(self.project_root)}"
                    )
                    shutil.rmtree(old)
                else:
                    logger.info(
                        f"  Removing old file: {old.relative_to(self.project_root)}"
                    )
                    old.unlink()
                self.removed_count += 1

        # 4. Remove unused Dockerfiles
        unused_docker = self.identify_unused_dockerfiles()
        logger.info(f"\nFound {len(unused_docker)} unused Dockerfiles to remove")
        for docker in unused_docker:
            if docker.exists():
                logger.info(f"  Removing: {docker.relative_to(self.project_root)}")
                docker.unlink()
                self.removed_count += 1

        # 5. Remove the entire infrastructure/mcp_servers directory
        infra_mcp = self.project_root / "infrastructure/mcp_servers"
        if infra_mcp.exists():
            logger.info("\nRemoving entire directory: infrastructure/mcp_servers")
            shutil.rmtree(infra_mcp)
            self.removed_count += 1

        # 6. Clean up empty directories
        self.clean_empty_directories()

        logger.info(f"\n{'='*60}")
        logger.info("TECHNICAL DEBT REMOVAL COMPLETE")
        logger.info(f"{'='*60}")
        logger.info(f"Total items removed: {self.removed_count}")
        logger.info("\nThe MCP server structure is now clean and unified!")
        logger.info(
            f"All servers will deploy to Lambda Labs Kubernetes at {self.project_root / 'config/unified_mcp_configuration.yaml'}"
        )

    def clean_empty_directories(self):
        """Remove empty directories"""
        logger.info("\nCleaning empty directories...")

        for root, dirs, files in os.walk(self.project_root, topdown=False):
            root_path = Path(root)

            # Skip .git and node_modules
            if ".git" in str(root_path) or "node_modules" in str(root_path):
                continue

            # Check if directory is empty
            if not any(root_path.iterdir()):
                logger.info(
                    f"  Removing empty directory: {root_path.relative_to(self.project_root)}"
                )
                root_path.rmdir()
                self.removed_count += 1


if __name__ == "__main__":
    remover = MCPTechnicalDebtRemover()
    remover.remove_all_technical_debt()
