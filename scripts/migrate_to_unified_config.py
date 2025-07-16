#!/usr/bin/env python3
"""
🔄 Migrate to Unified Configuration System

This script migrates from legacy .env patterns to unified Pulumi ESC configuration.
It updates all code files to use the centralized get_config_value() function.

Usage:
    python scripts/migrate_to_unified_config.py
    python scripts/migrate_to_unified_config.py --dry-run
    python scripts/migrate_to_unified_config.py --file specific_file.py
"""

import re
import glob
import argparse
from typing import List
import sys
from datetime import datetime

# Common environment variable patterns to migrate
MIGRATION_PATTERNS = [
    # Direct os.getenv patterns
    (r'os\.getenv\([\'"]([^\'\"]+)[\'"](?:,\s*[^)]+)?\)', r'get_config_value("\1")'),
    
    # os.environ.get patterns
    (r'os\.environ\.get\([\'"]([^\'\"]+)[\'"](?:,\s*[^)]+)?\)', r'get_config_value("\1")'),
    
    # os.environ direct access
    (r'os\.environ\[[\'"]([^\'\"]+)[\'"]\]', r'get_config_value("\1")'),
    
    # Environment variable access with fallback
    (r'os\.getenv\([\'"]([^\'\"]+)[\'"],\s*([^)]+)\)', r'get_config_value("\1", default=\2)'),
    
    # More complex patterns
    (r'os\.environ\.get\([\'"]([^\'\"]+)[\'"],\s*([^)]+)\)', r'get_config_value("\1", default=\2)'),
]

# Files to exclude from migration
EXCLUDE_PATTERNS = [
    '.git',
    '__pycache__',
    '.pytest_cache',
    'node_modules',
    '.venv',
    'venv',
    '.env',
    'build',
    'dist',
    '.tox',
    '.mypy_cache',
    'logs',
    'tmp',
    'temp',
    'migrations',  # Database migrations often need raw env vars
    'tests/fixtures',  # Test fixtures might need specific patterns
]

# Files that should be migrated
INCLUDE_EXTENSIONS = ['.py', '.pyx']

# Import statement to add
IMPORT_STATEMENT = "from backend.core.auto_esc_config import get_config_value"

