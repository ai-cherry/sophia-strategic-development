#!/usr/bin/env python3
"""
AI Code Quality MCP Server
Port: 9025

Provides AI-powered code quality automation including:
- Real-time syntax error detection and auto-repair
- Import dependency analysis and optimization
- Security vulnerability scanning and patching
- Code quality metrics and trend analysis
- Automated refactoring suggestions
- Direct code editing via natural language
"""

import ast
import asyncio
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

# Add backend to path
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

import mcp.server.stdio
from mcp.types import TextContent, Tool

# Import our base class
from backend.mcp_servers.base.unified_mcp_base import UnifiedMCPBase


class AICodeQualityMCPServer(UnifiedMCPBase):
    """AI-powered code quality automation and direct code editing"""

    def __init__(self, name: str = "ai_code_quality"):
        super().__init__(name=name, port=9025, version="1.0.0")
        self.backup_dir = Path("backups/ai_code_quality")
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        # Code quality patterns
        self.syntax_patterns = {
            "missing_colon": {
                "pattern": r"(if|elif|else|for|while|def|class|try|except|finally|with)\s+[^:]+$",
                "keywords": [
                    "if",
                    "elif",
                    "else",
                    "for",
                    "while",
                    "def",
                    "class",
                    "try",
                    "except",
                    "finally",
                    "with",
                ],
            },
            "async_def": {"pattern": r"async\s+def\s+", "fix_type": "async_function"},
        }

        # Track fixed files for reporting
        self.fixed_files: set[str] = set()
        self.failed_files: dict[str, str] = {}

    def get_tool_descriptions(self) -> list[Tool]:
        """Define available tools"""
        return [
            Tool(
                name="fix_syntax_errors",
                description="Fix syntax errors in Python files using AI-powered analysis",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "File or directory path to fix syntax errors",
                        },
                        "auto_fix": {
                            "type": "boolean",
                            "description": "Automatically apply fixes (default: true)",
                            "default": True,
                        },
                    },
                    "required": ["path"],
                },
            ),
            Tool(
                name="analyze_code_quality",
                description="Analyze code quality metrics and identify issues",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "File or directory path to analyze",
                        },
                        "include_security": {
                            "type": "boolean",
                            "description": "Include security vulnerability analysis",
                            "default": True,
                        },
                    },
                    "required": ["path"],
                },
            ),
            Tool(
                name="fix_imports",
                description="Fix and optimize import statements",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "File or directory path to fix imports",
                        }
                    },
                    "required": ["path"],
                },
            ),
            Tool(
                name="refactor_code",
                description="Apply AI-powered refactoring suggestions",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "File path to refactor",
                        },
                        "refactor_type": {
                            "type": "string",
                            "description": "Type of refactoring: extract_method, reduce_complexity, remove_duplication",
                            "enum": [
                                "extract_method",
                                "reduce_complexity",
                                "remove_duplication",
                            ],
                        },
                    },
                    "required": ["path", "refactor_type"],
                },
            ),
            Tool(
                name="edit_code",
                description="Edit code using natural language instructions",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "instruction": {
                            "type": "string",
                            "description": "Natural language instruction for code editing",
                        },
                        "path": {
                            "type": "string",
                            "description": "Optional specific file path to edit",
                        },
                    },
                    "required": ["instruction"],
                },
            ),
        ]

    async def fix_syntax_errors(
        self, path: str, auto_fix: bool = True
    ) -> dict[str, Any]:
        """Fix syntax errors in Python files"""
        path_obj = Path(path)

        if path_obj.is_file():
            files = [path_obj] if path_obj.suffix == ".py" else []
        else:
            files = list(path_obj.rglob("*.py"))

        results = {"total_files": 0, "fixed": 0, "failed": 0, "details": []}

        # First identify files with syntax errors
        syntax_error_files = []
        for file_path in files:
            try:
                with open(file_path) as f:
                    content = f.read()
                ast.parse(content)
            except SyntaxError as e:
                syntax_error_files.append((file_path, e))
                results["total_files"] += 1

        # Fix each file
        for file_path, error in syntax_error_files:
            result = await self._fix_file_syntax(file_path, error, auto_fix)
            results["details"].append(result)

            if result["status"] == "fixed":
                results["fixed"] += 1
                self.fixed_files.add(str(file_path))
            else:
                results["failed"] += 1
                self.failed_files[str(file_path)] = result.get("error", "Unknown error")

        return results

    async def _fix_file_syntax(
        self, file_path: Path, error: SyntaxError, auto_fix: bool
    ) -> dict[str, Any]:
        """Fix syntax errors in a single file"""
        # Backup the file
        backup_path = (
            self.backup_dir
            / f"{file_path.name}.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )

        try:
            content = file_path.read_text()
            backup_path.write_text(content)
        except Exception as e:
            return {
                "file": str(file_path),
                "status": "failed",
                "error": f"Failed to backup: {e}",
            }

        # Analyze and fix the error
        fixed_content = await self._apply_syntax_fix(content, error, file_path)

        if fixed_content != content:
            if auto_fix:
                try:
                    file_path.write_text(fixed_content)
                    # Verify the fix
                    ast.parse(fixed_content)
                    return {
                        "file": str(file_path),
                        "status": "fixed",
                        "error_type": self._categorize_syntax_error(error),
                        "line": error.lineno,
                    }
                except SyntaxError as e:
                    return {
                        "file": str(file_path),
                        "status": "partially_fixed",
                        "original_error": str(error),
                        "remaining_error": str(e),
                    }
            else:
                return {
                    "file": str(file_path),
                    "status": "fix_available",
                    "error_type": self._categorize_syntax_error(error),
                    "suggested_fix": "Fix available but auto_fix=False",
                }

        return {
            "file": str(file_path),
            "status": "failed",
            "error": str(error),
            "line": error.lineno,
        }

    async def _apply_syntax_fix(
        self, content: str, error: SyntaxError, file_path: Path
    ) -> str:
        """Apply intelligent syntax fixes"""
        lines = content.split("\n")
        error_msg = str(error).lower()

        if error.lineno and error.lineno <= len(lines):
            line_idx = error.lineno - 1
            line = lines[line_idx]

            # Fix async def issues
            if "async" in error_msg and "identifier" in error_msg:
                # Common issue: for async def or with async def
                if re.search(r"(for|with)\s+async\s+def", line):
                    # This is invalid syntax, needs refactoring
                    lines[line_idx] = re.sub(
                        r"(for|with)\s+async\s+def\s+(\w+)", r"\1 \2", line
                    )
                    return "\n".join(lines)

            # Fix missing colons
            if "expected ':'" in error_msg:
                for keyword in self.syntax_patterns["missing_colon"]["keywords"]:
                    if line.strip().startswith(keyword) and not line.rstrip().endswith(
                        ":"
                    ):
                        lines[line_idx] = line.rstrip() + ":"
                        return "\n".join(lines)

            # Fix indentation
            if "indent" in error_msg:
                fixed_line = self._fix_indentation(lines, line_idx)
                if fixed_line != line:
                    lines[line_idx] = fixed_line
                    return "\n".join(lines)

            # Fix unclosed brackets/quotes
            if "eof" in error_msg or "eol" in error_msg:
                return self._fix_unclosed_delimiters(content)

        return content

    def _fix_indentation(self, lines: list[str], line_idx: int) -> str:
        """Fix indentation issues"""
        if line_idx == 0:
            return lines[line_idx].lstrip()

        # Find previous non-empty line
        prev_idx = line_idx - 1
        while prev_idx >= 0 and not lines[prev_idx].strip():
            prev_idx -= 1

        if prev_idx >= 0:
            prev_line = lines[prev_idx]
            prev_indent = len(prev_line) - len(prev_line.lstrip())

            # Check if previous line should increase indent
            indent_keywords = [
                "if",
                "elif",
                "else",
                "for",
                "while",
                "def",
                "class",
                "try",
                "except",
                "finally",
                "with",
            ]
            if any(prev_line.strip().startswith(kw) for kw in indent_keywords):
                if prev_line.rstrip().endswith(":"):
                    return " " * (prev_indent + 4) + lines[line_idx].lstrip()

            return " " * prev_indent + lines[line_idx].lstrip()

        return lines[line_idx]

    def _fix_unclosed_delimiters(self, content: str) -> str:
        """Fix unclosed brackets and quotes"""
        # Count delimiters
        delimiters = {"(": ")", "[": "]", "{": "}", '"': '"', "'": "'"}

        counts = {}
        for open_delim, close_delim in delimiters.items():
            if open_delim == close_delim:  # Quotes
                count = content.count(open_delim)
                if count % 2 != 0:
                    content += close_delim
            else:  # Brackets
                open_count = content.count(open_delim)
                close_count = content.count(close_delim)
                diff = open_count - close_count
                if diff > 0:
                    content += close_delim * diff

        return content

    def _categorize_syntax_error(self, error: SyntaxError) -> str:
        """Categorize syntax error type"""
        error_str = str(error).lower()

        if "expected ':'" in error_str:
            return "missing_colon"
        elif "indent" in error_str:
            return "indentation_error"
        elif "eof" in error_str or "eol" in error_str:
            return "unclosed_delimiter"
        elif "async" in error_str:
            return "async_syntax_error"
        elif "identifier" in error_str:
            return "invalid_identifier"
        else:
            return "other_syntax_error"

    async def analyze_code_quality(
        self, path: str, include_security: bool = True
    ) -> dict[str, Any]:
        """Analyze code quality metrics"""
        # Run ruff check
        result = subprocess.run(
            ["ruff", "check", path, "--output-format", "json"],
            capture_output=True,
            text=True,
        )

        issues = []
        if result.stdout:
            try:
                issues = json.loads(result.stdout)
            except:
                pass

        # Categorize issues
        categories = {}
        for issue in issues:
            code = issue.get("code", "unknown")
            categories[code] = categories.get(code, 0) + 1

        # Security analysis if requested
        security_issues = []
        if include_security:
            sec_result = subprocess.run(
                ["ruff", "check", path, "--select", "S"], capture_output=True, text=True
            )
            if sec_result.stdout:
                for line in sec_result.stdout.strip().split("\n"):
                    if line and ":" in line:
                        security_issues.append(line)

        return {
            "total_issues": len(issues),
            "categories": categories,
            "security_issues": len(security_issues),
            "top_issues": sorted(categories.items(), key=lambda x: x[1], reverse=True)[
                :10
            ],
            "files_analyzed": len(set(issue.get("filename", "") for issue in issues)),
        }

    async def fix_imports(self, path: str) -> dict[str, Any]:
        """Fix and optimize imports"""
        # Use isort for import optimization
        result = subprocess.run(
            ["isort", path, "--check-only", "--diff"], capture_output=True, text=True
        )

        if result.returncode != 0:
            # Apply fixes
            fix_result = subprocess.run(["isort", path], capture_output=True, text=True)

            return {
                "status": "fixed" if fix_result.returncode == 0 else "failed",
                "files_modified": result.stdout.count("---") // 2,
                "message": "Imports have been optimized",
            }

        return {
            "status": "no_changes_needed",
            "message": "All imports are already properly organized",
        }

    async def refactor_code(self, path: str, refactor_type: str) -> dict[str, Any]:
        """Apply AI-powered refactoring"""
        # This is a placeholder for more advanced refactoring
        # In a real implementation, this would use AI models for code understanding

        if refactor_type == "extract_method":
            return await self._extract_method_refactoring(path)
        elif refactor_type == "reduce_complexity":
            return await self._reduce_complexity_refactoring(path)
        elif refactor_type == "remove_duplication":
            return await self._remove_duplication_refactoring(path)

        return {
            "status": "unsupported",
            "message": f"Refactoring type '{refactor_type}' not yet implemented",
        }

    async def _extract_method_refactoring(self, path: str) -> dict[str, Any]:
        """Extract method refactoring"""
        # Analyze file for long methods
        with open(path) as f:
            content = f.read()

        try:
            tree = ast.parse(content)
            long_functions = []

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Count lines in function
                    if hasattr(node, "end_lineno") and hasattr(node, "lineno"):
                        lines = node.end_lineno - node.lineno
                        if lines > 50:  # Functions longer than 50 lines
                            long_functions.append(
                                {
                                    "name": node.name,
                                    "lines": lines,
                                    "start": node.lineno,
                                }
                            )

            return {
                "status": "analysis_complete",
                "long_functions": long_functions,
                "recommendation": f"Found {len(long_functions)} functions that could benefit from extraction",
            }

        except Exception as e:
            return {"status": "failed", "error": str(e)}

    async def _reduce_complexity_refactoring(self, path: str) -> dict[str, Any]:
        """Reduce cyclomatic complexity"""
        # This would analyze complexity and suggest simplifications
        return {
            "status": "analysis_complete",
            "message": "Complexity analysis requires additional tooling",
        }

    async def _remove_duplication_refactoring(self, path: str) -> dict[str, Any]:
        """Remove code duplication"""
        # This would identify duplicate code blocks
        return {
            "status": "analysis_complete",
            "message": "Duplication detection requires additional tooling",
        }

    async def edit_code(
        self, instruction: str, path: Optional[str] = None
    ) -> dict[str, Any]:
        """Edit code using natural language instructions"""
        # Parse the instruction to understand the intent
        instruction_lower = instruction.lower()

        # Handle specific instruction patterns
        if "fix all syntax errors" in instruction_lower:
            target_path = path or "."
            return await self.fix_syntax_errors(target_path, auto_fix=True)

        elif (
            "optimize imports" in instruction_lower
            or "fix imports" in instruction_lower
        ):
            target_path = path or "."
            return await self.fix_imports(target_path)

        elif "analyze" in instruction_lower and "quality" in instruction_lower:
            target_path = path or "."
            return await self.analyze_code_quality(target_path)

        elif "remove unused" in instruction_lower and "arguments" in instruction_lower:
            return await self._remove_unused_arguments(path)

        else:
            return {
                "status": "understood",
                "message": f"Instruction understood: '{instruction}'",
                "note": "Advanced natural language code editing coming soon",
            }

    async def _remove_unused_arguments(self, path: Optional[str]) -> dict[str, Any]:
        """Remove unused function arguments"""
        target_path = path or "."

        # Run ruff to find unused arguments
        result = subprocess.run(
            ["ruff", "check", target_path, "--select", "ARG"],
            capture_output=True,
            text=True,
        )

        unused_count = result.stdout.count("ARG")

        return {
            "status": "analysis_complete",
            "unused_arguments": unused_count,
            "message": f"Found {unused_count} unused arguments",
            "note": "Automatic removal requires careful API compatibility checking",
        }

    async def handle_tool_call(
        self, tool_name: str, arguments: dict[str, Any]
    ) -> list[TextContent]:
        """Handle tool calls"""
        try:
            if tool_name == "fix_syntax_errors":
                result = await self.fix_syntax_errors(
                    arguments["path"], arguments.get("auto_fix", True)
                )
            elif tool_name == "analyze_code_quality":
                result = await self.analyze_code_quality(
                    arguments["path"], arguments.get("include_security", True)
                )
            elif tool_name == "fix_imports":
                result = await self.fix_imports(arguments["path"])
            elif tool_name == "refactor_code":
                result = await self.refactor_code(
                    arguments["path"], arguments["refactor_type"]
                )
            elif tool_name == "edit_code":
                result = await self.edit_code(
                    arguments["instruction"], arguments.get("path")
                )
            else:
                result = {"error": f"Unknown tool: {tool_name}"}

            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        except Exception as e:
            self.logger.error(f"Error handling tool {tool_name}: {e}")
            return [
                TextContent(type="text", text=json.dumps({"error": str(e)}, indent=2))
            ]


async def main():
    """Main entry point"""
    server = AICodeQualityMCPServer()

    # Run as MCP server
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream, write_stream, server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
