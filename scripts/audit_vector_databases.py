#!/usr/bin/env python3
"""
Audit Vector Database Usage in Sophia AI
Finds all references to Pinecone, Weaviate, and other vector DBs
Date: July 9, 2025
"""

import json
from datetime import datetime
from pathlib import Path


class VectorDatabaseAuditor:
    """Comprehensive auditor for vector database usage"""

    def __init__(self):
        self.vector_dbs = {
            "pinecone": {
                "imports": ["pinecone", "from pinecone", "import pinecone"],
                "config_keys": [
                    "pinecone_api_key",
                    "pinecone_environment",
                    "PINECONE_",
                ],
                "clients": ["PineconeClient", "pinecone.Index", "pinecone.init"],
                "files": [],
            },
            "weaviate": {
                "imports": ["weaviate", "from weaviate", "import weaviate"],
                "config_keys": ["weaviate_url", "weaviate_api_key", "WEAVIATE_"],
                "clients": ["WeaviateClient", "weaviate.Client", "weaviate.connect"],
                "files": [],
            },
            "chromadb": {
                "imports": ["chromadb", "from chromadb", "import chromadb"],
                "config_keys": ["chroma_", "CHROMA_"],
                "clients": ["ChromaClient", "chromadb.Client"],
                "files": [],
            },
            "qdrant": {
                "imports": ["qdrant", "from qdrant", "import qdrant"],
                "config_keys": ["qdrant_", "QDRANT_"],
                "clients": ["QdrantClient", "qdrant.Client"],
                "files": [],
            },
        }

        self.snowflake_cortex = {
            "usage": [],
            "cortex_functions": [
                "CORTEX.EMBED_TEXT",
                "CORTEX.COMPLETE",
                "VECTOR_DISTANCE",
            ],
        }

        self.ignore_dirs = {
            ".git",
            "__pycache__",
            ".pytest_cache",
            "node_modules",
            ".venv",
            "venv",
        }

    def audit_file(self, filepath: Path) -> dict[str, list[tuple[int, str]]]:
        """Audit a single file for vector database usage"""
        findings = {db: [] for db in self.vector_dbs}
        snowflake_findings = []

        try:
            with open(filepath, encoding="utf-8") as f:
                lines = f.readlines()

            for line_num, line in enumerate(lines, 1):
                line_lower = line.lower()

                # Check each vector database
                for db_name, db_patterns in self.vector_dbs.items():
                    # Check imports
                    for import_pattern in db_patterns["imports"]:
                        if import_pattern in line_lower:
                            findings[db_name].append((line_num, line.strip()))

                    # Check config keys
                    for config_key in db_patterns["config_keys"]:
                        if config_key.lower() in line_lower:
                            findings[db_name].append((line_num, line.strip()))

                    # Check client usage
                    for client_pattern in db_patterns["clients"]:
                        if client_pattern.lower() in line_lower:
                            findings[db_name].append((line_num, line.strip()))

                # Check for Snowflake Cortex usage (good!)
                for cortex_func in self.snowflake_cortex["cortex_functions"]:
                    if cortex_func in line.upper():
                        snowflake_findings.append((line_num, line.strip()))

        except Exception as e:
            print(f"Error reading {filepath}: {e}")

        # Store findings
        for db_name, db_findings in findings.items():
            if db_findings:
                self.vector_dbs[db_name]["files"].append(
                    {"path": str(filepath), "findings": db_findings}
                )

        if snowflake_findings:
            self.snowflake_cortex["usage"].append(
                {"path": str(filepath), "findings": snowflake_findings}
            )

        return findings

    def scan_directory(self, root_dir: str = ".") -> None:
        """Scan entire directory tree for vector database usage"""
        root_path = Path(root_dir)

        print(f"🔍 Scanning directory: {root_path.absolute()}")
        print("=" * 80)

        total_files = 0

        for filepath in root_path.rglob("*"):
            # Skip ignored directories
            if any(ignore_dir in filepath.parts for ignore_dir in self.ignore_dirs):
                continue

            # Only check Python files and config files
            if filepath.is_file() and (
                filepath.suffix in [".py", ".yaml", ".yml", ".json", ".toml"]
            ):
                total_files += 1
                self.audit_file(filepath)

        print(f"\n✅ Scanned {total_files} files")

    def generate_report(self) -> dict:
        """Generate comprehensive audit report"""
        report = {
            "audit_date": datetime.now().isoformat(),
            "actual_date": "2025-07-09",  # The real date!
            "summary": {},
            "details": {},
            "migration_scope": {},
            "snowflake_cortex_adoption": {},
        }

        # Summary statistics
        for db_name, db_data in self.vector_dbs.items():
            file_count = len(db_data["files"])
            total_references = sum(len(f["findings"]) for f in db_data["files"])

            report["summary"][db_name] = {
                "files_affected": file_count,
                "total_references": total_references,
                "status": "NEEDS_MIGRATION" if file_count > 0 else "CLEAN",
            }

            if file_count > 0:
                report["details"][db_name] = db_data["files"]

        # Snowflake Cortex adoption
        report["snowflake_cortex_adoption"] = {
            "files_using_cortex": len(self.snowflake_cortex["usage"]),
            "total_cortex_calls": sum(
                len(f["findings"]) for f in self.snowflake_cortex["usage"]
            ),
            "files": self.snowflake_cortex["usage"],
        }

        # Migration scope
        total_files_to_migrate = sum(
            len(db_data["files"])
            for db_name, db_data in self.vector_dbs.items()
            if db_name in ["pinecone", "weaviate"]
        )

        report["migration_scope"] = {
            "total_files_to_migrate": total_files_to_migrate,
            "primary_targets": ["pinecone", "weaviate"],
            "estimated_effort_days": max(
                1, total_files_to_migrate // 5
            ),  # 5 files per day estimate
        }

        return report

    def print_summary(self, report: dict) -> None:
        """Print a human-readable summary"""
        print("\n" + "=" * 80)
        print("📊 VECTOR DATABASE AUDIT REPORT")
        print("📅 Date: July 9, 2025")
        print("=" * 80)

        # Summary table
        print("\n🎯 SUMMARY:")
        print(f"{'Database':<15} {'Files':<10} {'References':<15} {'Status':<20}")
        print("-" * 60)

        for db_name, stats in report["summary"].items():
            status_emoji = "❌" if stats["status"] == "NEEDS_MIGRATION" else "✅"
            print(
                f"{db_name:<15} {stats['files_affected']:<10} {stats['total_references']:<15} {status_emoji} {stats['status']:<18}"
            )

        # Snowflake Cortex adoption
        cortex_stats = report["snowflake_cortex_adoption"]
        print("\n🎉 Snowflake Cortex Adoption:")
        print(f"   Files using Cortex: {cortex_stats['files_using_cortex']}")
        print(f"   Total Cortex calls: {cortex_stats['total_cortex_calls']}")

        # Migration scope
        scope = report["migration_scope"]
        print("\n🚀 MIGRATION SCOPE:")
        print(f"   Total files to migrate: {scope['total_files_to_migrate']}")
        print(f"   Primary targets: {', '.join(scope['primary_targets'])}")
        print(f"   Estimated effort: {scope['estimated_effort_days']} days")

        # Detailed findings for Pinecone and Weaviate
        for db_name in ["pinecone", "weaviate"]:
            if db_name in report["details"]:
                print(f"\n🔍 {db_name.upper()} USAGE DETAILS:")
                for file_data in report["details"][db_name][:5]:  # Show first 5 files
                    print(f"\n   📄 {file_data['path']}")
                    for line_num, line in file_data["findings"][
                        :3
                    ]:  # Show first 3 findings
                        print(f"      Line {line_num}: {line[:80]}...")

                if len(report["details"][db_name]) > 5:
                    print(
                        f"\n   ... and {len(report['details'][db_name]) - 5} more files"
                    )


def main():
    """Run the vector database audit"""
    auditor = VectorDatabaseAuditor()

    # Scan the codebase
    auditor.scan_directory(".")

    # Generate report
    report = auditor.generate_report()

    # Save detailed report
    report_path = "vector_database_audit_report.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n💾 Detailed report saved to: {report_path}")

    # Print summary
    auditor.print_summary(report)

    # Check if migration is needed
    if report["migration_scope"]["total_files_to_migrate"] > 0:
        print("\n⚠️  MIGRATION REQUIRED!")
        print("Run: python scripts/migrate_vectors_to_snowflake.py")
    else:
        print("\n✅ No migration needed - codebase is clean!")


if __name__ == "__main__":
    main()
