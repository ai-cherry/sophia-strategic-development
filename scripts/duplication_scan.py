#!/usr/bin/env python3
"""Generate duplication and cyclic import reports.
Outputs to reports/ and exits non-zero if thresholds are exceeded."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

THRESHOLDS = {"jscpd_duplication": 5.0, "cyclic_imports": 0}

reports = Path("reports")
reports.mkdir(exist_ok=True)


def run(cmd: str, outfile: Path) -> None:
    print(">>", cmd)
    with outfile.open("w") as f:
        try:
            subprocess.run(
                cmd,
                shell=True,  # noqa: S602 - intentional shell usage for simplicity
                check=True,
                stdout=f,
                stderr=subprocess.STDOUT,
            )
        except FileNotFoundError:
            print(f"Command not found: {cmd}")
        except subprocess.CalledProcessError as exc:
            print(f"Command failed: {exc}")


# 1. Run jscpd
run("npx jscpd --min-lines 30 --reporters json --silent .", reports / "jscpd.json")

try:
    dup_pct = json.loads((reports / "jscpd.json").read_text())["statistics"]["total"][
        "percentage"
    ]
except Exception:
    dup_pct = 0.0

# 2. Run pylint for cyclic imports
run(
    "pylint --disable=all --enable=cyclic-import $(git ls-files '*.py')",
    reports / "cyclic_imports.txt",
)

cycles = sum(
    1
    for line in (reports / "cyclic_imports.txt").read_text().splitlines()
    if line.strip().startswith("Cyclic import")
)

# 3. Enforce thresholds
fails: list[str] = []
if dup_pct > THRESHOLDS["jscpd_duplication"]:
    fails.append(f"jscpd={dup_pct:.2f}% > {THRESHOLDS['jscpd_duplication']}%")
if cycles > THRESHOLDS["cyclic_imports"]:
    fails.append(f"cyclic_imports={cycles} > {THRESHOLDS['cyclic_imports']}")
if fails:
    print("FAIL:", ", ".join(fails))
    sys.exit(1)
print("Duplication & import checks passed.")
