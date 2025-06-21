#!/usr/bin/env python3
"""Ensure the .cursorrules file exists for Cursor IDE."""
from pathlib import Path

CURSOR_RULES = Path(".cursorrules")
DEFAULT_CONTENT = "# Cursor IDE configuration\n"

def main() -> None:
    if CURSOR_RULES.exists():
        print("✅ .cursorrules already present")
    else:
        CURSOR_RULES.write_text(DEFAULT_CONTENT)
        print("📝 Created default .cursorrules")

if __name__ == "__main__":
    main()
