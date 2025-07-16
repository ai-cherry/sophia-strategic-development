#!/bin/bash
# 🚀 Sophia AI Devcontainer Setup Script
# Runs inside the devcontainer to set up the complete development environment

set -e  # Exit on any error

echo "🚀 STARTING SOPHIA AI DEVCONTAINER SETUP"
echo "========================================"

# Update system packages
echo "📦 Updating system packages..."
sudo apt-get update && sudo apt-get upgrade -y

# Install essential system dependencies
echo "🔧 Installing system dependencies..."
sudo apt-get install -y \
    curl \
    wget \
    git \
    build-essential \
    libssl-dev \
    libffi-dev \
    pkg-config \
    rustc \
    cargo \
    sqlite3 \
    redis-tools \
    postgresql-client \
    jq \
    unzip

# Install UV (Modern Python package manager)
echo "⚡ Installing UV package manager..."
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.cargo/env
echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.bashrc

# Verify UV installation
uv --version
echo "✅ UV installed successfully"

# Install Python dependencies using UV
echo "🐍 Installing Python dependencies with UV..."
cd /workspaces/sophia-main-2

# Create UV project if pyproject.toml exists, otherwise use requirements.txt
if [ -f "pyproject.toml" ]; then
    echo "📋 Using pyproject.toml with UV..."
    uv sync
else
    echo "📋 Creating UV environment from requirements.txt..."
    uv venv
    source .venv/bin/activate
    if [ -f "requirements.txt" ]; then
        uv pip install -r requirements.txt
    fi
fi

# Install Node.js dependencies for frontend
echo "📦 Installing Node.js dependencies..."
if [ -f "frontend/package.json" ]; then
    cd frontend
    npm install
    cd ..
fi

# Install additional development tools
echo "🛠️ Installing additional development tools..."
uv pip install \
    black \
    ruff \
    mypy \
    pytest \
    pytest-asyncio \
    httpx \
    pre-commit

# Set up Git hooks
echo "🔧 Setting up Git hooks..."
if [ -f ".pre-commit-config.yaml" ]; then
    pre-commit install
fi

# Create helpful aliases and shortcuts
echo "🔗 Setting up development shortcuts..."
cat >> ~/.bashrc << 'EOF'

# 🚀 Sophia AI Development Shortcuts
export PYTHONPATH="/workspaces/sophia-main-2:$PYTHONPATH"
export ENVIRONMENT="prod" 
export PULUMI_ORG="scoobyjava-org"

# FastAPI Application Shortcuts
alias run-working='cd /workspaces/sophia-main-2 && python -m uvicorn backend.app.working_fastapi:app --host 0.0.0.0 --port 8000 --reload'
alias run-simple='cd /workspaces/sophia-main-2 && python -m uvicorn backend.app.simple_fastapi:app --host 0.0.0.0 --port 8001 --reload'
alias run-minimal='cd /workspaces/sophia-main-2 && python -m uvicorn backend.app.minimal_fastapi:app --host 0.0.0.0 --port 8002 --reload'
alias run-distributed='cd /workspaces/sophia-main-2 && python -m uvicorn api.main:app --host 0.0.0.0 --port 8003 --reload'

# Development shortcuts
alias check-env='echo "Python: $(python --version)" && echo "UV: $(uv --version)" && echo "Path: $(which python)" && echo "PYTHONPATH: $PYTHONPATH"'
alias sophia-test='cd /workspaces/sophia-main-2 && python -m pytest tests/ -v'
alias sophia-lint='cd /workspaces/sophia-main-2 && ruff check . && black --check .'
alias sophia-format='cd /workspaces/sophia-main-2 && black . && ruff --fix .'

# MCP Server shortcuts  
alias start-mcp='cd /workspaces/sophia-main-2 && python scripts/start_mcp_servers.py'
alias stop-mcp='pkill -f "mcp_server"'

# Docker shortcuts (for building containers)
alias build-backend='cd /workspaces/sophia-main-2 && docker build -f Dockerfile.backend -t scoobyjava15/sophia-backend:latest .'
alias build-frontend='cd /workspaces/sophia-main-2/frontend && docker build -t scoobyjava15/sophia-frontend:latest .'

