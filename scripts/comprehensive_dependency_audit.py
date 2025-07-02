#!/usr/bin/env python3
"""
Comprehensive Dependency Audit Script for Sophia AI
Identifies all imports, checks availability, and generates requirements
"""

import ast
import importlib.util
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


class DependencyAuditor:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.all_imports: set[str] = set()
        self.missing_imports: set[str] = set()
        self.internal_imports: set[str] = set()
        self.external_imports: set[str] = set()
        self.import_locations: dict[str, list[str]] = defaultdict(list)
        self.circular_dependencies: list[tuple[str, str]] = []
        self.unused_imports: dict[str, list[str]] = defaultdict(list)

    def audit_project(self) -> dict[str, Any]:
        """Complete dependency audit of the project"""
        print("🔍 Starting comprehensive dependency audit...")

        # 1. Scan all Python files
        python_files = self._find_python_files()
        print(f"Found {len(python_files)} Python files to analyze")

        # 2. Extract all imports
        for file_path in python_files:
            self._analyze_file(file_path)

        # 3. Categorize imports
        self._categorize_imports()

        # 4. Check availability
        self._check_import_availability()

        # 5. Detect circular dependencies
        self._detect_circular_dependencies()

        # 6. Generate reports
        report = self._generate_report()

        # 7. Generate requirements files
        self._generate_requirements()

        return report

    def _find_python_files(self) -> list[Path]:
        """Find all Python files in the project"""
        python_files = []
        exclude_dirs = {
            ".venv",
            "venv",
            "__pycache__",
            ".git",
            "node_modules",
            "docs_backup",
        }

        for root, dirs, files in os.walk(self.project_root):
            # Remove excluded directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]

            for file in files:
                if file.endswith(".py"):
                    python_files.append(Path(root) / file)

        return python_files

    def _analyze_file(self, file_path: Path) -> None:
        """Analyze a single Python file for imports"""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Parse AST
            try:
                tree = ast.parse(content)
            except SyntaxError as e:
                print(f"⚠️  Syntax error in {file_path}: {e}")
                return

            # Extract imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        import_name = alias.name
                        self.all_imports.add(import_name)
                        self.import_locations[import_name].append(str(file_path))

                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        import_name = node.module
                        self.all_imports.add(import_name)
                        self.import_locations[import_name].append(str(file_path))

                        # Also track specific imports
                        for alias in node.names:
                            full_import = f"{node.module}.{alias.name}"
                            self.all_imports.add(full_import)
                            self.import_locations[full_import].append(str(file_path))

        except Exception as e:
            print(f"❌ Error analyzing {file_path}: {e}")

    def _categorize_imports(self) -> None:
        """Categorize imports as internal or external"""
        # Common patterns for internal imports
        internal_patterns = [
            r"^backend\.",
            r"^frontend\.",
            r"^scripts\.",
            r"^tests\.",
            r"^infrastructure\.",
            r"^external\.",
        ]

        for import_name in self.all_imports:
            is_internal = any(
                re.match(pattern, import_name) for pattern in internal_patterns
            )

            if is_internal:
                self.internal_imports.add(import_name)
            else:
                # Check if it's a relative import that exists in project
                parts = import_name.split(".")
                if len(parts) > 0:
                    potential_path = (
                        self.project_root / Path(*parts[:-1]) / f"{parts[-1]}.py"
                    )
                    if potential_path.exists():
                        self.internal_imports.add(import_name)
                    else:
                        self.external_imports.add(import_name)
                else:
                    self.external_imports.add(import_name)

    def _check_import_availability(self) -> None:
        """Check if imports are available"""
        print("\n🔍 Checking import availability...")

        # Check external imports
        for import_name in self.external_imports:
            if not self._is_import_available(import_name):
                self.missing_imports.add(import_name)

        # Check internal imports
        for import_name in self.internal_imports:
            if not self._is_internal_import_valid(import_name):
                self.missing_imports.add(import_name)

    def _is_import_available(self, import_name: str) -> bool:
        """Check if an external import is available"""
        # Handle special cases
        base_module = import_name.split(".")[0]

        # Try to find the module spec
        try:
            spec = importlib.util.find_spec(base_module)
            return spec is not None
        except (ImportError, ModuleNotFoundError, ValueError):
            return False

    def _is_internal_import_valid(self, import_name: str) -> bool:
        """Check if an internal import path is valid"""
        # Convert import to file path
        parts = import_name.split(".")

        # Try different combinations
        # As a Python file
        potential_paths = [
            self.project_root / Path(*parts) / "__init__.py",
            self.project_root / Path(*parts[:-1]) / f"{parts[-1]}.py",
            self.project_root / f"{parts[0]}.py",
        ]

        return any(path.exists() for path in potential_paths)

    def _detect_circular_dependencies(self) -> None:
        """Detect circular import dependencies"""
        print("\n🔍 Checking for circular dependencies...")

        # Build import graph
        import_graph = defaultdict(set)

        for file_path in self._find_python_files():
            file_imports = self._get_file_imports(file_path)
            for imp in file_imports:
                if imp in self.internal_imports:
                    import_graph[str(file_path)].add(imp)

        # Simple cycle detection (could be enhanced)
        visited = set()
        rec_stack = set()

        def has_cycle(node, graph, visited, rec_stack):
            visited.add(node)
            rec_stack.add(node)

            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    if has_cycle(neighbor, graph, visited, rec_stack):
                        return True
                elif neighbor in rec_stack:
                    self.circular_dependencies.append((node, neighbor))
                    return True

            rec_stack.remove(node)
            return False

        for node in import_graph:
            if node not in visited:
                has_cycle(node, import_graph, visited, rec_stack)

    def _get_file_imports(self, file_path: Path) -> set[str]:
        """Get all imports from a specific file"""
        imports = set()
        for import_name, locations in self.import_locations.items():
            if str(file_path) in locations:
                imports.add(import_name)
        return imports

    def _generate_report(self) -> dict[str, Any]:
        """Generate comprehensive audit report"""
        report = {
            "summary": {
                "total_imports": len(self.all_imports),
                "internal_imports": len(self.internal_imports),
                "external_imports": len(self.external_imports),
                "missing_imports": len(self.missing_imports),
                "circular_dependencies": len(self.circular_dependencies),
                "files_analyzed": len(self._find_python_files()),
            },
            "missing_imports": {"count": len(self.missing_imports), "details": {}},
            "circular_dependencies": self.circular_dependencies,
            "most_imported": {},
            "recommendations": [],
        }

        # Add missing import details
        for missing in self.missing_imports:
            report["missing_imports"]["details"][missing] = {
                "locations": self.import_locations.get(missing, []),
                "type": "internal" if missing in self.internal_imports else "external",
            }

        # Find most imported modules
        import_counts = defaultdict(int)
        for import_name, locations in self.import_locations.items():
            import_counts[import_name] = len(locations)

        # Top 20 most imported
        sorted_imports = sorted(
            import_counts.items(), key=lambda x: x[1], reverse=True
        )[:20]
        report["most_imported"] = dict(sorted_imports)

        # Generate recommendations
        if self.missing_imports:
            report["recommendations"].append(
                f"Install {len([m for m in self.missing_imports if m not in self.internal_imports])} missing external dependencies"
            )

        if self.circular_dependencies:
            report["recommendations"].append(
                f"Resolve {len(self.circular_dependencies)} circular dependencies"
            )

        # Save detailed report
        report_path = self.project_root / "dependency_audit_report.json"
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        print(f"\n📊 Detailed report saved to: {report_path}")

        return report

    def _generate_requirements(self) -> None:
        """Generate requirements.txt files"""
        print("\n📝 Generating requirements files...")

        # Map of known packages to their pip names
        package_mapping = {
            "cv2": "opencv-python",
            "sklearn": "scikit-learn",
            "skimage": "scikit-image",
            "yaml": "pyyaml",
            "dotenv": "python-dotenv",
            "jwt": "pyjwt",
            "openai": "openai",
            "anthropic": "anthropic",
            "fastapi": "fastapi",
            "uvicorn": "uvicorn",
            "pydantic": "pydantic",
            "sqlalchemy": "sqlalchemy",
            "alembic": "alembic",
            "httpx": "httpx",
            "aiohttp": "aiohttp",
            "redis": "redis",
            "asyncpg": "asyncpg",
            "psycopg2": "psycopg2-binary",
            "snowflake": "snowflake-connector-python",
            "pandas": "pandas",
            "numpy": "numpy",
            "prometheus_client": "prometheus-client",
            "structlog": "structlog",
            "slowapi": "slowapi",
            "aiomysql": "aiomysql",
        }

        # Collect external dependencies
        requirements = set()
        dev_requirements = set()

        for import_name in self.external_imports:
            if import_name in self.missing_imports:
                continue

            # Get base package name
            base_package = import_name.split(".")[0]

            # Skip standard library
            if base_package in sys.stdlib_module_names:
                continue

            # Map to pip package name
            pip_name = package_mapping.get(base_package, base_package)

            # Categorize as dev or prod
            if any(test in import_name for test in ["pytest", "test", "mock"]):
                dev_requirements.add(pip_name)
            else:
                requirements.add(pip_name)

        # Add missing external imports
        for missing in self.missing_imports:
            if missing not in self.internal_imports:
                base_package = missing.split(".")[0]
                if base_package not in sys.stdlib_module_names:
                    pip_name = package_mapping.get(base_package, base_package)
                    requirements.add(f"{pip_name}  # MISSING - needs installation")

        # Write requirements.txt
        req_path = self.project_root / "requirements_generated.txt"
        with open(req_path, "w") as f:
            f.write("# Auto-generated requirements from dependency audit\n")
            f.write("# Review and update versions as needed\n\n")
            for req in sorted(requirements):
                f.write(f"{req}\n")

        # Write requirements-dev.txt
        dev_req_path = self.project_root / "requirements-dev_generated.txt"
        with open(dev_req_path, "w") as f:
            f.write("# Auto-generated dev requirements from dependency audit\n\n")
            for req in sorted(dev_requirements):
                f.write(f"{req}\n")

        print(f"✅ Generated {req_path}")
        print(f"✅ Generated {dev_req_path}")

    def print_summary(self, report: dict[str, Any]) -> None:
        """Print a summary of the audit results"""
        print("\n" + "=" * 60)
        print("📊 DEPENDENCY AUDIT SUMMARY")
        print("=" * 60)

        summary = report["summary"]
        print(f"\nFiles analyzed: {summary['files_analyzed']}")
        print(f"Total imports found: {summary['total_imports']}")
        print(f"  - Internal: {summary['internal_imports']}")
        print(f"  - External: {summary['external_imports']}")
        print(f"\n⚠️  Missing imports: {summary['missing_imports']}")
        print(f"🔄 Circular dependencies: {summary['circular_dependencies']}")

        if report["missing_imports"]["details"]:
            print("\n❌ MISSING IMPORTS:")
            for imp, details in list(report["missing_imports"]["details"].items())[:10]:
                print(f"  - {imp} ({details['type']})")
                for loc in details["locations"][:3]:
                    print(f"    Used in: {loc}")
                if len(details["locations"]) > 3:
                    print(f"    ... and {len(details["locations"]) - 3} more files")

        if report["circular_dependencies"]:
            print("\n🔄 CIRCULAR DEPENDENCIES:")
            for dep1, dep2 in report["circular_dependencies"][:5]:
                print(f"  - {dep1} <-> {dep2}")

        print("\n📈 MOST IMPORTED MODULES:")
        for module, count in list(report["most_imported"].items())[:10]:
            print(f"  - {module}: {count} times")

        if report["recommendations"]:
            print("\n💡 RECOMMENDATIONS:")
            for rec in report["recommendations"]:
                print(f"  - {rec}")

        print("\n" + "=" * 60)


def main():
    """Run the dependency audit"""
    auditor = DependencyAuditor()
    report = auditor.audit_project()
    auditor.print_summary(report)

    # Check for critical issues
    if report["summary"]["missing_imports"] > 0:
        print(
            "\n⚠️  Found missing imports! Check dependency_audit_report.json for details."
        )
        sys.exit(1)
    else:
        print("\n✅ All imports are available!")
        sys.exit(0)


if __name__ == "__main__":
    main()
