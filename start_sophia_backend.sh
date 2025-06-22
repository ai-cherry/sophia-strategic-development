#!/bin/bash
echo "🧠 Starting Sophia AI Backend..."
source .venv/bin/activate
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload 