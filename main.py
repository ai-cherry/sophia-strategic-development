#!/usr/bin/env python3
"""
Sophia AI - Enterprise AI Orchestration Platform
Main Application Entry Point

This is the canonical entry point for the Sophia AI platform.
It imports and runs the production-ready unified backend.
"""

import logging
import sys
from pathlib import Path

# Set up logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add the current directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))


def main():
    """
    Main entry point for Sophia AI platform.
    
    This function serves as the canonical entry point and delegates
    to the production-ready unified backend implementation.
    """
    try:
        logger.info("🚀 Starting Sophia AI Enterprise Platform...")
        logger.info("📍 Entry Point: main.py (canonical)")
        logger.info("🔗 Backend: sophia_production_unified.py")
        
        # Import and run the production backend
        try:
            import sophia_production_unified
            import uvicorn
            from backend.core.auto_esc_config import get_config_value
            
            # Get the FastAPI app from the unified backend
            app = sophia_production_unified.app
            
            # Configuration
            host = get_config_value("HOST") or "0.0.0.0"
            port = int(get_config_value("PORT") or "8000")
            
            logger.info(f"🌐 Starting server on {host}:{port}")
            
            # Run the server
            uvicorn.run(
                app,
                host=host,
                port=port,
                log_level="info",
                access_log=True,
                reload=False  # Production mode
            )
            
        except ImportError as e:
            logger.error(f"❌ Failed to import required modules: {e}")
            logger.error("🔧 Please ensure all dependencies are installed via requirements.txt")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        sys.exit(1)


async def create_application():
    """
    Create the FastAPI application instance.
    
    This function provides an async interface for creating the app,
    useful for testing and programmatic usage.
    
    Returns:
        FastAPI: The configured application instance
    """
    try:
        import sophia_production_unified
        return sophia_production_unified.app
    except Exception as e:
        logger.error(f"❌ Application creation failed: {e}")
        raise


def get_app():
    """
    Get the FastAPI application instance for ASGI servers.
    
    Returns:
        FastAPI: The configured application instance
    """
    try:
        import sophia_production_unified
        return sophia_production_unified.app
    except Exception as e:
        logger.error(f"❌ Failed to get app: {e}")
        raise


if __name__ == "__main__":
    main()
