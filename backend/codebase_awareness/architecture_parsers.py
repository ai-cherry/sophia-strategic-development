"""Architectural Parsers for the Codebase Awareness System.

Handles extracting structured information from various components of the codebase,
such as API routes, MCP tool definitions, and database schemas.
"""

import ast
import logging
import re
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class ArchitectureParser:
    """A class containing static methods to parse different architectural.

            components of the Sophia AI codebase.
    """

    @staticmethod
    def parse_fastapi_routes(file_content: str, file_path: str) -> List[Dict[str, Any]]:
        """Parses a Python file to find FastAPI route definitions.

                        Args:
                            file_content: The content of the Python file.
                            file_path: The path of the file, for context.

                        Returns:
                            A list of dictionaries, each representing a discovered API endpoint.
        """endpoints = []

        try:
            tree = ast.parse(file_content)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.decorator_list:
                    for decorator in node.decorator_list:
                        if (
                            isinstance(decorator, ast.Call)
                            and hasattr(decorator.func, "value")
                            and hasattr(decorator.func.value, "id")
                            and decorator.func.value.id in ["router", "app"]
                        ):
                            http_method = decorator.func.attr.upper()  # GET, POST, etc.
                            path = (
                                decorator.args[0].s
                                if decorator.args
                                and isinstance(decorator.args[0], ast.Constant)
                                else "unknown"
                            )

                            endpoints.append(
                                {
                                    "type": "api_endpoint",
                                    "method": http_method,
                                    "path": path,
                                    "function_name": node.name,
                                    "docstring": ast.get_docstring(node) or "",
                                    "file_path": file_path,
                                }
                            )
        except SyntaxError as e:
            logger.error(f"Syntax error parsing FastAPI routes in {file_path}: {e}")
        return endpoints

    @staticmethod
    def parse_mcp_tools(file_content: str, file_path: str) -> List[Dict[str, Any]]:
        """Parses a Python file to find MCP Tool definitions.

                        Args:
                            file_content: The content of the Python file.
                            file_path: The path of the file, for context.

                        Returns:
                            A list of dictionaries, each representing a discovered MCP tool.
        """tools = []

        try:
            tree = ast.parse(file_content)
            for node in ast.walk(tree):
                if (
                    isinstance(node, ast.Call)
                    and hasattr(node.func, "id")
                    and node.func.id == "Tool"
                ):
                    tool_info = {"type": "mcp_tool", "file_path": file_path}
                    for kw in node.keywords:
                        if kw.arg == "name" and isinstance(kw.value, ast.Constant):
                            tool_info["name"] = kw.value.s
                        elif kw.arg == "description" and isinstance(
                            kw.value, ast.Constant
                        ):
                            tool_info["description"] = kw.value.s
                    if "name" in tool_info:
                        tools.append(tool_info)
        except SyntaxError as e:
            logger.error(f"Syntax error parsing MCP tools in {file_path}: {e}")
        return tools

    @staticmethod
    def parse_db_schema(file_content: str, file_path: str) -> List[Dict[str, Any]]:
        """Parses a SQL file to find table definitions.

                        Args:
                            file_content: The content of the SQL file.
                            file_path: The path of the file, for context.

                        Returns:
                            A list of dictionaries, each representing a discovered database table.
        """tables = []

        # A simple regex to find CREATE TABLE statements and their columns.
        # A real implementation might use a more robust SQL parsing library.
        table_pattern = re.compile(
            r"CREATE TABLE\s+(\w+)\s+\((.*?)\);", re.DOTALL | re.IGNORECASE
        )
        column_pattern = re.compile(r"^\s*(\w+)\s+([\w\(\)]+)", re.MULTILINE)

        for match in table_pattern.finditer(file_content):
            table_name = match.group(1)
            columns_str = match.group(2)
            columns = [
                f"{col_match.group(1)} ({col_match.group(2)})"
                for col_match in column_pattern.finditer(columns_str)
            ]

            tables.append(
                {
                    "type": "db_table",
                    "table_name": table_name,
                    "columns": columns,
                    "raw_schema": f"CREATE TABLE {table_name} ({columns_str.strip()});",
                    "file_path": file_path,
                }
            )
        return tables

    @staticmethod
    def parse_python_code(file_content: str, file_path: str) -> List[Dict[str, Any]]:
        """Parses a Python file to extract classes and functions.

                        Args:
                            file_content: The content of the Python file.
                            file_path: The path of the file, for context.

                        Returns:
                            A list of dictionaries, each representing a class or function.
        """
        items = []
        try:
            tree = ast.parse(file_content)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    items.append(
                        {
                            "type": "python_function",
                            "name": node.name,
                            "docstring": ast.get_docstring(node) or "",
                            "code": ast.get_source_segment(file_content, node),
                            "file_path": file_path,
                        }
                    )
                elif isinstance(node, ast.ClassDef):
                    items.append(
                        {
                            "type": "python_class",
                            "name": node.name,
                            "docstring": ast.get_docstring(node) or "",
                            "code": ast.get_source_segment(file_content, node),
                            "file_path": file_path,
                        }
                    )
        except (SyntaxError, TypeError) as e:
            logger.error(f"Error parsing Python code in {file_path}: {e}")
        return items
