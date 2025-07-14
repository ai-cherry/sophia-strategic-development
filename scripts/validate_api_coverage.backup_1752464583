#!/usr/bin/env python3
"""validate_api_coverage.py

Simple validation tool for Source-Coverage Registry (SCR) YAML files.

It performs three groups of checks:
1.  Structural – each `*_coverage.yml` file must contain the required
    top-level keys and every endpoint entry must have the mandatory
    fields.
2.  Coverage – proportion of endpoints whose `status` is "implemented"
    must meet a configurable threshold (default 0.80 / 80 %).
3.  Presence  – at least one SCR file must exist; this prevents new MCP
    servers from being merged without a registry.

Exit status is non-zero if any check fails so that CI/GitHub Actions can
block the merge.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

try:
    import yaml  # type: ignore
except ModuleNotFoundError:  # pragma: no cover ‑- CI installs PyYAML
    print("Missing dependency: PyYAML \u2192 `pip install PyYAML`", file=sys.stderr)
    sys.exit(1)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
MIN_COVERAGE = float(os.getenv("MIN_COVERAGE", "0.80"))  # 80 % default
COVERAGE_DIR = Path("config/mcp")
REQ_TOP_KEYS = {"vendor", "api_name", "api_version", "endpoints"}
REQ_ENDPOINT_KEYS = {"path", "method", "status"}


class ValidationError(Exception):
    """Raised when validation fails."""


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------


def load_yaml(path: Path):
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def validate_file(path: Path) -> float:
    """Validate a single SCR file.

    Returns the coverage ratio (implemented / total).
    Raises ValidationError on any structural error or insufficient
    coverage.
    """
    data = load_yaml(path)

    if data is None:
        raise ValidationError(f"{path}: empty or invalid YAML")

    missing_keys = REQ_TOP_KEYS - data.keys()
    if missing_keys:
        raise ValidationError(f"{path}: missing keys {', '.join(missing_keys)}")

    endpoints = data["endpoints"]
    if not isinstance(endpoints, list):
        raise ValidationError(f"{path}: 'endpoints' should be a list")

    implemented = 0
    for idx, ep in enumerate(endpoints):
        if not isinstance(ep, dict):
            raise ValidationError(f"{path}: endpoint #{idx} is not a mapping")
        missing_ep = REQ_ENDPOINT_KEYS - ep.keys()
        if missing_ep:
            raise ValidationError(
                f"{path}: endpoint #{idx} missing keys {', '.join(missing_ep)}"
            )
        if ep.get("status") == "implemented":
            implemented += 1

    total = len(endpoints)
    coverage = implemented / total if total else 0.0

    if coverage < MIN_COVERAGE:
        raise ValidationError(
            f"{path}: coverage {coverage:.0%} < required {MIN_COVERAGE:.0%}"
        )

    return coverage


# ---------------------------------------------------------------------------
# Main entry-point
# ---------------------------------------------------------------------------


def main() -> None:
    scr_files = list(COVERAGE_DIR.glob("*_coverage.yml"))

    if not scr_files:
        print("ERROR: No SCR files found in config/mcp/.", file=sys.stderr)
        sys.exit(1)

    failures: list[str] = []
    summaries: list[str] = []

    for fp in scr_files:
        try:
            cov = validate_file(fp)
            summaries.append(f"{fp}: {cov:.0%} implemented")
        except ValidationError as err:
            failures.append(str(err))

    print("\n== SCR Validation Summary ==")
    for line in summaries:
        print("✔", line)

    if failures:
        print("\n== FAILURES ==")
        for line in failures:
            print("✖", line)
        sys.exit(1)

    print("\nAll SCR checks passed ✓")


if __name__ == "__main__":
    main()
