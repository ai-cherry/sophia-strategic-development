"""Minimal safe filesystem helpers."""

from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class FilesystemTools:
    """Utility wrapper around simple file operations within the project root."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root.resolve()

    def _is_safe(self, path: Path) -> bool:
        try:
            return self.project_root in path.resolve().parents or path.resolve() == self.project_root
        except Exception:
            return False

    def read_file(self, file_path: str) -> str:
        path = self.project_root / file_path
        if not self._is_safe(path) or not path.is_file():
            raise FileNotFoundError(file_path)
        return path.read_text(encoding="utf-8")

    def write_to_file(self, file_path: str, content: str, append: bool = False) -> str:
        path = self.project_root / file_path
        if not self._is_safe(path):
            raise PermissionError(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        mode = "a" if append else "w"
        with open(path, mode, encoding="utf-8") as f:
            f.write(content)
        logger.info("Wrote to %s", path)
        return str(path)


project_root_path = Path(__file__).resolve().parents[2]
filesystem_tools = FilesystemTools(project_root_path)
