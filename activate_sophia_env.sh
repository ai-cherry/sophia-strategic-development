#!/bin/bash
# =============================================================================
# SOPHIA AI VIRTUAL ENVIRONMENT ACTIVATION SCRIPT
# =============================================================================
# This script ensures consistent virtual environment usage across all AI coding tools
# including Cursor AI, Cline, and other assistants.
#
# Usage: source activate_sophia_env.sh
# =============================================================================

echo "🚀 Activating Sophia AI Virtual Environment..."

# Store original directory
ORIGINAL_DIR=$(pwd)

# Navigate to project directory if not already there
if [[ ! -f "pyproject.toml" ]] && [[ ! -f ".venv/bin/activate" ]]; then
    if [[ -d "/Users/lynnmusil/sophia-main-2" ]]; then
        cd "/Users/lynnmusil/sophia-main-2"
        echo "📁 Navigated to: $(pwd)"
    else
        echo "❌ ERROR: Cannot find Sophia AI project directory"
        return 1
    fi
fi

# Check if virtual environment exists
if [[ ! -d ".venv" ]]; then
    echo "❌ ERROR: Virtual environment not found in $(pwd)"
    echo "💡 Run: python -m venv .venv"
    return 1
fi

# Remove any conflicting python aliases temporarily
if alias python >/dev/null 2>&1; then
    echo "🔧 Removing conflicting python alias..."
    unalias python 2>/dev/null || true
fi

# Deactivate any existing virtual environment
if [[ -n "$VIRTUAL_ENV" ]]; then
    echo "🔄 Deactivating existing virtual environment..."
    deactivate 2>/dev/null || true
fi

# Activate the virtual environment
echo "🔧 Activating .venv virtual environment..."
source .venv/bin/activate

# Verify activation
if [[ -n "$VIRTUAL_ENV" ]]; then
    echo "✅ VIRTUAL ENVIRONMENT ACTIVATED SUCCESSFULLY"
    echo ""
    echo "📊 Environment Details:"
    echo "   VIRTUAL_ENV: $VIRTUAL_ENV"
    echo "   Python: $(which python)"
    echo "   Python Version: $(python --version)"
    echo "   Pip: $(which pip)"
    echo "   Project Directory: $(pwd)"
    
    # Test critical packages
    echo ""
    echo "🧪 Package Verification:"
    
    if python -c "import fastapi" 2>/dev/null; then
        FASTAPI_VERSION=$(python -c "import fastapi; print(fastapi.__version__)")
        echo "   ✅ FastAPI: $FASTAPI_VERSION"
    else
        echo "   ❌ FastAPI: Not installed"
    fi
    
    if python -c "import uvicorn" 2>/dev/null; then
        UVICORN_VERSION=$(python -c "import uvicorn; print(uvicorn.__version__)")
        echo "   ✅ Uvicorn: $UVICORN_VERSION"
    else
        echo "   ❌ Uvicorn: Not installed"
    fi
    
    if python -c "import sqlalchemy" 2>/dev/null; then
        SQLALCHEMY_VERSION=$(python -c "import sqlalchemy; print(sqlalchemy.__version__)")
        echo "   ✅ SQLAlchemy: $SQLALCHEMY_VERSION"
    else
        echo "   ❌ SQLAlchemy: Not installed"
    fi
    
    echo ""
    echo "🎯 READY FOR AI CODING TOOLS"
    echo "   This environment works with: Cursor AI, Cline, GitHub Copilot, etc."
    echo ""
    
    # Set helpful aliases for this session
    alias run-working="python backend/app/working_fastapi.py"
    alias run-simple="python backend/app/simple_fastapi.py"
    alias run-minimal="python backend/app/minimal_fastapi.py"
    alias run-distributed="python api/main.py"
    alias check-env="python -c 'import sys; print(f\"✅ Using: {sys.executable}\")'"
    
    echo "🔧 Available Shortcuts:"
    echo "   run-working    -> Start working FastAPI (port 8000)"
    echo "   run-simple     -> Start simple FastAPI (port 8001)"
    echo "   run-minimal    -> Start minimal FastAPI (port 8002)"
    echo "   run-distributed -> Start distributed API (port 8003)"
    echo "   check-env      -> Verify Python environment"
    
else
    echo "❌ FAILED to activate virtual environment"
    return 1
fi

# Export environment variable for other tools
export SOPHIA_AI_ENV_ACTIVE="true"
export PYTHONPATH="$PWD:$PYTHONPATH"

echo ""
echo "🌟 SOPHIA AI ENVIRONMENT READY!"
echo "   For AI assistants: Always use 'python' command (not python3)"
echo "   Environment will persist until shell is closed"
echo "" 