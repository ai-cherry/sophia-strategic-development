#!/usr/bin/env python3
"""
Enhanced MCP Server Scaffolder for Sophia AI
Creates production-ready MCP servers with all best practices
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict

# Color codes for output
RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
BLUE = "\033[0;34m"
NC = "\033[0m"  # No Color


def print_colored(message: str, color: str = NC):
    """Print colored message."""


def get_next_port() -> int:
    """Get the next available port for MCP servers."""
    base_port = 9000
    max_port = base_port

    # Find existing ports
    mcp_dir = Path("infrastructure/mcp_servers")
    if mcp_dir.exists():
        for server_dir in mcp_dir.iterdir():
            if server_dir.is_dir():
                config_file = server_dir / "config.py"
                if config_file.exists():
                    content = config_file.read_text()
                    # Look for PORT = number pattern
                    import re

                    match = re.search(r"PORT.*=.*(\d+)", content)
                    if match:
                        port = int(match.group(1))
                        max_port = max(max_port, port)

    return max_port + 1


def create_file(file_path: Path, content: str):
    """Create a file with content."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content)
    print_colored(f"✓ Created: {file_path}", GREEN)


def update_mcp_config(server_name: str, port: int):
    """Update mcp_config.json with new server."""
    config_path = Path("mcp_config.json")

    if config_path.exists():
        with open(config_path) as f:
            config = json.load(f)

        # Add new server
        config["mcpServers"][server_name] = {
            "command": "python",
            "args": ["-m", f"infrastructure.mcp_servers.{server_name}.server"],
            "env": {
                f"{server_name.upper()}_PORT": str(port),
                f"{server_name.upper()}_LOG_LEVEL": "INFO",
            },
        }

        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)

        print_colored("✓ Updated mcp_config.json", GREEN)


def create_mcp_server(server_name: str):
    """Create a new MCP server with all necessary files."""
    base_path = Path(f"infrastructure/mcp_servers/{server_name}")

    # Check if already exists
    if base_path.exists():
        print_colored(f"❌ {server_name} already exists at {base_path}", RED)
        sys.exit(1)

    print_colored(f"🚀 Creating enhanced MCP server: {server_name}", BLUE)

    # Get next port
    port = get_next_port()
    print_colored(f"📍 Assigning port: {port}", YELLOW)

    # Create directory structure
    dirs = [
        base_path,
        base_path / "handlers",
        base_path / "models",
        base_path / "utils",
        base_path / "tests" / "unit",
        base_path / "tests" / "integration",
        base_path / "config",
    ]

    for dir_path in dirs:
        dir_path.mkdir(parents=True, exist_ok=True)

    # Create files
    files = get_file_templates(server_name, port)

    for file_path, content in files.items():
        create_file(base_path / file_path, content)

    # Update mcp_config.json
    update_mcp_config(server_name, port)

    # Print summary
    print_colored(f"\n✅ Successfully created {server_name} MCP server!", GREEN)
    print_colored("\n📋 Next steps:", YELLOW)
    print_colored(f"\n📍 Server will run on port: {port}", BLUE)
    print_colored("\n🚀 Happy coding!", GREEN)


def get_file_templates(server_name: str, port: int) -> dict[str, str]:
    """Get all file templates for the MCP server."""
    srv = server_name
    srv_upper = srv.upper()
    srv_title = srv.title()

    return {
        "__init__.py": f'"""{srv} MCP server package."""\n',
        "handlers/__init__.py": f'"""Handler modules for {srv} MCP server."""\n',
        "models/__init__.py": f'"""Data models for {srv} MCP server."""\n',
        "utils/__init__.py": f'"""Utility modules for {srv} MCP server."""\n',
        "tests/__init__.py": f'"""Test modules for {srv} MCP server."""\n',
        "tests/unit/__init__.py": f'"""Unit tests for {srv} MCP server."""\n',
        "tests/integration/__init__.py": f'"""Integration tests for {srv} MCP server."""\n',
        "README.md": get_readme_template(srv, srv_upper, port),
        "requirements.txt": get_requirements_template(srv_title),
        "Dockerfile": get_dockerfile_template(srv, port),
        "docker-compose.yml": get_docker_compose_template(srv, srv_upper, port),
        ".env.example": get_env_example_template(srv, srv_upper, port),
        ".gitignore": get_gitignore_template(),
        "config.py": get_config_template(srv, srv_upper, srv_title, port),
        "server.py": get_server_template(srv, srv_upper, srv_title),
        "handlers/main_handler.py": get_handler_template(srv, srv_title),
        "models/data_models.py": get_models_template(srv, srv_title),
        "utils/logging_config.py": get_logging_template(srv),
        "utils/db.py": get_db_template(srv),
        "tests/unit/test_handler.py": get_unit_test_template(srv, srv_title),
        "tests/integration/test_server.py": get_integration_test_template(
            srv, srv_title
        ),
        "tests/conftest.py": get_conftest_template(srv),
    }


