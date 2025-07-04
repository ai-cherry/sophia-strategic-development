#!/bin/bash
echo "🎨 Starting Sophia AI Frontend..."
if [ -d "frontend" ]; then
    cd frontend
    npm run dev
else
    echo "❌ Frontend directory not found"
    exit 1
fi
