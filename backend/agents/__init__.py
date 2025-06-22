"""Agent package initialization.

This package used to eagerly import the :class:`NLCommandAgent` on module load
which in turn pulled in a number of optional third‑party dependencies.  During
test collection those imports failed when the optional packages were not
available.  To avoid hard import errors we lazily expose ``NLCommandAgent`` only
when it is actually requested by consumers.
"""

from importlib import import_module
from typing import Any

__all__ = ["NLCommandAgent"]


def __getattr__(name: str) -> Any:  # pragma: no cover - thin wrapper
    """Lazily import :class:`NLCommandAgent` when accessed."""
    if name == "NLCommandAgent":
        module = import_module("backend.agents.nl_command_agent")
        obj = getattr(module, "NLCommandAgent")
        globals()["NLCommandAgent"] = obj
        return obj
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