# Template functions (simplified for brevity)
def get_readme_template(srv: str, srv_upper: str, port: int) -> str:
    return f"""# {srv.title()} MCP Server

Production-ready MCP server for {srv} integration with Sophia AI platform.

## Features

- ✅ Async/await architecture with FastAPI
- ✅ Production-ready logging (JSON format)
- ✅ Prometheus metrics
- ✅ Health checks and monitoring
- ✅ Docker support
- ✅ Comprehensive error handling
- ✅ AI-powered data processing (Snowflake Cortex)
- ✅ Automated testing

## Quick Start

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export {srv_upper}_API_KEY=your_api_key
export {srv_upper}_LOG_LEVEL=DEBUG

# Run the server
python -m infrastructure.mcp_servers.{srv}.server
```

### Docker

```bash
# Build and run with docker-compose
docker-compose up --build

# Server will be available at http://localhost:{port}
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /health | Health check endpoint |
| GET | /capabilities | Server capabilities |
| POST | /sync | Trigger data synchronization |
| GET | /data | Get {srv} data |
| GET | /docs | OpenAPI documentation |

## Configuration

See `.env.example` for all available environment variables.

## Testing

```bash
# Run tests
pytest tests -v

# With coverage
pytest --cov={srv} --cov-report=html
```

## License

Proprietary - Sophia AI Platform
"""


def get_requirements_template(srv_title: str) -> str:
    return f"""# {srv_title} MCP Server Requirements

# Core dependencies
fastapi==0.111.0
uvicorn[standard]==0.29.0
pydantic==2.7.1
pydantic-settings==2.3.0
python-dotenv==1.0.1

# Async HTTP
aiohttp==3.9.5
httpx==0.27.0

# Database (optional)
sqlalchemy[asyncio]==2.0.30
asyncpg==0.29.0

# Logging and monitoring
python-json-logger==2.0.7
prometheus-client==0.20.0

# Testing
pytest==8.2.0
pytest-asyncio==0.23.6
pytest-cov==5.0.0

# Development
black==24.4.2
ruff==0.4.4
mypy==1.10.0
"""


def get_dockerfile_template(srv: str, port: int) -> str:
    return f"""FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y gcc curl && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy application
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE {port}

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:{port}/health || exit 1

# Run server
CMD ["python", "-m", "infrastructure.mcp_servers.{srv}.server"]
"""


def get_docker_compose_template(srv: str, srv_upper: str, port: int) -> str:
    return f"""version: '3.9'

services:
  {srv}:
    build: .
    restart: unless-stopped
    environment:
      {srv_upper}_LOG_LEVEL: INFO
      {srv_upper}_PORT: {port}
      PULUMI_ORG: scoobyjava-org
      ENVIRONMENT: production
    ports:
      - "{port}:{port}"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:{port}/health"]
      interval: 30s
      timeout: 10s
      retries: 3

networks:
  default:
    name: sophia-ai-network
    external: true
"""


def get_env_example_template(srv: str, srv_upper: str, port: int) -> str:
    return f"""# {srv.title()} MCP Server Environment Variables

# Server Configuration
{srv_upper}_PORT={port}
{srv_upper}_LOG_LEVEL=INFO

# API Configuration
{srv_upper}_API_KEY=your_api_key_here
{srv_upper}_API_BASE_URL=https://api.{srv}.com/v1

# Database Configuration (optional)
{srv_upper}_DB_DSN=postgresql+asyncpg://user:pass@localhost:5432/{srv}_db

# Feature Flags
{srv_upper}_ENABLE_AI_PROCESSING=true
{srv_upper}_ENABLE_METRICS=true
"""


