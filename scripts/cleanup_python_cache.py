#!/usr/bin/env python3
"""
Clean up Python cache files and virtual environments
Preserves the main .venv directory at project root
"""

import os
import shutil
import sys
from pathlib import Path
from typing import List, Tuple


class PythonCacheCleaner:
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path).resolve()
        self.preserved_venvs = {self.root_path / ".venv"}  # Preserve main venv
        self.stats = {
            "pycache_removed": 0,
            "pyc_removed": 0,
            "venv_removed": 0,
            "space_freed_mb": 0,
        }

    def get_directory_size(self, path: Path) -> int:
        """Get total size of directory in bytes"""
        total = 0
        try:
            for entry in path.rglob("*"):
                if entry.is_file():
                    total += entry.stat().st_size
        except (OSError, PermissionError):
            pass
        return total

    def find_pycache_dirs(self) -> list[Path]:
        """Find all __pycache__ directories"""
        return [p for p in self.root_path.rglob("__pycache__") if p.is_dir()]

    def find_pyc_files(self) -> list[Path]:
        """Find all .pyc files"""
        return [p for p in self.root_path.rglob("*.pyc") if p.is_file()]

    def find_venv_dirs(self) -> list[Path]:
        """Find all virtual environment directories"""
        venvs = []
        for pattern in ["venv", ".venv", "env", ".env"]:
            for p in self.root_path.rglob(pattern):
                if p.is_dir() and p not in self.preserved_venvs:
                    # Check if it's actually a venv by looking for key files
                    if (p / "bin" / "python").exists() or (
                        p / "Scripts" / "python.exe"
                    ).exists():
                        venvs.append(p)
        return venvs

    def clean_pycache(self) -> tuple[int, float]:
        """Remove all __pycache__ directories"""
        dirs = self.find_pycache_dirs()
        total_size = 0

        for cache_dir in dirs:
            try:
                size = self.get_directory_size(cache_dir)
                total_size += size
                shutil.rmtree(cache_dir)
                self.stats["pycache_removed"] += 1
            except (OSError, PermissionError) as e:
                print(f"Warning: Could not remove {cache_dir}: {e}")

        return len(dirs), total_size / (1024 * 1024)  # Return count and MB

    def clean_pyc_files(self) -> tuple[int, float]:
        """Remove all .pyc files"""
        files = self.find_pyc_files()
        total_size = 0

        for pyc_file in files:
            try:
                size = pyc_file.stat().st_size
                total_size += size
                pyc_file.unlink()
                self.stats["pyc_removed"] += 1
            except (OSError, PermissionError) as e:
                print(f"Warning: Could not remove {pyc_file}: {e}")

        return len(files), total_size / (1024 * 1024)  # Return count and MB

    def clean_venvs(self) -> tuple[int, float]:
        """Remove virtual environment directories (except preserved ones)"""
        venvs = self.find_venv_dirs()
        total_size = 0

        for venv_dir in venvs:
            try:
                size = self.get_directory_size(venv_dir)
                total_size += size
                print(f"Removing venv: {venv_dir.relative_to(self.root_path)}")
                shutil.rmtree(venv_dir)
                self.stats["venv_removed"] += 1
            except (OSError, PermissionError) as e:
                print(f"Warning: Could not remove {venv_dir}: {e}")

        return len(venvs), total_size / (1024 * 1024)  # Return count and MB

    def update_gitignore(self):
        """Ensure .gitignore has proper Python entries"""
        gitignore_path = self.root_path / ".gitignore"

        python_ignores = [
            "__pycache__/",
            "*.py[cod]",
            "*$py.class",
            "*.pyc",
            ".Python",
            "venv/",
            ".venv/",
            "env/",
            ".env/",
            "ENV/",
            "env.bak/",
            "venv.bak/",
        ]

        existing_lines = set()
        if gitignore_path.exists():
            with open(gitignore_path) as f:
                existing_lines = set(line.strip() for line in f)

        lines_to_add = [line for line in python_ignores if line not in existing_lines]

        if lines_to_add:
            with open(gitignore_path, "a") as f:
                f.write("\n# Python\n")
                for line in lines_to_add:
                    f.write(f"{line}\n")
            print(f"✅ Updated .gitignore with {len(lines_to_add)} Python entries")

    def run(self, dry_run: bool = False):
        """Run the cleanup process"""
        print("🧹 Python Cache Cleanup Tool")
        print(f"📁 Working directory: {self.root_path}")
        print(
            f"🛡️  Preserving: {', '.join(str(p.relative_to(self.root_path)) for p in self.preserved_venvs)}"
        )
        print()

        # Analyze
        pycache_dirs = self.find_pycache_dirs()
        pyc_files = self.find_pyc_files()
        venv_dirs = self.find_venv_dirs()

        print("📊 Analysis Results:")
        print(f"  - __pycache__ directories: {len(pycache_dirs)}")
        print(f"  - .pyc files: {len(pyc_files)}")
        print(f"  - Virtual environments: {len(venv_dirs)}")

        if dry_run:
            print("\n🔍 DRY RUN MODE - No files will be deleted")
            return

        if not any([pycache_dirs, pyc_files, venv_dirs]):
            print("\n✨ Nothing to clean!")
            return

        # Get confirmation
        response = input("\n⚠️  Proceed with cleanup? (y/N): ")
        if response.lower() != "y":
            print("❌ Cleanup cancelled")
            return

        print("\n🚀 Starting cleanup...")

        # Clean
        pycache_count, pycache_mb = self.clean_pycache()
        pyc_count, pyc_mb = self.clean_pyc_files()
        venv_count, venv_mb = self.clean_venvs()

        total_mb = pycache_mb + pyc_mb + venv_mb
        self.stats["space_freed_mb"] = total_mb

        # Update .gitignore
        self.update_gitignore()

        # Report
        print("\n✅ Cleanup Complete!")
        print(
            f"  - Removed {self.stats['pycache_removed']} __pycache__ directories ({pycache_mb:.1f} MB)"
        )
        print(f"  - Removed {self.stats['pyc_removed']} .pyc files ({pyc_mb:.1f} MB)")
        print(
            f"  - Removed {self.stats['venv_removed']} virtual environments ({venv_mb:.1f} MB)"
        )
        print(f"  - Total space freed: {total_mb:.1f} MB")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Clean Python cache files and virtual environments"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be cleaned without deleting",
    )
    parser.add_argument(
        "--path", default=".", help="Root path to clean (default: current directory)"
    )

    args = parser.parse_args()

    cleaner = PythonCacheCleaner(args.path)
    cleaner.run(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
