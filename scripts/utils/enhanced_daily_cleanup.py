#!/usr/bin/env python3
"""
Enhanced Daily Technical Debt Prevention with Clean by Design Audit
Runs automatically via GitHub Actions to prevent accumulation of dead code
Now includes: dry-run mode, MCP duplicate detection, .env leak scanning, Slack alerts
"""

import os
import shutil
import json
import re
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Set, Optional
import logging
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedDailyCleanup:
    def __init__(self):
        self.base_path = Path(".")
        self.cleanup_log = []
        self.warnings = []
        self.dry_run = os.getenv('DRY_RUN', 'false').lower() == 'true'
        self.scan_report = {
            "timestamp": datetime.now().isoformat(),
            "dry_run": self.dry_run,
            "findings": {
                "one_time_scripts": [],
                "archive_directories": [],
                "backup_files": [],
                "stale_documentation": [],
                "large_files": [],
                "mcp_duplicates": [],
                "env_leaks": []
            },
            "metrics": {
                "total_size_to_remove": 0,
                "total_files_to_remove": 0,
                "total_dirs_to_remove": 0
            }
        }
        
        # Forbidden directory patterns
        self.forbidden_dirs = [
            "archive", "backup", "_archived", "old", "deprecated",
            "migration_backup", "temp", "draft", "obsolete", "cleanup_backup"
        ]
        
        # Forbidden file patterns
        self.forbidden_files = [
            "*.backup", "*.bak", "*.old", "*.tmp", "*.temp",
            "*.orig", "*.swp", "*.swo", "*~", "*.pyc", "__pycache__"
        ]
        
        # Protected directories (never clean)
        self.protected_dirs = {
            ".git", ".venv", "node_modules", "external",
            "frontend/node_modules", "infrastructure/node_modules",
            "npm-mcp-servers/node_modules", "uv.lock", ".python-version"
        }
        
        # Secret patterns for .env leak detection
        self.secret_patterns = [
            r'(?i)(api_key|api-key|apikey)\s*[=:]\s*[\'""]?([a-zA-Z0-9_\-]{20,})[\'""]?',
            r'(?i)(secret|token|password|passwd|pwd)\s*[=:]\s*[\'""]?([a-zA-Z0-9_\-!@#$%^&*()]{8,})[\'""]?',
            r'(?i)bearer\s+[a-zA-Z0-9_\-\.]{20,}',
            r'sk-[a-zA-Z0-9]{48}',  # OpenAI
            r'sk-ant-[a-zA-Z0-9\-]{40,}',  # Anthropic
            r'pul-[a-f0-9]{40}',  # Pulumi
            r'ghp_[a-zA-Z0-9]{36}',  # GitHub PAT
            r'ghs_[a-zA-Z0-9]{36}',  # GitHub Secret
            r'pcsk_[a-zA-Z0-9_]{40,}',  # Pinecone
            r'xoxb-[0-9]{10,13}-[0-9]{10,13}-[a-zA-Z0-9]{24}',  # Slack
            r'(?i)(aws_access_key_id|aws_secret_access_key)\s*[=:]\s*[\'""]?([a-zA-Z0-9/+=]{20,})[\'""]?',
        ]
        
        # MCP configuration
        self.mcp_config_path = self.base_path / "config" / "consolidated_mcp_ports.json"
        self.mcp_servers_dir = self.base_path / "mcp-servers"
    
    def get_file_size(self, path: Path) -> int:
        """Get file or directory size in bytes"""
        if path.is_file():
            return path.stat().st_size
        elif path.is_dir():
            total = 0
            for item in path.rglob('*'):
                if item.is_file():
                    total += item.stat().st_size
            return total
        return 0
    
    def cleanup_one_time_scripts(self) -> int:
        """Remove one-time scripts older than 30 days"""
        logger.info("🔧 Checking one-time scripts...")
        
        one_time_dir = self.base_path / "scripts" / "one_time"
        if not one_time_dir.exists():
            logger.info("📁 Creating scripts/one_time/ directory")
            if not self.dry_run:
                one_time_dir.mkdir(parents=True, exist_ok=True)
                # Create README
                readme_content = '''# One-Time Scripts Directory

🚨 **CRITICAL RULES:**
1. All scripts in this directory are AUTOMATICALLY DELETED after 30 days
2. Add deletion date to filename: `script_name_DELETE_2025_08_15.py`
3. Include deletion reminder in script header

✅ **PERMANENT SCRIPTS GO IN:**
- `scripts/utils/` (reusable utilities)
- `scripts/monitoring/` (ongoing monitoring)  
- `scripts/maintenance/` (regular maintenance)
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
                        size = self.get_file_size(script)
                        self.scan_report["findings"]["one_time_scripts"].append({
                            "path": str(script),
                            "reason": f"Expired on {delete_date.strftime('%Y-%m-%d')}",
                            "size": size
                        })
                        self.scan_report["metrics"]["total_size_to_remove"] += size
                        self.scan_report["metrics"]["total_files_to_remove"] += 1
                        
                        if not self.dry_run:
                            script.unlink()
                            self.cleanup_log.append(f"Deleted expired script: {script}")
                            logger.info(f"🗑️  Deleted expired script: {script.name}")
                        else:
                            logger.info(f"🚫 Dry-run: Would delete expired script: {script.name}")
                        deleted_count += 1
                except Exception as e:
                    logger.warning(f"⚠️  Could not parse deletion date from {script.name}: {e}")
            
            # Check if script is older than 30 days without deletion date
            elif script.stat().st_mtime < cutoff_date.timestamp():
                self.warnings.append(f"Old script without deletion date: {script}")
                logger.warning(f"⚠️  Old script needs deletion date: {script.name}")
        
        return deleted_count
    
    def scan_mcp_duplicates(self) -> List[Dict]:
        """Scan for MCP server duplicates based on consolidated configuration"""
        logger.info("🔍 Scanning for MCP server duplicates...")
        
        duplicates = []
        
        if not self.mcp_config_path.exists():
            logger.warning(f"⚠️  MCP config not found at {self.mcp_config_path}")
            return duplicates
        
        try:
            with open(self.mcp_config_path) as f:
                mcp_config = json.load(f)
            
            # Get list of active servers from config
            active_servers = set(mcp_config.get("active_servers", {}).keys())
            removed_servers = set(mcp_config.get("removed_servers", []))
            
            # Check each directory in mcp-servers
            if self.mcp_servers_dir.exists():
                for server_dir in self.mcp_servers_dir.iterdir():
                    if server_dir.is_dir() and not server_dir.name.startswith('__'):
                        # Check if it's a removed server
                        if server_dir.name in removed_servers:
                            size = self.get_file_size(server_dir)
                            duplicates.append({
                                "path": str(server_dir),
                                "reason": "Server marked as removed in consolidated config",
                                "type": "removed_server",
                                "size": size
                            })
                            self.scan_report["metrics"]["total_size_to_remove"] += size
                            self.scan_report["metrics"]["total_dirs_to_remove"] += 1
                        
                        # Check for duplicates by port conflicts
                        # Get all ports used
                        ports_used = {}
                        for category in ["active_servers", "unified_mcp_servers"]:
                            if category == "active_servers":
                                for name, port in mcp_config.get(category, {}).items():
                                    if name not in ports_used:
                                        ports_used[port] = name
                            elif category == "unified_mcp_servers":
                                for tier in mcp_config.get(category, {}).values():
                                    if isinstance(tier, dict):
                                        for server_info in tier.values():
                                            if isinstance(server_info, dict) and "port" in server_info:
                                                port = server_info["port"]
                                                name = server_info.get("name", "unknown")
                                                if port not in ports_used:
                                                    ports_used[port] = name
                        
                        # Check for v2 duplicates (e.g., ai_memory and ai_memory_v2)
                        base_name = server_dir.name.replace("_v2", "").replace("_unified", "")
                        for other_dir in self.mcp_servers_dir.iterdir():
                            if other_dir.is_dir() and other_dir != server_dir:
                                other_base = other_dir.name.replace("_v2", "").replace("_unified", "")
                                if base_name == other_base and server_dir.name != other_dir.name:
                                    # This is a potential duplicate
                                    size = self.get_file_size(server_dir)
                                    duplicates.append({
                                        "path": str(server_dir),
                                        "reason": f"Potential duplicate of {other_dir.name}",
                                        "type": "version_duplicate",
                                        "size": size
                                    })
            
            self.scan_report["findings"]["mcp_duplicates"] = duplicates
            
        except Exception as e:
            logger.error(f"❌ Error scanning MCP duplicates: {e}")
        
        return duplicates
    
    def scan_env_leaks(self) -> List[Dict]:
        """Scan for potential secret leaks in files"""
        logger.info("🔐 Scanning for potential .env leaks...")
        
        leaks = []
        files_to_scan = []
        
        # Patterns for files likely to contain secrets
        risky_patterns = ["*.env", "*.env.*", "config*.json", "settings*.py", 
                         "*.yml", "*.yaml", "*.sh", "*.js", "*.ts", "*.py"]
        
        # Collect files to scan
        for pattern in risky_patterns:
            for file_path in self.base_path.rglob(pattern):
                if (file_path.is_file() and 
                    self._is_safe_to_scan(file_path) and 
                    file_path.stat().st_size < 1024 * 1024):  # Skip files > 1MB
                    files_to_scan.append(file_path)
        
        # Scan files for secrets
        for file_path in files_to_scan:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                found_secrets = []
                for pattern in self.secret_patterns:
                    matches = re.findall(pattern, content)
                    if matches:
                        # Hash the secret for reporting without exposing it
                        for match in matches:
                            secret_value = match[1] if isinstance(match, tuple) else match
                            if len(str(secret_value)) > 8:  # Only flag substantial secrets
                                secret_hash = hashlib.sha256(str(secret_value).encode()).hexdigest()[:8]
                                found_secrets.append(f"Pattern: {pattern.split('(')[0]}..., Hash: {secret_hash}")
                
                if found_secrets:
                    leaks.append({
                        "path": str(file_path),
                        "patterns_found": found_secrets,
                        "size": file_path.stat().st_size
                    })
                    
            except Exception as e:
                logger.debug(f"Could not scan {file_path}: {e}")
        
        self.scan_report["findings"]["env_leaks"] = leaks
        return leaks
    
    def prevent_archive_directories(self) -> int:
        """Prevent creation of archive directories"""
        logger.info("📁 Checking for forbidden archive directories...")
        
        removed_count = 0
        
        for forbidden in self.forbidden_dirs:
            for path in self.base_path.rglob(f"*{forbidden}*"):
                if self._is_safe_to_remove(path) and path.is_dir():
                    size = self.get_file_size(path)
                    empty = len(list(path.iterdir())) == 0
                    
                    self.scan_report["findings"]["archive_directories"].append({
                        "path": str(path),
                        "empty": empty,
                        "size": size,
                        "pattern": forbidden
                    })
                    
                    if empty:
                        self.scan_report["metrics"]["total_size_to_remove"] += size
                        self.scan_report["metrics"]["total_dirs_to_remove"] += 1
                        
                        if not self.dry_run:
                            path.rmdir()
                            self.cleanup_log.append(f"Removed empty forbidden dir: {path}")
                            logger.info(f"🗑️  Removed empty forbidden directory: {path}")
                        else:
                            logger.info(f"🚫 Dry-run: Would remove empty forbidden directory: {path}")
                        removed_count += 1
                    else:
                        self.warnings.append(f"Non-empty forbidden directory: {path}")
                        logger.warning(f"⚠️  Non-empty forbidden directory: {path} ({size} bytes)")
        
        return removed_count
    
    def cleanup_backup_files(self) -> int:
        """Remove backup files"""
        logger.info("💾 Checking for backup files...")
        
        removed_count = 0
        
        for pattern in self.forbidden_files:
            for file_path in self.base_path.rglob(pattern):
                if self._is_safe_to_remove(file_path) and file_path.is_file():
                    size = self.get_file_size(file_path)
                    
                    self.scan_report["findings"]["backup_files"].append({
                        "path": str(file_path),
                        "pattern": pattern,
                        "size": size
                    })
                    self.scan_report["metrics"]["total_size_to_remove"] += size
                    self.scan_report["metrics"]["total_files_to_remove"] += 1
                    
                    if not self.dry_run:
                        file_path.unlink()
                        self.cleanup_log.append(f"Removed backup file: {file_path}")
                        logger.info(f"🗑️  Removed backup file: {file_path}")
                    else:
                        logger.info(f"🚫 Dry-run: Would remove backup file: {file_path}")
                    removed_count += 1
        
        return removed_count
    
    def check_documentation_freshness(self) -> int:
        """Flag stale documentation for review"""
        logger.info("📄 Checking documentation freshness...")
        
        stale_count = 0
        stale_cutoff = datetime.now() - timedelta(days=90)
        
        # Keywords that indicate temporary documentation
        temp_keywords = [
            "_complete", "_final", "_summary", "_report",
            "implementation_", "plan_", "strategy_", "migration_",
            "deployment_", "guide_", "setup_", "install_", "fix_",
            "_success", "_backup", "_old", "_archive"
        ]
        
        for doc in self.base_path.rglob("*.md"):
            if self._is_safe_to_remove(doc):
                doc_name_lower = doc.name.lower()
                
                # Check if it's temporary documentation
                if any(keyword in doc_name_lower for keyword in temp_keywords):
                    mod_time = datetime.fromtimestamp(doc.stat().st_mtime)
                    
                    if mod_time < stale_cutoff:
                        size = self.get_file_size(doc)
                        self.scan_report["findings"]["stale_documentation"].append({
                            "path": str(doc),
                            "last_modified": mod_time.strftime('%Y-%m-%d'),
                            "age_days": (datetime.now() - mod_time).days,
                            "size": size
                        })
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
                
                size_bytes = file_path.stat().st_size
                size_mb = size_bytes / (1024 * 1024)
                
                self.scan_report["findings"]["large_files"].append({
                    "path": str(file_path),
                    "size": size_bytes,
                    "size_mb": round(size_mb, 2)
                })
                
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
            ".git/" in path_str or
            "uv.lock" in path_str or
            ".python-version" in path_str):
            return False
        
        return True
    
    def _is_safe_to_scan(self, path: Path) -> bool:
        """Check if path is safe to scan for secrets"""
        path_str = str(path)
        
        # Skip binary and media files
        skip_extensions = {
            '.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg',
            '.mp4', '.mp3', '.wav', '.avi',
            '.zip', '.tar', '.gz', '.rar',
            '.exe', '.dll', '.so', '.dylib',
            '.pyc', '.pyo', '.whl',
            '.lock', '.sum'
        }
        
        if path.suffix.lower() in skip_extensions:
            return False
        
        # Use same safety checks as removal
        return self._is_safe_to_remove(path)
    
    def send_slack_alert(self, message: str, webhook_url: Optional[str] = None):
        """Send alert to Slack webhook"""
        if not webhook_url:
            # Try to get from environment or Pulumi ESC
            webhook_url = os.getenv('SLACK_WEBHOOK_URL')
            if not webhook_url:
                try:
                    from backend.core.auto_esc_config import get_config_value
                    webhook_url = get_config_value('SLACK_WEBHOOK_URL')
                except:
                    logger.info("ℹ️  Slack webhook not configured, skipping alert")
                    return
        
        if webhook_url:
            try:
                payload = {
                    "text": f"🧹 Sophia AI Cleanup Alert\n{message}",
                    "username": "Cleanup Bot",
                    "icon_emoji": ":broom:"
                }
                response = requests.post(webhook_url, json=payload, timeout=5)
                if response.status_code != 200:
                    logger.warning(f"⚠️  Slack alert failed: {response.status_code}")
            except Exception as e:
                logger.warning(f"⚠️  Could not send Slack alert: {e}")
    
    def generate_report(self) -> Dict:
        """Generate comprehensive cleanup report"""
        # Calculate summary metrics
        total_items = sum(len(findings) for findings in self.scan_report["findings"].values())
        
        # Format size nicely
        size_mb = self.scan_report["metrics"]["total_size_to_remove"] / (1024 * 1024)
        
        return {
            "timestamp": self.scan_report["timestamp"],
            "dry_run": self.dry_run,
            "summary": {
                "total_items_found": total_items,
                "total_size_mb": round(size_mb, 2),
                "total_files": self.scan_report["metrics"]["total_files_to_remove"],
                "total_dirs": self.scan_report["metrics"]["total_dirs_to_remove"],
                "cleanup_actions": len(self.cleanup_log),
                "warnings": len(self.warnings)
            },
            "findings": self.scan_report["findings"],
            "actions": self.cleanup_log,
            "warnings": self.warnings
        }
    
    def save_json_report(self, report: Dict, filename: str = "cleanup_scan_report.json"):
        """Save report to JSON file"""
        report_path = self.base_path / filename
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        logger.info(f"📄 Report saved to {report_path}")
        return report_path
    
    def run_daily_cleanup(self) -> Dict:
        """Run all daily cleanup tasks"""
        logger.info(f"🚀 Starting enhanced daily cleanup (dry_run={self.dry_run})...")
        
        # Run all scanning/cleanup tasks
        scripts_deleted = self.cleanup_one_time_scripts()
        dirs_removed = self.prevent_archive_directories()
        backups_removed = self.cleanup_backup_files()
        stale_docs = self.check_documentation_freshness()
        large_files = self.check_large_files()
        
        # Run new scanners
        mcp_duplicates = self.scan_mcp_duplicates()
        env_leaks = self.scan_env_leaks()
        
        # Generate report
        report = self.generate_report()
        
        # Save JSON report
        if self.dry_run:
            self.save_json_report(report, "cleanup_scan_report.json")
        else:
            self.save_json_report(report, "cleanup_execution_report.json")
        
        # Send Slack summary
        summary_msg = f"""
Cleanup {'Scan' if self.dry_run else 'Execution'} Complete!
• Items found: {report['summary']['total_items_found']}
• Size to remove: {report['summary']['total_size_mb']} MB
• One-time scripts: {len(self.scan_report['findings']['one_time_scripts'])}
• Archive dirs: {len(self.scan_report['findings']['archive_directories'])}
• Backup files: {len(self.scan_report['findings']['backup_files'])}
• MCP duplicates: {len(mcp_duplicates)}
• Potential leaks: {len(env_leaks)}
• Warnings: {len(self.warnings)}
"""
        
        if not self.dry_run and self.cleanup_log:
            summary_msg += f"\n✅ Actions taken: {len(self.cleanup_log)}"
        
        self.send_slack_alert(summary_msg)
        
        logger.info(f"✅ Enhanced daily cleanup complete!")
        
        return report

def main():
    """Execute enhanced daily cleanup"""
    cleanup = EnhancedDailyCleanup()
    result = cleanup.run_daily_cleanup()
    
    # Print summary
    print("\n🧹 Enhanced Daily Cleanup Summary")
    print("=" * 60)
    print(f"Mode: {'DRY RUN' if cleanup.dry_run else 'EXECUTION'}")
    print(f"Total items found: {result['summary']['total_items_found']}")
    print(f"Total size: {result['summary']['total_size_mb']} MB")
    print(f"Files to remove: {result['summary']['total_files']}")
    print(f"Directories to remove: {result['summary']['total_dirs']}")
    
    # Show breakdown
    print("\n📊 Findings Breakdown:")
    for category, items in result['findings'].items():
        if items:
            print(f"  • {category}: {len(items)} items")
    
    # Show warnings if any
    if result['warnings']:
        print(f"\n⚠️  Warnings ({len(result['warnings'])}):")
        for warning in result['warnings'][:5]:
            print(f"  - {warning}")
        if len(result['warnings']) > 5:
            print(f"  ... and {len(result['warnings']) - 5} more")
    
    # Show actions if any
    if result['actions']:
        print(f"\n✅ Actions taken ({len(result['actions'])}):")
        for action in result['actions'][:5]:
            print(f"  - {action}")
        if len(result['actions']) > 5:
            print(f"  ... and {len(result['actions']) - 5} more")
    
    print(f"\n📄 Full report saved to: cleanup_{'scan' if cleanup.dry_run else 'execution'}_report.json")
    
    return result

if __name__ == "__main__":
    main() 