"""
Sophia AI - Project Root Path Utility

This utility ensures that the project's root directory is in the system path,
allowing for consistent and absolute imports across different scripts and
modules, especially those located in nested directories like scripts/ or
infrastructure/.

This helps avoid `ModuleNotFoundError` and satisfies linters that enforce
strict import ordering.

Date: July 12, 2025
"""

import sys
from pathlib import Path

def add_project_root_to_path():
    """
    Adds the project root directory to the Python path if it's not already there.
    """
    project_root = Path(__file__).resolve().parent.parent.parent
    if str(project_root) not in sys.path:
        sys.path.append(str(project_root))

# Automatically add the path when this module is imported.
add_project_root_to_path()
