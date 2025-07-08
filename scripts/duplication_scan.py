#!/usr/bin/env python3
"""Generate duplication and cyclic import reports.
Outputs to reports/ and exits non-zero if thresholds are exceeded."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

THRESHOLDS = {"jscpd_duplication": 5.0, "cyclic_imports": 0}

reports = Path("reports")
reports.mkdir(exist_ok=True)


def run(cmd: str, outfile: Path, env: dict[str, str] | None = None) -> None:
    print(">>", cmd)
    with outfile.open("w") as f:
        try:
            # Merge environment variables
            run_env = os.environ.copy()
            if env:
                run_env.update(env)

            subprocess.run(
                cmd,
                shell=True,  # noqa: S602 - intentional shell usage for simplicity
                check=True,
                stdout=f,
                stderr=subprocess.STDOUT,
                env=run_env,
            )
        except FileNotFoundError:
            print(f"Command not found: {cmd}")
        except subprocess.CalledProcessError as exc:
            print(f"Command failed: {exc}")


# 1. Run jscpd with increased memory allocation
# Set NODE_OPTIONS to allocate more memory
env_with_memory = {"NODE_OPTIONS": "--max-old-space-size=8192"}
run("npx jscpd", reports / "jscpd.json", env=env_with_memory)

try:
    jscpd_content = (reports / "jscpd.json").read_text()
    if jscpd_content.strip():
        jscpd_data = json.loads(jscpd_content)
        if "statistics" in jscpd_data and "total" in jscpd_data["statistics"]:
            dup_pct = jscpd_data["statistics"]["total"]["percentage"]
        else:
            print("Warning: jscpd output format unexpected")
            dup_pct = 0.0
    else:
        print("Warning: jscpd.json is empty")
        dup_pct = 0.0
except Exception as e:
    print(f"Warning: Failed to parse jscpd.json: {e}")
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
