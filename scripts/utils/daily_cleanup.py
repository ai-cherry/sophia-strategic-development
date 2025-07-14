#!/usr/bin/env python3
"""
Daily Technical Debt Prevention
Runs automatically via GitHub Actions to prevent accumulation of dead code
"""

import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DailyCleanup:
    def __init__(self):
        self.base_path = Path(".")
        self.cleanup_log = []
        self.warnings = []
        
        # Forbidden directory patterns
        self.forbidden_dirs = [
            "archive", "backup", "_archived", "old", "deprecated",
            "migration_backup", "temp", "draft", "obsolete"
        ]
        
        # Forbidden file patterns
        self.forbidden_files = [
            "*.backup", "*.bak", "*.old", "*.tmp", "*.temp",
            "*.orig", "*.swp", "*.swo", "*~"
        ]
        
        # Protected directories (never clean)
        self.protected_dirs = {
            ".git", ".venv", "node_modules", "external",
            "frontend/node_modules", "infrastructure/node_modules"
        }
    
    def cleanup_one_time_scripts(self) -> int:
        """Remove one-time scripts older than 30 days"""
        logger.info("🔧 Checking one-time scripts...")
        
        one_time_dir = self.base_path / "scripts" / "one_time"
        if not one_time_dir.exists():
            logger.info("📁 Creating scripts/one_time/ directory")
            one_time_dir.mkdir(parents=True, exist_ok=True)
            
            # Create README for one-time scripts
            readme_content = '''# One-Time Scripts Directory

🚨 **CRITICAL RULES:**
1. All scripts in this directory are AUTOMATICALLY DELETED after 30 days
2. Add deletion date to filename: `script_name_DELETE_2025_08_15.py`
3. Include deletion reminder in script header
4. Use for: deployments, migrations, fixes, tests, setups

✅ **PERMANENT SCRIPTS GO IN:**
- `scripts/utils/` (reusable utilities)
- `scripts/monitoring/` (ongoing monitoring)  
- `scripts/maintenance/` (regular maintenance)

## Example One-Time Script Header:
```python
#!/usr/bin/env python3
"""
One-time script: Fix authentication issue
DELETE AFTER: 2025-08-15
Created: 2025-07-13
Purpose: Fix specific auth bug in production
"""
```
'''
            with open(one_time_dir / "README.md", 'w') as f:
                f.write(readme_content)
            
            return 0
        
        deleted_count = 0
        cutoff_date = datetime.now() - timedelta(days=30)
        
        for script in one_time_dir.glob("*.py"):
            # Check if script has deletion date in name
            if "DELETE_" in script.name:
                try:
                    date_str = script.name.split("DELETE_")[1].split(".")[0]
                    delete_date = datetime.strptime(date_str, "%Y_%m_%d")
                    
                    if datetime.now() > delete_date:
                        script.unlink()
                        self.cleanup_log.append(f"Deleted expired script: {script}")
                        logger.info(f"🗑️  Deleted expired script: {script.name}")
                        deleted_count += 1
                except Exception as e:
                    logger.warning(f"⚠️  Could not parse deletion date from {script.name}: {e}")
            
            # Check if script is older than 30 days without deletion date
            elif script.stat().st_mtime < cutoff_date.timestamp():
                self.warnings.append(f"Old script without deletion date: {script}")
                logger.warning(f"⚠️  Old script needs deletion date: {script.name}")
        
        return deleted_count
    
    def prevent_archive_directories(self) -> int:
        """Prevent creation of archive directories"""
        logger.info("📁 Checking for forbidden archive directories...")
        
        removed_count = 0
        
        for forbidden in self.forbidden_dirs:
            for path in self.base_path.rglob(forbidden):
                if self._is_safe_to_remove(path) and path.is_dir():
                    # Only remove if empty
                    if len(list(path.iterdir())) == 0:
                        path.rmdir()
                        self.cleanup_log.append(f"Removed empty forbidden dir: {path}")
                        logger.info(f"🗑️  Removed empty forbidden directory: {path}")
                        removed_count += 1
                    else:
                        self.warnings.append(f"Non-empty forbidden directory: {path}")
                        logger.warning(f"⚠️  Non-empty forbidden directory: {path}")
        
        return removed_count
    
    def cleanup_backup_files(self) -> int:
        """Remove backup files"""
        logger.info("💾 Checking for backup files...")
        
        removed_count = 0
        
        for pattern in self.forbidden_files:
            for file_path in self.base_path.rglob(pattern):
                if self._is_safe_to_remove(file_path) and file_path.is_file():
                    file_path.unlink()
                    self.cleanup_log.append(f"Removed backup file: {file_path}")
                    logger.info(f"🗑️  Removed backup file: {file_path}")
                    removed_count += 1
        
        return removed_count
    
    def check_documentation_freshness(self) -> int:
        """Flag stale documentation for review"""
        logger.info("📄 Checking documentation freshness...")
        
        stale_count = 0
        stale_cutoff = datetime.now() - timedelta(days=90)
        
        # Keywords that indicate temporary documentation
        temp_keywords = [
            "implementation", "plan", "strategy", "migration", "deployment",
            "guide", "setup", "install", "fix", "complete", "final", "summary"
        ]
        
        for doc in self.base_path.rglob("*.md"):
            if self._is_safe_to_remove(doc):
                doc_name_lower = doc.name.lower()
                
                # Check if it's temporary documentation
                if any(keyword in doc_name_lower for keyword in temp_keywords):
                    mod_time = datetime.fromtimestamp(doc.stat().st_mtime)
                    
                    if mod_time < stale_cutoff:
                        self.warnings.append(f"Stale documentation: {doc} (modified {mod_time.strftime('%Y-%m-%d')})")
                        logger.warning(f"📄 Stale documentation: {doc}")
                        stale_count += 1
        
        return stale_count
    
    def check_large_files(self) -> int:
        """Check for unexpectedly large files"""
        logger.info("📏 Checking for large files...")
        
        large_files = 0
        size_limit = 10 * 1024 * 1024  # 10MB
        
        for file_path in self.base_path.rglob("*"):
            if (file_path.is_file() and 
                self._is_safe_to_remove(file_path) and 
                file_path.stat().st_size > size_limit):
                
                size_mb = file_path.stat().st_size / (1024 * 1024)
                self.warnings.append(f"Large file: {file_path} ({size_mb:.1f}MB)")
                logger.warning(f"📏 Large file: {file_path} ({size_mb:.1f}MB)")
                large_files += 1
        
        return large_files
    
    def _is_safe_to_remove(self, path: Path) -> bool:
        """Check if path is safe to remove"""
        path_str = str(path)
        
        # Skip protected directories
        for protected in self.protected_dirs:
            if protected in path_str:
                return False
        
        # Skip if in external or node_modules
        if ("external/" in path_str or 
            "node_modules/" in path_str or 
            ".venv/" in path_str or
            ".git/" in path_str):
            return False
        
        return True
    
    def generate_report(self) -> Dict:
        """Generate cleanup report"""
        return {
            "timestamp": datetime.now().isoformat(),
            "cleanup_actions": len(self.cleanup_log),
            "warnings": len(self.warnings),
            "actions": self.cleanup_log,
            "warnings_list": self.warnings
        }
    
    def run_daily_cleanup(self) -> Dict:
        """Run all daily cleanup tasks"""
        logger.info("🚀 Starting daily technical debt prevention...")
        
        # Run cleanup tasks
        scripts_deleted = self.cleanup_one_time_scripts()
        dirs_removed = self.prevent_archive_directories()
        backups_removed = self.cleanup_backup_files()
        stale_docs = self.check_documentation_freshness()
        large_files = self.check_large_files()
        
        # Generate summary
        summary = {
            "scripts_deleted": scripts_deleted,
            "directories_removed": dirs_removed,
            "backup_files_removed": backups_removed,
            "stale_documentation": stale_docs,
            "large_files_detected": large_files,
            "total_actions": len(self.cleanup_log),
            "total_warnings": len(self.warnings)
        }
        
        logger.info(f"✅ Daily cleanup complete: {summary}")
        
        return {
            "summary": summary,
            "details": self.generate_report()
        }

