#!/usr/bin/env python3
"""Simple lint check focusing on cyclic imports only"""
import subprocess
import sys

# Run pylint for cyclic imports
print("Checking for cyclic imports...")
try:
    result = subprocess.run(
        [
            "pylint",
            "--disable=all",
            "--enable=cyclic-import",
            "core/",
            "infrastructure/",
            "backend/",
            "scripts/",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    print("STDOUT:")
    print(result.stdout)
    print("\nSTDERR:")
    print(result.stderr)
    print(f"\nReturn code: {result.returncode}")

    # Count cyclic imports
    cycles = sum(1 for line in result.stdout.splitlines() if "Cyclic import" in line)
    print(f"\nFound {cycles} cyclic import issues")

    # Exit with success if no cycles found
    sys.exit(0 if cycles == 0 else 1)

except Exception as e:
    print(f"Error running pylint: {e}")
    sys.exit(1)
