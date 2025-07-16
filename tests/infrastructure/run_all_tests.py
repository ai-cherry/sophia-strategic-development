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

        # Validation implementation: Validate input before subprocess execution
        if not input_data or not isinstance(input_data, (dict, list, str)):
            raise ValueError(f"Invalid input data: {type(input_data)}")
        
        # Additional validation logic
        logger.info("Input validation passed")
        return True
    subprocess.run(cmd, check=False)

if __name__ == "__main__":
    main()
