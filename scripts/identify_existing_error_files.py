#!/usr/bin/env python3
"""
Identify which files from the syntax error report actually exist.
This helps focus our fixing efforts on real files.
"""

import json
from pathlib import Path


def main():
    """Main function to identify existing files with errors."""

    try:
        with open("syntax_validation_report.json") as f:
            report = json.load(f)

        errors = report.get("errors", {})
        existing_files = []
        missing_files = []

        for file_path_str, error_msg in errors.items():
            # Skip node_modules
            if "node_modules" in file_path_str:
                continue

            file_path = Path(file_path_str)

            if file_path.exists():
                existing_files.append((file_path_str, error_msg))
            else:
                missing_files.append(file_path_str)

        if existing_files:
            for file_path, _error in existing_files[:20]:  # Show first 20
                pass

            if len(existing_files) > 20:
                pass

        # Save the list of existing files for targeted fixing
        existing_files_list = [f[0] for f in existing_files]
        with open("existing_error_files.json", "w") as f:
            json.dump(existing_files_list, f, indent=2)

    except Exception:
        pass


if __name__ == "__main__":
    main()
