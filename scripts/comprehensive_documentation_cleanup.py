#!/usr/bin/env python3
"""
Comprehensive Documentation and Script Cleanup for Sophia AI
Removes archived, backup, one-time use documents, and unnecessary scripts
"""

import logging
import shutil
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


class ComprehensiveCleanup:
    """Comprehensive cleanup of documentation and scripts"""

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.root_path = Path(".")
        self.removed_files: List[Path] = []
        self.removed_dirs: List[Path] = []
        self.total_size_freed = 0
        self.cleanup_log = {
            "timestamp": datetime.now().isoformat(),
            "dry_run": dry_run,
            "categories": {}
        }

    def get_cleanup_targets(self) -> Dict[str, List[str]]:
        """Define all cleanup targets"""
        return {
            "archived_docs": [
                # Archive directories
                "docs_archive_*",
                "archive/modernization_*",
                "final_cleanup_backup_*",
                "uv_migration_backups",
                "docs_backup",
                "backups",
                
                # Archived documentation files
                "CLEANUP_REPORT.md",
                "documentation_cleanup_log.json",
                "*_IMPLEMENTATION_SUMMARY.md",
                "*_SUCCESS_SUMMARY.md",
                "*_COMPLETION_REPORT.md",
                "*_ANALYSIS_REPORT.md",
                "corrupted_files.txt",
                "syntax_error_files.txt",
                "syntax_validation_report*.json",
                "optimization_report.json",
                "type_safety_audit_report.json",
            ],
            
            "one_time_reports": [
                # One-time implementation reports
                "CRITICAL_PRIORITY_FIXES_REPORT.md",
                "FINAL_CRITICAL_PRIORITY_SUCCESS_REPORT.md",
                "RUFF_LINTING_COMPREHENSIVE_REPORT.md",
                "MCP_DEEP_ANALYSIS_COMPLETE_SUCCESS_REPORT.md",
                "CRITICAL_COMPLEXITY_REFACTORING_REPORT.md",
                "PHASE1_CRITICAL_REFACTORING_REPORT.md",
                "PHASE3_SYSTEMATIC_REMEDIATION_REPORT.md",
                "UV_CONFLICT_RESOLUTION_REPORT.md",
                "PULUMI_INFRASTRUCTURE_SUCCESS_REPORT.md",
                "COMPREHENSIVE_CODEBASE_CLEANUP_SUMMARY.md",
                "SOPHIA_AI_COMPREHENSIVE_COMPLETION_REPORT.md",
                "MCP_ECOSYSTEM_ENHANCEMENT_SUMMARY.md",
                "PHASE_1_IMPLEMENTATION_SUCCESS_REPORT.md",
                
                # Strategic planning documents (one-time use)
                "SOPHIA_AI_MCP_ECOSYSTEM_ENHANCEMENT_PLAN.md",
                "COMPREHENSIVE_KNOWLEDGE_BASE_IMPLEMENTATION_PLAN.md",
                "SOPHIA_AI_DATA_INGESTION_ANALYSIS_REPORT.md",
                "SOPHIA_SNOWFLAKE_ECOSYSTEM_DEEP_DIVE.md",
                "sophia-ai-compliance-integration-strategy.md",
            ],
            
            "one_time_scripts": [
                # One-time fix scripts
                "fix_github_pulumi_sync_permanently.py",
                "fix_snowflake_connection.py",
                "fix_sql_ansi_compliance.py",
                "run_test_suite.py",
                "test_snowflake_connection.py",
                "configure_github_security.py",
                
                # Deployment scripts (one-time use)
                "scripts/execute_modernization_now.py",
                "scripts/execute_modernization_day1.py",
                "scripts/infrastructure_cleanup_phase1.py",
                "scripts/documentation_cleanup.py",
                "scripts/comprehensive_dead_code_cleanup.py",
                "scripts/fix_undefined_imports.py",
                "scripts/fix_remaining_undefined_names.py",
                "scripts/systematic_quality_improvement.py",
                
                # Test scripts
                "mcp-servers/test_server.py",
                "mcp-servers/hubspot/tests/test_mcp_ticket_conversations.py",
                "mcp-servers/hubspot/tests/test_closed_tickets.py",
                "external/dynamike_snowflake/tests/test_snowflake_conn.py",
            ],
            
            "duplicate_docs": [
                # Documentation duplicates with numbers
                "**/AGNO_*_SUMMARY 2.md",
                "**/AGNO_*_SUMMARY 3.md", 
                "**/AGNO_*_SUMMARY 4.md",
                "**/ARCHITECTURE_REVIEW_SUMMARY 2.md",
                "**/ARCHITECTURE_REVIEW_SUMMARY 3.md",
                "**/ARCHITECTURE_REVIEW_SUMMARY 4.md",
                "**/ENHANCED_ARCHITECTURE_RECOMMENDATIONS 2.md",
                "**/ENHANCED_ARCHITECTURE_RECOMMENDATIONS 3.md",
                "**/AGNO_SOPHIA_INTEGRATION_STRATEGY 2.md",
                "**/AGNO_SOPHIA_INTEGRATION_STRATEGY 3.md",
                "**/CODEBASE_REVIEW_FINAL_SUMMARY 2.md",
                "**/*-dev 2.txt",
                "**/*-dev 3.txt",
                "**/*-dev 4.txt",
                "**/*-dev 5.txt",
            ],
            
            "deprecated_configs": [
                # Deprecated configuration files
                "config/agno_vsa_configuration.yaml",
                "snowflake_connection_fix.patch",
                
                # Log files
                "fastapi.log",
                "fastapi_fixed.log",
                "*.pid",
                "*.lock",
            ],
            
            "empty_directories": [
                # Empty or unused directories
                "backend/watched_costar_files",
                "watched_costar_files",
                "mcp-servers/logs",
                "logs",
            ]
        }

    def get_file_size(self, path: Path) -> int:
        """Get file size safely"""
        try:
            if path.is_file():
                return path.stat().st_size
            elif path.is_dir():
                return sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
            return 0
        except (OSError, PermissionError):
            return 0

    def remove_file(self, file_path: Path, category: str) -> bool:
        """Remove a file and track it"""
        try:
            size = self.get_file_size(file_path)
            
            if self.dry_run:
                logger.info(f"[DRY RUN] Would remove {category}: {file_path}")
                self.removed_files.append(file_path)
                self.total_size_freed += size
                return True
            else:
                file_path.unlink()
                logger.info(f"✅ Removed {category}: {file_path}")
                self.removed_files.append(file_path)
                self.total_size_freed += size
                return True
                
        except Exception as e:
            logger.error(f"❌ Failed to remove {file_path}: {e}")
            return False

    def remove_directory(self, dir_path: Path, category: str) -> bool:
        """Remove a directory and track it"""
        try:
            size = self.get_file_size(dir_path)
            
            if self.dry_run:
                logger.info(f"[DRY RUN] Would remove {category}: {dir_path}/")
                self.removed_dirs.append(dir_path)
                self.total_size_freed += size
                return True
            else:
                shutil.rmtree(dir_path)
                logger.info(f"✅ Removed {category}: {dir_path}/")
                self.removed_dirs.append(dir_path)
                self.total_size_freed += size
                return True
                
        except Exception as e:
            logger.error(f"❌ Failed to remove {dir_path}: {e}")
            return False

    def should_preserve_file(self, file_path: Path) -> bool:
        """Check if file should be preserved"""
        preserve_patterns = [
            # Preserve important documentation
            "README.md",
            "CONTRIBUTING.md", 
            "LICENSE",
            "CHANGELOG.md",
            ".cursorrules",
            
            # Preserve active configuration
            "pyproject.toml",
            "requirements.txt",
            "package.json",
            
            # Preserve current documentation structure
            "docs/README.md",
            "docs/*/README.md",
        ]
        
        file_str = str(file_path)
        for pattern in preserve_patterns:
            if pattern in file_str:
                return True
        
        return False

    def cleanup_category(self, category: str, patterns: List[str]):
        """Clean up a specific category of files"""
        logger.info(f"🧹 Cleaning up {category}...")
        
        removed_count = 0
        category_size = 0
        
        for pattern in patterns:
            # Handle different glob patterns
            if pattern.startswith("**/"):
                matches = list(self.root_path.rglob(pattern[3:]))
            else:
                matches = list(self.root_path.glob(pattern))
            
            for path in matches:
                if self.should_preserve_file(path):
                    logger.info(f"🔒 Preserving: {path}")
                    continue
                    
                if path.is_file():
                    if self.remove_file(path, category):
                        removed_count += 1
                elif path.is_dir():
                    if self.remove_directory(path, category):
                        removed_count += 1
        
        self.cleanup_log["categories"][category] = {
            "removed_count": removed_count,
            "patterns": patterns
        }
        
        logger.info(f"  ✅ {category}: {removed_count} items removed")

    def generate_cleanup_report(self):
        """Generate comprehensive cleanup report"""
        logger.info("📊 Generating cleanup report...")
        
        size_mb = self.total_size_freed / (1024 * 1024)
        
        self.cleanup_log.update({
            "summary": {
                "files_removed": len(self.removed_files),
                "directories_removed": len(self.removed_dirs),
                "total_size_freed_mb": round(size_mb, 2)
            },
            "removed_files": [str(f) for f in self.removed_files],
            "removed_directories": [str(d) for d in self.removed_dirs]
        })
        
        # Save cleanup log
        log_file = Path("comprehensive_cleanup_log.json")
        if not self.dry_run:
            with open(log_file, "w") as f:
                json.dump(self.cleanup_log, f, indent=2)
            logger.info(f"📄 Cleanup log saved to {log_file}")
        
        # Print summary
        logger.info(f"📊 Summary:")
        logger.info(f"  • Files removed: {len(self.removed_files)}")
        logger.info(f"  • Directories removed: {len(self.removed_dirs)}")
        logger.info(f"  • Space freed: {size_mb:.2f} MB")

    def run_comprehensive_cleanup(self):
        """Execute comprehensive cleanup"""
        logger.info("🚀 Starting Comprehensive Documentation & Script Cleanup")
        logger.info("=" * 60)
        
        if self.dry_run:
            logger.info("🔍 DRY RUN MODE - No files will be actually removed")
        else:
            logger.info("⚠️  LIVE MODE - Files will be permanently removed")
        
        # Get cleanup targets
        cleanup_targets = self.get_cleanup_targets()
        
        # Execute cleanup by category
        for category, patterns in cleanup_targets.items():
            self.cleanup_category(category, patterns)
        
        # Generate final report
        self.generate_cleanup_report()
        
        logger.info("🎉 Comprehensive cleanup completed successfully!")
        
        return True


def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Comprehensive Documentation & Script Cleanup")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be removed without actually removing")
    parser.add_argument("--live", action="store_true", help="Actually remove files (use with caution)")
    
    args = parser.parse_args()
    
    if not args.dry_run and not args.live:
        logger.info("Please specify either --dry-run or --live")
        return
    
    if args.live:
        response = input("⚠️  This will permanently remove files. Are you sure? (yes/no): ")
        if response.lower() != "yes":
            logger.info("Cleanup cancelled.")
            return
    
    cleanup = ComprehensiveCleanup(dry_run=args.dry_run)
    cleanup.run_comprehensive_cleanup()


if __name__ == "__main__":
    main() 