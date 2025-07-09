"""safe_imports.py
Utility to import third-party modules in a linter-safe and runtime-optional
way.  If the requested package is not present, we create a lightweight stub
`types.ModuleType` that exposes the attributes we know we will touch so that
static analysers (MyPy, Ruff) do not complain about missing modules or
attributes.

Example
-------
>>> aiohttp = safe_import("aiohttp", {"ClientSession": object, "ClientTimeout": object})
>>> aiohttp.ClientSession  # either real class or `object` stub
<object ...>
"""
from __future__ import annotations

import sys
from types import ModuleType
from typing import Any, Mapping

__all__ = ["safe_import"]

def safe_import(name: str, fallback_attrs: Mapping[str, Any] | None = None) -> ModuleType:  # noqa: D401
    """Import *name* with graceful degradation.

    If the real package is installed we return it unmodified.  Otherwise we
    construct a stub `ModuleType` instance, populate it with *fallback_attrs*,
    register it in `sys.modules`, and return it.  This ensures downstream code
    and static analysers can access the expected attributes without import
    errors.
    """
    try:
        return __import__(name)
    except ModuleNotFoundError:  # pragma: no cover – executed only in minimal envs
        stub = ModuleType(name)
        if fallback_attrs:
            for attr, value in fallback_attrs.items():
                setattr(stub, attr, value)
        sys.modules[name] = stub
        return stub