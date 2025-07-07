#!/usr/bin/env python3
"""
Comprehensive Archive Cleanup System
Safely removes archived, legacy, and deprecated files from Sophia AI codebase
"""

import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional


class ArchiveCleanupSystem:
    """Comprehensive system for cleaning up archived and legacy files"""
    
    def __init__(self, repo_root: Path = None):
        self.repo_root = repo_root or Path.cwd()
        self.cleanup_report = {
            "timestamp": datetime.utcnow().isoformat(),
            "total_files_analyzed": 0,
            "total_size_analyzed": 0,
            "files_to_delete": [],
            "directories_to_delete": [],
            "preserved_files": [],
            "safety_checks": [],
            "cleanup_summary": {}
        }
        
        # Define patterns for archived/legacy content
        self.archive_patterns = {
            "directories": [
                "*archive*", "*backup*", "*legacy*", "*deprecated*", 
                "*old*", "*temp*", "*tmp*", "docs_backup_*"
            ],
            "files": [
                "*.backup", "*.bak", "*_backup_*", "*_old", 
                "*_deprecated", "*_legacy", "*.tmp", "*.temp"
            ]
        }
        
        # Critical files/directories to preserve
        self.preserve_patterns = {
            "directories": [
                ".git", "node_modules", "venv", ".venv", "__pycache__",
                "backend/services", "frontend", "infrastructure", "scripts"
            ],
            "files": [
                "README.md", "requirements.txt", "package.json", 
                "pyproject.toml", ".gitignore", ".env*"
            ]
        }
        
        # Files that are safe to delete (confirmed obsolete)
        self.safe_delete_targets = {
            "large_archives": [
                "docs_backup_20250705_112838",  # 3.3M - old documentation backup
                "backups",                       # 1.8M - general backup directory
                "cleanup_backup_20250706_180710", # 612K - cleanup backup
                "backup_deployment_fix_20250705_135353", # 444K - deployment fix backup
                "backup_deployment_cleanup_20250707_001424", # 76K - recent deployment backup
            ],
            "archived_dockerfiles": [
                "archived_dockerfiles",  # 32K - old Docker configurations
            ],
            "archived_services": [
                "backend/services/_archived_chat_services",  # 56K - archived chat services
                "archived_fastapi_apps",  # 12K - old FastAPI apps
            ],
            "backup_configs": [
                "backup_compose_files",  # 92K - backup Docker compose files
            ],
            "individual_backups": [
                "backend/services/unified_llm_service.py.backup",
                "config/cursor_enhanced_mcp_config.json.backup",
                "config/unified_mcp_config.json.backup",
            ]
        }
    
    def scan_archived_content(self) -> Dict[str, List[Path]]:
        """Scan for all archived and legacy content"""
        print("🔍 Scanning for archived and legacy content...")
        
        archived_content = {
            "directories": [],
            "files": [],
            "large_files": [],
            "recent_backups": []
        }
        
        # Find archived directories
        for pattern in self.archive_patterns["directories"]:
            for path in self.repo_root.glob(f"**/{pattern}"):
                if path.is_dir() and not self._is_preserved(path):
                    archived_content["directories"].append(path)
        
        # Find archived files
        for pattern in self.archive_patterns["files"]:
            for path in self.repo_root.glob(f"**/{pattern}"):
                if path.is_file() and not self._is_preserved(path):
                    archived_content["files"].append(path)
        
        # Find large files that might be archives
        for path in self.repo_root.rglob("*"):
            if path.is_file() and path.stat().st_size > 1024 * 1024:  # > 1MB
                if any(keyword in str(path).lower() for keyword in ["backup", "archive", "old", "deprecated"]):
                    archived_content["large_files"].append(path)
        
        # Find recent backups (last 30 days)
        cutoff_time = datetime.now().timestamp() - (30 * 24 * 3600)
        for path in archived_content["directories"] + archived_content["files"]:
            if path.stat().st_mtime > cutoff_time:
                archived_content["recent_backups"].append(path)
        
        return archived_content
    
    def _is_preserved(self, path: Path) -> bool:
        """Check if a path should be preserved"""
        path_str = str(path.relative_to(self.repo_root))
        
        # Check preserve patterns
        for pattern in self.preserve_patterns["directories"]:
            if pattern in path_str:
                return True
        
        for pattern in self.preserve_patterns["files"]:
            if path.name == pattern or path.match(pattern):
                return True
        
        return False
    
    def analyze_dependencies(self, archived_content: Dict[str, List[Path]]) -> Dict[str, List[str]]:
        """Analyze dependencies and references to archived content"""
        print("🔗 Analyzing dependencies and references...")
        
        dependencies = {
            "import_references": [],
            "file_references": [],
            "config_references": [],
            "safe_to_delete": []
        }
        
        all_archived_paths = (
            archived_content["directories"] + 
            archived_content["files"] + 
            archived_content["large_files"]
        )
        
        for archived_path in all_archived_paths:
            path_name = archived_path.name
            relative_path = str(archived_path.relative_to(self.repo_root))
            
            # Check for import references
            try:
                result = subprocess.run([
                    "grep", "-r", f"from.*{path_name}\\|import.*{path_name}", 
                    "--include=*.py", str(self.repo_root)
                ], capture_output=True, text=True)
                
                if result.returncode == 0 and result.stdout.strip():
                    # Filter out references within archived directories themselves
                    refs = [line for line in result.stdout.split('\n') 
                           if line and not any(arch in line for arch in ["archive", "backup", "deprecated"])]
                    if refs:
                        dependencies["import_references"].append(f"{relative_path}: {len(refs)} references")
                
            except Exception:
                pass
            
            # Check for file path references
            try:
                result = subprocess.run([
                    "grep", "-r", relative_path, 
                    "--include=*.py", "--include=*.yml", "--include=*.yaml", 
                    "--include=*.json", str(self.repo_root)
                ], capture_output=True, text=True)
                
                if result.returncode == 0 and result.stdout.strip():
                    refs = [line for line in result.stdout.split('\n') 
                           if line and not any(arch in line for arch in ["archive", "backup", "deprecated"])]
                    if refs:
                        dependencies["file_references"].append(f"{relative_path}: {len(refs)} references")
                
            except Exception:
                pass
        
        # Identify safe-to-delete items (no active references)
        for category, paths in self.safe_delete_targets.items():
            for path_pattern in paths:
                matching_paths = [p for p in all_archived_paths 
                                if path_pattern in str(p.relative_to(self.repo_root))]
                for path in matching_paths:
                    relative_path = str(path.relative_to(self.repo_root))
                    if (relative_path not in [ref.split(':')[0] for ref in dependencies["import_references"]] and
                        relative_path not in [ref.split(':')[0] for ref in dependencies["file_references"]]):
                        dependencies["safe_to_delete"].append(relative_path)
        
        return dependencies
    
    def calculate_cleanup_impact(self, archived_content: Dict[str, List[Path]]) -> Dict[str, any]:
        """Calculate the impact of cleanup operations"""
        print("📊 Calculating cleanup impact...")
        
        impact = {
            "total_files": 0,
            "total_directories": 0,
            "total_size_bytes": 0,
            "total_size_human": "",
            "by_category": {},
            "largest_items": []
        }
        
        all_items = []
        
        # Process all archived content
        for category, items in archived_content.items():
            category_size = 0
            category_count = 0
            
            for item in items:
                try:
                    if item.is_dir():
                        size = sum(f.stat().st_size for f in item.rglob('*') if f.is_file())
                        impact["total_directories"] += 1
                    else:
                        size = item.stat().st_size
                        impact["total_files"] += 1
                    
                    category_size += size
                    category_count += 1
                    
                    all_items.append({
                        "path": str(item.relative_to(self.repo_root)),
                        "size": size,
                        "type": "directory" if item.is_dir() else "file"
                    })
                    
                except (OSError, PermissionError):
                    continue
            
            impact["by_category"][category] = {
                "count": category_count,
                "size_bytes": category_size,
                "size_human": self._format_size(category_size)
            }
            
            impact["total_size_bytes"] += category_size
        
        impact["total_size_human"] = self._format_size(impact["total_size_bytes"])
        
        # Find largest items
        impact["largest_items"] = sorted(all_items, key=lambda x: x["size"], reverse=True)[:10]
        for item in impact["largest_items"]:
            item["size_human"] = self._format_size(item["size"])
        
        return impact
    
    def _format_size(self, size_bytes: int) -> str:
        """Format size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f}{unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f}TB"
    
    def generate_cleanup_plan(self, archived_content: Dict[str, List[Path]], 
                            dependencies: Dict[str, List[str]], 
                            impact: Dict[str, any]) -> Dict[str, any]:
        """Generate comprehensive cleanup plan"""
        print("📋 Generating cleanup plan...")
        
        plan = {
            "immediate_deletion": [],
            "careful_review": [],
            "preserve": [],
            "total_space_recovery": 0,
            "safety_recommendations": []
        }
        
        # Items safe for immediate deletion
        for safe_path in dependencies["safe_to_delete"]:
            full_path = self.repo_root / safe_path
            if full_path.exists():
                try:
                    if full_path.is_dir():
                        size = sum(f.stat().st_size for f in full_path.rglob('*') if f.is_file())
                    else:
                        size = full_path.stat().st_size
                    
                    plan["immediate_deletion"].append({
                        "path": safe_path,
                        "size": size,
                        "size_human": self._format_size(size),
                        "reason": "No active references found"
                    })
                    plan["total_space_recovery"] += size
                    
                except (OSError, PermissionError):
                    continue
        
        # Items requiring careful review
        referenced_items = set()
        for ref in dependencies["import_references"] + dependencies["file_references"]:
            path = ref.split(':')[0]
            referenced_items.add(path)
        
        for item_list in archived_content.values():
            for item in item_list:
                relative_path = str(item.relative_to(self.repo_root))
                if relative_path in referenced_items:
                    plan["careful_review"].append({
                        "path": relative_path,
                        "reason": "Has active references - manual review needed"
                    })
        
        # Safety recommendations
        plan["safety_recommendations"] = [
            "Create full repository backup before deletion",
            "Test deployment after cleanup",
            "Review Git history for any missed references",
            "Update .gitignore to prevent future archive accumulation",
            "Implement automated cleanup in CI/CD pipeline"
        ]
        
        return plan
    
    def execute_cleanup(self, cleanup_plan: Dict[str, any], dry_run: bool = True) -> Dict[str, any]:
        """Execute the cleanup plan"""
        action = "DRY RUN" if dry_run else "EXECUTING"
        print(f"🧹 {action} cleanup plan...")
        
        results = {
            "deleted_items": [],
            "failed_deletions": [],
            "space_recovered": 0,
            "errors": []
        }
        
        for item in cleanup_plan["immediate_deletion"]:
            item_path = self.repo_root / item["path"]
            
            try:
                if not dry_run:
                    if item_path.is_dir():
                        shutil.rmtree(item_path)
                    else:
                        item_path.unlink()
                
                results["deleted_items"].append(item["path"])
                results["space_recovered"] += item["size"]
                
                print(f"{'[DRY RUN] Would delete' if dry_run else 'Deleted'}: {item['path']} ({item['size_human']})")
                
            except Exception as e:
                error_msg = f"Failed to delete {item['path']}: {str(e)}"
                results["failed_deletions"].append(item["path"])
                results["errors"].append(error_msg)
                print(f"❌ {error_msg}")
        
        return results
    
    def update_gitignore(self) -> bool:
        """Update .gitignore to prevent future archive accumulation"""
        gitignore_path = self.repo_root / ".gitignore"
        
        archive_patterns = [
            "# Archive and backup directories",
            "**/archive/",
            "**/backup*/",
            "**/legacy/",
            "**/deprecated/",
            "**/*_backup_*/",
            "docs_backup_*/",
            "",
            "# Backup files",
            "*.backup",
            "*.bak",
            "*_old",
            "*_deprecated",
            "*_legacy",
            "*.tmp",
            "*.temp"
        ]
        
        try:
            if gitignore_path.exists():
                content = gitignore_path.read_text()
                if "# Archive and backup directories" not in content:
                    with open(gitignore_path, 'a') as f:
                        f.write("\n\n" + "\n".join(archive_patterns))
                    return True
            else:
                gitignore_path.write_text("\n".join(archive_patterns))
                return True
        except Exception as e:
            print(f"❌ Failed to update .gitignore: {e}")
            return False
        
        return False
    
    def generate_report(self, archived_content: Dict[str, List[Path]], 
                       dependencies: Dict[str, List[str]], 
                       impact: Dict[str, any], 
                       cleanup_plan: Dict[str, any], 
                       execution_results: Dict[str, any] = None) -> Dict[str, any]:
        """Generate comprehensive cleanup report"""
        
        report = {
            "metadata": {
                "timestamp": datetime.utcnow().isoformat(),
                "repository": str(self.repo_root),
                "scan_summary": {
                    "total_archived_directories": len(archived_content.get("directories", [])),
                    "total_archived_files": len(archived_content.get("files", [])),
                    "total_large_files": len(archived_content.get("large_files", [])),
                    "recent_backups": len(archived_content.get("recent_backups", []))
                }
            },
            "impact_analysis": impact,
            "dependency_analysis": dependencies,
            "cleanup_plan": cleanup_plan,
            "execution_results": execution_results,
            "recommendations": [
                "Implement automated cleanup in CI/CD pipeline",
                "Set up monitoring for archive accumulation",
                "Establish retention policies for backups",
                "Use Git for version control instead of manual backups",
                "Implement proper deployment rollback mechanisms"
            ]
        }
        
        return report
    
    def run_comprehensive_cleanup(self, dry_run: bool = True) -> Dict[str, any]:
        """Run complete cleanup analysis and execution"""
        print("🚀 Starting comprehensive archive cleanup...")
        print(f"Repository: {self.repo_root}")
        print(f"Mode: {'DRY RUN' if dry_run else 'LIVE EXECUTION'}")
        print("-" * 60)
        
        # Step 1: Scan archived content
        archived_content = self.scan_archived_content()
        
        # Step 2: Analyze dependencies
        dependencies = self.analyze_dependencies(archived_content)
        
        # Step 3: Calculate impact
        impact = self.calculate_cleanup_impact(archived_content)
        
        # Step 4: Generate cleanup plan
        cleanup_plan = self.generate_cleanup_plan(archived_content, dependencies, impact)
        
        # Step 5: Execute cleanup
        execution_results = self.execute_cleanup(cleanup_plan, dry_run)
        
        # Step 6: Update .gitignore
        if not dry_run:
            gitignore_updated = self.update_gitignore()
            execution_results["gitignore_updated"] = gitignore_updated
        
        # Step 7: Generate report
        report = self.generate_report(
            archived_content, dependencies, impact, 
            cleanup_plan, execution_results
        )
        
        return report


def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Comprehensive Archive Cleanup System")
    parser.add_argument("--execute", action="store_true", 
                       help="Execute cleanup (default is dry run)")
    parser.add_argument("--repo-path", type=str, default=".", 
                       help="Repository path (default: current directory)")
    parser.add_argument("--output", type=str, default="archive_cleanup_report.json",
                       help="Output report file")
    
    args = parser.parse_args()
    
    # Initialize cleanup system
    repo_path = Path(args.repo_path).resolve()
    cleanup_system = ArchiveCleanupSystem(repo_path)
    
    try:
        # Run cleanup
        report = cleanup_system.run_comprehensive_cleanup(dry_run=not args.execute)
        
        # Save report
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 CLEANUP SUMMARY")
        print("=" * 60)
        
        if report["execution_results"]:
            results = report["execution_results"]
            print(f"Items processed: {len(results['deleted_items'])}")
            print(f"Space recovered: {cleanup_system._format_size(results['space_recovered'])}")
            print(f"Failed deletions: {len(results['failed_deletions'])}")
            
            if results["errors"]:
                print("\n❌ Errors encountered:")
                for error in results["errors"]:
                    print(f"   {error}")
        
        impact = report["impact_analysis"]
        print(f"\nTotal archived content: {impact['total_size_human']}")
        print(f"Files: {impact['total_files']}, Directories: {impact['total_directories']}")
        
        print(f"\n📄 Full report saved to: {args.output}")
        
        if args.execute:
            print("\n✅ Cleanup execution completed!")
        else:
            print("\n🔍 Dry run completed. Use --execute to perform actual cleanup.")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

