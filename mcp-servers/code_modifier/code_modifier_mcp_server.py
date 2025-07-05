"""
Code Modifier MCP Server - Natural language code modification through MCP protocol
"""

import asyncio
import logging
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from fastapi import APIRouter

from backend.mcp_servers.base.standardized_mcp_server import (
    HealthCheckResult,
    HealthStatus,
    MCPServerConfig,
    ModelProvider,
    ServerCapability,
    StandardizedMCPServer,
    SyncPriority,
)
from backend.services.code_modification_service import CodeModificationService

logger = logging.getLogger(__name__)


class CodeModifierMCPServer(StandardizedMCPServer):
    """
    MCP server for code modification operations
    """

    def __init__(self):
        config = MCPServerConfig(
            server_name="code_modifier",
            port=9050,
            sync_priority=SyncPriority.HIGH,  # Use enum value
            enable_ai_processing=True,
            enable_webfetch=False,
            enable_self_knowledge=True,
            enable_improved_diff=True,
            preferred_model=ModelProvider.CLAUDE_4,
        )
        super().__init__(config)
        self.code_service = CodeModificationService()
        self.workspace_root = Path(os.getenv("WORKSPACE_ROOT", os.getcwd()))

        # Setup routes
        self._setup_server_routes()

    def _setup_server_routes(self):
        """Setup server-specific routes"""
        router = APIRouter()

        @router.post("/modify_file")
        async def modify_file(
            file_path: str, instructions: str, preview_only: bool = True
        ) -> dict[str, Any]:
            """Modify a file based on natural language instructions"""
            return await self.modify_file(file_path, instructions, preview_only)

        @router.post("/create_file")
        async def create_file(
            file_path: str, description: str, content: str | None = None
        ) -> dict[str, Any]:
            """Create a new file"""
            return await self.create_file(file_path, description, content)

        @router.post("/analyze_file")
        async def analyze_file(file_path: str) -> dict[str, Any]:
            """Analyze a file and suggest improvements"""
            return await self.analyze_file(file_path)

        @router.get("/list_files")
        async def list_files(
            directory: str = ".", pattern: str | None = None
        ) -> dict[str, Any]:
            """List files in a directory"""
            return await self.list_files(directory, pattern)

        self.app.include_router(router, prefix="/api/v1")

    async def server_specific_init(self) -> None:
        """Server-specific initialization logic"""
        logger.info("Initializing Code Modifier MCP Server...")
        # Initialize code service if needed

    async def server_specific_cleanup(self) -> None:
        """Server-specific cleanup logic"""
        logger.info("Cleaning up Code Modifier MCP Server...")

    async def server_specific_health_check(self) -> HealthCheckResult:
        """Server-specific health check logic"""
        try:
            # Check if workspace is accessible
            workspace_exists = self.workspace_root.exists()

            return HealthCheckResult(
                component="code_modifier",  # Add component name
                status=HealthStatus.HEALTHY
                if workspace_exists
                else HealthStatus.DEGRADED,
                response_time_ms=10,
                error_message=None if workspace_exists else "Workspace not accessible",
                metadata={"workspace": str(self.workspace_root)},
            )
        except Exception as e:
            return HealthCheckResult(
                component="code_modifier",  # Add component name
                status=HealthStatus.UNHEALTHY,
                response_time_ms=0,
                error_message=str(e),
            )

    async def check_external_api(self) -> bool:
        """Check if external API is accessible"""
        # Code modifier doesn't have external API dependencies
        return True

    async def get_server_capabilities(self) -> list[ServerCapability]:
        """Get server-specific capabilities"""
        return [
            ServerCapability(
                name="modify_file",
                description="Modify code files using natural language instructions",
                category="code",
                available=True,
                version="1.0.0",
                metadata={"preview_mode": True},
            ),
            ServerCapability(
                name="create_file",
                description="Create new files with AI-generated content",
                category="code",
                available=True,
                version="1.0.0",
            ),
            ServerCapability(
                name="analyze_file",
                description="Analyze code files and suggest improvements",
                category="code",
                available=True,
                version="1.0.0",
            ),
            ServerCapability(
                name="list_files",
                description="List files in the workspace",
                category="filesystem",
                available=True,
                version="1.0.0",
            ),
        ]

    async def sync_data(self) -> dict[str, Any]:
        """Synchronize data with external platform"""
        # Code modifier doesn't sync with external platforms
        return {
            "status": "success",
            "message": "No external sync required",
            "timestamp": datetime.now(UTC).isoformat(),
        }

    async def process_with_ai(
        self, data: Any, model: ModelProvider | None = None
    ) -> Any:
        """Process data using AI capabilities"""
        # This is handled by the code_service
        return {"message": "AI processing handled by code service"}

    async def modify_file(
        self, file_path: str, instructions: str, preview_only: bool = True
    ) -> dict[str, Any]:
        """
        Modify a file based on natural language instructions

        Args:
            file_path: Path to the file to modify
            instructions: Natural language instructions for modification
            preview_only: If True, only preview changes without applying

        Returns:
            Dict with modification results including diff and validation
        """
        logger.info(
            f"Modifying file {file_path} with instructions: {instructions[:100]}..."
        )

        result = await self.code_service.modify_code(
            file_path, instructions, {"workspace_root": str(self.workspace_root)}
        )

        if result["success"] and not preview_only:
            # Apply the changes
            full_path = self.workspace_root / file_path
            try:
                full_path.write_text(result["modified_code"])
                result["applied"] = True
                logger.info(f"Applied changes to {file_path}")
            except Exception as e:
                result["applied"] = False
                result["apply_error"] = str(e)
                logger.error(f"Failed to apply changes: {e}")
        else:
            result["applied"] = False

        return result

    async def create_file(
        self, file_path: str, description: str, content: str | None = None
    ) -> dict[str, Any]:
        """
        Create a new file

        Args:
            file_path: Path where the file should be created
            description: Description of what the file should contain
            content: Optional content to use (if not provided, will be generated)

        Returns:
            Dict with creation results
        """
        logger.info(f"Creating file {file_path}: {description}")

        full_path = self.workspace_root / file_path

        # Check if file already exists
        if full_path.exists():
            return {"success": False, "error": f"File already exists: {file_path}"}

        # Ensure directory exists
        full_path.parent.mkdir(parents=True, exist_ok=True)

        # Generate content if needed
        if not content:
            content = await self.code_service.generate_file_content(
                file_path, description
            )

        # Write file
        try:
            full_path.write_text(content)

            return {
                "success": True,
                "file_path": file_path,
                "size": len(content),
                "created": True,
                "content": content,
            }
        except Exception as e:
            return {"success": False, "error": f"Failed to create file: {str(e)}"}

    async def analyze_file(self, file_path: str) -> dict[str, Any]:
        """
        Analyze a file and suggest improvements

        Args:
            file_path: Path to the file to analyze

        Returns:
            Dict with analysis results and suggestions
        """
        logger.info(f"Analyzing file {file_path}")

        full_path = self.workspace_root / file_path

        if not full_path.exists():
            return {"success": False, "error": f"File not found: {file_path}"}

        try:
            content = full_path.read_text()

            # Use code service to validate
            validation = await self.code_service._validate_modifications(
                file_path, content, content  # Same content for analysis
            )

            # Calculate metrics
            metrics = self.code_service._calculate_change_metrics(
                content, content  # Same content for baseline
            )

            # Language detection
            language = self.code_service._detect_language(file_path)

            return {
                "success": True,
                "file_path": file_path,
                "language": language,
                "metrics": {
                    "lines": metrics["original_lines"],
                    "size": len(content),
                    "has_syntax_errors": validation.get("has_syntax_errors", False),
                },
                "validation": validation,
                "suggestions": self._generate_suggestions(validation, language),
            }

        except Exception as e:
            return {"success": False, "error": f"Failed to analyze file: {str(e)}"}

    async def list_files(
        self, directory: str = ".", pattern: str | None = None
    ) -> dict[str, Any]:
        """
        List files in a directory

        Args:
            directory: Directory to list (relative to workspace root)
            pattern: Optional glob pattern to filter files

        Returns:
            Dict with file listing
        """
        logger.info(f"Listing files in {directory}")

        full_path = self.workspace_root / directory

        if not full_path.exists():
            return {"success": False, "error": f"Directory not found: {directory}"}

        if not full_path.is_dir():
            return {"success": False, "error": f"Not a directory: {directory}"}

        try:
            files = []

            if pattern:
                # Use glob pattern
                for file_path in full_path.glob(pattern):
                    if file_path.is_file():
                        relative_path = file_path.relative_to(self.workspace_root)
                        files.append(
                            {
                                "path": str(relative_path),
                                "size": file_path.stat().st_size,
                                "modified": file_path.stat().st_mtime,
                            }
                        )
            else:
                # List all files
                for file_path in full_path.iterdir():
                    if file_path.is_file():
                        relative_path = file_path.relative_to(self.workspace_root)
                        files.append(
                            {
                                "path": str(relative_path),
                                "size": file_path.stat().st_size,
                                "modified": file_path.stat().st_mtime,
                            }
                        )

            return {
                "success": True,
                "directory": directory,
                "files": sorted(files, key=lambda x: x["path"]),
                "count": len(files),
            }

        except Exception as e:
            return {"success": False, "error": f"Failed to list files: {str(e)}"}

    def _generate_suggestions(
        self, validation: dict[str, Any], language: str
    ) -> list[str]:
        """Generate improvement suggestions based on validation"""

        suggestions = []

        if not validation["syntax_valid"]:
            suggestions.append("Fix syntax errors before proceeding")

        if not validation["imports_valid"]:
            suggestions.append("Review and fix import statements")

        if validation["warnings"]:
            for warning in validation["warnings"]:
                suggestions.append(f"Warning: {warning}")

        # Language-specific suggestions
        if language == "python":
            suggestions.append("Consider adding type hints for better code clarity")
            suggestions.append("Ensure PEP 8 compliance with proper formatting")

        elif language in ["javascript", "typescript"]:
            suggestions.append("Consider using ESLint for code quality")
            suggestions.append("Add JSDoc comments for better documentation")

        return suggestions


# Entry point for running as standalone server
if __name__ == "__main__":
    server = CodeModifierMCPServer()
    asyncio.run(server.start())
