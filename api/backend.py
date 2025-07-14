# Vercel API Handler for Sophia AI Backend
import sys
from pathlib import Path

# Add backend to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import the FastAPI app
from backend.app.unified_chat_backend import app

# Vercel expects a handler
handler = app