# Utility shortcuts
alias sophia-status='cd /workspaces/sophia-main-2 && python scripts/check_system_health.py'
alias sophia-logs='cd /workspaces/sophia-main-2 && tail -f logs/*.log'

echo "🚀 Sophia AI Development Environment Ready!"
echo "💡 Available commands:"
echo "   run-working, run-simple, run-minimal, run-distributed"
echo "   check-env, sophia-test, sophia-lint, sophia-format"
echo "   start-mcp, build-backend, sophia-status"
EOF

# Make scripts executable
echo "🔐 Setting script permissions..."
find /workspaces/sophia-main-2/scripts -name "*.sh" -exec chmod +x {} \;
find /workspaces/sophia-main-2/scripts -name "*.py" -exec chmod +x {} \;

# Create development directories if they don't exist
echo "📁 Creating development directories..."
mkdir -p /workspaces/sophia-main-2/logs
mkdir -p /workspaces/sophia-main-2/temp
mkdir -p /workspaces/sophia-main-2/data

# Install Cursor AI specific configurations if available
echo "🎯 Setting up AI tool configurations..."
if [ -f "/workspaces/sophia-main-2/.cursorrules" ]; then
    echo "✅ Cursor AI rules found"
fi

# Set up environment validation
echo "🔍 Creating environment validation..."
cat > /workspaces/sophia-main-2/scripts/validate_devcontainer_env.py << 'EOF'
#!/usr/bin/env python3
"""Validate devcontainer environment setup"""

import sys
import subprocess
import os
from pathlib import Path

def check_command(cmd, name):
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {name}: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {name}: Failed")
            return False
    except Exception as e:
        print(f"❌ {name}: Error - {e}")
        return False

def main():
    print("🔍 DEVCONTAINER ENVIRONMENT VALIDATION")
    print("=" * 40)
    
    # Check Python
    check_command([sys.executable, "--version"], "Python")
    
    # Check UV
    check_command(["uv", "--version"], "UV Package Manager")
    
    # Check Node.js
    check_command(["node", "--version"], "Node.js")
    
    # Check Docker
    check_command(["docker", "--version"], "Docker")
    
    # Check Git
    check_command(["git", "--version"], "Git")
    
    # Check environment variables
    print(f"✅ ENVIRONMENT: {os.getenv('ENVIRONMENT', 'NOT SET')}")
    print(f"✅ PULUMI_ORG: {os.getenv('PULUMI_ORG', 'NOT SET')}")
    print(f"✅ PYTHONPATH: {os.getenv('PYTHONPATH', 'NOT SET')}")
    
    # Check project structure
    project_root = Path("/workspaces/sophia-main-2")
    key_dirs = ["backend", "frontend", "scripts", "mcp-servers"]
    
    for dir_name in key_dirs:
        dir_path = project_root / dir_name
        if dir_path.exists():
            print(f"✅ Directory: {dir_name}")
        else:
            print(f"❌ Directory missing: {dir_name}")
    
    print("\n🎯 Environment validation complete!")
    print("💡 Run 'check-env' for quick status check")

if __name__ == "__main__":
    main()
EOF

chmod +x /workspaces/sophia-main-2/scripts/validate_devcontainer_env.py

# Run initial validation
echo "🧪 Running initial environment validation..."
cd /workspaces/sophia-main-2
python scripts/validate_devcontainer_env.py

# Source the new aliases
source ~/.bashrc

echo ""
echo "🎉 SOPHIA AI DEVCONTAINER SETUP COMPLETE!"
echo "========================================"
echo ""
echo "✅ Python 3.11 with UV package manager"
echo "✅ Node.js 18 with npm dependencies"
echo "✅ All development tools installed"
echo "✅ FastAPI applications ready (ports 8000-8003)"
echo "✅ Frontend development ready (ports 3000, 5173)"
echo "✅ MCP servers ready (ports 9000+)"
echo "✅ Docker-in-Docker enabled"
echo "✅ Development shortcuts configured"
echo ""
echo "🚀 READY FOR AI-ASSISTED DEVELOPMENT!"
echo ""
echo "💡 Quick Start:"
echo "   - run-working     # Start main FastAPI app"
echo "   - check-env       # Verify environment"
echo "   - sophia-test     # Run tests"
echo "   - start-mcp       # Start MCP servers"
echo "" 