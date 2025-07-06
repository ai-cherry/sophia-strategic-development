#!/usr/bin/env python3
"""
Update H200 references to GH200
This script updates all H200 references to match the actual GH200 deployment
"""

import os
import re
from datetime import datetime
from pathlib import Path


class H200ToGH200Updater:
    def __init__(self):
        self.updates_made = []
        self.files_updated = 0

        # Define replacement patterns
        self.replacements = [
            # GPU type references
            ("gpu_1x_gh200", "gpu_1x_gh200"),
            ("NVIDIA GH200", "NVIDIA GH200"),
            ("GH200 GPU", "GGH200 GPU"),
            ("gh200-gpu", "ggh200-gpu"),
            # Memory specifications
            ("96GB", "96GB"),
            ("96 GB", "96 GB"),
            ("96GB HBM3e", "96GB HBM3e"),
            # File names (we'll handle these separately)
            ("Dockerfile.gh200", "Dockerfile.gh200"),
            ("requirements-gh200.txt", "requirements-gh200.txt"),
            ("enhanced-gh200-stack.ts", "enhanced-gh200-stack.ts"),
            # Variable/config names
            ("gh200_memory", "ggh200_memory"),
            ("GH200_MEMORY", "GGH200_MEMORY"),
            ("gh200-config", "ggh200-config"),
            ("GH200_CONFIG", "GGH200_CONFIG"),
            # Keep SSH key names as is (lynn-sophia-h200-key) for compatibility
        ]

        # Files to rename
        self.files_to_rename = {
            "Dockerfile.gh200": "Dockerfile.gh200",
            "requirements-gh200.txt": "requirements-gh200.txt",
            "infrastructure/pulumi/enhanced-gh200-stack.ts": "infrastructure/pulumi/enhanced-gh200-stack.ts",
        }

        # Directories to skip
        self.skip_dirs = {".git", "node_modules", "__pycache__", ".venv", "venv", "env"}

        # File extensions to process
        self.valid_extensions = {
            ".py",
            ".ts",
            ".js",
            ".jsx",
            ".tsx",
            ".yml",
            ".yaml",
            ".json",
            ".md",
            ".txt",
            ".dockerfile",
            ".sh",
        }

    def should_process_file(self, file_path):
        """Check if file should be processed"""
        path = Path(file_path)

        # Check extension
        if path.suffix.lower() not in self.valid_extensions and path.name not in [
            "Dockerfile",
            "Dockerfile.gh200",
            "Dockerfile.gh200",
        ]:
            return False

        # Skip binary files
        try:
            with open(file_path, encoding="utf-8") as f:
                f.read(1)
            return True
        except:
            return False

    def update_file_content(self, file_path):
        """Update content of a single file"""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            original_content = content
            updates = []

            # Apply replacements
            for old_text, new_text in self.replacements:
                if old_text in content:
                    count = content.count(old_text)
                    content = content.replace(old_text, new_text)
                    updates.append(f"{old_text} → {new_text} ({count} occurrences)")

            # Special handling for memory pool calculations
            # Update memory pools based on 0.68 scaling factor (96/141)
            memory_pool_patterns = [
                (r"Active Models:\s*60GB", "Active Models: 41GB"),
                (r"Inference Cache:\s*40GB", "Inference Cache: 27GB"),
                (r"Vector Cache:\s*30GB", "Vector Cache: 20GB"),
                (r"Buffer:\s*11GB", "Buffer: 8GB"),
            ]

            for pattern, replacement in memory_pool_patterns:
                if re.search(pattern, content):
                    content = re.sub(pattern, replacement, content)
                    updates.append(f"Memory pool: {pattern} → {replacement}")

            # Save if changed
            if content != original_content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)

                self.files_updated += 1
                self.updates_made.append({"file": file_path, "updates": updates})

                return True
        except Exception as e:
            print(f"Error processing {file_path}: {e}")

        return False

    def rename_files(self):
        """Rename files from H200 to GH200"""
        renamed = []

        for old_name, new_name in self.files_to_rename.items():
            if os.path.exists(old_name):
                try:
                    os.rename(old_name, new_name)
                    renamed.append(f"{old_name} → {new_name}")
                    print(f"✅ Renamed: {old_name} → {new_name}")
                except Exception as e:
                    print(f"❌ Failed to rename {old_name}: {e}")

        return renamed

    def scan_directory(self, directory="."):
        """Scan directory recursively for files to update"""
        for root, dirs, files in os.walk(directory):
            # Skip certain directories
            dirs[:] = [d for d in dirs if d not in self.skip_dirs]

            for file in files:
                file_path = os.path.join(root, file)

                if self.should_process_file(file_path):
                    if self.update_file_content(file_path):
                        print(f"✅ Updated: {file_path}")

    def generate_report(self):
        """Generate update report"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        report = f"""# H200 to GH200 Update Report

**Date**: {timestamp}
**Files Updated**: {self.files_updated}

## Summary

Updated all H200 references to GH200 to match actual Lambda Labs deployment:
- GPU Type: H200 → GH200
- Memory: 96GB → 96GB
- Instance Type: gpu_1x_gh200 → gpu_1x_gh200

## Files Updated

"""

        for update in self.updates_made:
            report += f"\n### {update['file']}\n"
            for change in update["updates"]:
                report += f"- {change}\n"

        return report

    def run(self):
        """Run the update process"""
        print("🔄 Starting H200 → GH200 update process...")
        print("=" * 60)

        # First rename files
        print("\n📝 Renaming files...")
        renamed = self.rename_files()

        # Then update content
        print("\n📝 Updating file contents...")
        self.scan_directory()

        # Generate report
        report = self.generate_report()

        # Save report
        report_file = (
            f"h200_to_gh200_update_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        )
        with open(report_file, "w") as f:
            f.write(report)

        # Print summary
        print("\n" + "=" * 60)
        print("✅ Update Complete!")
        print(f"📊 Files updated: {self.files_updated}")
        print(f"📊 Files renamed: {len(renamed)}")
        print(f"📄 Report saved to: {report_file}")

        if renamed:
            print("\n📝 Renamed files:")
            for r in renamed:
                print(f"  - {r}")


if __name__ == "__main__":
    updater = H200ToGH200Updater()
    updater.run()
