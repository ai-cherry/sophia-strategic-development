#!/bin/bash

# Start Sophia AI Backend

echo "🚀 Starting Sophia AI Backend..."

# Kill any existing process on port 8000
lsof -ti:8000 | xargs kill -9 2>/dev/null || true

# Set environment variables
export ENVIRONMENT=production
export PULUMI_ORG=scoobyjava-org
export PULUMI_STACK=sophia-ai-production

# Start the backend
cd /Users/lynnmusil/sophia-main
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload &

# Store the PID
echo $! > backend.pid

# Wait a moment for startup
sleep 5

# Check if it's running
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend started successfully!"
    echo "📍 Access at: http://localhost:8000"
    echo "📚 API Docs: http://localhost:8000/docs"
else
    echo "❌ Backend failed to start. Check logs."
fi
