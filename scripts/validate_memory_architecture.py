#!/usr/bin/env python3
"""
Validate Memory Architecture Compliance
Ensures no code uses forbidden vector databases (Pinecone, Weaviate, etc.)
and that all memory operations go through UnifiedMemoryService

Date: July 9, 2025
"""

import ast
import sys
from pathlib import Path

# Forbidden imports that should NEVER appear
FORBIDDEN_IMPORTS = [
    "pinecone",
    "weaviate",
    "chromadb",
    "qdrant_client",  # Except for Mem0's internal use
    "chroma",
    "milvus",
    "faiss",
]

# Allowed memory-related imports
ALLOWED_IMPORTS = [
    "backend.services.unified_memory_service",
    "redis",
    "snowflake.connector",
    "mem0",
]

# Files/directories to ignore
IGNORE_PATTERNS = [
    ".git",
    "__pycache__",
    ".pytest_cache",
    "node_modules",
    ".venv",
    "venv",
    "external/",  # External repos might have their own vector DBs
    "scripts/audit_vector_databases.py",  # Our audit script mentions them
    "scripts/validate_memory_architecture.py",  # This file
    "vector_database_audit_report.json",  # Audit report
]


class MemoryArchitectureValidator:
    """Validates compliance with unified memory architecture"""

    def __init__(self):
        self.violations = []
        self.warnings = []
        self.validated_files = 0
        self.total_violations = 0

    def should_ignore_file(self, filepath: Path) -> bool:
        """Check if file should be ignored"""
        filepath_str = str(filepath)

        return any(pattern in filepath_str for pattern in IGNORE_PATTERNS)

    def check_imports(self, filepath: Path) -> list[tuple[int, str, str]]:
        """Check a Python file for forbidden imports"""
        violations = []

        try:
            with open(filepath, encoding="utf-8") as f:
                content = f.read()

            # Parse the AST
            tree = ast.parse(content)

            for node in ast.walk(tree):
                # Check import statements
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        for forbidden in FORBIDDEN_IMPORTS:
                            if forbidden in alias.name:
                                violations.append(
                                    (node.lineno, f"import {alias.name}", forbidden)
                                )

                # Check from imports
                elif isinstance(node, ast.ImportFrom) and node.module:
                    for forbidden in FORBIDDEN_IMPORTS:
                        if forbidden in node.module:
                            violations.append(
                                (
                                    node.lineno,
                                    f"from {node.module} import ...",
                                    forbidden,
                                )
                            )

        except Exception as e:
            self.warnings.append(f"Error parsing {filepath}: {e}")

        return violations

    def check_direct_usage(self, filepath: Path) -> list[tuple[int, str]]:
        """Check for direct usage of forbidden libraries"""
        violations = []

        try:
            with open(filepath, encoding="utf-8") as f:
                lines = f.readlines()

            forbidden_patterns = [
                ("pinecone.init", "Pinecone initialization"),
                ("pinecone.Index", "Pinecone index usage"),
                ("weaviate.Client", "Weaviate client usage"),
                ("chromadb.Client", "ChromaDB client usage"),
                ("QdrantClient", "Qdrant client usage"),
                ("Pinecone(", "Pinecone client creation"),
                ("Weaviate(", "Weaviate client creation"),
            ]

            for line_num, line in enumerate(lines, 1):
                for pattern, description in forbidden_patterns:
                    if pattern in line and not line.strip().startswith("#"):
                        violations.append((line_num, description))

        except Exception as e:
            self.warnings.append(f"Error reading {filepath}: {e}")

        return violations

    def check_unified_memory_usage(self, filepath: Path) -> bool:
        """Check if file uses UnifiedMemoryService correctly"""
        try:
            with open(filepath, encoding="utf-8") as f:
                content = f.read()

            # Check for correct import
            has_unified_import = any(
                [
                    "from backend.services.unified_memory_service import" in content,
                    "import backend.services.unified_memory_service" in content,
                    "from backend.services import unified_memory_service" in content,
                ]
            )

            # Check for vector operations
            has_vector_ops = any(
                [
                    "search_knowledge" in content,
                    "add_knowledge" in content,
                    "embed" in content.lower() and "snowflake" not in content.lower(),
                    "vector" in content.lower() and "snowflake" not in content.lower(),
                ]
            )

            # If file has vector operations but no unified import, it's suspicious
            return not (has_vector_ops and not has_unified_import)

        except Exception as e:
            self.warnings.append(f"Error checking unified usage in {filepath}: {e}")
            return True

    def validate_file(self, filepath: Path) -> bool:
        """Validate a single Python file"""
        if self.should_ignore_file(filepath):
            return True

        self.validated_files += 1
        file_valid = True

        # Check for forbidden imports
        import_violations = self.check_imports(filepath)
        if import_violations:
            file_valid = False
            for line_num, code, forbidden in import_violations:
                self.violations.append(
                    {
                        "file": str(filepath),
                        "line": line_num,
                        "type": "forbidden_import",
                        "code": code,
                        "forbidden": forbidden,
                    }
                )
                self.total_violations += 1

        # Check for direct usage
        usage_violations = self.check_direct_usage(filepath)
        if usage_violations:
            file_valid = False
            for line_num, description in usage_violations:
                self.violations.append(
                    {
                        "file": str(filepath),
                        "line": line_num,
                        "type": "direct_usage",
                        "description": description,
                    }
                )
                self.total_violations += 1

        # Check for proper unified memory usage
        if not self.check_unified_memory_usage(filepath):
            self.warnings.append(
                f"{filepath} appears to have vector operations without UnifiedMemoryService"
            )

        return file_valid

    def validate_directory(self, root_dir: str = ".") -> bool:
        """Validate all Python files in directory"""
        root_path = Path(root_dir)
        all_valid = True

        print("🔍 Validating memory architecture compliance...")
        print(f"📍 Directory: {root_path.absolute()}")
        print("=" * 80)

        for filepath in root_path.rglob("*.py"):
            if not self.validate_file(filepath):
                all_valid = False

        return all_valid

    def print_report(self):
        """Print validation report"""
        print("\n" + "=" * 80)
        print("📊 MEMORY ARCHITECTURE VALIDATION REPORT")
        print("📅 Date: July 9, 2025")
        print("=" * 80)

        print(f"\n✅ Files validated: {self.validated_files}")
        print(f"❌ Total violations: {self.total_violations}")

        if self.violations:
            print("\n🚨 VIOLATIONS FOUND:")

            # Group by file
            by_file = {}
            for violation in self.violations:
                file_path = violation["file"]
                if file_path not in by_file:
                    by_file[file_path] = []
                by_file[file_path].append(violation)

            for file_path, file_violations in by_file.items():
                print(f"\n📄 {file_path}")
                for v in file_violations:
                    if v["type"] == "forbidden_import":
                        print(
                            f"   Line {v['line']}: {v['code']} (forbidden: {v['forbidden']})"
                        )
                    else:
                        print(f"   Line {v['line']}: {v['description']}")

        if self.warnings:
            print("\n⚠️  WARNINGS:")
            for warning in self.warnings:
                print(f"   {warning}")

        if not self.violations:
            print("\n✅ NO VIOLATIONS FOUND! Architecture is compliant.")
        else:
            print("\n❌ VIOLATIONS MUST BE FIXED!")
            print("Replace all vector database usage with UnifiedMemoryService")

        return len(self.violations) == 0


def main():
    """Run validation"""
    validator = MemoryArchitectureValidator()

    # Check if running as pre-commit hook
    if len(sys.argv) > 1:
        # Validate specific files
        all_valid = True
        for filepath in sys.argv[1:]:
            if filepath.endswith(".py"):
                if not validator.validate_file(Path(filepath)):
                    all_valid = False

        if not all_valid:
            validator.print_report()
            sys.exit(1)
    else:
        # Validate entire directory
        valid = validator.validate_directory(".")
        validator.print_report()

        if not valid:
            print("\n🔧 To fix violations:")
            print("1. Remove all Pinecone/Weaviate imports")
            print(
                "2. Replace with: from backend.services.unified_memory_service import get_unified_memory_service"
            )
            print("3. Use memory.search_knowledge() instead of pinecone.query()")
            print("4. Use memory.add_knowledge() instead of pinecone.upsert()")
            sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
