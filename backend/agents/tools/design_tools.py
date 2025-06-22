"""Very small helper utilities used by tests."""

from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Directory where generated components are placed. This is only created when the
# helper is used and does not attempt to modify the repository outside tests.
SAFE_COMPONENTS_DIR = Path("sophia-dashboard/src/components/generated")


def create_react_component(component_name: str, jsx_code: str) -> str:
    """Create a React component in the sandbox directory."""
    if ".." in component_name or "/" in component_name:
        raise ValueError("Invalid component name")

    SAFE_COMPONENTS_DIR.mkdir(parents=True, exist_ok=True)
    file_path = SAFE_COMPONENTS_DIR / f"{component_name}.jsx"
    with open(file_path, "w") as f:
        f.write(jsx_code)
    logger.info("Created React component %s", file_path)
    return str(file_path)


design_tools = {
    "create_react_component": create_react_component,
}
