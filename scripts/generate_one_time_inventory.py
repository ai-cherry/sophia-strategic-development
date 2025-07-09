#!/usr/bin/env python3
"""Generate inventory of one-time artefacts in the repository."""

import csv
import re
import subprocess
import time
from pathlib import Path

PATTERNS = [
    re.compile(
        r"^(fix_|migrate_|phase\d+_|quick_cleanup|dead_code_|split_service_layer|push_.*_bypass_hooks|recreate_|backup_|cleanup_).*\.py$",
        re.IGNORECASE,
    ),
    re.compile(r".*_(REPORT|SUMMARY|STATUS)\.md$", re.IGNORECASE),
    re.compile(r".*backup.*", re.IGNORECASE),
]

ROOT = Path(".")
CUTOFF_DAYS = 30
NOW = time.time()


def flagged(path: Path) -> bool:
    if any(p.search(path.name) for p in PATTERNS):
        return True
    if "backup" in path.parts:
        return True
    return False


def referenced(path: Path) -> bool:
    result = subprocess.run(["rg", "-q", path.name], check=False, capture_output=True)
    return result.returncode == 0


rows = []
for item in ROOT.rglob("*"):
    if item.is_file() and flagged(item):
        age_days = (NOW - item.stat().st_mtime) / 86400
        rows.append(
            {
                "path": str(item),
                "size_kb": round(item.stat().st_size / 1024, 1),
                "age_days": round(age_days, 1),
                "referenced_elsewhere": referenced(item),
                "confidence": (
                    "HIGH"
                    if age_days > CUTOFF_DAYS and not referenced(item)
                    else "MEDIUM"
                ),
                "action": "",
            }
        )

if rows:
    with open("one_time_inventory.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print("📄 one_time_inventory.csv generated")
else:
    print("No candidates found.")
