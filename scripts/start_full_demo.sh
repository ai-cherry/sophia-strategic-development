#!/usr/bin/env bash
set -euo pipefail

ROOT="$PWD"
FRONTEND_DIR="$ROOT/frontend"
VENV_DIR="$ROOT/.venv"
LOGDIR="$ROOT/logs"
mkdir -p "$LOGDIR"

echo "====== Sophia AI Full Demo Startup ======"
echo "Time: $(date)"
echo "Root: $ROOT"

echo ""
echo "====== 1) Activate Python venv ======"
if [ ! -d "$VENV_DIR" ]; then
    echo "❌ Virtual env not found at $VENV_DIR"
    echo "Run: python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

source "$VENV_DIR/bin/activate"
echo "✅ Python venv activated"

echo ""
echo "====== 2) Start FastAPI backend on port 8000 ======"
if [ -f "$ROOT/backend/app/fastapi_app_enhanced.py" ]; then
    echo "Starting backend with fastapi_app_enhanced.py..."
    uvicorn backend.app.fastapi_app_enhanced:app --reload --port 8000 --log-level info > "$LOGDIR/backend.log" 2>&1 &
    BACKEND_PID=$!
    echo "✅ Backend started (PID: $BACKEND_PID) - logs: $LOGDIR/backend.log"
elif [ -f "$ROOT/backend/app/unified_chat_backend.py" ]; then
    echo "Starting backend with unified_chat_backend.py..."
    uvicorn backend.app.unified_chat_backend:app --reload --port 8000 --log-level info > "$LOGDIR/backend.log" 2>&1 &
    BACKEND_PID=$!
    echo "✅ Backend started (PID: $BACKEND_PID) - logs: $LOGDIR/backend.log"
else
    echo "❌ No FastAPI app found in backend/app/"
    exit 1
fi

echo ""
echo "====== 3) Start React frontend on port 3000 ======"
if [ ! -d "$FRONTEND_DIR" ]; then
    echo "❌ Frontend directory not found at $FRONTEND_DIR"
    exit 1
fi

cd "$FRONTEND_DIR"
if [ ! -f "package.json" ]; then
    echo "❌ No package.json found in frontend"
    exit 1
fi

# Install frontend deps if needed
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

echo "Starting frontend dev server..."
npm run dev > "$LOGDIR/frontend.log" 2>&1 &
FRONTEND_PID=$!
echo "✅ Frontend started (PID: $FRONTEND_PID) - logs: $LOGDIR/frontend.log"

cd "$ROOT"

echo ""
echo "====== 4) Start key MCP servers ======"

# Start base MCP server
if [ -f "mcp-servers/base/unified_standardized_base.py" ]; then
    python mcp-servers/base/unified_standardized_base.py > "$LOGDIR/mcp-base.log" 2>&1 &
    MCP_BASE_PID=$!
    echo "✅ Base MCP server started (PID: $MCP_BASE_PID)"
fi

echo ""
echo "====== 5) Health checks ======"
sleep 8

echo "Checking backend health..."
if curl -f http://localhost:8000/health 2>/dev/null; then
    echo "✅ Backend healthy"
else
    echo "⚠️  Backend not responding yet (may need more time)"
fi

echo "Checking frontend..."
if curl -f http://localhost:3000 2>/dev/null; then
    echo "✅ Frontend healthy"
else
    echo "⚠️  Frontend not responding yet (may need more time)"
fi

echo ""
echo "====== 🚀 SOPHIA AI DEMO READY ======"
echo ""
echo "📊 Backend API:     http://localhost:8000"
echo "📊 API Docs:        http://localhost:8000/docs"
echo "📊 Dashboard:       http://localhost:8000/dashboard"
echo "💬 Simple Chat:     POST http://localhost:8000/chat"
echo "🎨 Frontend:        http://localhost:3000"
echo "🎨 CEO Dashboard:   http://localhost:3000/dashboard/ceo-enhanced"
echo ""
echo "📁 Logs directory:  $LOGDIR"
echo "🔍 Backend logs:    tail -f $LOGDIR/backend.log"
echo "🔍 Frontend logs:   tail -f $LOGDIR/frontend.log"
echo ""
echo "🛑 To stop all services: kill $BACKEND_PID $FRONTEND_PID"
if [ -n "${MCP_BASE_PID:-}" ]; then
    echo "🛑 To stop MCP server: kill $MCP_BASE_PID"
fi
echo ""
echo "Press Ctrl+C to stop monitoring, services will continue running..."

# Monitor logs
trap 'echo "Stopping monitoring..."; exit 0' INT
tail -f "$LOGDIR/backend.log" "$LOGDIR/frontend.log" 2>/dev/null || echo "Monitoring stopped" 