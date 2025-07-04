#!/usr/bin/env python3
"""
Comprehensive Linting Remediation Script for Sophia AI
"""

import os
import re
import subprocess


def main():
    print("🔧 Starting comprehensive linting remediation...")

    # 1. Fix unused import in foundational_knowledge_routes.py
    fix_unused_cache_manager_import()

    # 2. Fix lru_cache issue in performance.py
    fix_lru_cache_issue()

    # 3. Fix undefined names
    fix_undefined_names()

    # 4. Run final cleanup
    run_final_cleanup()

    print("✅ Linting remediation completed!")


def fix_unused_cache_manager_import():
    """Remove unused CacheManager import"""
    file_path = "backend/api/foundational_knowledge_routes.py"
    if not os.path.exists(file_path):
        return

    with open(file_path) as f:
        content = f.read()

    # Remove the unused import line
    content = re.sub(
        r"^from backend\.core\.cache_manager import CacheManager\n",
        "",
        content,
        flags=re.MULTILINE,
    )

    with open(file_path, "w") as f:
        f.write(content)

    print(f"✅ Fixed unused import in {file_path}")


def fix_lru_cache_issue():
    """Fix lru_cache usage on instance method"""
    file_path = "api/config/performance.py"
    if not os.path.exists(file_path):
        return

    with open(file_path) as f:
        content = f.read()

    # Replace lru_cache import with cached_property
    content = content.replace(
        "from functools import lru_cache", "from functools import cached_property"
    )

    # Replace the problematic method
    old_method = """    @lru_cache(maxsize=128)
    def get_environment_config(self) -> dict[str, Any]:"""

    new_method = """    @cached_property
    def environment_config(self) -> dict[str, Any]:"""

    content = content.replace(old_method, new_method)

    with open(file_path, "w") as f:
        f.write(content)

    print(f"✅ Fixed lru_cache issue in {file_path}")


def fix_undefined_names():
    """Fix undefined name errors"""

    # Fix get_config_value in UI/UX agent files
    files_needing_config_import = [
        "ui-ux-agent/mcp-servers/langchain-agents/ui_ux_agent.py",
        "ui-ux-agent/start_ui_ux_agent_system.py",
    ]

    for file_path in files_needing_config_import:
        if os.path.exists(file_path):
            with open(file_path) as f:
                content = f.read()

            # Add the missing import if not present
            if (
                "from backend.core.auto_esc_config import get_config_value"
                not in content
            ):
                # Find the right place to add it (after other imports)
                lines = content.split("\n")
                import_index = 0
                for i, line in enumerate(lines):
                    if line.startswith(("import ", "from ")) and "backend" not in line:
                        import_index = i + 1

                lines.insert(
                    import_index,
                    "from backend.core.auto_esc_config import get_config_value",
                )
                content = "\n".join(lines)

                with open(file_path, "w") as f:
                    f.write(content)

                print(f"✅ Added missing import to {file_path}")


def run_final_cleanup():
    """Run final linting and formatting"""
    try:
        # Run ruff with fixes
        print("🔧 Running ruff fixes...")
        subprocess.run(["ruff", "check", ".", "--fix"], capture_output=True)

        print("✅ Final cleanup completed")

    except Exception as e:
        print(f"⚠️ Warning: Final cleanup had issues: {e}")


if __name__ == "__main__":
    main()
