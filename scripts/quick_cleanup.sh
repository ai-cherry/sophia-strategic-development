#!/bin/bash
# Quick cleanup script for Python cache files

echo "🧹 Quick Python Cache Cleanup"
echo "============================"

# Count before cleanup
echo "📊 Before cleanup:"
echo "  __pycache__ dirs: $(find . -type d -name "__pycache__" 2>/dev/null | wc -l)"
echo "  .pyc files: $(find . -type f -name "*.pyc" 2>/dev/null | wc -l)"

echo ""
echo "⚠️  This will remove all Python cache files except in .venv"
read -p "Continue? (y/N): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🚀 Starting cleanup..."

    # Remove __pycache__ directories (except in .venv)
    find . -path "./.venv" -prune -o -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null

    # Remove .pyc files (except in .venv)
    find . -path "./.venv" -prune -o -type f -name "*.pyc" -exec rm -f {} + 2>/dev/null

    # Remove extra venvs (preserve main .venv)
    find . -path "./.venv" -prune -o -type d -name "venv" -exec rm -rf {} + 2>/dev/null
    find . -path "./.venv" -prune -o -type d -name ".venv" -exec rm -rf {} + 2>/dev/null

    echo "✅ Cleanup complete!"

    # Count after cleanup
    echo ""
    echo "📊 After cleanup:"
    echo "  __pycache__ dirs: $(find . -type d -name "__pycache__" 2>/dev/null | wc -l)"
    echo "  .pyc files: $(find . -type f -name "*.pyc" 2>/dev/null | wc -l)"
else
    echo "❌ Cleanup cancelled"
fi
