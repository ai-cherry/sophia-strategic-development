#!/usr/bin/env python3
"""
Audit ETL Processes for Estuary Flow Compliance
Identifies all ETL processes not using Estuary Flow

Date: July 9, 2025
"""

import json
import re
from pathlib import Path


class EstuaryETLAuditor:
    """Audits ETL processes for Estuary Flow compliance"""

    def __init__(self):
        self.violations = {
            "direct_api_calls": [],
            "custom_etl_scripts": [],
            "direct_db_writes": [],
            "manual_transforms": [],
            "custom_schedulers": [],
        }
        self.estuary_compliant = []

        # Patterns indicating non-Estuary ETL
        self.violation_patterns = {
            "direct_api_calls": [
                r"requests\.(get|post|put|delete)",
                r"aiohttp.*\.(get|post|put|delete)",
                r"httpx\.(get|post|put|delete)",
                r"GONG_API",
                r"HUBSPOT_API",
                r"direct.*api.*extract",
            ],
            "direct_db_writes": [
                r"cursor\.execute.*INSERT",
                r"executemany.*INSERT",
                r"bulk_insert_mappings",
                r"to_sql\(",
                r"df\.to_sql",
                r"snowflake.*write",
            ],
            "manual_transforms": [
                r"def transform_.*data",
                r"apply.*transformation",
                r"normalize_.*data",
                r"clean_.*data",
            ],
            "custom_schedulers": [
                r"@schedule\.",
                r"cron.*=",
                r"APScheduler",
                r"airflow",
                r"while True:.*sleep",
            ],
        }

        # Patterns indicating Estuary compliance
        self.estuary_patterns = [
            r"EstuaryFlow",
            r"FlowClient",
            r"estuary.*collection",
            r"flow.*specification",
            r"materialize-snowflake",
        ]

    def audit_all(self):
        """Run complete ETL audit"""
        print("🔍 Estuary Flow ETL Compliance Audit")
        print("=" * 60)

        # Directories to scan
        etl_dirs = ["infrastructure/etl", "backend/etl", "scripts", "backend/scripts"]

        # Scan each directory
        for dir_path in etl_dirs:
            if Path(dir_path).exists():
                self._scan_directory(Path(dir_path))

        # Check Estuary config files
        self._check_estuary_configs()

        # Print results
        self._print_results()

        # Generate migration plan
        self._generate_migration_plan()

    def _scan_directory(self, directory: Path):
        """Scan a directory for ETL files"""
        for py_file in directory.rglob("*.py"):
            self._analyze_file(py_file)

    def _analyze_file(self, file_path: Path):
        """Analyze a single file for ETL patterns"""
        try:
            content = file_path.read_text()

            # Skip test files
            if "test" in str(file_path).lower():
                return

            # Check for Estuary compliance
            is_estuary = any(
                re.search(pattern, content, re.IGNORECASE)
                for pattern in self.estuary_patterns
            )

            if is_estuary:
                self.estuary_compliant.append(str(file_path))
                return

            # Check for violations
            for violation_type, patterns in self.violation_patterns.items():
                for pattern in patterns:
                    matches = list(re.finditer(pattern, content, re.IGNORECASE))
                    if matches:
                        for match in matches:
                            line_num = content[: match.start()].count("\n") + 1
                            self.violations[violation_type].append(
                                {
                                    "file": str(file_path),
                                    "line": line_num,
                                    "pattern": pattern,
                                    "code": content.split("\n")[line_num - 1].strip(),
                                }
                            )

        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")

    def _check_estuary_configs(self):
        """Check for Estuary Flow configuration files"""
        estuary_config_paths = [
            "config/estuary",
            "estuary-config",
            "infrastructure/estuary",
        ]

        print("\n📁 Checking Estuary Configuration Files...")

        for config_path in estuary_config_paths:
            path = Path(config_path)
            if path.exists():
                yaml_files = list(path.glob("*.yaml")) + list(path.glob("*.yml"))
                json_files = list(path.glob("*.json"))

                if yaml_files or json_files:
                    print(f"✅ Found Estuary configs in {config_path}:")
                    for f in yaml_files + json_files:
                        print(f"   - {f.name}")

    def _print_results(self):
        """Print audit results"""
        total_violations = sum(len(v) for v in self.violations.values())

        print("\n📊 Audit Summary")
        print("-" * 60)
        print(f"Total Violations: {total_violations}")
        print(f"Estuary Compliant Files: {len(self.estuary_compliant)}")

        # Violation breakdown
        print("\n⚠️  Violations by Type:")
        for violation_type, violations in self.violations.items():
            if violations:
                print(
                    f"\n{violation_type.replace('_', ' ').title()} ({len(violations)} found):"
                )

                # Group by file
                by_file = {}
                for v in violations:
                    if v["file"] not in by_file:
                        by_file[v["file"]] = []
                    by_file[v["file"]].append(v)

                for file, file_violations in sorted(by_file.items()):
                    print(f"\n  📄 {file}:")
                    for v in file_violations[:3]:  # Show first 3
                        print(f"     Line {v['line']}: {v['code'][:60]}...")
                    if len(file_violations) > 3:
                        print(
                            f"     ... and {len(file_violations) - 3} more violations"
                        )

        # Compliant files
        if self.estuary_compliant:
            print(f"\n✅ Estuary Compliant Files ({len(self.estuary_compliant)}):")
            for file in sorted(self.estuary_compliant):
                print(f"  - {file}")

    def _generate_migration_plan(self):
        """Generate migration plan for violations"""
        print("\n" + "=" * 60)
        print("📋 Migration Plan")
        print("=" * 60)

        # Identify key files needing migration
        critical_files = set()
        for violations in self.violations.values():
            for v in violations:
                critical_files.add(v["file"])

        if not critical_files:
            print("✅ No migrations needed - fully compliant!")
            return

        print(f"\nFiles Requiring Migration: {len(critical_files)}")

        # Priority order
        priority_files = []

        # High priority: Direct API extractors
        for file in critical_files:
            if "gong" in file.lower() or "hubspot" in file.lower():
                priority_files.append((file, "HIGH"))
            elif "etl" in file or "pipeline" in file:
                priority_files.append((file, "MEDIUM"))
            else:
                priority_files.append((file, "LOW"))

        print("\n🎯 Migration Priority:")
        for priority in ["HIGH", "MEDIUM", "LOW"]:
            files = [f for f, p in priority_files if p == priority]
            if files:
                print(f"\n{priority} Priority:")
                for f in sorted(files):
                    print(f"  - {f}")

        # Estuary Flow replacements
        print("\n🔄 Estuary Flow Replacements:")

        replacements = {
            "gong_api_extractor": "source-gong connector",
            "hubspot": "source-hubspot connector",
            "slack": "source-slack connector",
            "asana": "source-asana connector",
            "direct api": "appropriate source connector",
            "custom transform": "Estuary transformation",
            "scheduler": "Estuary Flow schedule",
        }

        for old, new in replacements.items():
            matching_files = [f for f in critical_files if old in f.lower()]
            if matching_files:
                print(f"\n{old} → {new}:")
                for f in matching_files:
                    print(f"  - {f}")

        # Next steps
        print("\n📌 Next Steps:")
        print("1. Create Estuary Flow specifications for each data source")
        print("2. Configure source connectors in Estuary")
        print("3. Set up Snowflake materializations")
        print("4. Parallel run for validation")
        print("5. Deprecate and remove old scripts")

    def save_results(self):
        """Save detailed results to file"""
        results = {
            "audit_date": "2025-07-09",
            "violations": self.violations,
            "compliant_files": self.estuary_compliant,
            "summary": {
                "total_violations": sum(len(v) for v in self.violations.values()),
                "compliant_files": len(self.estuary_compliant),
                "violation_breakdown": {k: len(v) for k, v in self.violations.items()},
            },
        }

        with open("etl_estuary_audit_results.json", "w") as f:
            json.dump(results, f, indent=2)

        print("\n💾 Detailed results saved to: etl_estuary_audit_results.json")


def main():
    """Run the ETL audit"""
    auditor = EstuaryETLAuditor()
    auditor.audit_all()
    auditor.save_results()


if __name__ == "__main__":
    main()
