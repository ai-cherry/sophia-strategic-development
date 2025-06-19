"""
Filesystem Tools for AI Agents
Provides safe, encapsulated tools for agents to read and write files
within the project directory.
"""
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class FilesystemTools:
    """
    A toolkit for safe file operations, restricted to the project root.
    """
    def __init__(self, project_root: Path):
        self.project_root = project_root.resolve()

    def _is_path_safe(self, path_to_check: Path) -> bool:
        """
        Ensures the path is within the project directory to prevent
        the agent from accessing arbitrary files on the system.
        """
        resolved_path = path_to_check.resolve()
        return self.project_root in resolved_path.parents or self.project_root == resolved_path

    def read_file(self, file_path: str) -> str:
        """
        Reads the content of a file.
        
        Args:
            file_path: The relative path to the file from the project root.
            
        Returns:
            The content of the file as a string, or an error message.
        """
        try:
            full_path = self.project_root / file_path
            if not self._is_path_safe(full_path):
                logger.error(f"Path traversal attempt blocked: {file_path}")
                return "Error: Access denied. Path is outside the project directory."
                
            if not full_path.is_file():
                logger.error(f"File not found for reading: {full_path}")
                return f"Error: File not found at {file_path}"
                
            logger.info(f"Reading file: {full_path}")
            return full_path.read_text(encoding='utf-8')
        except Exception as e:
            logger.error(f"Failed to read file {file_path}: {e}", exc_info=True)
            return f"Error: Failed to read file. {e}"

    def write_to_file(self, file_path: str, content: str, append: bool = False) -> str:
        """
        Writes content to a file.
        
        Args:
            file_path: The relative path to the file from the project root.
            content: The content to write to the file.
            append: If True, appends to the file. Otherwise, overwrites.
            
        Returns:
            A success or error message.
        """
        try:
            full_path = self.project_root / file_path
            if not self._is_path_safe(full_path):
                logger.error(f"Path traversal attempt blocked: {file_path}")
                return "Error: Access denied. Path is outside the project directory."
            
            # Ensure parent directory exists
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            mode = 'a' if append else 'w'
            logger.info(f"Writing to file: {full_path} (mode: {mode})")
            
            with open(full_path, mode, encoding='utf-8') as f:
                f.write(content)
                
            return f"Successfully wrote to {file_path}"
        except Exception as e:
            logger.error(f"Failed to write to file {file_path}: {e}", exc_info=True)
            return f"Error: Failed to write to file. {e}"

# Global instance for agents to use
# The project root is assumed to be the parent of the 'backend' directory
project_root_path = Path(__file__).parent.parent.parent
filesystem_tools = FilesystemTools(project_root=project_root_path) 