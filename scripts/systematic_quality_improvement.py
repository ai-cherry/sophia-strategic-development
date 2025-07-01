#!/usr/bin/env python3
"""
Systematic Quality Improvement Script
Addresses remaining high-priority code quality issues in Sophia AI
"""

import re
import subprocess
from pathlib import Path


def fix_remaining_undefined_names() -> int:
    """Fix remaining undefined names that can be automatically resolved"""
    fixes_applied = 0

    # Common undefined name fixes
    undefined_fixes = {
        "UTC": {"import": "from datetime import datetime, UTC", "files": []},
        "shlex": {"import": "import shlex", "files": []},
        "get_config_value": {
            "import": "from backend.core.auto_esc_config import get_config_value",
            "files": [],
        },
    }

    # Get files with these specific undefined names
    try:
        result = subprocess.run(
            ["ruff", "check", ".", "--select=F821"],
            capture_output=True,
            text=True,
            cwd=Path.cwd(),
        )

        for line in result.stdout.split("\n"):
            if "F821" in line and "Undefined name" in line:
                for name in undefined_fixes.keys():
                    if f"`{name}`" in line:
                        file_path = line.split(":")[0]
                        if file_path and Path(file_path).exists():
                            undefined_fixes[name]["files"].append(file_path)

        # Apply fixes
        for name, fix_info in undefined_fixes.items():
            for file_path in fix_info["files"]:
                if fix_undefined_name_in_file(file_path, name, fix_info["import"]):
                    fixes_applied += 1
                    print(f"✅ Fixed {name} in {file_path}")

    except Exception as e:
        print(f"Error fixing undefined names: {e}")

    return fixes_applied


def fix_undefined_name_in_file(file_path: str, name: str, import_line: str) -> bool:
    """Fix a specific undefined name in a file"""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        # Check if name is used but not imported
        if name not in content:
            return False

        # Check if already imported
        if import_line in content:
            return False

        lines = content.split("\n")

        # Find the best place to add the import
        import_idx = 0
        for i, line in enumerate(lines):
            if line.strip().startswith(("import ", "from ")):
                import_idx = i + 1
            elif line.strip() and not line.strip().startswith("#"):
                break

        lines.insert(import_idx, import_line)

        # Write back the file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        return True

    except Exception as e:
        print(f"❌ Error fixing {name} in {file_path}: {e}")
        return False


def fix_exception_chaining() -> int:
    """Fix raise without from inside except (B904) issues"""
    fixes_applied = 0

    try:
        result = subprocess.run(
            ["ruff", "check", ".", "--select=B904"],
            capture_output=True,
            text=True,
            cwd=Path.cwd(),
        )

        files_to_fix = set()
        for line in result.stdout.split("\n"):
            if "B904" in line:
                file_path = line.split(":")[0]
                if file_path and Path(file_path).exists():
                    files_to_fix.add(file_path)

        for file_path in files_to_fix:
            if fix_exception_chaining_in_file(file_path):
                fixes_applied += 1
                print(f"✅ Fixed exception chaining in {file_path}")

    except Exception as e:
        print(f"Error fixing exception chaining: {e}")

    return fixes_applied


def fix_exception_chaining_in_file(file_path: str) -> bool:
    """Fix exception chaining in a specific file"""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        # Pattern to find raise statements in except blocks that should chain
        # Look for: raise SomeException(...) inside except blocks

        def replace_raise(match):
            indent = match.group(1)
            raise_stmt = match.group(2)
            return f"{indent}{raise_stmt} from err"

        # Only apply if the except block captures the exception as 'e' or 'err'
        lines = content.split("\n")
        new_lines = []
        in_except_block = False
        except_var = None

        for line in lines:
            stripped = line.strip()

            # Check if we're entering an except block
            if stripped.startswith("except ") and " as " in stripped:
                in_except_block = True
                # Extract the exception variable name
                parts = stripped.split(" as ")
                if len(parts) > 1:
                    except_var = parts[1].rstrip(":").strip()
                new_lines.append(line)
                continue

            # Check if we're leaving the except block
            if in_except_block and line and not line[0].isspace():
                in_except_block = False
                except_var = None

            # Fix raise statements in except blocks
            if in_except_block and "raise " in line and " from " not in line:
                if except_var and (except_var == "e" or except_var == "err"):
                    # Apply the fix
                    if re.search(r"raise\s+\w+Exception\(", line):
                        line = re.sub(
                            r"(\s+)(raise\s+\w+Exception\([^)]*\))\s*$",
                            rf"\1\2 from {except_var}",
                            line,
                        )

            new_lines.append(line)

        new_content = "\n".join(new_lines)

        if new_content != content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            return True

        return False

    except Exception as e:
        print(f"❌ Error fixing exception chaining in {file_path}: {e}")
        return False


