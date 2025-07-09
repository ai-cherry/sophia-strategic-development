import pathlib
import textwrap

deprecated_root = pathlib.Path("backend/_deprecated")

for f in deprecated_root.rglob("*.py"):
    guard = (
        '"""DEPRECATED - moved to quarantine."""\n'
        'raise ImportError("Module {} is deprecated; see migration docs.")\n'
    ).format(f.name)
    f.write_text(guard)
