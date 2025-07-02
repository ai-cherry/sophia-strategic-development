#!/usr/bin/env python3
"""
Fix Missing Internal Imports Script
Analyzes and fixes incorrect internal import paths in Sophia AI
"""

import ast
import json
import os
import re
from pathlib import Path


class ImportFixer:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.import_mapping: dict[str, str] = {}
        self.fixed_count = 0
        self.error_count = 0

        # Load the dependency audit report
        self.audit_report = self._load_audit_report()

    def _load_audit_report(self) -> dict:
        """Load the dependency audit report"""
        report_path = self.project_root / "dependency_audit_report.json"
        if report_path.exists():
            with open(report_path) as f:
                return json.load(f)
        return {}

    def fix_all_missing_imports(self):
        """Fix all missing internal imports"""
        print("🔧 Starting to fix missing internal imports...")

        # Get missing internal imports
        missing_imports = self._get_missing_internal_imports()
        print(f"Found {len(missing_imports)} missing internal imports to fix")

        # Build import mapping
        self._build_import_mapping()

        # Fix each missing import
        for import_name, locations in missing_imports.items():
            self._fix_import(import_name, locations)

        print(f"\n✅ Fixed {self.fixed_count} imports")
        print(f"❌ Failed to fix {self.error_count} imports")

    def _get_missing_internal_imports(self) -> dict[str, list[str]]:
        """Get all missing internal imports from the audit report"""
        missing_internal = {}

        if "missing_imports" in self.audit_report:
            for import_name, details in self.audit_report["missing_imports"][
                "details"
            ].items():
                if details["type"] == "internal":
                    missing_internal[import_name] = details["locations"]

        return missing_internal

    def _build_import_mapping(self):
        """Build a mapping of possible import corrections"""
        print("\n🔍 Building import mapping...")

        # Common patterns for fixing imports
        self.import_mapping.update(
            {
                # MCP server base imports
                "backend.mcp_servers.base.standardized_mcp_server": "backend.mcp_servers.base.sophia_mcp_base",
                "backend.mcp_servers.server": "backend.mcp_servers.base.sophia_mcp_base",
                # Service imports
                "backend.services.mcp_orchestration_service.orchestration_service": "backend.services.mcp_orchestration_service",
                "backend.services.enhanced_unified_chat_service.app": "backend.services.enhanced_unified_chat_service",
                # Database imports
                "backend.core.database.get_session": "backend.core.dependencies.get_db",
                # API route imports
                "backend.api.mcp_integration_routes.router": "backend.api.mcp_integration_routes",
                # Agent imports
                "backend.integrations.enhanced_microsoft_gong_integration.EnhancedMicrosoftGongIntegration": "backend.integrations.gong_integration.GongIntegration",
            }
        )

        # Scan for actual module locations
        self._scan_for_modules()

    def _scan_for_modules(self):
        """Scan the project to find actual module locations"""
        for root, _dirs, files in os.walk(self.project_root):
            # Skip certain directories
            if any(
                skip in root
                for skip in [".venv", "__pycache__", ".git", "node_modules"]
            ):
                continue

            for file in files:
                if file.endswith(".py"):
                    file_path = Path(root) / file
                    module_path = self._file_to_module_path(file_path)

                    # Check if this file exports classes/functions that might be imported
                    exports = self._get_file_exports(file_path)
                    for export in exports:
                        possible_import = f"{module_path}.{export}"
                        if possible_import not in self.import_mapping:
                            self.import_mapping[possible_import] = module_path

    def _file_to_module_path(self, file_path: Path) -> str:
        """Convert file path to module import path"""
        # Remove project root and .py extension
        relative_path = file_path.relative_to(self.project_root)
        module_parts = list(relative_path.parts[:-1]) + [relative_path.stem]

        # Handle __init__.py files
        if module_parts[-1] == "__init__":
            module_parts = module_parts[:-1]

        return ".".join(module_parts)

    def _get_file_exports(self, file_path: Path) -> list[str]:
        """Get exported classes and functions from a file"""
        exports = []

        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    exports.append(node.name)
                elif isinstance(node, ast.FunctionDef):
                    if not node.name.startswith("_"):  # Skip private functions
                        exports.append(node.name)
                elif isinstance(node, ast.Assign):
                    # Check for module-level assignments
                    for target in node.targets:
                        if isinstance(target, ast.Name) and not target.id.startswith(
                            "_"
                        ):
                            exports.append(target.id)

        except Exception:
            pass  # Skip files with syntax errors

        return exports

    def _fix_import(self, import_name: str, locations: list[str]):
        """Fix a specific import in all its locations"""
        print(f"\n🔧 Fixing import: {import_name}")

        # Find the correct import
        correct_import = self._find_correct_import(import_name)

        if not correct_import:
            print(f"  ❌ Could not find correct import for {import_name}")
            self.error_count += 1
            return

        print(f"  ✅ Found correct import: {correct_import}")

        # Fix in each location
        for location in locations:
            if self._fix_import_in_file(location, import_name, correct_import):
                self.fixed_count += 1
            else:
                self.error_count += 1

    def _find_correct_import(self, import_name: str) -> str | None:
        """Find the correct import path"""
        # Check direct mapping
        if import_name in self.import_mapping:
            return self.import_mapping[import_name]

        # Try to find similar imports
        parts = import_name.split(".")

        # Try removing the last part (might be a specific class/function)
        if len(parts) > 1:
            base_import = ".".join(parts[:-1])
            if base_import in self.import_mapping:
                return self.import_mapping[base_import]

        # Try to find the module by searching for the file
        possible_paths = self._find_module_file(parts)
        if possible_paths:
            return possible_paths[0]

        return None

    def _find_module_file(self, parts: list[str]) -> list[str]:
        """Find possible module files for import parts"""
        possible_modules = []

        # Try different combinations
        for i in range(len(parts)):
            path_parts = parts[: i + 1]
            remaining_parts = parts[i + 1 :]

            # Check if this path exists
            potential_path = self.project_root / Path(*path_parts)

            # Check as directory with __init__.py
            if potential_path.is_dir() and (potential_path / "__init__.py").exists():
                if remaining_parts:
                    # Check for specific file
                    file_path = potential_path / f"{remaining_parts[0]}.py"
                    if file_path.exists():
                        module_path = ".".join(path_parts + remaining_parts[:1])
                        possible_modules.append(module_path)
                else:
                    module_path = ".".join(path_parts)
                    possible_modules.append(module_path)

            # Check as .py file
            py_file = (
                self.project_root / Path(*path_parts[:-1]) / f"{path_parts[-1]}.py"
            )
            if py_file.exists():
                module_path = ".".join(path_parts)
                possible_modules.append(module_path)

        return possible_modules

    def _fix_import_in_file(
        self, file_path: str, old_import: str, new_import: str
    ) -> bool:
        """Fix import in a specific file"""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Pattern to match the import
            patterns = [
                # from x import y
                (
                    f"from {re.escape(old_import)} import (\\w+)",
                    f"from {new_import} import \\1",
                ),
                # from x import y as z
                (
                    f"from {re.escape(old_import)} import (\\w+) as (\\w+)",
                    f"from {new_import} import \\1 as \\2",
                ),
                # import x
                (f"import {re.escape(old_import)}\\b", f"import {new_import}"),
                # import x as y
                (
                    f"import {re.escape(old_import)} as (\\w+)",
                    f"import {new_import} as \\1",
                ),
            ]

            # Try to match the parent module import
            old_parts = old_import.split(".")
            if len(old_parts) > 1:
                parent_module = ".".join(old_parts[:-1])
                child = old_parts[-1]
                patterns.extend(
                    [
                        (
                            f"from {re.escape(parent_module)} import {re.escape(child)}",
                            f"from {new_import} import {child}",
                        ),
                        (
                            f"from {re.escape(parent_module)} import .*{re.escape(child)}",
                            f"from {new_import} import {child}",
                        ),
                    ]
                )

            modified = False
            for pattern, replacement in patterns:
                new_content, count = re.subn(pattern, replacement, content)
                if count > 0:
                    content = new_content
                    modified = True

            if modified:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"  ✅ Fixed in {file_path}")
                return True
            else:
                print(f"  ⚠️  Could not fix in {file_path}")
                return False

        except Exception as e:
            print(f"  ❌ Error fixing {file_path}: {e}")
            return False


def main():
    """Run the import fixer"""
    fixer = ImportFixer()
    fixer.fix_all_missing_imports()

    # Create a summary report
    summary = {
        "total_missing": len(fixer._get_missing_internal_imports()),
        "fixed": fixer.fixed_count,
        "failed": fixer.error_count,
        "success_rate": fixer.fixed_count
        / max(fixer.fixed_count + fixer.error_count, 1)
        * 100,
    }

    print("\n" + "=" * 60)
    print("📊 IMPORT FIX SUMMARY")
    print("=" * 60)
    print(f"Total missing internal imports: {summary['total_missing']}")
    print(f"Successfully fixed: {summary['fixed']}")
    print(f"Failed to fix: {summary['failed']}")
    print(f"Success rate: {summary['success_rate']:.1f}%")
    print("=" * 60)


if __name__ == "__main__":
    main()
