import pathlib

deprecated_root = pathlib.Path("backend/_deprecated")

for f in deprecated_root.rglob("*.py"):
    guard = (
        '"""DEPRECATED - moved to quarantine."""\n'
        f'raise ImportError("Module {f.name} is deprecated; see migration docs.")\n'
    )
    f.write_text(guard)
