"""Naively fix lines with excessive closing parentheses."""
from pathlib import Path
import re

UNBALANCED = re.compile(r"\)\)\)+")

for path in Path('.').rglob('*.py'):
    text = path.read_text().splitlines(True)
    changed = False
    new_lines = []
    for line in text:
        if UNBALANCED.search(line):
            new_lines.append(line.replace(')))', '))'))
            changed = True
        else:
            new_lines.append(line)
    if changed:
        path.write_text(''.join(new_lines))
        print(f"Auto-patched {path}")
