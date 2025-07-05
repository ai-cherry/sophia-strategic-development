"""
Code Modification Service - Handles natural language code modifications
"""

import ast
import difflib
import logging
import os
import re
from pathlib import Path
from typing import Any

from backend.core.config_manager import ConfigManager
from backend.services.smart_ai_service import LLMRequest, SmartAIService, TaskType

logger = logging.getLogger(__name__)


class CodeModificationService:
    """
    Service for modifying code through natural language instructions
    """

    def __init__(self):
        self.smart_ai = SmartAIService()
        self.config = ConfigManager()
        self.workspace_root = Path(os.getcwd())

    async def modify_code(
        self, file_path: str, instructions: str, context: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Modify code based on natural language instructions
        """
        logger.info(
            f"Modifying code in {file_path} with instructions: {instructions[:100]}..."
        )

        # Read current code
        full_path = self.workspace_root / file_path
        if not full_path.exists():
            return {"success": False, "error": f"File not found: {file_path}"}

        try:
            current_code = full_path.read_text()
        except Exception as e:
            return {"success": False, "error": f"Error reading file: {str(e)}"}

        # Generate modifications using AI
        modified_code = await self._generate_modifications(
            current_code, instructions, file_path, context
        )

        # Create diff for review
        diff = self._create_diff(current_code, modified_code, file_path)

        # Validate modifications
        validation = await self._validate_modifications(
            file_path, current_code, modified_code
        )

        # Calculate change metrics
        metrics = self._calculate_change_metrics(current_code, modified_code)

        return {
            "success": True,
            "file_path": file_path,
            "diff": diff,
            "validation": validation,
            "modified_code": modified_code,
            "metrics": metrics,
            "requires_approval": self._requires_approval(metrics, validation),
        }

    async def _generate_modifications(
        self,
        current_code: str,
        instructions: str,
        file_path: str,
        context: dict[str, Any],
    ) -> str:
        """Generate code modifications using AI"""

        # Detect language
        language = self._detect_language(file_path)

        # Get recent changes from memory if available
        recent_changes = context.get("memory_context", [])
        recent_changes_text = ""
        if recent_changes:
            recent_changes_text = "\n\nRecent related changes:\n" + "\n".join(
                f"- {change.get('content', '')}" for change in recent_changes[:3]
            )

        prompt = f"""
        Modify the following {language} code based on these instructions:

        File: {file_path}
        Instructions: {instructions}

        Current code:
        ```{language}
        {current_code}
        ```

        Context:
        - Project: Sophia AI (Enterprise AI Orchestrator)
        - Language: {language}
        - Coding standards: Follow PEP 8 for Python, ESLint for JavaScript/TypeScript
        - Important: Preserve all existing functionality unless explicitly asked to change it
        {recent_changes_text}

        Generate the complete modified code following best practices.
        Only output the modified code, no explanations.
        """

        request = LLMRequest(
            messages=[{"role": "user", "content": prompt}],
            task_type=TaskType.CODE_GENERATION,
            user_id=context.get("user_id", "developer"),
            temperature=0.2,  # Lower temperature for code generation
            max_tokens=4000,
        )

        response = await self.smart_ai.generate_response(request)

        # Extract code from response
        modified_code = self._extract_code_from_response(response.content, language)

        return modified_code

    def _extract_code_from_response(self, response: str, language: str) -> str:
        """Extract code from AI response"""

        # Look for code blocks
        code_block_pattern = rf"```{language}?\n(.*?)```"
        matches = re.findall(code_block_pattern, response, re.DOTALL)

        if matches:
            return matches[0].strip()

        # If no code blocks, assume entire response is code
        return response.strip()

    def _create_diff(self, original: str, modified: str, file_path: str) -> str:
        """Create a unified diff between original and modified code"""

        original_lines = original.splitlines(keepends=True)
        modified_lines = modified.splitlines(keepends=True)

        diff = difflib.unified_diff(
            original_lines,
            modified_lines,
            fromfile=f"a/{file_path}",
            tofile=f"b/{file_path}",
            n=3,  # Context lines
        )

        return "".join(diff)

    async def _validate_modifications(
        self, file_path: str, original: str, modified: str
    ) -> dict[str, Any]:
        """Validate the modifications"""

        validation = {
            "syntax_valid": True,
            "imports_valid": True,
            "has_syntax_errors": False,
            "warnings": [],
            "errors": [],
        }

        language = self._detect_language(file_path)

        if language == "python":
            # Validate Python syntax
            try:
                ast.parse(modified)
                validation["syntax_valid"] = True
            except SyntaxError as e:
                validation["syntax_valid"] = False
                validation["has_syntax_errors"] = True
                validation["errors"].append(f"Syntax error at line {e.lineno}: {e.msg}")

            # Check for missing imports
            validation["imports_valid"] = self._validate_python_imports(
                original, modified
            )

        elif language in ["javascript", "typescript"]:
            # Basic JS/TS validation
            # Check for balanced brackets
            if not self._check_balanced_brackets(modified):
                validation["syntax_valid"] = False
                validation["errors"].append("Unbalanced brackets detected")

        # Check for common issues
        if len(modified) < len(original) * 0.1:
            validation["warnings"].append(
                "Code reduced by more than 90% - possible data loss"
            )

        if "TODO" in modified and "TODO" not in original:
            validation["warnings"].append("New TODO comments added")

        return validation

    def _validate_python_imports(self, original: str, modified: str) -> bool:
        """Validate Python imports are preserved"""

        try:
            original_tree = ast.parse(original)
            modified_tree = ast.parse(modified)

            original_imports = set()
            modified_imports = set()

            for node in ast.walk(original_tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        original_imports.add(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        original_imports.add(f"{module}.{alias.name}")

            for node in ast.walk(modified_tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        modified_imports.add(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        modified_imports.add(f"{module}.{alias.name}")

            # Check if any imports were removed
            removed_imports = original_imports - modified_imports

            return len(removed_imports) == 0

        except:
            return True  # If we can't parse, assume imports are valid

    def _check_balanced_brackets(self, code: str) -> bool:
        """Check if brackets are balanced in code"""

        stack = []
        brackets = {"(": ")", "[": "]", "{": "}"}

        for char in code:
            if char in brackets:
                stack.append(char)
            elif char in brackets.values():
                if not stack:
                    return False
                if brackets[stack.pop()] != char:
                    return False

        return len(stack) == 0

    def _calculate_change_metrics(self, original: str, modified: str) -> dict[str, int]:
        """Calculate metrics about the changes"""

        original_lines = original.splitlines()
        modified_lines = modified.splitlines()

        # Calculate diff statistics
        matcher = difflib.SequenceMatcher(None, original_lines, modified_lines)

        added = 0
        removed = 0
        modified_count = 0

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == "insert":
                added += j2 - j1
            elif tag == "delete":
                removed += i2 - i1
            elif tag == "replace":
                removed += i2 - i1
                added += j2 - j1
                modified_count += min(i2 - i1, j2 - j1)

        return {
            "lines_added": added,
            "lines_removed": removed,
            "lines_modified": modified_count,
            "total_changes": added + removed + modified_count,
            "original_lines": len(original_lines),
            "modified_lines": len(modified_lines),
        }

    def _requires_approval(
        self, metrics: dict[str, int], validation: dict[str, Any]
    ) -> bool:
        """Determine if changes require approval"""

        # Always require approval for syntax errors
        if not validation["syntax_valid"]:
            return True

        # Require approval for large changes
        if metrics["total_changes"] > 50:
            return True

        # Require approval if more than 30% of file changed
        if metrics["original_lines"] > 0:
            change_percentage = metrics["total_changes"] / metrics["original_lines"]
            if change_percentage > 0.3:
                return True

        # Require approval for any errors
        return bool(validation["errors"])

    def _detect_language(self, file_path: str) -> str:
        """Detect programming language from file extension"""

        ext_to_lang = {
            ".py": "python",
            ".js": "javascript",
            ".jsx": "javascript",
            ".ts": "typescript",
            ".tsx": "typescript",
            ".java": "java",
            ".cpp": "cpp",
            ".c": "c",
            ".go": "go",
            ".rs": "rust",
            ".rb": "ruby",
            ".php": "php",
            ".swift": "swift",
            ".kt": "kotlin",
            ".scala": "scala",
            ".r": "r",
            ".m": "matlab",
            ".jl": "julia",
            ".sh": "bash",
            ".ps1": "powershell",
            ".sql": "sql",
            ".html": "html",
            ".css": "css",
            ".scss": "scss",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".json": "json",
            ".xml": "xml",
            ".md": "markdown",
        }

        ext = Path(file_path).suffix.lower()
        return ext_to_lang.get(ext, "text")

    async def generate_file_content(self, file_path: str, description: str) -> str:
        """Generate content for a new file based on description"""

        language = self._detect_language(file_path)

        prompt = f"""
        Create a new {language} file with the following requirements:

        File: {file_path}
        Description: {description}

        Context:
        - Project: Sophia AI (Enterprise AI Orchestrator)
        - Language: {language}
        - Include appropriate imports, documentation, and error handling
        - Follow best practices and coding standards

        Generate complete, production-ready code.
        """

        request = LLMRequest(
            messages=[{"role": "user", "content": prompt}],
            task_type=TaskType.CODE_GENERATION,
            user_id="developer",
            temperature=0.3,
            max_tokens=4000,
        )

        response = await self.smart_ai.generate_response(request)

        # Extract code from response
        return self._extract_code_from_response(response.content, language)