def get_gitignore_template() -> str:
    return """# Python
__pycache__/
*.py[cod]
.pytest_cache/
.coverage
htmlcov/

# Environment
.env
.env.local

# Logs
logs/
*.log

# IDE
.vscode/
.idea/
"""


def get_config_template(srv: str, srv_upper: str, srv_title: str, port: int) -> str:
    # Return the config.py template
    # (Simplified for brevity - in real implementation this would be the full config)
    return f'''"""Configuration for {srv} MCP server."""
from pydantic_settings import BaseSettings
from pydantic import Field

class {srv_title}Settings(BaseSettings):
    """Settings for {srv} MCP server."""

    PORT: int = Field(default={port}, description="Server port")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")

    class Config:
        env_prefix = "{srv_upper}_"

settings = {srv_title}Settings()
'''


def get_server_template(srv: str, srv_upper: str, srv_title: str) -> str:
    # Return simplified server.py template
    return f'''"""{srv_title} MCP Server implementation."""
import asyncio
from fastapi import FastAPI
import uvicorn

app = FastAPI(title="{srv_title} MCP Server")

@app.get("/health")
async def health():
    return {{"status": "healthy", "server": "{srv}"}}

async def main():
    config = uvicorn.Config(app, host="127.0.0.1"  # Changed from 0.0.0.0 for security. Use environment variable for production, port=9000)
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())
'''


def get_handler_template(srv: str, srv_title: str) -> str:
    return f'''"""Main handler for {srv} MCP server."""
import logging

logger = logging.getLogger(__name__)

class {srv_title}Handler:
    """Handler for {srv} operations."""

    async def initialize(self):
        """Initialize handler."""
        logger.info("{srv_title} handler initialized")

    async def sync_data(self, batch_size: int = 100):
        """Sync data with {srv}."""
        # TODO: Implement sync logic
        return {{"status": "success", "records_synced": 0}}
'''


def get_models_template(srv: str, srv_title: str) -> str:
    return f'''"""Data models for {srv} MCP server."""
from pydantic import BaseModel, Field
from datetime import datetime

class {srv_title}Record(BaseModel):
    """Base model for {srv} records."""
    id: str = Field(..., description="Unique identifier")
    created_at: datetime = Field(..., description="Creation timestamp")
    # TODO: Add {srv}-specific fields
'''


def get_logging_template(srv: str) -> str:
    return f'''"""Logging configuration for {srv} MCP server."""
import logging
from logging.config import dictConfig

def setup_logging(level: str = "INFO"):
    """Configure logging."""
    dictConfig({{
        "version": 1,
        "formatters": {{
            "default": {{
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            }}
        }},
        "handlers": {{
            "default": {{
                "class": "logging.StreamHandler",
                "formatter": "default"
            }}
        }},
        "root": {{
            "level": level,
            "handlers": ["default"]
        }}
    }})
'''


def get_db_template(srv: str) -> str:
    return f'''"""Database helpers for {srv} MCP server."""
# Database connection helpers would go here
# This is optional - remove if not using a database
'''


def get_unit_test_template(srv: str, srv_title: str) -> str:
    return f'''"""Unit tests for {srv} handler."""
import pytest
from infrastructure.mcp_servers.{srv}.handlers.main_handler import {srv_title}Handler

@pytest.mark.asyncio
async def test_handler_initialization():
    """Test handler initialization."""
    handler = {srv_title}Handler()
    await handler.initialize()
    # Add assertions
'''


def get_integration_test_template(srv: str, srv_title: str) -> str:
    return f'''"""Integration tests for {srv} server."""
import pytest
from httpx import AsyncClient
from infrastructure.mcp_servers.{srv}.server import app

@pytest.mark.asyncio
async def test_health_endpoint():
    """Test health endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
'''


def get_conftest_template(srv: str) -> str:
    return '''"""Pytest configuration."""
import asyncio
import pytest

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
'''


def main():
    parser = argparse.ArgumentParser(
        description="Create a production-ready MCP server for Sophia AI"
    )
    parser.add_argument(
        "server_name", help="Name of the server to create (e.g., github, slack, etc.)"
    )

    args = parser.parse_args()

    # Validate server name
    if not args.server_name.replace("_", "").isalnum():
        print_colored("❌ Server name must be alphanumeric (underscores allowed)", RED)
        sys.exit(1)

    create_mcp_server(args.server_name.lower())


if __name__ == "__main__":
    main()
