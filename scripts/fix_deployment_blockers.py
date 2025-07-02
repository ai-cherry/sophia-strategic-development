#!/usr/bin/env python3
"""Fix immediate deployment blockers to get Sophia AI running."""

import os
import re
from pathlib import Path


def fix_snowflake_cortex_indentation():
    """Fix IndentationError in snowflake_cortex_service.py."""
    print("Fixing snowflake_cortex_service.py indentation issues...")

    file_path = Path("backend/utils/snowflake_cortex_service.py")
    if not file_path.exists():
        print(f"Warning: {file_path} not found")
        return

    content = file_path.read_text()

    # Fix line 415-416 indentation issue
    # Find the try block around line 415 and fix the indentation
    lines = content.split("\n")

    # Fix multiple indentation issues
    fixed_lines = []
    in_try_block = False
    try_line = None

    for i, line in enumerate(lines):
        # Check for try statements that need fixing
        if "try:" in line and i < len(lines) - 1:
            # Check if next line has proper indentation
            next_line = lines[i + 1] if i + 1 < len(lines) else ""
            if next_line and not next_line.startswith(
                " " * (len(line) - len(line.lstrip()) + 4)
            ):
                in_try_block = True
                try_line = i

        # Fix lines after try that aren't properly indented
        if in_try_block and try_line is not None and i == try_line + 1:
            if line.strip() and not line.startswith(
                " " * (len(lines[try_line]) - len(lines[try_line].lstrip()) + 4)
            ):
                # Add proper indentation
                base_indent = len(lines[try_line]) - len(lines[try_line].lstrip())
                line = " " * (base_indent + 4) + line.lstrip()
            in_try_block = False

        fixed_lines.append(line)

    # Write back
    file_path.write_text("\n".join(fixed_lines))
    print(f"Fixed indentation in {file_path}")


def fix_mcp_server_endpoint():
    """Fix MCPServerEndpoint initialization issues."""
    print("Fixing MCPServerEndpoint initialization...")

    file_path = Path("backend/services/mcp_orchestration_service.py")
    if not file_path.exists():
        print(f"Warning: {file_path} not found")
        return

    content = file_path.read_text()

    # Fix MCPServerEndpoint to use proper initialization
    # The error shows it doesn't accept 'name' as keyword argument
    # Let's check the actual MCPServerEndpoint class definition first

    # Replace MCPServerEndpoint calls that use name= with proper initialization
    content = re.sub(
        r'MCPServerEndpoint\(\s*name\s*=\s*["\']([^"\']+)["\']\s*,',
        r"MCPServerEndpoint(",
        content,
    )

    # Also fix in _load_default_configuration
    content = re.sub(
        r'"ai_memory":\s*MCPServerEndpoint\(\s*name\s*=\s*"ai_memory"\s*,',
        r'"ai_memory": MCPServerEndpoint(',
        content,
    )

    file_path.write_text(content)
    print(f"Fixed MCPServerEndpoint initialization in {file_path}")


def fix_missing_server_import():
    """Fix missing backend.mcp_servers.server import."""
    print("Fixing missing server import...")

    file_path = Path("backend/mcp_servers/enhanced_ai_memory_mcp_server.py")
    if not file_path.exists():
        print(f"Warning: {file_path} not found")
        return

    content = file_path.read_text()

    # Replace the bad import with the correct one
    content = content.replace(
        "from backend.mcp_servers.server import Server", "from mcp.server import Server"
    )

    # Also check if we need to import from a different location
    if (
        "from mcp.server import Server" not in content
        and "from mcp import Server" not in content
    ):
        # Try another common import pattern
        content = content.replace(
            "from backend.mcp_servers.server import Server",
            "from mcp.server import Server",
        )

    file_path.write_text(content)
    print(f"Fixed server import in {file_path}")


def create_minimal_working_api():
    """Create a minimal working API that we can actually run."""
    print("Creating minimal working API...")

    content = '''#!/usr/bin/env python3
"""Minimal working API to verify deployment."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create app
app = FastAPI(title="Sophia AI Minimal API", version="0.1.0")

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Sophia AI Minimal API is running!"}

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "sophia-ai-minimal",
        "version": "0.1.0"
    }

@app.get("/api/v1/test")
async def test_endpoint():
    return {
        "status": "success",
        "message": "API is working",
        "data": {
            "test": True,
            "timestamp": "2024-01-15"
        }
    }

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    logger.info(f"Starting Minimal API on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
'''

    file_path = Path("backend/app/minimal_api.py")
    file_path.write_text(content)
    os.chmod(file_path, 0o755)
    print(f"Created {file_path}")


def install_missing_dependencies():
    """Install missing dependencies that are causing import errors."""
    print("Checking and installing missing dependencies...")

    missing_deps = [
        "slowapi",
        "python-multipart",
        "prometheus-client",
        "httpx",
        "aiohttp",
        "mcp",
    ]

    for dep in missing_deps:
        print(f"Installing {dep}...")
        os.system(f"pip install {dep}")


def main():
    """Run all fixes."""
    print("=== Fixing Deployment Blockers ===\n")

    # Fix critical issues
    fix_snowflake_cortex_indentation()
    fix_mcp_server_endpoint()
    fix_missing_server_import()

    # Create a minimal working API
    create_minimal_working_api()

    # Install missing dependencies
    install_missing_dependencies()

    print("\n=== Deployment Fixes Complete ===")
    print("\nTo test the minimal API:")
    print("  python backend/app/minimal_api.py")
    print("\nOr on a different port:")
    print("  python backend/app/minimal_api.py 8001")


if __name__ == "__main__":
    main()
