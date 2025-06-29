#!/usr/bin/env python3
from __future__ import annotations
"""Merge integration_registry.json and service_registry.json into services_registry.json."""


import json
from pathlib import Path
from typing import Any


def load(path: Path) -> dict[str, Any]:
    """Load JSON data from ``path`` if it exists."""
    if not path.exists():
        return {}
    with path.open() as f:
        return json.load(f)


def merge_dicts(primary: dict[str, Any], secondary: dict[str, Any]) -> dict[str, Any]:
    """Merge two service registries."""
    result: dict[str, Any] = {}
    keys = set(primary) | set(secondary)
    for key in sorted(keys):
        a = primary.get(key, {})
        b = secondary.get(key, {})
        merged = {**a, **b}
        for list_key in ["config_keys", "secret_keys", "dependencies", "features"]:
            if list_key in a or list_key in b:
                merged[list_key] = sorted(
                    set(a.get(list_key, []) + b.get(list_key, []))
                )
        result[key] = merged
    return result


def main() -> None:
    integration_file = Path("integration_registry.json")
    service_file = Path("service_registry.json")
    unified_file = Path("services_registry.json")

    integration = load(integration_file)
    service = load(service_file)
    unified = merge_dicts(integration, service)

    with unified_file.open("w") as f:
        json.dump(unified, f, indent=2)
    print(f"Wrote {len(unified)} services to {unified_file}")


if __name__ == "__main__":
    main()
