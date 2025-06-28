#!/usr/bin/env python3
"""
Sophia AI Documentation Cleanup Script
Automatically organizes, consolidates, and validates documentation
"""

import re
import shutil
from datetime import datetime
from pathlib import Path


class DocumentationCleaner:
    """Cleans up and organizes Sophia AI documentation"""

    def __init__(self):
        self.docs_dir = Path("docs")
        self.backup_dir = Path("docs_backup")
        self.deprecated_patterns = [
            r".*_BACKUP\.md$",
            r".*_OLD\.md$",
            r".*\.bak$",
            r"AGNO_.*\.md$",  # Agno was removed
            r".*_TEMP\.md$",
            r".*_DRAFT\.md$",
        ]
        self.consolidation_groups = {
            "cline_v3_18": {
                "pattern": r"CLINE_V3_18.*\.md$",
                "target": "CLINE_V3_18_MASTER_GUIDE.md",
                "keep_separate": ["CLINE_V3_18_QUICK_REFERENCE.md"],
            },
            "architecture": {
                "pattern": r".*ARCHITECTURE.*\.md$",
                "target": "ARCHITECTURE_MASTER_GUIDE.md",
                "keep_separate": ["ARCHITECTURE_PATTERNS_AND_STANDARDS.md"],
            },
            "deployment": {
                "pattern": r".*DEPLOYMENT.*\.md$",
                "target": "DEPLOYMENT_MASTER_GUIDE.md",
                "keep_separate": [],
            },
            "integration": {
                "pattern": r".*INTEGRATION.*\.md$",
                "target": "INTEGRATION_MASTER_GUIDE.md",
                "keep_separate": [],
            },
        }

    def analyze_documentation(self) -> dict:
        """Analyze current documentation structure"""
        if not self.docs_dir.exists():
            return {"error": "docs directory not found"}

        all_files = list(self.docs_dir.rglob("*.md"))

        analysis = {
            "total_files": len(all_files),
            "deprecated_files": [],
            "consolidation_candidates": {},
            "orphaned_files": [],
            "large_files": [],
            "recent_files": [],
            "old_files": [],
        }

        current_time = datetime.now()

        for file_path in all_files:
            relative_path = file_path.relative_to(self.docs_dir)
            file_name = file_path.name

            # Check file size
            file_size = file_path.stat().st_size
            if file_size > 50000:  # Files larger than 50KB
                analysis["large_files"].append(
                    {"path": str(relative_path), "size_kb": file_size // 1024}
                )

            # Check modification time
            mod_time = datetime.fromtimestamp(file_path.stat().st_mtime)
            days_old = (current_time - mod_time).days

            if days_old < 7:
                analysis["recent_files"].append(str(relative_path))
            elif days_old > 90:
                analysis["old_files"].append(
                    {"path": str(relative_path), "days_old": days_old}
                )

            # Check for deprecated files
            for pattern in self.deprecated_patterns:
                if re.match(pattern, file_name, re.IGNORECASE):
                    analysis["deprecated_files"].append(str(relative_path))
                    break

            # Check for consolidation candidates
            for group_name, group_config in self.consolidation_groups.items():
                if re.match(group_config["pattern"], file_name, re.IGNORECASE):
                    if group_name not in analysis["consolidation_candidates"]:
                        analysis["consolidation_candidates"][group_name] = []

                    if file_name not in group_config["keep_separate"]:
                        analysis["consolidation_candidates"][group_name].append(
                            str(relative_path)
                        )

        return analysis

    def create_backup(self) -> bool:
        """Create backup of current documentation"""
        try:
            if self.backup_dir.exists():
                shutil.rmtree(self.backup_dir)

            shutil.copytree(self.docs_dir, self.backup_dir)
            print(f"✅ Created backup at {self.backup_dir}")
            return True

        except Exception as e:
            print(f"❌ Failed to create backup: {e}")
            return False

    def remove_deprecated_files(self, deprecated_files: list[str]) -> int:
        """Remove deprecated files"""
        removed_count = 0

        for file_path in deprecated_files:
            full_path = self.docs_dir / file_path
            try:
                if full_path.exists():
                    full_path.unlink()
                    print(f"🗑️  Removed: {file_path}")
                    removed_count += 1
            except Exception as e:
                print(f"❌ Failed to remove {file_path}: {e}")

        return removed_count

    def consolidate_documentation_group(
        self, group_name: str, files: list[str]
    ) -> bool:
        """Consolidate a group of documentation files"""
        group_config = self.consolidation_groups[group_name]
        target_file = self.docs_dir / group_config["target"]

        try:
            # Read all files in the group
            combined_content = []
            combined_content.append(
                f"# {group_name.title().replace('_', ' ')} Master Guide"
            )
            combined_content.append(f"\n> Consolidated documentation for {group_name}")
            combined_content.append(
                f"\n> Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            combined_content.append(f"\n> Consolidated from {len(files)} files")
            combined_content.append("\n" + "=" * 80 + "\n")

            for file_path in files:
                full_path = self.docs_dir / file_path
                if full_path.exists():
                    combined_content.append(f"\n## From: {file_path}")
                    combined_content.append("-" * 40)

                    with open(full_path, encoding="utf-8") as f:
                        content = f.read()
                        # Remove the main title if it exists
                        lines = content.split("\n")
                        if lines and lines[0].startswith("#"):
                            lines = lines[1:]
                        combined_content.append("\n".join(lines))

                    combined_content.append("\n" + "=" * 80 + "\n")

            # Write consolidated file
            with open(target_file, "w", encoding="utf-8") as f:
                f.write("\n".join(combined_content))

            # Remove original files
            for file_path in files:
                full_path = self.docs_dir / file_path
                if full_path.exists():
                    full_path.unlink()
                    print(f"📄 Consolidated: {file_path} → {group_config['target']}")

            print(f"✅ Created consolidated file: {group_config['target']}")
            return True

        except Exception as e:
            print(f"❌ Failed to consolidate {group_name}: {e}")
            return False

    def create_directory_structure(self) -> bool:
        """Create organized directory structure"""
        directories = [
            "01-getting-started",
            "02-development",
            "03-architecture",
            "04-deployment",
            "05-integrations",
            "06-mcp-servers",
            "07-performance",
            "08-security",
            "99-reference",
            "archive",
        ]

        try:
            for directory in directories:
                dir_path = self.docs_dir / directory
                dir_path.mkdir(exist_ok=True)

                # Create README for each directory
                readme_path = dir_path / "README.md"
                if not readme_path.exists():
                    with open(readme_path, "w") as f:
                        f.write(f"# {directory.replace('-', ' ').title()}\n\n")
                        f.write(
                            f"Documentation for {directory.replace('-', ' ').lower()}.\n"
                        )

            print("✅ Created organized directory structure")
            return True

        except Exception as e:
            print(f"❌ Failed to create directory structure: {e}")
            return False

    def generate_documentation_index(self) -> bool:
        """Generate comprehensive documentation index"""
        try:
            index_content = []
            index_content.append("# 📚 Sophia AI Documentation Index")
            index_content.append("\n> Automatically generated documentation index")
            index_content.append(
                f"\n> Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            index_content.append("\n" + "=" * 80 + "\n")

            # Scan all documentation files
            for directory in sorted(self.docs_dir.iterdir()):
                if directory.is_dir() and not directory.name.startswith("."):
                    index_content.append(
                        f"\n## {directory.name.replace('-', ' ').title()}"
                    )
                    index_content.append("")

                    md_files = sorted(directory.glob("*.md"))
                    for md_file in md_files:
                        if md_file.name != "README.md":
                            # Try to extract title from file
                            try:
                                with open(md_file, encoding="utf-8") as f:
                                    first_line = f.readline().strip()
                                    if first_line.startswith("#"):
                                        title = first_line.lstrip("#").strip()
                                    else:
                                        title = md_file.stem.replace("_", " ").title()
                            except:
                                title = md_file.stem.replace("_", " ").title()

                            relative_path = md_file.relative_to(self.docs_dir)
                            index_content.append(f"- **[{title}]({relative_path})**")

            # Write index file
            index_file = self.docs_dir / "README.md"
            with open(index_file, "w", encoding="utf-8") as f:
                f.write("\n".join(index_content))

            print("✅ Generated documentation index")
            return True

        except Exception as e:
            print(f"❌ Failed to generate index: {e}")
            return False

    def run_cleanup(self, dry_run: bool = False) -> dict:
        """Run complete documentation cleanup"""
        print("🧹 Starting Sophia AI Documentation Cleanup")
        print("=" * 50)

        # Analyze current state
        analysis = self.analyze_documentation()

        if "error" in analysis:
            return analysis

        print("📊 Analysis Results:")
        print(f"   Total files: {analysis['total_files']}")
        print(f"   Deprecated files: {len(analysis['deprecated_files'])}")
        print(f"   Consolidation groups: {len(analysis['consolidation_candidates'])}")
        print(f"   Large files (>50KB): {len(analysis['large_files'])}")
        print(f"   Old files (>90 days): {len(analysis['old_files'])}")

        if dry_run:
            print("\n🔍 DRY RUN - No changes will be made")
            return analysis

        # Create backup
        if not self.create_backup():
            return {"error": "Failed to create backup"}

        cleanup_results = {
            "removed_files": 0,
            "consolidated_groups": 0,
            "created_structure": False,
            "generated_index": False,
        }

        # Remove deprecated files
        cleanup_results["removed_files"] = self.remove_deprecated_files(
            analysis["deprecated_files"]
        )

        # Consolidate documentation groups
        for group_name, files in analysis["consolidation_candidates"].items():
            if files:  # Only consolidate if there are files to consolidate
                if self.consolidate_documentation_group(group_name, files):
                    cleanup_results["consolidated_groups"] += 1

        # Create organized directory structure
        cleanup_results["created_structure"] = self.create_directory_structure()

        # Generate documentation index
        cleanup_results["generated_index"] = self.generate_documentation_index()

        print("\n✅ Documentation cleanup completed!")
        print(f"   Removed files: {cleanup_results['removed_files']}")
        print(f"   Consolidated groups: {cleanup_results['consolidated_groups']}")
        print(f"   Created structure: {cleanup_results['created_structure']}")
        print(f"   Generated index: {cleanup_results['generated_index']}")

        return cleanup_results


def main():
    """Main function for documentation cleanup"""
    import argparse

    parser = argparse.ArgumentParser(description="Clean up Sophia AI documentation")
    parser.add_argument(
        "--dry-run", action="store_true", help="Analyze without making changes"
    )
    parser.add_argument("--backup-only", action="store_true", help="Only create backup")

    args = parser.parse_args()

    cleaner = DocumentationCleaner()

    if args.backup_only:
        cleaner.create_backup()
        return

    result = cleaner.run_cleanup(dry_run=args.dry_run)

    if "error" in result:
        print(f"❌ Error: {result['error']}")
        exit(1)


if __name__ == "__main__":
    main()
