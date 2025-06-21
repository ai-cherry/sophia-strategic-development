#!/usr/bin/env python3
"""Clean up all temporary fix scripts created during syntax fixing."""

import os
from pathlib import Path


def cleanup_fix_scripts():
    """Remove all temporary fix scripts."""
    scripts_to_remove = [
        "scripts/fix_precommit_issues.py",
        "scripts/fix_precommit_issues_v2.py",
        "scripts/fix_precommit_final.py",
        "scripts/fix_precommit_complete.py",
        "scripts/fix_docstrings_v2.py",
        "scripts/fix_syntax_errors.py",
        "scripts/fix_docstrings_improved.py",
        "scripts/fix_all_syntax_issues.py",
        "scripts/fix_python_syntax_complete.py",
        "scripts/fix_syntax_final.py",
        "scripts/fix_final_syntax_issues.py",
        "scripts/fix_docstring_syntax_final.py",
        "scripts/fix_streaming_sql_strings.py",
        "scripts/fix_sql_multiline_strings.py",
        "scripts/fix_duplicate_sql_calls.py",
        "scripts/fix_streaming_final.py",
        "scripts/fix_comprehensive_syntax.py",
        "scripts/final_cleanup.py",
        "scripts/fix_critical_files.py",
        "scripts/fix_syntax_comprehensive.py",
        "scripts/validate_syntax_fixes.py",
        "scripts/fix_syntax_robust.py",
        "scripts/fix_syntax_ultimate.py",
        "scripts/fix_remaining_syntax.py",
        "scripts/fix_final_syntax.py",
        "scripts/fix_docstring_formatting.py",
        "scripts/fix_syntax_comprehensive_final.py",
        "scripts/fix_docstring_concatenation.py",
        "scripts/fix_docstring_issues_final.py",
        "scripts/fix_docstring_manual.py",
        "scripts/fix_remaining_syntax_issues.py",
    ]

    removed_count = 0
    for script_path in scripts_to_remove:
        path = Path(script_path)
        if path.exists():
            try:
                os.remove(path)
                print(f"✅ Removed {script_path}")
                removed_count += 1
            except Exception as e:
                print(f"❌ Error removing {script_path}: {e}")
        else:
            print(f"⏭️  Already removed: {script_path}")

    print(f"\n✨ Cleanup complete. Removed {removed_count} temporary fix scripts.")

    # Keep the comprehensive fix script for future use
    print("\n📌 Keeping scripts/fix_all_syntax_comprehensive.py for future use.")


if __name__ == "__main__":
    cleanup_fix_scripts()
