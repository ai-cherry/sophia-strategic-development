#!/usr/bin/env python3
"""Delete artifact paths matching forbidden patterns.
Dry-run by default; use --apply to remove."""
from __future__ import annotations

import argparse
import pathlib
import re
import subprocess

PATTERN = re.compile(r".*(backup|archive|optimized|bak|~|\.old)(/|$)", re.I)


def git_rm(path: pathlib.Path, apply: bool) -> None:
    if apply:
        subprocess.run(["git", "rm", "-r", str(path)], check=True)
    else:
        print("Would remove:", path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="actually remove files")
    args = parser.parse_args()

    for file in pathlib.Path(".").rglob("*"):
        if PATTERN.match(str(file)) and not file.is_symlink():
            git_rm(file, args.apply)
    if not args.apply:
        print("\nDry-run complete. Re-run with --apply to execute.")


if __name__ == "__main__":
    main()
