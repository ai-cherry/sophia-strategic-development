#!/usr/bin/env python3
"""
Fix Undefined Imports Script
Automatically adds missing get_config_value imports across the Sophia AI codebase
"""

import re
import subprocess
from pathlib import Path


def get_files_with_undefined_get_config_value() -> list[str]:
    """Get all files with undefined get_config_value references"""
    try:
        result = subprocess.run(
            ["ruff", "check", ".", "--select=F821", "--output-format=json"],
            capture_output=True,
            text=True,
            cwd=Path.cwd()
        )

        if result.returncode != 0:
            # Parse the text output instead
            result = subprocess.run(
                ["ruff", "check", ".", "--select=F821"],
                capture_output=True,
                text=True,
                cwd=Path.cwd()
            )

            files = set()
            for line in result.stdout.split('\n'):
                if 'get_config_value' in line and 'F821' in line:
                    # Extract filename from line like: "file:line:col: F821 message"
                    file_path = line.split(':')[0]
                    if file_path and Path(file_path).exists():
                        files.add(file_path)

            return list(files)

    except Exception as e:
        print(f"Error getting undefined references: {e}")
        return []


def fix_get_config_value_import(file_path: str) -> bool:
    """Fix missing get_config_value import in a specific file"""
    try:
        with open(file_path, encoding='utf-8') as f:
            content = f.read()

        # Check if get_config_value is used but not imported
        if 'get_config_value' not in content:
            return False

        # Check if already imported
        if 'from backend.core.auto_esc_config import' in content and 'get_config_value' in content:
            return False

        lines = content.split('\n')

        # Find the best place to add the import
        import_line = "from backend.core.auto_esc_config import get_config_value"

        # Look for existing backend imports
        backend_import_idx = -1
        last_import_idx = -1

        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('from backend.') or stripped.startswith('import backend.'):
                backend_import_idx = i
            elif stripped.startswith(('import ', 'from ')) and not stripped.startswith('#'):
                last_import_idx = i

        # Insert the import
        if backend_import_idx >= 0:
            # Add after other backend imports
            lines.insert(backend_import_idx + 1, import_line)
        elif last_import_idx >= 0:
            # Add after last import
            lines.insert(last_import_idx + 1, import_line)
        else:
            # Add after docstring/comments at the top
            insert_idx = 0
            for i, line in enumerate(lines):
                stripped = line.strip()
                if not stripped or stripped.startswith('#') or '"""' in stripped or "'''" in stripped:
                    continue
                insert_idx = i
                break
            lines.insert(insert_idx, import_line)
            lines.insert(insert_idx + 1, "")  # Add blank line

        # Write back the file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

        print(f"✅ Fixed import in {file_path}")
        return True

    except Exception as e:
        print(f"❌ Error fixing {file_path}: {e}")
        return False


def fix_bare_except_clauses() -> int:
    """Fix bare except clauses by replacing with specific exceptions"""
    try:
        # Get files with bare except clauses
        result = subprocess.run(
            ["ruff", "check", ".", "--select=E722"],
            capture_output=True,
            text=True,
            cwd=Path.cwd()
        )

        files_fixed = 0
        files_to_fix = set()

        for line in result.stdout.split('\n'):
            if 'E722' in line:
                file_path = line.split(':')[0]
                if file_path and Path(file_path).exists():
                    files_to_fix.add(file_path)

        for file_path in files_to_fix:
            if fix_bare_except_in_file(file_path):
                files_fixed += 1

        return files_fixed

    except Exception as e:
        print(f"Error fixing bare except clauses: {e}")
        return 0


def fix_bare_except_in_file(file_path: str) -> bool:
    """Fix bare except clauses in a specific file"""
    try:
        with open(file_path, encoding='utf-8') as f:
            content = f.read()

        # Replace bare except with Exception
        # Pattern: except: -> except Exception:
        pattern = r'(\s+)except:\s*$'
        replacement = r'\1except Exception:'

        new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)

        if new_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"✅ Fixed bare except in {file_path}")
            return True

        return False

    except Exception as e:
        print(f"❌ Error fixing bare except in {file_path}: {e}")
        return False


def main():
    """Main function to fix all undefined imports and bare except clauses"""
    print("🔧 Fixing Critical Priority Issues in Sophia AI")
    print("=" * 60)

    # Fix undefined get_config_value imports
    print("\n1️⃣ Fixing undefined get_config_value imports...")
    undefined_files = get_files_with_undefined_get_config_value()

    if not undefined_files:
        print("✅ No undefined get_config_value references found")
    else:
        print(f"Found {len(undefined_files)} files with undefined get_config_value")

        fixed_count = 0
        for file_path in undefined_files:
            if fix_get_config_value_import(file_path):
                fixed_count += 1

        print(f"✅ Fixed imports in {fixed_count}/{len(undefined_files)} files")

    # Fix bare except clauses
    print("\n2️⃣ Fixing bare except clauses...")
    fixed_except_count = fix_bare_except_clauses()
    print(f"✅ Fixed bare except clauses in {fixed_except_count} files")

    # Run final check
    print("\n3️⃣ Running final validation...")
    result = subprocess.run(
        ["ruff", "check", ".", "--select=F821,E722", "--statistics"],
        capture_output=True,
        text=True,
        cwd=Path.cwd()
    )

    print("Final status:")
    print(result.stdout)

    print("\n✅ Critical priority fixes complete!")


if __name__ == "__main__":
    main()
