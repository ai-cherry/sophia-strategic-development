#!/bin/bash
# Universal Virtual Environment Enforcer for Sophia AI
# This script ensures any operation runs in the correct virtual environment

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_PATH="$PROJECT_ROOT/.venv"
VENV_PYTHON="$VENV_PATH/bin/python"

echo "🔧 Ensuring Sophia AI virtual environment..."

# Check if we're in the project root
if [[ ! -f "$PROJECT_ROOT/.envrc" ]]; then
    echo "❌ Not in Sophia AI project root"
    echo "💡 Expected: $PROJECT_ROOT"
    exit 1
fi

# Check if virtual environment exists
if [[ ! -f "$VENV_PYTHON" ]]; then
    echo "❌ Virtual environment not found at $VENV_PATH"
    echo "💡 Creating virtual environment..."
    python3 -m venv "$VENV_PATH"
    echo "💡 Installing dependencies..."
    "$VENV_PYTHON" -m # UV handles package management
    "$VENV_PYTHON" -m pip install -r "$PROJECT_ROOT/requirements.txt"
fi

# Force activation if not already active
if [[ "$VIRTUAL_ENV" != "$VENV_PATH" ]]; then
    echo "🔄 Activating virtual environment..."
    source "$VENV_PATH/bin/activate"
    export PATH="$VENV_PATH/bin:$PATH"
fi

# Validate environment
echo "✅ Virtual environment: $VIRTUAL_ENV"
echo "✅ Python executable: $(which python)"
echo "✅ Working directory: $(pwd)"

# Run the validation script
if [[ -f "$PROJECT_ROOT/scripts/validate_dev_environment.py" ]]; then
    python "$PROJECT_ROOT/scripts/validate_dev_environment.py"
fi

echo "🎉 Environment ready for Sophia AI development!"
