#!/usr/bin/env python3
"""
Run Architecture Migration
This script automates the entire architecture migration process.
"""

import asyncio
import json
import logging
import os
import sys
import subprocess
from typing import Dict, Any, List, Optional
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ArchitectureMigration:
    """
    Automates the architecture migration process.
    """
    
    def __init__(self, root_dir: str = "."):
        self.root_dir = root_dir
        self.results = {
            "check_before": {},
            "vector_store_migration": {},
            "check_after": {},
            "admin_dashboard": {},
            "success": False
        }
    
    async def run_command(self, command: str) -> Dict[str, Any]:
        """Run a command and return the result."""
        logger.info(f"Running command: {command}")
        
        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            stdout_str = stdout.decode().strip()
            stderr_str = stderr.decode().strip()
            
            if process.returncode != 0:
                logger.error(f"Command failed with exit code {process.returncode}")
                logger.error(f"stderr: {stderr_str}")
                return {
                    "success": False,
                    "exit_code": process.returncode,
                    "stdout": stdout_str,
                    "stderr": stderr_str
                }
            
            return {
                "success": True,
                "exit_code": process.returncode,
                "stdout": stdout_str,
                "stderr": stderr_str
            }
            
        except Exception as e:
            logger.error(f"Error running command: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def check_architecture_consistency(self, output_file: str = "architecture_consistency_report.md") -> Dict[str, Any]:
        """Run the architecture consistency checker."""
        logger.info("Running architecture consistency checker...")
        
        result = await self.run_command(f"python scripts/check_architecture_consistency.py")
        
        # Check if the report file was created
        if result["success"] and os.path.exists(output_file):
            with open(output_file, 'r') as f:
                report_content = f.read()
            
            result["report"] = report_content
        
        return result
    
    async def migrate_vector_store_access(self) -> Dict[str, Any]:
        """Run the vector store access migration script."""
        logger.info("Running vector store access migration...")
        
        result = await self.run_command("python scripts/migrate_vector_store_access.py")
        return result
    
    async def build_admin_dashboard(self) -> Dict[str, Any]:
        """Run the admin dashboard builder script."""
        logger.info("Building admin dashboard...")
        
        result = await self.run_command("python scripts/build_admin_dashboard.py")
        return result
    
    async def run_migration(self) -> Dict[str, Any]:
        """Run the entire migration process."""
        logger.info("Starting architecture migration...")
        
        # Step 1: Check architecture consistency before migration
        logger.info("Step 1: Checking architecture consistency before migration...")
        self.results["check_before"] = await self.check_architecture_consistency("architecture_consistency_before.md")
        
        if not self.results["check_before"]["success"]:
            logger.error("Architecture consistency check failed. Aborting migration.")
            return self.results
        
        # Step 2: Migrate vector store access
        logger.info("Step 2: Migrating vector store access...")
        self.results["vector_store_migration"] = await self.migrate_vector_store_access()
        
        if not self.results["vector_store_migration"]["success"]:
            logger.error("Vector store migration failed. Aborting migration.")
            return self.results
        
        # Step 3: Check architecture consistency after migration
        logger.info("Step 3: Checking architecture consistency after migration...")
        self.results["check_after"] = await self.check_architecture_consistency("architecture_consistency_after.md")
        
        if not self.results["check_after"]["success"]:
            logger.warning("Architecture consistency check after migration failed.")
        
        # Step 4: Build admin dashboard
        logger.info("Step 4: Building admin dashboard...")
        self.results["admin_dashboard"] = await self.build_admin_dashboard()
        
        if not self.results["admin_dashboard"]["success"]:
            logger.warning("Admin dashboard build failed.")
        
        # Migration completed
        self.results["success"] = (
            self.results["check_before"]["success"] and
            self.results["vector_store_migration"]["success"]
        )
        
        logger.info(f"Architecture migration {'completed successfully' if self.results['success'] else 'failed'}.")
        return self.results
    
    def generate_report(self) -> str:
        """Generate a report of the migration process."""
        report = "# Architecture Migration Report\n\n"
        
        report += "## Summary\n\n"
        report += f"Migration {'completed successfully' if self.results['success'] else 'failed'}.\n\n"
        
        report += "## Steps\n\n"
        
        # Step 1: Check architecture consistency before migration
        report += "### Step 1: Check Architecture Consistency Before Migration\n\n"
        report += f"Status: {'Success' if self.results['check_before']['success'] else 'Failed'}\n\n"
        
        if "report" in self.results["check_before"]:
            report += "Summary of inconsistencies before migration:\n\n"
            report += self.extract_summary_from_report(self.results["check_before"]["report"])
            report += "\n"
        
        # Step 2: Migrate vector store access
        report += "### Step 2: Migrate Vector Store Access\n\n"
        report += f"Status: {'Success' if self.results['vector_store_migration']['success'] else 'Failed'}\n\n"
        
        if "stdout" in self.results["vector_store_migration"]:
            report += "Output:\n\n"
            report += "```\n"
            report += self.results["vector_store_migration"]["stdout"]
            report += "\n```\n\n"
        
        # Step 3: Check architecture consistency after migration
        report += "### Step 3: Check Architecture Consistency After Migration\n\n"
        report += f"Status: {'Success' if self.results['check_after']['success'] else 'Failed'}\n\n"
        
        if "report" in self.results["check_after"]:
            report += "Summary of inconsistencies after migration:\n\n"
            report += self.extract_summary_from_report(self.results["check_after"]["report"])
            report += "\n"
        
        # Step 4: Build admin dashboard
        report += "### Step 4: Build Admin Dashboard\n\n"
        report += f"Status: {'Success' if self.results['admin_dashboard']['success'] else 'Failed'}\n\n"
        
        if "stdout" in self.results["admin_dashboard"]:
            report += "Output:\n\n"
            report += "```\n"
            report += self.results["admin_dashboard"]["stdout"]
            report += "\n```\n\n"
        
        # Comparison of inconsistencies before and after migration
        report += "## Comparison of Inconsistencies\n\n"
        
        if "report" in self.results["check_before"] and "report" in self.results["check_after"]:
            before_inconsistencies = self.extract_inconsistencies_from_report(self.results["check_before"]["report"])
            after_inconsistencies = self.extract_inconsistencies_from_report(self.results["check_after"]["report"])
            
            report += "| Inconsistency Type | Before | After | Difference |\n"
            report += "|-------------------|--------|-------|------------|\n"
            
            for inconsistency_type in before_inconsistencies.keys():
                before_count = before_inconsistencies.get(inconsistency_type, 0)
                after_count = after_inconsistencies.get(inconsistency_type, 0)
                difference = before_count - after_count
                
                report += f"| {inconsistency_type.replace('_', ' ').title()} | {before_count} | {after_count} | {difference} |\n"
        
        # Next steps
        report += "## Next Steps\n\n"
        
        if self.results["success"]:
            report += "1. Review the architecture consistency report after migration to identify any remaining inconsistencies.\n"
            report += "2. Manually fix any remaining inconsistencies.\n"
            report += "3. Use the new deployment script for future deployments: `python deploy_production_mcp.py`\n"
            report += "4. Use the Retool admin dashboard instead of the old UI.\n"
        else:
            report += "1. Review the error messages to identify the cause of the failure.\n"
            report += "2. Fix the issues and run the migration again.\n"
        
        return report
    
    def extract_summary_from_report(self, report: str) -> str:
        """Extract the summary from an architecture consistency report."""
        lines = report.split("\n")
        summary = []
        
        for i, line in enumerate(lines):
            if line.startswith("Scanned") or line.startswith("Found"):
                summary.append(line)
            elif line.startswith("### ") and i + 1 < len(lines) and lines[i + 1].strip():
                summary.append(line)
                summary.append(lines[i + 1])
        
        return "\n".join(summary)
    
    def extract_inconsistencies_from_report(self, report: str) -> Dict[str, int]:
        """Extract the inconsistency counts from an architecture consistency report."""
        inconsistencies = {}
        lines = report.split("\n")
        
        for i, line in enumerate(lines):
            if line.startswith("### "):
                parts = line.split(":")
                if len(parts) == 2:
                    inconsistency_type = parts[0].replace("### ", "").strip().lower()
                    count = int(parts[1].strip())
                    inconsistencies[inconsistency_type] = count
        
        return inconsistencies
    
    async def run(self):
        """Run the migration process and generate a report."""
        await self.run_migration()
        
        report = self.generate_report()
        report_path = os.path.join(self.root_dir, "architecture_migration_report.md")
        
        with open(report_path, 'w') as f:
            f.write(report)
        
        logger.info(f"Migration report written to {report_path}")
        return self.results


async def main():
    """
    Main function to run the architecture migration.
    """
    root_dir = "."
    if len(sys.argv) > 1:
        root_dir = sys.argv[1]
    
    migration = ArchitectureMigration(root_dir)
    results = await migration.run()
    
    print("\n--- Architecture Migration Summary ---")
    print(f"Migration {'completed successfully' if results['success'] else 'failed'}.")
    print("\nSee architecture_migration_report.md for details.")


if __name__ == "__main__":
    asyncio.run(main())
