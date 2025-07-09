#!/usr/bin/env python3
"""Compile all Python files and record syntax errors."""
import json
import re
import subprocess
import sys
from pathlib import Path

LOG = Path("compile.log")

with LOG.open("w") as log:
    subprocess.run(
        [sys.executable, "-m", "compileall", "."],
        check=False,
        stdout=log,
        stderr=subprocess.STDOUT,
    )

errors = []
pattern = re.compile(r"\.\/(.+?): line (\d+)")
for line in LOG.read_text().splitlines():
    if "SyntaxError" in line or "IndentationError" in line:
        match = pattern.search(line)
        if match:
            errors.append(
                {
                    "file": match.group(1),
                    "line": int(match.group(2)),
                    "msg": line.split(":", 3)[-1].strip(),
                }
            )

Path("syntax_errors.json").write_text(json.dumps(errors, indent=2))
print(f"Detected {len(errors)} syntax errors. Results written to syntax_errors.json")
