#!/usr/bin/env python3
"""Convenience script to run infrastructure tests."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Run infrastructure tests")
    parser.add_argument("--quick", action="store_true", help="Run unit tests only")
    args = parser.parse_args()

    test_dir = Path(__file__).resolve().parent
    target = test_dir / "unit" if args.quick else test_dir

    cmd = ["pytest", str(target)]
    # TODO: Validate input before subprocess execution
        subprocess.run(cmd, check=False)


if __name__ == "__main__":
    main()