class CodeMigrator:
    """Migrates code from legacy environment patterns to unified configuration"""
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.files_processed = 0
        self.files_modified = 0
        self.total_replacements = 0
        self.errors = []
        
    def migrate_codebase(self, target_file: str = None) -> bool:
        """Migrate entire codebase or specific file"""
        
        print("🔄 Starting code migration to unified configuration...")
        print(f"🏃 Mode: {'DRY RUN' if self.dry_run else 'LIVE'}")
        
        if target_file:
            files_to_process = [target_file]
        else:
            files_to_process = self.find_python_files()
        
        print(f"📊 Found {len(files_to_process)} files to process")
        
        for file_path in files_to_process:
            try:
                self.migrate_file(file_path)
            except Exception as e:
                self.errors.append(f"Error processing {file_path}: {e}")
                print(f"❌ Error processing {file_path}: {e}")
        
        self.print_summary()
        return len(self.errors) == 0
    
    def find_python_files(self) -> List[str]:
        """Find all Python files that should be migrated"""
        
        files = []
        for ext in INCLUDE_EXTENSIONS:
            pattern = f"**/*{ext}"
            found_files = glob.glob(pattern, recursive=True)
            files.extend(found_files)
        
        # Filter out excluded patterns
        filtered_files = []
        for file_path in files:
            if self.should_migrate_file(file_path):
                filtered_files.append(file_path)
        
        return filtered_files
    
    def should_migrate_file(self, file_path: str) -> bool:
        """Check if file should be migrated"""
        
        # Skip files matching exclude patterns
        for pattern in EXCLUDE_PATTERNS:
            if pattern in file_path:
                return False
        
        # Skip files that are already using unified config
        if self.already_uses_unified_config(file_path):
            return False
        
        # Skip files with no environment variable usage
        if not self.has_env_var_usage(file_path):
            return False
        
        return True
    
    def already_uses_unified_config(self, file_path: str) -> bool:
        """Check if file already uses unified configuration"""
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                return "get_config_value" in content
        except:
            return False
    
    def has_env_var_usage(self, file_path: str) -> bool:
        """Check if file has environment variable usage"""
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Check for any of the patterns we want to migrate
                for pattern, _ in MIGRATION_PATTERNS:
                    if re.search(pattern, content):
                        return True
                
                return False
        except:
            return False
    
    def migrate_file(self, file_path: str):
        """Migrate a single file"""
        
        self.files_processed += 1
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
        except Exception as e:
            raise Exception(f"Could not read file: {e}")
        
        # Apply migration patterns
        modified_content = original_content
        file_replacements = 0
        
        for pattern, replacement in MIGRATION_PATTERNS:
            modified_content, count = re.subn(pattern, replacement, modified_content)
            file_replacements += count
        
        # Add import if needed and modifications were made
        if file_replacements > 0:
            modified_content = self.add_import_if_needed(modified_content)
            
            if not self.dry_run:
                # Write back the modified content
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(modified_content)
            
            self.files_modified += 1
            self.total_replacements += file_replacements
            
            print(f"✅ {'[DRY RUN] ' if self.dry_run else ''}Migrated: {file_path} ({file_replacements} replacements)")
        else:
            print(f"⚪ Skipped: {file_path} (no changes needed)")
    
    def add_import_if_needed(self, content: str) -> str:
        """Add the required import statement if not present"""
        
        if IMPORT_STATEMENT in content:
            return content
        
        # Parse the file to find the right place to add the import
        lines = content.split('\n')
        
        # Find the last import line
        last_import_line = -1
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('import ') or stripped.startswith('from '):
                last_import_line = i
        
        # Insert the import after the last import or at the beginning
        if last_import_line >= 0:
            lines.insert(last_import_line + 1, IMPORT_STATEMENT)
        else:
            # Find the first non-comment, non-docstring line
            insert_line = 0
            for i, line in enumerate(lines):
                stripped = line.strip()
                if stripped and not stripped.startswith('#') and not stripped.startswith('"""') and not stripped.startswith("'''"):
                    insert_line = i
                    break
            
            lines.insert(insert_line, IMPORT_STATEMENT)
            lines.insert(insert_line + 1, "")  # Add empty line after import
        
        return '\n'.join(lines)
    
    def print_summary(self):
        """Print migration summary"""
        
        print("\n📊 Migration Summary:")
        print(f"📁 Files processed: {self.files_processed}")
        print(f"✅ Files modified: {self.files_modified}")
        print(f"🔄 Total replacements: {self.total_replacements}")
        print(f"❌ Errors: {len(self.errors)}")
        
        if self.errors:
            print("\n❌ Errors encountered:")
            for error in self.errors:
                print(f"  - {error}")
        
        if not self.dry_run:
            self.generate_migration_report()
    
    def generate_migration_report(self):
        """Generate detailed migration report"""
        
        report = f"""# 🔄 Code Migration Report: Unified Configuration

**Timestamp**: {datetime.now().isoformat()}
**Mode**: {'DRY RUN' if self.dry_run else 'LIVE'}

## 📊 Summary
- **Files Processed**: {self.files_processed}
- **Files Modified**: {self.files_modified}
- **Total Replacements**: {self.total_replacements}
- **Errors**: {len(self.errors)}
- **Success Rate**: {((self.files_processed - len(self.errors)) / self.files_processed * 100) if self.files_processed > 0 else 0:.1f}%

## 🔄 Migration Patterns Applied
"""
        
        for i, (pattern, replacement) in enumerate(MIGRATION_PATTERNS, 1):
            report += f"{i}. `{pattern}` → `{replacement}`\n"
        
        report += f"""
## 🎯 Results
{"✅ MIGRATION SUCCESSFUL" if len(self.errors) == 0 else "⚠️ MIGRATION COMPLETED WITH ISSUES"}

## 🔧 Next Steps
1. Test the application with unified configuration
2. Update any remaining manual environment variable access
3. Run the application to verify all secrets are accessible
4. Update documentation for new configuration patterns

## 📋 Commands to Test
```bash
# Test unified configuration
python -c "from backend.core.auto_esc_config import get_config_value; print('Config system working!')"

# Test specific secrets
python -c "from backend.core.auto_esc_config import get_config_value; print('OpenAI key: ' + str(get_config_value('openai_api_key')[:10]) + '...')"

# Run application
python -m backend.app.main
```

## ❌ Errors
"""
        
        if self.errors:
            for error in self.errors:
                report += f"- {error}\n"
        else:
            report += "No errors encountered.\n"
        
        try:
            report_file = f"migration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            with open(report_file, 'w') as f:
                f.write(report)
            print(f"📋 Migration report saved: {report_file}")
        except Exception as e:
            print(f"⚠️  Could not save report: {e}")

def validate_unified_config():
    """Validate that unified configuration is working"""
    
    print("🔍 Validating unified configuration system...")
    
    try:
        # Try to import the unified config
        sys.path.insert(0, '.')
        from backend.core.auto_esc_config import get_config_value
        
        # Test basic functionality
        test_value = get_config_value("test_key", default="test_default")
        if test_value == "test_default":
            print("✅ Unified configuration system is working")
            return True
        else:
            print("⚠️  Unified configuration system returned unexpected value")
            return False
            
    except ImportError as e:
        print(f"❌ Cannot import unified configuration: {e}")
        return False
    except Exception as e:
        print(f"❌ Unified configuration validation failed: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description="Migrate codebase to unified configuration system"
    )
    parser.add_argument(
        "--dry-run", 
        action="store_true", 
        help="Show what would be migrated without making changes"
    )
    parser.add_argument(
        "--file", 
        help="Migrate specific file instead of entire codebase"
    )
    parser.add_argument(
        "--validate", 
        action="store_true", 
        help="Validate unified configuration system"
    )
    
    args = parser.parse_args()
    
    if args.validate:
        success = validate_unified_config()
        sys.exit(0 if success else 1)
    
    # Initialize migrator
    migrator = CodeMigrator(dry_run=args.dry_run)
    
    # Run migration
    success = migrator.migrate_codebase(target_file=args.file)
    
    if success:
        print("\n🎉 Code migration completed successfully!")
        if not args.dry_run:
            print("🚀 Codebase now uses unified configuration system!")
            print("🔧 Run with --validate to test the configuration system")
    else:
        print("\n❌ Code migration failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 