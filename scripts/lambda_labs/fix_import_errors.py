#!/usr/bin/env python3
"""
Fix Known Import Errors in Sophia AI Codebase
Addresses the OptimizedCache import issue and other dependency problems
"""

import ast
import logging
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Known import fixes
IMPORT_FIXES = {
    # Fix the critical OptimizedCache import error
    "from core.optimized_cache import OptimizedCache": "from core.optimized_cache import OptimizedHierarchicalCache as OptimizedCache",
    # Additional common import fixes
    "from backend.core.optimized_cache import OptimizedCache": "from backend.core.optimized_cache import OptimizedHierarchicalCache as OptimizedCache",
    "from infrastructure.services.optimized_cache import OptimizedCache": "from infrastructure.services.optimized_cache import OptimizedHierarchicalCache as OptimizedCache",
}

# Files to check for import issues
TARGET_PATTERNS = [
    "**/*.py",
    "backend/**/*.py",
    "infrastructure/**/*.py",
    "core/**/*.py",
]

# Files to skip
SKIP_PATTERNS = [
    "__pycache__",
    ".git",
    "venv",
    ".venv",
    "node_modules",
    "build",
    "dist",
]


class ImportFixer:
    """Fix import errors in Python files"""

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.fixed_files = []
        self.errors = []

    def should_skip_path(self, path: Path) -> bool:
        """Check if path should be skipped"""
        path_str = str(path)
        return any(skip in path_str for skip in SKIP_PATTERNS)

    def find_python_files(self) -> list[Path]:
        """Find all Python files to check"""
        python_files = []

        for pattern in TARGET_PATTERNS:
            for file_path in Path(".").glob(pattern):
                if file_path.is_file() and not self.should_skip_path(file_path):
                    python_files.append(file_path)

        return sorted(set(python_files))

    def check_imports(self, file_path: Path) -> list[tuple[int, str, str]]:
        """Check a file for import issues"""
        fixes_needed = []

        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
                lines = content.splitlines()

            # Parse AST to find imports
            try:
                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom):
                        # Reconstruct import statement
                        if node.module:
                            import_stmt = f"from {node.module} import "
                            names = []
                            for alias in node.names:
                                if alias.asname:
                                    names.append(f"{alias.name} as {alias.asname}")
                                else:
                                    names.append(alias.name)
                            import_stmt += ", ".join(names)

                            # Check if this import needs fixing
                            for bad_import, good_import in IMPORT_FIXES.items():
                                if bad_import in import_stmt:
                                    line_num = node.lineno
                                    fixes_needed.append(
                                        (line_num, import_stmt, good_import)
                                    )

            except SyntaxError as e:
                logger.warning(f"Syntax error in {file_path}: {e}")

            # Also do text-based search for imports
            for i, line in enumerate(lines, 1):
                if line.strip().startswith(("from ", "import ")):
                    for bad_import, good_import in IMPORT_FIXES.items():
                        if bad_import in line:
                            # Check if not already found by AST
                            if not any(fix[0] == i for fix in fixes_needed):
                                fixes_needed.append((i, line.strip(), good_import))

        except Exception as e:
            self.errors.append((file_path, str(e)))
            logger.error(f"Error reading {file_path}: {e}")

        return fixes_needed

    def fix_file(self, file_path: Path, fixes: list[tuple[int, str, str]]) -> bool:
        """Apply fixes to a file"""
        if not fixes:
            return True

        try:
            with open(file_path, encoding="utf-8") as f:
                lines = f.readlines()

            # Apply fixes
            for line_num, old_import, new_import in fixes:
                # Line numbers are 1-based
                idx = line_num - 1
                if idx < len(lines):
                    old_line = lines[idx]
                    # Replace the problematic import
                    for bad, good in IMPORT_FIXES.items():
                        if bad in old_line:
                            lines[idx] = old_line.replace(bad, good)
                            logger.info(f"  Line {line_num}: {bad} → {good}")

            # Write back
            if not self.dry_run:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.writelines(lines)
                logger.info(f"  ✅ Fixed {file_path}")
            else:
                logger.info(f"  🔍 Would fix {file_path}")

            self.fixed_files.append(file_path)
            return True

        except Exception as e:
            self.errors.append((file_path, str(e)))
            logger.error(f"Error fixing {file_path}: {e}")
            return False

    def validate_imports(self, file_path: Path) -> list[str]:
        """Validate that imports can be resolved"""
        unresolved = []

        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    module = node.module
                    if module:
                        # Check if module exists
                        module_path = module.replace(".", "/")

                        # Check various possible locations
                        possible_paths = [
                            f"{module_path}.py",
                            f"{module_path}/__init__.py",
                            f"backend/{module_path}.py",
                            f"backend/{module_path}/__init__.py",
                            f"infrastructure/{module_path}.py",
                            f"infrastructure/{module_path}/__init__.py",
                        ]

                        if not any(Path(p).exists() for p in possible_paths):
                            for alias in node.names:
                                unresolved.append(f"from {module} import {alias.name}")

        except Exception:
            pass

        return unresolved

    def run(self):
        """Run the import fixer"""
        logger.info("🔍 Scanning for import errors...")

        python_files = self.find_python_files()
        logger.info(f"Found {len(python_files)} Python files to check")

        files_with_issues = 0
        total_fixes = 0

        for file_path in python_files:
            fixes = self.check_imports(file_path)

            if fixes:
                files_with_issues += 1
                total_fixes += len(fixes)
                logger.info(f"\n📄 {file_path} - {len(fixes)} issues found:")

                for line_num, old_import, new_import in fixes:
                    logger.info(f"  Line {line_num}: {old_import}")

                if not self.dry_run:
                    self.fix_file(file_path, fixes)

            # Also check for unresolved imports
            unresolved = self.validate_imports(file_path)
            if unresolved:
                logger.warning(f"\n⚠️  {file_path} has unresolved imports:")
                for imp in unresolved:
                    logger.warning(f"  - {imp}")

        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("IMPORT FIX SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Files scanned: {len(python_files)}")
        logger.info(f"Files with issues: {files_with_issues}")
        logger.info(f"Total fixes: {total_fixes}")
        logger.info(f"Files fixed: {len(self.fixed_files)}")

        if self.errors:
            logger.error(f"\nErrors encountered: {len(self.errors)}")
            for file_path, error in self.errors:
                logger.error(f"  {file_path}: {error}")

        if self.dry_run:
            logger.info("\n🔍 DRY RUN - No files were modified")
            logger.info("Run without --dry-run to apply fixes")

        return files_with_issues == 0


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Fix import errors in Sophia AI codebase"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be fixed without modifying files",
    )
    parser.add_argument(
        "--check-only", action="store_true", help="Only check for issues, don't fix"
    )

    args = parser.parse_args()

    if args.check_only:
        args.dry_run = True

    fixer = ImportFixer(dry_run=args.dry_run)
    success = fixer.run()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
