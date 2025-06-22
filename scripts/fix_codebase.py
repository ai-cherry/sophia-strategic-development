import ast
import re
import shutil
import subprocess  # nosec B404
from pathlib import Path
from typing import List, Tuple

import isort
from black import FileMode, format_str

EXCLUDE_DIRS = {
    "__pycache__",
    ".venv",
    "venv",
    ".git",
    "sophia_venv",
}


def fix_docstrings(source: str) -> str:
    """Improve docstring formatting within source."""
    pattern = re.compile(r'("""|\'\'\')(.+?)(\1)', re.DOTALL)

    def repl(match: re.Match[str]) -> str:
        quotes = match.group(1)
        content = match.group(2).strip()
        if not content:
            return f"{quotes}{quotes}"
        lines = content.split("\n")
        first = lines[0].strip()
        if first and not first.endswith((".", "?", "!")):
            first += "."
        rest = [line.rstrip() for line in lines[1:]]
        while rest and not rest[0]:
            rest.pop(0)
        if rest:
            return f"{quotes}{first}\n\n" + "\n".join(rest) + f"{quotes}"
        return f"{quotes}{first}{quotes}"

    return pattern.sub(repl, source)


def sort_imports(source: str) -> str:
    """Apply isort to the given source string."""
    return isort.code(source, profile="black")


def format_code(source: str) -> str:
    """Format code using Black."""
    return format_str(source, mode=FileMode())


def fix_file(path: Path) -> Tuple[bool, List[str]]:
    """Fix a single Python file.

    Returns a tuple of whether changes were made and a list of actions
    performed on the file.
    """
    actions: List[str] = []
    text = path.read_text(encoding="utf-8")
    original = text

    new_text = fix_docstrings(text)
    if new_text != text:
        actions.append("docstrings")
        text = new_text

    new_text = sort_imports(text)
    if new_text != text:
        actions.append("isort")
        text = new_text

    new_text = format_code(text)
    if new_text != text:
        actions.append("black")
        text = new_text

    try:
        ast.parse(text)
    except SyntaxError as exc:
        actions.append(f"syntax-error: {exc}")

    changed = text != original
    if changed:
        path.write_text(text, encoding="utf-8")
    return changed, actions


def find_python_files(base: Path) -> List[Path]:
    """Return all Python files under base excluding EXCLUDE_DIRS."""
    files = []
    for p in base.rglob("*.py"):
        if any(part in EXCLUDE_DIRS for part in p.parts):
            continue
        files.append(p)
    return files


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    files = find_python_files(root)
    changed_files = []
    for file in files:
        changed, actions = fix_file(file)
        if changed:
            changed_files.append((file, actions))
            print(f"Fixed {file}: {', '.join(actions)}")
    print(f"\nTotal files changed: {len(changed_files)}")

    # validate with external tools
    for cmd in (("ruff", "--fix"), ("bandit", "-c", "pyproject.toml")):
        executable = shutil.which(cmd[0])
        if not executable:
            print(f"Tool missing: {cmd[0]}")
            continue
        try:
            subprocess.run(
                [executable, *cmd[1:]],
                check=False,
                shell=False,
            )  # nosec B404,B603
        except Exception as exc:  # nosec B110
            print(f"Failed to run {cmd[0]}: {exc}")


if __name__ == "__main__":
    main()