def fix_unused_imports() -> int:
    """Remove unused imports (F401)"""
    fixes_applied = 0

    try:
        result = subprocess.run(
            ["ruff", "check", ".", "--select=F401", "--fix"],
            capture_output=True,
            text=True,
            cwd=Path.cwd(),
        )

        # Count the fixes from the output
        for line in result.stdout.split("\n"):
            if "Fixed" in line or "✓" in line:
                fixes_applied += 1

        print("✅ Removed unused imports automatically")

    except Exception as e:
        print(f"Error fixing unused imports: {e}")

    return fixes_applied


def update_pyproject_toml() -> bool:
    """Update pyproject.toml to use new ruff configuration format"""
    try:
        pyproject_path = Path("pyproject.toml")
        if not pyproject_path.exists():
            print("⚠️  pyproject.toml not found")
            return False

        with open(pyproject_path, encoding="utf-8") as f:
            content = f.read()

        # Check if already updated
        if "[tool.ruff.lint]" in content:
            print("✅ pyproject.toml already uses new format")
            return True

        # Update the configuration
        new_content = content.replace(
            "[tool.ruff]",
            """[tool.ruff]
line-length = 88
target-version = "py311"

[tool.ruff.lint]""",
        )

        # Move settings to lint section
        new_content = re.sub(
            r"select = \[(.*?)\]",
            r"[tool.ruff.lint]\nselect = [\1]",
            new_content,
            flags=re.DOTALL,
        )

        with open(pyproject_path, "w", encoding="utf-8") as f:
            f.write(new_content)

        print("✅ Updated pyproject.toml to new ruff format")
        return True

    except Exception as e:
        print(f"❌ Error updating pyproject.toml: {e}")
        return False


def generate_quality_report() -> dict:
    """Generate a comprehensive quality report"""
    try:
        result = subprocess.run(
            ["ruff", "check", ".", "--statistics"],
            capture_output=True,
            text=True,
            cwd=Path.cwd(),
        )

        # Parse the statistics
        stats = {}
        for line in result.stdout.split("\n"):
            if (
                line.strip()
                and not line.startswith("warning:")
                and not line.startswith("Found")
            ):
                parts = line.strip().split()
                if len(parts) >= 3:
                    count = parts[0]
                    code = parts[1]
                    if count.isdigit():
                        stats[code] = int(count)

        return stats

    except Exception as e:
        print(f"Error generating quality report: {e}")
        return {}


def main():
    """Main function to systematically improve code quality"""
    print("🔧 Systematic Quality Improvement for Sophia AI")
    print("=" * 60)

    # Get initial stats
    print("📊 Initial Quality Assessment...")
    initial_stats = generate_quality_report()
    initial_total = sum(initial_stats.values())
    print(f"Initial issues: {initial_total}")

    total_fixes = 0

    # 1. Fix remaining undefined names
    print("\n1️⃣ Fixing remaining undefined names...")
    fixes = fix_remaining_undefined_names()
    total_fixes += fixes
    print(f"✅ Fixed {fixes} undefined name issues")

    # 2. Fix exception chaining
    print("\n2️⃣ Improving exception handling...")
    fixes = fix_exception_chaining()
    total_fixes += fixes
    print(f"✅ Fixed {fixes} exception chaining issues")

    # 3. Remove unused imports
    print("\n3️⃣ Cleaning up unused imports...")
    fixes = fix_unused_imports()
    total_fixes += fixes
    print("✅ Removed unused imports")

    # 4. Update configuration
    print("\n4️⃣ Updating configuration...")
    if update_pyproject_toml():
        print("✅ Configuration updated")

    # 5. Apply any remaining fixable issues
    print("\n5️⃣ Applying remaining automatic fixes...")
    subprocess.run(["ruff", "check", ".", "--fix"], capture_output=True)
    print("✅ Applied remaining automatic fixes")

    # Generate final report
    print("\n📊 Final Quality Assessment...")
    final_stats = generate_quality_report()
    final_total = sum(final_stats.values())

    improvement = initial_total - final_total
    improvement_pct = (improvement / initial_total * 100) if initial_total > 0 else 0

    print(f"Final issues: {final_total}")
    print(f"Issues fixed: {improvement}")
    print(f"Improvement: {improvement_pct:.1f}%")

    # Show top remaining issues
    print("\n🎯 Top Remaining Issues:")
    sorted_issues = sorted(final_stats.items(), key=lambda x: x[1], reverse=True)[:5]
    for code, count in sorted_issues:
        print(f"  {code}: {count} issues")

    print("\n✅ Systematic quality improvement complete!")
    print(f"Total fixes applied: {total_fixes}")


if __name__ == "__main__":
    main()