def main():
    """Execute daily cleanup"""
    cleanup = DailyCleanup()
    result = cleanup.run_daily_cleanup()
    
    # Print summary
    print("\n🧹 Daily Technical Debt Prevention Summary")
    print("=" * 50)
    
    summary = result["summary"]
    print(f"Scripts deleted: {summary['scripts_deleted']}")
    print(f"Directories removed: {summary['directories_removed']}")
    print(f"Backup files removed: {summary['backup_files_removed']}")
    print(f"Stale docs detected: {summary['stale_documentation']}")
    print(f"Large files detected: {summary['large_files_detected']}")
    print(f"Total actions: {summary['total_actions']}")
    print(f"Total warnings: {summary['total_warnings']}")
    
    # Show warnings if any
    if result["details"]["warnings_list"]:
        print(f"\n⚠️  Warnings ({len(result['details']['warnings_list'])}):")
        for warning in result["details"]["warnings_list"][:10]:  # Show first 10
            print(f"  - {warning}")
        if len(result["details"]["warnings_list"]) > 10:
            print(f"  ... and {len(result['details']['warnings_list']) - 10} more")
    
    # Show actions if any
    if result["details"]["actions"]:
        print(f"\n✅ Actions taken ({len(result['details']['actions'])}):")
        for action in result["details"]["actions"][:10]:  # Show first 10
            print(f"  - {action}")
        if len(result["details"]["actions"]) > 10:
            print(f"  ... and {len(result['details']['actions']) - 10} more")
    
    if summary['total_actions'] == 0 and summary['total_warnings'] == 0:
        print("\n🎉 Repository is clean! No technical debt detected.")
    
    return result

if __name__ == "__main__":
    main() 